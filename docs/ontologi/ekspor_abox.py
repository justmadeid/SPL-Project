"""Ekspor ABox (instance) dari Neo4j ke docs/ontologi/abox.ttl.

ABox = fakta tentang individu:
  - instance referensi yang dimuat saat seed (Sumber, KategoriEkonomi, Dokumen, Rule, ...);
  - pendaftar beserta fakta masukan dan fakta hasil inferensi (satu node terbaru per nama).

Pemetaan Neo4j -> RDF:
  - label Neo4j / relasi INSTANCE_DARI  -> rdf:type
  - properti node                       -> properti data (tipe xsd mengikuti nilai)
  - relasi antar node                   -> properti objek (nama tipe relasi)
  - properti pada relasi (MEMICU.urutan, BERDASARKAN.bagian) -> reifikasi rdf:Statement

Pakai (Neo4j harus menyala, kredensial dibaca dari backend/.env):
  uv run --directory backend --with rdflib python ../docs/ontologi/ekspor_abox.py
"""

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "backend"))

from rdflib import BNode, Graph, Literal, Namespace, URIRef  # noqa: E402
from rdflib.namespace import RDF, RDFS, XSD  # noqa: E402

from app import db  # noqa: E402

KIP = Namespace("http://pintukuliah.local/ontologi#")

# label -> properti kunci yang dipakai untuk IRI individu
KUNCI = {
    "Sumber": "kode", "KategoriEkonomi": "kode", "KondisiKhusus": "kode", "AlasanGugur": "kode",
    "Keputusan": "kode", "Dokumen": "kode", "BiayaPendidikan": "kode", "ZonaBiayaHidup": "zona",
    "Jenjang": "kode", "ProgramProfesi": "kode", "Rule": "id",
}
# label turunan inferensi: dicatat sebagai rdf:type sendiri (rdfs9 menurunkan :Pendaftar dari subkelas)
LABEL_PENDAFTAR = ["Pendaftar", "PendaftarLayak", "PendaftarTidakLayak"]


def slug(teks: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]+", "_", str(teks)).strip("_")


def literal(v):
    if isinstance(v, bool):
        return Literal(v, datatype=XSD.boolean)
    if isinstance(v, int):
        return Literal(v, datatype=XSD.integer)
    if isinstance(v, float):
        return Literal(v, datatype=XSD.decimal)
    return Literal(str(v))


def main():
    g = Graph()
    g.bind("kip", KIP)
    iri = {}  # elementId Neo4j -> IRI

    # Kelas (dipakai sebagai objek KULIAH_DI: PTN / PTS)
    for r in db.run("MATCH (c:Kelas) RETURN elementId(c) AS id, c.nama AS nama"):
        iri[r["id"]] = KIP[r["nama"]]

    # Instance referensi
    for label, kunci in KUNCI.items():
        for r in db.run(f"MATCH (n:{label}) RETURN elementId(n) AS id, properties(n) AS p ORDER BY n.{kunci}"):
            s = KIP[f"{label}_{slug(r['p'][kunci])}"]
            iri[r["id"]] = s
            g.add((s, RDF.type, KIP[label]))
            for k, v in r["p"].items():
                if v is not None and not isinstance(v, list):
                    g.add((s, KIP[k], literal(v)))
            label_teks = r["p"].get("nama") or r["p"].get("teks") or r["p"].get("judul")
            if label_teks:
                g.add((s, RDFS.label, Literal(label_teks)))

    # Pendaftar: node terbaru per nama
    pendaftar = db.run(
        """
        MATCH (p:Pendaftar) WITH p.nama AS nama, p ORDER BY p.dibuat DESC
        WITH nama, collect(p)[0] AS p
        RETURN elementId(p) AS id, labels(p) AS labels, properties(p) AS p ORDER BY nama
        """
    )
    for r in pendaftar:
        s = KIP[f"pendaftar_{slug(r['p']['nama'])}"]
        iri[r["id"]] = s
        for lbl in r["labels"]:
            if lbl in LABEL_PENDAFTAR:
                g.add((s, RDF.type, KIP[lbl]))
        g.add((s, RDFS.label, Literal(r["p"]["nama"])))
        for k, v in r["p"].items():
            if v is None or isinstance(v, list):
                continue
            g.add((s, KIP[k], Literal(v, datatype=XSD.dateTime) if k == "dibuat" else literal(v)))

    # Relasi antar node yang diekspor
    rels = db.run(
        """
        MATCH (a)-[r]->(b)
        WHERE elementId(a) IN $ids AND elementId(b) IN $ids
          AND NOT type(r) IN ['INSTANCE_DARI', 'SUBKELAS_DARI']
        RETURN elementId(a) AS a, type(r) AS t, elementId(b) AS b, properties(r) AS p
        ORDER BY t, coalesce(r.urutan, 0)
        """,
        ids=list(iri),
    )
    for r in rels:
        s, p, o = iri[r["a"]], KIP[r["t"]], iri[r["b"]]
        g.add((s, p, o))
        if r["p"]:
            st = BNode()
            g.add((st, RDF.type, RDF.Statement))
            g.add((st, RDF.subject, s))
            g.add((st, RDF.predicate, p))
            g.add((st, RDF.object, o))
            for k, v in r["p"].items():
                g.add((st, KIP[k], literal(v)))

    keluar = HERE / "abox.ttl"
    kepala = (
        "# ABox ontologi KIP Kuliah (Pintu Kuliah), diekspor dari Neo4j oleh ekspor_abox.py.\n"
        "# Jangan disunting manual; jalankan ulang skripnya. TBox ada di tbox.ttl.\n"
        f"# Isi: {len(KUNCI)} kelas referensi, {len(pendaftar)} pendaftar (node terbaru per nama), {len(rels)} relasi.\n\n"
    )
    keluar.write_text(kepala + g.serialize(format="turtle"), encoding="utf-8")
    print(f"{keluar}: {len(g)} triple")


if __name__ == "__main__":
    main()
