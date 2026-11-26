"""Profil contoh (kasus uji T1–T10 dari Rules-Revisi.md) untuk demo dan presentasi."""

BASE = dict(
    tahun_daftar=2026, tahun_lulus=2025, status_seleksi="Lulus", jenis_kampus="PTN", nama_kampus="",
    akreditasi_prodi="A", jenis_kelas="Reguler", beasiswa_lain=False, kip_sma=False, dtks=False, pkh=False,
    kks=False, terdata_p3ke=False, desil_p3ke=None, panti=False, penghasilan=9_000_000, anggota_keluarga=4,
    sktm=False, bukti_sktm=False, asal_3t=False, asli_papua=False, anak_tki=False, bencana=False, konflik=False,
    korban_kekerasan=False, korban_ham=False, nama_prodi="Informatika", rumpun_prodi="Lainnya", jenjang="Sarjana", zona="C",
)

PRESETS = [
    ("T1", "Rina, pemegang KIP SMA", "Diterima di PTN, punya KIP SMA.",
     dict(nama="Rina Wulandari", kip_sma=True, nama_kampus="Universitas Gadjah Mada", penghasilan=2_500_000)),
    ("T2", "Bayu, KIP SMA di PTS", "Kampus swasta, prodi akreditasi B.",
     dict(nama="Bayu Saputra", jenis_kampus="PTS", kip_sma=True, akreditasi_prodi="B", nama_kampus="Universitas Ahmad Dahlan")),
    ("T3", "Yohana, asli Papua", "Ekonomi keluarga cukup, tetapi orang asli Papua.",
     dict(nama="Yohana Wenda", asli_papua=True, nama_kampus="Universitas Cenderawasih", zona="E")),
    ("T4", "Dimas, kelas karyawan", "Keluarga pemegang KKS, tetapi kuliah di kelas karyawan.",
     dict(nama="Dimas Prakoso", kks=True, jenis_kelas="Karyawan")),
    ("T5", "Salsa, penerima beasiswa APBD", "Punya KIP SMA dan sudah menerima beasiswa pemda.",
     dict(nama="Salsabila Putri", kip_sma=True, beasiswa_lain=True)),
    ("T6", "Arif, salah input tahun", "Tahun lulus setelah tahun pendaftaran.",
     dict(nama="Arif Hidayat", tahun_lulus=2027)),
    ("T7", "Nanda, punya SKTM", "PTS, penghasilan Rp5 juta untuk 5 orang, punya SKTM.",
     dict(nama="Nanda Lestari", jenis_kampus="PTS", penghasilan=5_000_000, anggota_keluarga=5, sktm=True, bukti_sktm=True,
          akreditasi_prodi="Baik_Sekali")),
    ("T8", "Fajar, P3KE dan panti", "Terdata P3KE desil 2 sekaligus anak panti asuhan.",
     dict(nama="Fajar Ramadhan", terdata_p3ke=True, desil_p3ke=2, panti=True, penghasilan=0, anggota_keluarga=1)),
    ("T9", "Putri, lulus 2022", "Punya KIP SMA, tetapi lulus 4 tahun lalu.",
     dict(nama="Putri Maharani", tahun_lulus=2022, kip_sma=True)),
    ("T10", "Gilang, calon dokter", "Kedokteran akreditasi Unggul, keluarga terdata DTKS.",
     dict(nama="Gilang Permana", akreditasi_prodi="Unggul", nama_prodi="Pendidikan Dokter", rumpun_prodi="Kedokteran",
          dtks=True, penghasilan=3_200_000, nama_kampus="Universitas Airlangga", zona="D")),
]


def daftar():
    return [{"kode": k, "judul": j, "deskripsi": d, "data": {**BASE, **x}} for k, j, d, x in PRESETS]
