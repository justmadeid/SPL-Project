"""Mesin inferensi forward chaining di atas Neo4j + perakitan hasil & penjelasan."""

import re
import uuid
from datetime import datetime, timezone

from . import db
from .rules import ASAL_TURUNAN, RULES, LAPIS, cypher

INPUT_FIELDS = [
    "nama", "tahun_daftar", "tahun_lulus", "status_seleksi", "jenis_kampus", "nama_kampus", "akreditasi_prodi",
    "jenis_kelas", "beasiswa_lain", "kip_sma", "dtks", "pkh", "kks", "terdata_p3ke", "desil_p3ke", "panti",
    "penghasilan", "anggota_keluarga", "sktm", "bukti_sktm", "asal_3t", "asli_papua", "anak_tki", "bencana",
    "konflik", "korban_kekerasan", "korban_ham", "nama_prodi", "rumpun_prodi", "jenjang", "zona",
]

_COMPILED = [(r, cypher(r)) for r in RULES]


def infer(pid: str) -> int:
    """Jalankan rule per strata sampai tidak ada rule baru yang menyala (fixpoint)."""
    urutan = 0
    for strata in sorted({r["strata"] for r in RULES}):
        while True:
            fired = False
            for r, q in _COMPILED:
                if r["strata"] != strata:
                    continue
                res = db.run(q, pid=pid, rid=r["id"], urutan=urutan + 1)
                if res and res[0]["n"] > 0:
                    urutan += 1
                    fired = True
            if not fired:
                break
    return urutan


DERIVED_PROPS = [
    "selisih_tahun", "tingkat_akreditasi", "prodi_terakreditasi", "penerima_bansos", "rentan_p3ke",
    "miskin_penghasilan", "miskin_sktm", "syarat_tahun_ok", "status_administrasi", "prioritas",
    "kategori_ekonomi", "kategori_nama", "kondisi_khusus", "keputusan", "jalur",
]


def _tautkan_ontologi(pid: str):
    db.run(
        "MATCH (p:Pendaftar {id: $pid}) "
        "WITH p MATCH (c:Kelas {nama: 'Pendaftar'}) MERGE (p)-[:INSTANCE_DARI]->(c) "
        "WITH p OPTIONAL MATCH (k:Kelas {nama: p.jenis_kampus}) "
        "FOREACH (_ IN CASE WHEN k IS NULL THEN [] ELSE [1] END | MERGE (p)-[:KULIAH_DI]->(k))",
        pid=pid,
    )


def inferensi_ulang_semua() -> int:
    """Dipanggil setelah ontologi/aturan dimuat ulang: hapus fakta turunan lama lalu jalankan ulang inferensi."""
    ids = [r["id"] for r in db.run("MATCH (p:Pendaftar) RETURN p.id AS id")]
    for pid in ids:
        db.run(
            "MATCH (p:Pendaftar {id: $pid}) OPTIONAL MATCH (p)-[e]->() DELETE e "
            "WITH DISTINCT p REMOVE p:PendaftarLayak:PendaftarTidakLayak "
            + "".join(f" REMOVE p.{k}" for k in DERIVED_PROPS),
            pid=pid,
        )
        _tautkan_ontologi(pid)
        infer(pid)
    return len(ids)


def evaluasi(data: dict, pratinjau: bool = False) -> dict:
    pid = uuid.uuid4().hex[:12]
    props = {k: data.get(k) for k in INPUT_FIELDS}
    if not props.get("terdata_p3ke"):
        props["desil_p3ke"] = None
    db.run(
        "CREATE (p:Pendaftar {id: $pid}) SET p += $props, p.dibuat = $ts",
        pid=pid, props=props, ts=datetime.now(timezone.utc).isoformat(),
    )
    _tautkan_ontologi(pid)
    infer(pid)
    h = hasil(pid)
    if pratinjau:
        db.run("MATCH (p:Pendaftar {id: $pid}) DETACH DELETE p", pid=pid)
    return h


def hasil(pid: str) -> dict | None:
    rows = db.run(
        """
        MATCH (p:Pendaftar {id: $pid})
        OPTIONAL MATCH (p)-[:BERKATEGORI]->(kat:KategoriEkonomi)
        RETURN p {.*} AS p, kat {.*} AS kategori,
          [(p)-[:COCOK_PRIORITAS]->(k) | k {.*}] AS cocok,
          [(p)-[:GUGUR_KARENA]->(a) | a {.*}] AS gugur,
          [(p)-[:MEMILIKI_KONDISI]->(k) | k {.*}] AS kondisi,
          [(p)-[:WAJIB_MENYERAHKAN]->(d) | d {.*}] AS dokumen,
          [(p)-[:MENDAPAT]->(b:BiayaPendidikan) | b {.*}] AS ukt,
          [(p)-[:MENDAPAT]->(z:ZonaBiayaHidup) | z {.*}] AS zona,
          [(p)-[:MENDAPAT]->(j:Jenjang) | j {.*}] AS jenjang,
          [(p)-[:MENDAPAT]->(x:ProgramProfesi) | x {.*}] AS profesi
        """,
        pid=pid,
    )
    if not rows:
        return None
    row = rows[0]
    p = row["p"]
    trace = db.run(
        """
        MATCH (p:Pendaftar {id: $pid})-[m:MEMICU]->(r:Rule)
        OPTIONAL MATCH (r)-[b:BERDASARKAN]->(s:Sumber)
        WITH m, r, collect(CASE WHEN s IS NULL THEN NULL ELSE {kode: s.kode, judul: s.judul, bagian: b.bagian} END) AS sumber
        RETURN m.urutan AS urutan, r.id AS id, r.lapis AS lapis, r.lapis_nama AS lapis_nama, r.nama AS nama,
               r.jika AS jika, r.maka AS maka, m.kesimpulan AS kesimpulan, sumber
        ORDER BY urutan
        """,
        pid=pid,
    )
    for t in trace:  # format angka rupiah dari Cypher: "Rp 3200000" -> "Rp3.200.000"
        t["turunan"] = ASAL_TURUNAN.get(t["id"])
        t["kesimpulan"] = re.sub(r"Rp ?(\d{4,})", lambda mm: "Rp" + f"{int(mm.group(1)):,}".replace(",", "."), t["kesimpulan"])
    dok_order = ["DOK-AKUN", "DOK-KIP", "DOK-BANSOS", "DOK-P3KE", "DOK-PANTI", "DOK-PENGHASILAN", "DOK-SKTM", "DOK-KHUSUS"]
    dokumen = sorted(row["dokumen"], key=lambda d: dok_order.index(d["kode"]) if d["kode"] in dok_order else 99)
    zona = row["zona"][0] if row["zona"] else None
    return {
        "id": pid,
        "input": {k: p.get(k) for k in INPUT_FIELDS},
        "dibuat": p.get("dibuat"),
        "keputusan": p.get("keputusan"),
        "jalur": p.get("jalur"),
        "status_administrasi": p.get("status_administrasi"),
        "prioritas": p.get("prioritas"),
        "kategori": row["kategori"],
        "cocok_prioritas": sorted(row["cocok"], key=lambda k: k["prioritas"]),
        "alasan_gugur": sorted(row["gugur"], key=lambda a: a["kode"]),
        "kondisi_khusus": row["kondisi"],
        "dokumen": dokumen,
        "manfaat": {
            "ukt": row["ukt"][0] if row["ukt"] else None,
            "biaya_hidup": ({**zona, "per_semester": zona["per_bulan"] * 6} if zona else None),
            "jenjang": row["jenjang"][0] if row["jenjang"] else None,
            "profesi": row["profesi"][0] if row["profesi"] else None,
        },
        "trace": trace,
    }


def graf_pendaftar(pid: str) -> dict:
    """Subgraf kasus: pendaftar, konsep yang terhubung, rule yang menyala, dan sumbernya."""
    rows = db.run(
        """
        MATCH (p:Pendaftar {id: $pid})
        OPTIONAL MATCH (p)-[rel]->(n) WHERE NOT n:Kelas OR type(rel) = 'KULIAH_DI'
        WITH p, collect({rel: type(rel), node: n}) AS out
        OPTIONAL MATCH (p)-[:MEMICU]->(:Rule)-[:BERDASARKAN]->(s:Sumber)
        WITH p, out, collect(DISTINCT s) AS sumber
        OPTIONAL MATCH (p)-[:MEMICU]->(r:Rule)-[:BERDASARKAN]->(s2:Sumber)
        RETURN p, out, sumber, collect(DISTINCT {r: r.id, s: s2.kode}) AS rs
        """,
        pid=pid,
    )
    if not rows:
        return {"nodes": [], "links": []}
    row = rows[0]
    p = row["p"]
    nodes = {f"P:{pid}": {"id": f"P:{pid}", "label": p.get("nama") or "Pendaftar", "group": "Pendaftar"}}
    links = []
    for o in row["out"]:
        n = o["node"]
        if n is None:
            continue
        nid, label, group = _ident(n)
        nodes.setdefault(nid, {"id": nid, "label": label, "group": group})
        links.append({"source": f"P:{pid}", "target": nid, "label": o["rel"]})
    for s in row["sumber"]:
        nid, label, group = _ident(s)
        nodes.setdefault(nid, {"id": nid, "label": label, "group": group})
    for x in row["rs"]:
        if x["r"] and x["s"]:
            links.append({"source": f"Rule:{x['r']}", "target": f"Sumber:{x['s']}", "label": "BERDASARKAN"})
    return {"nodes": list(nodes.values()), "links": links}


def _ident(n: dict) -> tuple[str, str, str]:
    # Driver mengembalikan properti node sebagai dict; tebak jenisnya dari kuncinya.
    if "jika" in n:
        return f"Rule:{n['id']}", n["id"], "Rule"
    if "penerbit" in n:
        return f"Sumber:{n['kode']}", n["kode"], "Sumber"
    if "prioritas" in n:
        return f"Kat:{n['kode']}", f"Prioritas {n['prioritas']}", "KategoriEkonomi"
    if "properti" in n:
        return f"KK:{n['kode']}", n["nama"], "KondisiKhusus"
    if "teks" in n:
        return f"AG:{n['kode']}", n["teks"], "AlasanGugur"
    if "per_bulan" in n:
        return f"Zona:{n['zona']}", f"Zona {n['zona']}", "Manfaat"
    if "maks" in n:
        return f"UKT:{n['kode']}", n["nama"], "Manfaat"
    if "maks_semester" in n:
        return f"M:{n['kode']}", n["nama"], "Manfaat"
    if "keterangan" in n:
        return f"Dok:{n['kode']}", n["nama"], "Dokumen"
    if "deskripsi" in n:
        return f"Kelas:{n['nama']}", n["nama"], "Kelas"
    if n.get("kode") in ("LAYAK", "TIDAK_LAYAK"):
        return f"Kep:{n['kode']}", n["nama"], "Keputusan"
    return f"X:{n.get('kode', id(n))}", str(n.get("nama", n.get("kode", "?"))), "Lain"


def graf_ontologi() -> dict:
    rows = db.run(
        """
        MATCH (a)-[rel]->(b)
        WHERE NOT a:Pendaftar AND NOT b:Pendaftar AND type(rel) <> 'INSTANCE_DARI'
        RETURN a, type(rel) AS rel, b
        """
    )
    inst = db.run(
        """
        MATCH (a)-[:INSTANCE_DARI]->(c:Kelas) WHERE NOT a:Pendaftar AND NOT a:Rule
        RETURN a, c
        """
    )
    nodes, links = {}, []
    for r in rows:
        ia, la, ga = _ident(r["a"])
        ib, lb, gb = _ident(r["b"])
        nodes.setdefault(ia, {"id": ia, "label": la, "group": ga})
        nodes.setdefault(ib, {"id": ib, "label": lb, "group": gb})
        links.append({"source": ia, "target": ib, "label": r["rel"]})
    for r in inst:
        ia, la, ga = _ident(r["a"])
        ic, lc, gc = _ident(r["c"])
        nodes.setdefault(ia, {"id": ia, "label": la, "group": ga})
        nodes.setdefault(ic, {"id": ic, "label": lc, "group": gc})
        links.append({"source": ia, "target": ic, "label": "INSTANCE_DARI"})
    return {"nodes": list(nodes.values()), "links": links}


def daftar_aturan() -> list[dict]:
    rows = db.run(
        """
        MATCH (r:Rule)
        OPTIONAL MATCH (r)-[b:BERDASARKAN]->(s:Sumber)
        WITH r, collect(CASE WHEN s IS NULL THEN NULL ELSE {kode: s.kode, judul: s.judul, bagian: b.bagian} END) AS sumber
        RETURN r.id AS id, r.lapis AS lapis, r.lapis_nama AS lapis_nama, r.strata AS strata, r.nama AS nama,
               r.jika AS jika, r.maka AS maka, sumber
        ORDER BY r.urut
        """
    )
    for r in rows:
        r["turunan"] = ASAL_TURUNAN.get(r["id"])
    return rows


def lapis() -> dict:
    return LAPIS


def statistik() -> dict:
    row = db.run(
        """
        MATCH (n) WITH count(n) AS nodes
        MATCH ()-[e]->() WITH nodes, count(e) AS rels
        OPTIONAL MATCH (r:Rule) WITH nodes, rels, count(r) AS rules
        OPTIONAL MATCH (p:Pendaftar) RETURN nodes, rels, rules, count(p) AS pendaftar
        """
    )
    return row[0] if row else {}
