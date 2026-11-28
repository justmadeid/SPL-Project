"""Ontologi (TBox + instance referensi) KIP Kuliah yang disimpan di Neo4j.

Kelas dimodelkan sebagai node :Kelas dengan relasi :SUBKELAS_DARI (hierarki seperti
rdfs:subClassOf). Setiap instance referensi juga diberi label Neo4j sesuai kelasnya,
sehingga keanggotaan kelas bisa di-query langsung (mis. MATCH (k:KategoriEkonomi)).
"""

from . import db
from .rules import RULES, LAPIS


def rp(n: int) -> str:
    return "Rp " + f"{n:,}".replace(",", ".")


SUMBER = [
    {"kode": "PED", "judul": "Pedoman Pendaftaran KIP Kuliah 2025 v1.0", "penerbit": "Kemdiktisaintek", "tahun": 2025},
    {"kode": "PS", "judul": "Persesjen Kemendikbudristek No. 13 Tahun 2023 tentang Juklak PIP Pendidikan Tinggi", "penerbit": "Kemendikbudristek", "tahun": 2023},
    {"kode": "PM", "judul": "Permendikbud No. 10 Tahun 2020 tentang Program Indonesia Pintar", "penerbit": "Kemendikbud", "tahun": 2020},
]

# (nama kelas, superkelas, deskripsi)
KELAS = [
    ("Entitas", None, "Akar hierarki ontologi KIP Kuliah"),
    ("Pendaftar", "Entitas", "Calon mahasiswa yang dinilai kelayakannya"),
    ("PendaftarLayak", "Pendaftar", "Pendaftar yang disimpulkan layak menerima KIP Kuliah"),
    ("PendaftarTidakLayak", "Pendaftar", "Pendaftar yang disimpulkan tidak layak"),
    ("PerguruanTinggi", "Entitas", "Perguruan tinggi tujuan"),
    ("PTN", "PerguruanTinggi", "Perguruan Tinggi Negeri"),
    ("PTS", "PerguruanTinggi", "Perguruan Tinggi Swasta"),
    ("KategoriEkonomi", "Entitas", "Urutan prioritas ekonomi penerima KIP Kuliah"),
    ("KondisiKhusus", "Entitas", "Kondisi afirmasi / pertimbangan khusus"),
    ("AlasanGugur", "Entitas", "Alasan pendaftar gugur di tahap administrasi"),
    ("Keputusan", "Entitas", "Keputusan akhir kelayakan"),
    ("Dokumen", "Entitas", "Dokumen yang wajib diserahkan"),
    ("Manfaat", "Entitas", "Komponen manfaat KIP Kuliah"),
    ("BiayaPendidikan", "Manfaat", "Batas biaya pendidikan (UKT/SPP) per semester"),
    ("ZonaBiayaHidup", "Manfaat", "Klaster bantuan biaya hidup per wilayah kampus"),
    ("Jenjang", "Manfaat", "Jenjang studi dan masa pemberian beasiswa"),
    ("ProgramProfesi", "Manfaat", "Program profesi lanjutan setelah sarjana"),
    ("Rule", "Entitas", "Aturan IF-THEN dari pakar / regulasi"),
    ("Sumber", "Entitas", "Sumber pengetahuan (regulasi resmi)"),
]

KATEGORI = [
    {"kode": "P1", "prioritas": 1, "nama": "Pemegang KIP SMA di PTN", "kampus": "PTN", "dokumen": "DOK-KIP"},
    {"kode": "P2", "prioritas": 2, "nama": "Terdata DTKS / penerima bansos di PTN", "kampus": "PTN", "dokumen": "DOK-BANSOS"},
    {"kode": "P3", "prioritas": 3, "nama": "Pemegang KIP SMA di PTS", "kampus": "PTS", "dokumen": "DOK-KIP"},
    {"kode": "P4", "prioritas": 4, "nama": "Terdata DTKS / penerima bansos di PTS", "kampus": "PTS", "dokumen": "DOK-BANSOS"},
    {"kode": "P5", "prioritas": 5, "nama": "Miskin/rentan miskin P3KE desil 1–3 di PTN", "kampus": "PTN", "dokumen": "DOK-P3KE"},
    {"kode": "P6", "prioritas": 6, "nama": "Miskin/rentan miskin P3KE desil 1–3 di PTS", "kampus": "PTS", "dokumen": "DOK-P3KE"},
    {"kode": "P7", "prioritas": 7, "nama": "Berasal dari panti sosial / panti asuhan", "kampus": None, "dokumen": "DOK-PANTI"},
    {"kode": "P8", "prioritas": 8, "nama": "Miskin/rentan miskin dengan bukti penghasilan atau SKTM", "kampus": None, "dokumen": None},
]

KONDISI = [
    {"kode": "K-3T", "properti": "asal_3t", "nama": "Berasal dari daerah 3T"},
    {"kode": "K-PAPUA", "properti": "asli_papua", "nama": "Orang asli Papua"},
    {"kode": "K-TKI", "properti": "anak_tki", "nama": "Anak TKI di daerah perbatasan"},
    {"kode": "K-BENCANA", "properti": "bencana", "nama": "Terdampak bencana alam"},
    {"kode": "K-KONFLIK", "properti": "konflik", "nama": "Terdampak konflik sosial"},
    {"kode": "K-KEKERASAN", "properti": "korban_kekerasan", "nama": "Korban kekerasan"},
    {"kode": "K-HAM", "properti": "korban_ham", "nama": "Korban pelanggaran HAM berat"},
]

ALASAN = [
    {"kode": "B-02", "teks": "Lulus lebih dari 2 tahun sebelum tahun pendaftaran"},
    {"kode": "B-03", "teks": "Tahun lulus setelah tahun pendaftaran (data tidak valid)"},
    {"kode": "B-04", "teks": "Belum/tidak lulus seleksi masuk perguruan tinggi"},
    {"kode": "B-05", "teks": "Program studi belum terakreditasi"},
    {"kode": "B-06", "teks": "Diterima di kelas eksekutif, khusus, atau karyawan"},
    {"kode": "B-07", "teks": "Sedang menerima beasiswa atau bantuan biaya pendidikan lain"},
]

KEPUTUSAN = [
    {"kode": "LAYAK", "nama": "Layak menerima KIP Kuliah"},
    {"kode": "TIDAK_LAYAK", "nama": "Belum memenuhi syarat KIP Kuliah"},
]

DOKUMEN = [
    {"kode": "DOK-AKUN", "nama": "NIK, NISN, dan NPSN yang valid di Dapodik, serta email aktif", "keterangan": "Untuk membuat akun di laman KIP Kuliah"},
    {"kode": "DOK-KIP", "nama": "Kartu KIP Pendidikan Menengah (KIP SMA)", "keterangan": "Bukti prioritas 1 atau 3"},
    {"kode": "DOK-BANSOS", "nama": "Bukti terdata DTKS, kartu KKS, atau bukti kepesertaan PKH", "keterangan": "Bukti prioritas 2 atau 4"},
    {"kode": "DOK-P3KE", "nama": "Bukti terdata P3KE desil 1–3", "keterangan": "Bukti prioritas 5 atau 6"},
    {"kode": "DOK-PANTI", "nama": "Surat keterangan dari panti sosial / panti asuhan", "keterangan": "Bukti prioritas 7"},
    {"kode": "DOK-PENGHASILAN", "nama": "Slip gaji atau surat keterangan penghasilan orang tua/wali, dan kartu keluarga", "keterangan": "Bukti prioritas 8 (penghasilan)"},
    {"kode": "DOK-SKTM", "nama": "SKTM desa/kelurahan, rekening listrik, dan foto rumah", "keterangan": "Bukti prioritas 8 (SKTM)"},
    {"kode": "DOK-KHUSUS", "nama": "Surat keterangan pemerintah daerah/instansi berwenang sesuai kondisi khusus", "keterangan": "3T, orang asli Papua, anak TKI, bencana, konflik, atau korban kekerasan/HAM"},
]

BIAYA_PENDIDIKAN = [
    {"kode": "UKT-1", "tingkat": 1, "kedokteran": False, "maks": 8_000_000, "nama": "Akreditasi Unggul/A/Internasional (non-kedokteran)"},
    {"kode": "UKT-1K", "tingkat": 1, "kedokteran": True, "maks": 12_000_000, "nama": "Akreditasi Unggul/A/Internasional (kedokteran)"},
    {"kode": "UKT-2", "tingkat": 2, "kedokteran": False, "maks": 4_000_000, "nama": "Akreditasi Baik Sekali/B"},
    {"kode": "UKT-3", "tingkat": 3, "kedokteran": False, "maks": 2_400_000, "nama": "Akreditasi Baik/C"},
]

ZONA = [
    {"zona": "A", "per_bulan": 800_000},
    {"zona": "B", "per_bulan": 950_000},
    {"zona": "C", "per_bulan": 1_100_000},
    {"zona": "D", "per_bulan": 1_250_000},
    {"zona": "E", "per_bulan": 1_400_000},
]

JENJANG = [
    {"kode": "Sarjana", "nama": "Sarjana (S1)", "maks_semester": 8},
    {"kode": "Diploma_IV", "nama": "Diploma IV", "maks_semester": 8},
    {"kode": "Diploma_III", "nama": "Diploma III", "maks_semester": 6},
    {"kode": "Diploma_II", "nama": "Diploma II", "maks_semester": 4},
    {"kode": "Diploma_I", "nama": "Diploma I", "maks_semester": 2},
]

PROFESI = [
    {"kode": "PRO-DOKTER", "rumpun": "Kedokteran", "nama": "Profesi Dokter", "maks_semester": 4},
    {"kode": "PRO-DRG", "rumpun": "Kedokteran_Gigi", "nama": "Profesi Dokter Gigi", "maks_semester": 4},
    {"kode": "PRO-DRH", "rumpun": "Kedokteran_Hewan", "nama": "Profesi Dokter Hewan", "maks_semester": 4},
    {"kode": "PRO-NERS", "rumpun": "Keperawatan", "nama": "Profesi Ners", "maks_semester": 2},
    {"kode": "PRO-APT", "rumpun": "Farmasi", "nama": "Profesi Apoteker", "maks_semester": 2},
    {"kode": "PRO-BIDAN", "rumpun": "Kebidanan", "nama": "Profesi Bidan", "maks_semester": 2},
    {"kode": "PRO-PPG", "rumpun": "Kependidikan", "nama": "Pendidikan Profesi Guru", "maks_semester": 2},
]


def _add(label: str, rows: list[dict], key: str = "kode"):
    db.run(
        f"""
        UNWIND $rows AS row
        CREATE (n:{label}) SET n = row
        WITH n
        MATCH (c:Kelas {{nama: $label}})
        MERGE (n)-[:INSTANCE_DARI]->(c)
        """,
        rows=rows,
        label=label,
    )


def seed():
    """Bangun ulang ontologi + basis aturan. Data :Pendaftar tidak disentuh."""
    db.run("MATCH (n) WHERE NOT n:Pendaftar AND NOT n:SeedKunci DETACH DELETE n")
    db.run("CREATE CONSTRAINT pendaftar_id IF NOT EXISTS FOR (p:Pendaftar) REQUIRE p.id IS UNIQUE")
    db.run("CREATE CONSTRAINT rule_id IF NOT EXISTS FOR (r:Rule) REQUIRE r.id IS UNIQUE")

    db.run(
        """
        UNWIND $rows AS row
        CREATE (:Kelas {nama: row[0], deskripsi: row[2]})
        """,
        rows=KELAS,
    )
    db.run(
        """
        UNWIND $rows AS row
        WITH row WHERE row[1] IS NOT NULL
        MATCH (c:Kelas {nama: row[0]}), (s:Kelas {nama: row[1]})
        MERGE (c)-[:SUBKELAS_DARI]->(s)
        """,
        rows=KELAS,
    )

    _add("Sumber", SUMBER)
    _add("KategoriEkonomi", [{k: v for k, v in r.items() if k not in ("kampus", "dokumen")} for r in KATEGORI])
    _add("KondisiKhusus", KONDISI)
    _add("AlasanGugur", ALASAN)
    _add("Keputusan", KEPUTUSAN)
    _add("Dokumen", DOKUMEN)
    _add("BiayaPendidikan", BIAYA_PENDIDIKAN)
    _add("ZonaBiayaHidup", ZONA)
    _add("Jenjang", JENJANG)
    _add("ProgramProfesi", PROFESI)

    # Relasi antar konsep
    db.run(
        """
        UNWIND $rows AS row
        MATCH (k:KategoriEkonomi {kode: row.kode})
        OPTIONAL MATCH (c:Kelas {nama: row.kampus})
        OPTIONAL MATCH (d:Dokumen {kode: row.dokumen})
        FOREACH (_ IN CASE WHEN c IS NULL THEN [] ELSE [1] END | MERGE (k)-[:BERLAKU_DI]->(c))
        FOREACH (_ IN CASE WHEN d IS NULL THEN [] ELSE [1] END | MERGE (k)-[:MEMBUTUHKAN]->(d))
        """,
        rows=KATEGORI,
    )
    db.run(
        """
        MATCH (k:KategoriEkonomi {kode: 'P8'}), (d:Dokumen) WHERE d.kode IN ['DOK-PENGHASILAN', 'DOK-SKTM']
        MERGE (k)-[:MEMBUTUHKAN]->(d)
        """
    )
    db.run(
        """
        MATCH (k:KondisiKhusus), (d:Dokumen {kode: 'DOK-KHUSUS'}) MERGE (k)-[:MEMBUTUHKAN]->(d)
        """
    )

    # Basis aturan
    db.run(
        """
        UNWIND $rows AS row
        CREATE (r:Rule {id: row.id, lapis: row.lapis, lapis_nama: row.lapis_nama, strata: row.strata,
                        nama: row.nama, jika: row.jika, maka: row.maka, urut: row.urut})
        WITH r, row
        MATCH (c:Kelas {nama: 'Rule'}) MERGE (r)-[:INSTANCE_DARI]->(c)
        WITH r, row
        UNWIND row.sumber AS s
        MATCH (src:Sumber {kode: s.kode})
        MERGE (r)-[b:BERDASARKAN]->(src) SET b.bagian = s.bagian
        """,
        rows=[
            {
                "id": r["id"], "lapis": r["lapis"], "lapis_nama": LAPIS[r["lapis"]], "strata": r["strata"],
                "nama": r["nama"], "jika": r["jika"], "maka": r["maka"], "urut": i,
                "sumber": [{"kode": k, "bagian": b} for k, b in r["sumber"]],
            }
            for i, r in enumerate(RULES)
        ],
    )
    # Rule -> konsep yang disimpulkan (untuk visualisasi graf pengetahuan)
    for r in RULES:
        for label, key, val in r.get("target", []):
            db.run(
                f"MATCH (r:Rule {{id: $id}}), (t:{label} {{{key}: $val}}) MERGE (r)-[:MENYIMPULKAN]->(t)",
                id=r["id"], val=val,
            )
