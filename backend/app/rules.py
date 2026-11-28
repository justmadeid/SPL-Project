"""Basis aturan IF-THEN sistem pakar KIP Kuliah (lihat Expert Project/Rules-Revisi.md).

Setiap rule punya:
  cond : potongan WHERE Cypher atas node pendaftar `p` (bagian IF)
  act  : potongan Cypher yang menambah fakta baru (bagian THEN). Harus membiarkan `p` dan `r` tetap
         dalam scope (pakai `WITH p, r ...` bila perlu MATCH tambahan).
  kes  : ekspresi Cypher untuk teks kesimpulan yang dicatat di jejak penalaran.

Mesin inferensi (engine.py) menjalankan rule per strata secara forward chaining sampai fixpoint.
Setiap rule paling banyak menyala sekali per pendaftar dan meninggalkan relasi
(p)-[:MEMICU {urutan, kesimpulan}]->(r:Rule) sebagai jejak penjelasan.
"""

LAPIS = {
    "A": "Fakta pembantu",
    "B": "Validasi administrasi",
    "C": "Prioritas ekonomi",
    "D": "Kondisi khusus",
    "E": "Keputusan akhir",
    "F": "Dokumen wajib",
    "G": "Besaran & jangka waktu",
}

KONDISI_PROPS = ["asal_3t", "asli_papua", "anak_tki", "bencana", "konflik", "korban_kekerasan", "korban_ham"]


def rp(n: int) -> str:
    return "Rp " + f"{n:,}".replace(",", ".")


def q(s: str) -> str:
    """Literal string Cypher."""
    return "'" + s.replace("\\", "\\\\").replace("'", "\\'") + "'"


RULES: list[dict] = []

# Asal aturan yang tidak merujuk regulasi secara langsung. Hanya keterangan untuk penjelasan
# (halaman Aturan, Jejak, asisten); tidak dipakai mesin inferensi dan tidak disimpan di Neo4j.
ASAL_TURUNAN: dict[str, str] = {
    "B-03": "Validasi data (asumsi sistem): tahun lulus tidak boleh setelah tahun daftar; melengkapi B-02",
    "B-09": "Aturan turunan dari B-02–B-07: gugur jika ada minimal satu alasan gugur",
    "C-10": "Negasi C-01–C-08 (negation as failure): tidak ada prioritas ekonomi yang cocok",
    "D-02": "Negasi D-01 (negation as failure): tidak ada kondisi khusus",
    "E-01": "Aturan turunan dari B-09: gugur administrasi berarti tidak layak",
    "E-04": "Aturan turunan dari C-10 dan D-02: tidak ada prioritas ekonomi maupun kondisi khusus",
}


def rule(id, strata, nama, jika, maka, sumber, cond, act="", kes=None, target=()):
    RULES.append({
        "id": id, "lapis": id[0], "strata": strata, "nama": nama, "jika": jika, "maka": maka,
        "sumber": list(sumber), "cond": cond, "act": act, "kes": kes or q(maka), "target": list(target),
    })


LAYAK = "p.keputusan = 'Layak'"

# ---------------------------------------------------------------- Lapis A: fakta pembantu
rule("A-01", 1, "Selisih tahun lulus",
     "Tahun daftar dan tahun lulus SMA diketahui",
     "Selisih_Tahun = Tahun_Daftar − Tahun_Lulus_SMA",
     [("PED", "hal. 9 butir 2")],
     "p.tahun_daftar IS NOT NULL AND p.tahun_lulus IS NOT NULL",
     "SET p.selisih_tahun = p.tahun_daftar - p.tahun_lulus",
     "'Selisih tahun daftar dan tahun lulus = ' + toString(p.selisih_tahun) + ' tahun'")

for rid, nilai, tingkat, label in [
    ("A-02", ["Unggul", "A", "Internasional"], 1, "Unggul / A / Internasional"),
    ("A-03", ["Baik_Sekali", "B"], 2, "Baik Sekali / B"),
    ("A-04", ["Baik", "C"], 3, "Baik / C"),
]:
    rule(rid, 1, f"Peringkat akreditasi tingkat {tingkat}",
         f"Akreditasi prodi ∈ {{{label}}}",
         f"Prodi terakreditasi, peringkat tingkat {tingkat}",
         [("PED", "hal. 8")],
         f"p.akreditasi_prodi IN {nilai}",
         f"SET p.tingkat_akreditasi = {tingkat}, p.prodi_terakreditasi = true",
         q(f"Prodi terakreditasi ({label}) → peringkat tingkat {tingkat}"))

rule("A-05", 1, "Prodi belum terakreditasi",
     "Akreditasi prodi = Belum terakreditasi", "Prodi_Terakreditasi = False",
     [("PED", "hal. 9 butir 1")],
     "p.akreditasi_prodi = 'Belum_Terakreditasi'",
     "SET p.prodi_terakreditasi = false")

rule("A-06", 1, "Penerima bansos Kemensos",
     "Terdata DTKS ATAU penerima PKH ATAU pemegang KKS", "Penerima_Bansos = True",
     [("PS", "Bab I huruf C angka 1b(1)–(3)")],
     "coalesce(p.dtks, false) OR coalesce(p.pkh, false) OR coalesce(p.kks, false)",
     "SET p.penerima_bansos = true",
     "'Keluarga tercatat sebagai penerima bansos (' + "
     "substring(CASE WHEN coalesce(p.dtks,false) THEN ', DTKS' ELSE '' END + "
     "CASE WHEN coalesce(p.pkh,false) THEN ', PKH' ELSE '' END + "
     "CASE WHEN coalesce(p.kks,false) THEN ', KKS' ELSE '' END, 2) + ')'")

rule("A-07", 1, "Rentan miskin P3KE",
     "Terdata P3KE DAN desil ≤ 3", "Rentan_Miskin_P3KE = True",
     [("PED", "hal. 11 butir 5–6"), ("PS", "Bab I huruf C angka 1b(4)")],
     "coalesce(p.terdata_p3ke, false) AND p.desil_p3ke IS NOT NULL AND p.desil_p3ke <= 3",
     "SET p.rentan_p3ke = true",
     "'Terdata P3KE pada desil ' + toString(p.desil_p3ke) + ' (batas desil 3)'")

rule("A-08", 1, "Miskin berdasarkan penghasilan",
     f"Penghasilan gabungan ≤ {rp(4_000_000)} ATAU penghasilan / anggota keluarga ≤ {rp(750_000)}",
     "Miskin_Penghasilan = True",
     [("PED", "hal. 12 butir 8a"), ("PS", "Bab I huruf C angka 1b(6)")],
     "p.penghasilan IS NOT NULL AND (p.penghasilan <= 4000000 OR "
     "(coalesce(p.anggota_keluarga, 0) >= 1 AND toFloat(p.penghasilan) / p.anggota_keluarga <= 750000))",
     "SET p.miskin_penghasilan = true",
     "'Penghasilan gabungan Rp ' + toString(p.penghasilan) + '/bulan, per kapita Rp ' + "
     "CASE WHEN coalesce(p.anggota_keluarga,0) >= 1 THEN toString(toInteger(p.penghasilan / p.anggota_keluarga)) ELSE '-' END + "
     "' → memenuhi batas miskin/rentan miskin'")

rule("A-09", 1, "Miskin berdasarkan SKTM",
     "Memiliki SKTM DAN bukti dukung (rekening listrik + foto rumah)", "Miskin_SKTM = True",
     [("PED", "hal. 12 butir 8b")],
     "coalesce(p.sktm, false) AND coalesce(p.bukti_sktm, false)",
     "SET p.miskin_sktm = true",
     q("Memiliki SKTM desa/kelurahan beserta bukti dukung"))

# ---------------------------------------------------------------- Lapis B: administrasi
rule("B-01", 2, "Tahun lulus memenuhi",
     "0 ≤ Selisih_Tahun ≤ 2", "Syarat_Tahun_Lulus = Terpenuhi",
     [("PED", "hal. 9 butir 2")],
     "p.selisih_tahun >= 0 AND p.selisih_tahun <= 2",
     "SET p.syarat_tahun_ok = true",
     "'Lulus ' + toString(p.selisih_tahun) + ' tahun sebelum pendaftaran (maks 2 tahun) → memenuhi'")

for rid, nama, jika, cond, sumber in [
    ("B-02", "Gugur: melebihi batas tahun lulus", "Selisih_Tahun > 2", "p.selisih_tahun > 2", [("PED", "hal. 9 butir 2")]),
    ("B-03", "Gugur: data tahun tidak valid", "Selisih_Tahun < 0", "p.selisih_tahun < 0", []),
    ("B-04", "Gugur: tidak lulus seleksi PT", "Status seleksi PT = Tidak lulus", "p.status_seleksi = 'Tidak_Lulus'", [("PED", "hal. 9 butir 1")]),
    ("B-05", "Gugur: prodi belum terakreditasi", "Prodi_Terakreditasi = False", "p.prodi_terakreditasi = false",
     [("PED", "hal. 9 butir 1"), ("PS", "Bab I huruf D angka 3c")]),
    ("B-06", "Gugur: bukan kelas reguler", "Jenis kelas ∈ {Eksekutif, Khusus, Karyawan}",
     "p.jenis_kelas IN ['Eksekutif', 'Khusus', 'Karyawan']", [("PS", "Bab I huruf D angka 3i")]),
    ("B-07", "Gugur: menerima beasiswa lain", "Sedang menerima beasiswa APBN/APBD/sumber lain",
     "coalesce(p.beasiswa_lain, false)", [("PS", "Bab I huruf D angka 3h")]),
]:
    rule(rid, 2, nama, jika, "Tambah Alasan_Gugur", sumber, cond,
         f"WITH p, r MATCH (a:AlasanGugur {{kode: '{rid}'}}) MERGE (p)-[:GUGUR_KARENA]->(a)",
         "'Gugur: ' + a.teks", target=[("AlasanGugur", "kode", rid)])

rule("B-08", 3, "Administrasi memenuhi syarat",
     "Tahun lulus terpenuhi DAN lulus seleksi DAN prodi terakreditasi DAN kelas reguler "
     "DAN tidak menerima beasiswa lain DAN tidak ada Alasan_Gugur",
     "Status_Administrasi = Memenuhi_Syarat",
     [("PED", "hal. 9"), ("PS", "Bab I huruf D angka 3")],
     "p.syarat_tahun_ok = true AND p.status_seleksi = 'Lulus' AND p.prodi_terakreditasi = true "
     "AND p.jenis_kelas = 'Reguler' AND NOT coalesce(p.beasiswa_lain, false) AND NOT (p)-[:GUGUR_KARENA]->()",
     "SET p.status_administrasi = 'Memenuhi_Syarat'",
     q("Semua syarat administrasi terpenuhi"))

rule("B-09", 3, "Administrasi tidak memenuhi syarat",
     "Ada minimal satu Alasan_Gugur", "Status_Administrasi = Tidak_Memenuhi_Syarat", [],
     "(p)-[:GUGUR_KARENA]->()",
     "SET p.status_administrasi = 'Tidak_Memenuhi_Syarat' WITH p, r MATCH (p)-[:GUGUR_KARENA]->(a) WITH p, r, count(a) AS n",
     "'Gugur administrasi karena ' + toString(n) + ' alasan'")

# ---------------------------------------------------------------- Lapis C: prioritas ekonomi
PRIORITAS = [
    ("C-01", 1, "KIP SMA di PTN", "Memiliki KIP SMA DAN kampus PTN", "coalesce(p.kip_sma, false) AND p.jenis_kampus = 'PTN'", "hal. 10 butir 1"),
    ("C-02", 2, "DTKS/bansos di PTN", "Penerima_Bansos DAN kampus PTN", "p.penerima_bansos = true AND p.jenis_kampus = 'PTN'", "hal. 10 butir 2"),
    ("C-03", 3, "KIP SMA di PTS", "Memiliki KIP SMA DAN kampus PTS", "coalesce(p.kip_sma, false) AND p.jenis_kampus = 'PTS'", "hal. 10 butir 3"),
    ("C-04", 4, "DTKS/bansos di PTS", "Penerima_Bansos DAN kampus PTS", "p.penerima_bansos = true AND p.jenis_kampus = 'PTS'", "hal. 10 butir 4"),
    ("C-05", 5, "P3KE desil ≤ 3 di PTN", "Rentan_Miskin_P3KE DAN kampus PTN", "p.rentan_p3ke = true AND p.jenis_kampus = 'PTN'", "hal. 11 butir 5"),
    ("C-06", 6, "P3KE desil ≤ 3 di PTS", "Rentan_Miskin_P3KE DAN kampus PTS", "p.rentan_p3ke = true AND p.jenis_kampus = 'PTS'", "hal. 11 butir 6"),
    ("C-07", 7, "Panti sosial/asuhan", "Berasal dari panti sosial/asuhan (PTN atau PTS)", "coalesce(p.panti, false)", "hal. 11 butir 7"),
    ("C-08", 8, "Miskin/rentan miskin terbukti", "Miskin_Penghasilan ATAU Miskin_SKTM",
     "coalesce(p.miskin_penghasilan, false) OR coalesce(p.miskin_sktm, false)", "hal. 12 butir 8"),
]
for rid, k, nama, jika, cond, hal in PRIORITAS:
    rule(rid, 2, f"Prioritas {k}: {nama}", jika, f"Memenuhi_Prioritas += {k}", [("PED", hal)], cond,
         f"WITH p, r MATCH (k:KategoriEkonomi {{kode: 'P{k}'}}) MERGE (p)-[:COCOK_PRIORITAS]->(k)",
         f"'Cocok dengan prioritas {k}: ' + k.nama", target=[("KategoriEkonomi", "kode", f"P{k}")])

rule("C-09", 3, "Tetapkan kategori ekonomi",
     "Ada minimal satu prioritas yang cocok", "Kategori_Ekonomi = Prioritas MIN(k)",
     [("PED", "hal. 10–12 (urutan prioritas)")],
     "(p)-[:COCOK_PRIORITAS]->()",
     "WITH p, r MATCH (p)-[:COCOK_PRIORITAS]->(k:KategoriEkonomi) WITH p, r, k ORDER BY k.prioritas ASC LIMIT 1 "
     "SET p.prioritas = k.prioritas, p.kategori_ekonomi = k.kode, p.kategori_nama = k.nama "
     "MERGE (p)-[:BERKATEGORI]->(k)",
     "'Kategori ekonomi: Prioritas ' + toString(p.prioritas) + ' (' + p.kategori_nama + ')'")

rule("C-10", 3, "Tidak memenuhi syarat ekonomi",
     "Tidak ada prioritas yang cocok", "Kategori_Ekonomi = Tidak_Memenuhi_Syarat_Ekonomi", [],
     "NOT (p)-[:COCOK_PRIORITAS]->()",
     "SET p.kategori_ekonomi = 'Tidak_Memenuhi'",
     q("Tidak cocok dengan prioritas ekonomi mana pun"))

# ---------------------------------------------------------------- Lapis D: kondisi khusus
rule("D-01", 2, "Ada kondisi khusus",
     "3T ATAU asli Papua ATAU anak TKI perbatasan ATAU bencana ATAU konflik ATAU korban kekerasan ATAU korban HAM",
     "Status_Kondisi_Khusus = Ya",
     [("PS", "Bab I huruf C angka 1c–1f"), ("PED", "hal. 5")],
     "any(f IN " + str(KONDISI_PROPS) + " WHERE coalesce(p[f], false))",
     "SET p.kondisi_khusus = true WITH p, r MATCH (k:KondisiKhusus) WHERE coalesce(p[k.properti], false) "
     "MERGE (p)-[:MEMILIKI_KONDISI]->(k) WITH p, r, collect(k.nama) AS nm",
     "'Kondisi khusus: ' + reduce(s = '', x IN nm | s + CASE WHEN s = '' THEN '' ELSE ', ' END + x)")

rule("D-02", 3, "Tidak ada kondisi khusus",
     "Semua flag kondisi khusus bernilai False", "Status_Kondisi_Khusus = Tidak", [],
     "NOT any(f IN " + str(KONDISI_PROPS) + " WHERE coalesce(p[f], false))",
     "SET p.kondisi_khusus = false",
     q("Tidak memiliki kondisi khusus"))

# ---------------------------------------------------------------- Lapis E: keputusan
def _putus(kode, label, jalur_expr):
    return (f"SET p.keputusan = {q('Layak' if kode == 'LAYAK' else 'Tidak_Layak')}, p.jalur = {jalur_expr}, p:{label} "
            f"WITH p, r MATCH (k:Keputusan {{kode: '{kode}'}}) MERGE (p)-[:DIPUTUSKAN]->(k)")

rule("E-01", 4, "Tidak layak: gugur administrasi",
     "Status_Administrasi = Tidak_Memenuhi_Syarat", "Keputusan_Akhir = Tidak_Layak", [],
     "p.status_administrasi = 'Tidak_Memenuhi_Syarat'",
     _putus("TIDAK_LAYAK", "PendaftarTidakLayak", "'Gugur administrasi'"),
     q("Tidak layak karena gugur di tahap administrasi"), target=[("Keputusan", "kode", "TIDAK_LAYAK")])

rule("E-02", 4, "Layak: jalur ekonomi",
     "Administrasi memenuhi DAN kategori ekonomi Prioritas 1–8", "Keputusan_Akhir = Layak (jalur ekonomi)",
     [("PED", "hal. 9 butir 3")],
     "p.status_administrasi = 'Memenuhi_Syarat' AND p.prioritas IS NOT NULL",
     _putus("LAYAK", "PendaftarLayak", "'Ekonomi – Prioritas ' + toString(p.prioritas)"),
     "'Layak melalui jalur ekonomi Prioritas ' + toString(p.prioritas)", target=[("Keputusan", "kode", "LAYAK")])

rule("E-03", 4, "Layak: jalur kondisi khusus",
     "Administrasi memenuhi DAN tidak memenuhi syarat ekonomi DAN ada kondisi khusus",
     "Keputusan_Akhir = Layak (pertimbangan khusus)",
     [("PS", "Bab I huruf C angka 1b (dan/atau pertimbangan khusus)")],
     "p.status_administrasi = 'Memenuhi_Syarat' AND p.kategori_ekonomi = 'Tidak_Memenuhi' AND p.kondisi_khusus = true",
     _putus("LAYAK", "PendaftarLayak", "'Pertimbangan khusus'"),
     q("Layak melalui jalur pertimbangan khusus (afirmasi)"), target=[("Keputusan", "kode", "LAYAK")])

rule("E-04", 4, "Tidak layak: ekonomi & kondisi khusus",
     "Administrasi memenuhi DAN tidak memenuhi syarat ekonomi DAN tidak ada kondisi khusus",
     "Keputusan_Akhir = Tidak_Layak", [],
     "p.status_administrasi = 'Memenuhi_Syarat' AND p.kategori_ekonomi = 'Tidak_Memenuhi' AND p.kondisi_khusus = false",
     _putus("TIDAK_LAYAK", "PendaftarTidakLayak", "'Tidak memenuhi kriteria ekonomi'"),
     q("Tidak layak: tidak memenuhi kriteria ekonomi maupun kondisi khusus"), target=[("Keputusan", "kode", "TIDAK_LAYAK")])

# ---------------------------------------------------------------- Lapis F: dokumen
DOK_RULES = [
    ("F-00", "Data akun pendaftaran", "Keputusan = Layak", LAYAK, "DOK-AKUN", [("PED", "hal. 18"), ("PS", "Bab I huruf D angka 3c")]),
    ("F-01", "Dokumen prioritas 1/3", "Layak DAN Prioritas ∈ {1, 3}", f"{LAYAK} AND p.prioritas IN [1, 3]", "DOK-KIP", [("PED", "hal. 10")]),
    ("F-02", "Dokumen prioritas 2/4", "Layak DAN Prioritas ∈ {2, 4}", f"{LAYAK} AND p.prioritas IN [2, 4]", "DOK-BANSOS", [("PED", "hal. 10")]),
    ("F-03", "Dokumen prioritas 5/6", "Layak DAN Prioritas ∈ {5, 6}", f"{LAYAK} AND p.prioritas IN [5, 6]", "DOK-P3KE", [("PED", "hal. 11")]),
    ("F-04", "Dokumen prioritas 7", "Layak DAN Prioritas = 7", f"{LAYAK} AND p.prioritas = 7", "DOK-PANTI", [("PED", "hal. 11")]),
    ("F-05", "Dokumen prioritas 8 (penghasilan)", "Layak DAN Prioritas = 8 DAN Miskin_Penghasilan",
     f"{LAYAK} AND p.prioritas = 8 AND p.miskin_penghasilan = true", "DOK-PENGHASILAN", [("PED", "hal. 12 butir 8a")]),
    ("F-06", "Dokumen prioritas 8 (SKTM)", "Layak DAN Prioritas = 8 DAN Miskin_SKTM",
     f"{LAYAK} AND p.prioritas = 8 AND p.miskin_sktm = true", "DOK-SKTM", [("PED", "hal. 12 butir 8b")]),
    ("F-09", "Dokumen kondisi khusus", "Layak DAN Status_Kondisi_Khusus = Ya",
     f"{LAYAK} AND p.kondisi_khusus = true", "DOK-KHUSUS", [("PS", "Bab I huruf C angka 1c–1f")]),
]
for rid, nama, jika, cond, dok, sumber in DOK_RULES:
    rule(rid, 5, nama, jika, f"Wajib_Dokumen += {dok}", sumber, cond,
         f"WITH p, r MATCH (d:Dokumen {{kode: '{dok}'}}) MERGE (p)-[:WAJIB_MENYERAHKAN]->(d)",
         "'Wajib menyiapkan: ' + d.nama", target=[("Dokumen", "kode", dok)])

# ---------------------------------------------------------------- Lapis G: manfaat
UKT = [
    ("G-01", "UKT-1", 8_000_000, "Tingkat_1 DAN prodi bukan Kedokteran", "p.tingkat_akreditasi = 1 AND coalesce(p.rumpun_prodi, '') <> 'Kedokteran'"),
    ("G-02", "UKT-1K", 12_000_000, "Tingkat_1 DAN prodi Kedokteran", "p.tingkat_akreditasi = 1 AND p.rumpun_prodi = 'Kedokteran'"),
    ("G-03", "UKT-2", 4_000_000, "Tingkat_2", "p.tingkat_akreditasi = 2"),
    ("G-04", "UKT-3", 2_400_000, "Tingkat_3", "p.tingkat_akreditasi = 3"),
]
for rid, kode, maks, jika, cond in UKT:
    rule(rid, 5, f"Biaya pendidikan maks {rp(maks)}", f"Layak DAN {jika}",
         f"Beasiswa_Kuliah = maks {rp(maks)} / semester",
         [("PED", "hal. 8"), ("PS", "Bab III, Komponen Pembiayaan angka 1b")],
         f"{LAYAK} AND {cond}",
         f"WITH p, r MATCH (b:BiayaPendidikan {{kode: '{kode}'}}) MERGE (p)-[:MENDAPAT]->(b)",
         q(f"Biaya pendidikan ditanggung maks {rp(maks)} per semester"), target=[("BiayaPendidikan", "kode", kode)])

for i, (zona, per_bulan) in enumerate([("A", 800_000), ("B", 950_000), ("C", 1_100_000), ("D", 1_250_000), ("E", 1_400_000)]):
    rid = f"G-0{5 + i}"
    rule(rid, 5, f"Biaya hidup zona {zona}", f"Layak DAN zona kampus = {zona}",
         f"Beasiswa_Biaya_Hidup = {rp(per_bulan)} / bulan ({rp(per_bulan * 6)} / semester)",
         [("PED", "hal. 7 dan 14")],
         f"{LAYAK} AND p.zona = '{zona}'",
         f"WITH p, r MATCH (z:ZonaBiayaHidup {{zona: '{zona}'}}) MERGE (p)-[:MENDAPAT]->(z)",
         q(f"Biaya hidup zona {zona}: {rp(per_bulan)}/bulan, dicairkan {rp(per_bulan * 6)} per semester"),
         target=[("ZonaBiayaHidup", "zona", zona)])

for i, (kode, nama, maks) in enumerate([("Sarjana", "Sarjana", 8), ("Diploma_IV", "Diploma IV", 8), ("Diploma_III", "Diploma III", 6),
                                         ("Diploma_II", "Diploma II", 4), ("Diploma_I", "Diploma I", 2)]):
    rid = f"G-{10 + i}"
    rule(rid, 5, f"Masa beasiswa {nama}", f"Layak DAN jenjang = {nama}",
         f"Masa_Beasiswa_Maks = {maks} semester", [("PED", "hal. 15")],
         f"{LAYAK} AND p.jenjang = '{kode}'",
         f"WITH p, r MATCH (j:Jenjang {{kode: '{kode}'}}) MERGE (p)-[:MENDAPAT]->(j)",
         q(f"Beasiswa diberikan maksimal {maks} semester ({nama})"), target=[("Jenjang", "kode", kode)])

for i, (rumpun, kode, nama, maks) in enumerate([
    ("Kedokteran", "PRO-DOKTER", "Profesi Dokter", 4), ("Kedokteran_Gigi", "PRO-DRG", "Profesi Dokter Gigi", 4),
    ("Kedokteran_Hewan", "PRO-DRH", "Profesi Dokter Hewan", 4), ("Keperawatan", "PRO-NERS", "Profesi Ners", 2),
    ("Farmasi", "PRO-APT", "Profesi Apoteker", 2), ("Kebidanan", "PRO-BIDAN", "Profesi Bidan", 2),
    ("Kependidikan", "PRO-PPG", "Pendidikan Profesi Guru", 2),
]):
    rid = f"G-{15 + i}"
    rule(rid, 5, f"Lanjut {nama}", f"Layak DAN jenjang Sarjana DAN rumpun prodi = {rumpun.replace('_', ' ')}",
         f"Dapat dilanjutkan ke {nama}, maks {maks} semester",
         [("PED", "hal. 15"), ("PS", "Bab I huruf D angka 3e")],
         f"{LAYAK} AND p.jenjang = 'Sarjana' AND p.rumpun_prodi = '{rumpun}'",
         f"WITH p, r MATCH (x:ProgramProfesi {{kode: '{kode}'}}) MERGE (p)-[:MENDAPAT]->(x)",
         q(f"Setelah sarjana dapat dilanjutkan ke {nama} maks {maks} semester (selama tetap penerima KIP Kuliah)"),
         target=[("ProgramProfesi", "kode", kode)])


def cypher(r: dict) -> str:
    return f"""
    MATCH (p:Pendaftar {{id: $pid}})
    MATCH (r:Rule {{id: $rid}})
    WHERE NOT (p)-[:MEMICU]->(r) AND ({r['cond']})
    {r['act']}
    MERGE (p)-[m:MEMICU]->(r)
    SET m.urutan = $urutan, m.kesimpulan = {r['kes']}
    RETURN count(*) AS n
    """
