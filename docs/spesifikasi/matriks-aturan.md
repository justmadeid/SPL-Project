# Matriks aturan dan status tinjauan

Inventaris di bawah berasal dari basis aturan pada baseline c776a7c. Sumber adalah rujukan yang tercatat pada kode, bukan hasil verifikasi baru terhadap regulasi. Kondisi dan hasil tetap mencerminkan perilaku aktif. Semua 63 ID sudah tersedia; tidak semua merupakan konsep baru.

## Cara membaca status

- Baseline: dipertahankan sebagai perilaku pembanding, belum disahkan sebagai regulasi terkini.
- K02–K06: interpretasi domain terbuka, lihat daftar keputusan.
- V: perubahan prasyarat validasi/kelengkapan yang diusulkan, belum diterapkan.
- Sumber kosong: aturan teknis/komposisi; harus dijelaskan sebagai derivasi sistem, bukan diberi kutipan yang dibuat-buat.

Lapis: A=9, B=9, C=10, D=2, E=4, F=8, G=21. F-07/F-08 tidak didefinisikan pada revisi.

## Inventaris

| ID | Padanan lama | Kondisi aktif | Hasil aktif | Sumber tercatat | Tinjauan |
|---|---|---|---|---|---|
| A-01 | R-01 | Tahun daftar dan tahun lulus SMA diketahui | Selisih_Tahun = Tahun_Daftar − Tahun_Lulus_SMA | PED hal. 9 butir 2 | V |
| A-02 | R-01/R-03 dan R-21–R-24 | Akreditasi prodi ∈ {Unggul / A / Internasional} | Prodi terakreditasi, peringkat tingkat 1 | PED hal. 8 | K05 |
| A-03 | R-01/R-03 dan R-21–R-24 | Akreditasi prodi ∈ {Baik Sekali / B} | Prodi terakreditasi, peringkat tingkat 2 | PED hal. 8 | Baseline |
| A-04 | R-01/R-03 dan R-21–R-24 | Akreditasi prodi ∈ {Baik / C} | Prodi terakreditasi, peringkat tingkat 3 | PED hal. 8 | Baseline |
| A-05 | R-01/R-03 dan R-21–R-24 | Akreditasi prodi = Belum terakreditasi | Prodi_Terakreditasi = False | PED hal. 9 butir 1 | Baseline |
| A-06 | R-05/R-07 | Terdata DTKS ATAU penerima PKH ATAU pemegang KKS | Penerima_Bansos = True | PS Bab I huruf C angka 1b(1)–(3) | Baseline |
| A-07 | R-08/R-09 | Terdata P3KE DAN desil ≤ 3 | Rentan_Miskin_P3KE = True | PED hal. 11 butir 5–6; PS Bab I huruf C angka 1b(4) | V |
| A-08 | R-11 | Penghasilan gabungan ≤ Rp 4.000.000 ATAU penghasilan / anggota keluarga ≤ Rp 750.000 | Miskin_Penghasilan = True | PED hal. 12 butir 8a; PS Bab I huruf C angka 1b(6) | V |
| A-09 | Tambahan / pemecahan baru | Memiliki SKTM DAN bukti dukung (rekening listrik + foto rumah) | Miskin_SKTM = True | PED hal. 12 butir 8b | K02 |
| B-01 | R-01 | 0 ≤ Selisih_Tahun ≤ 2 | Syarat_Tahun_Lulus = Terpenuhi | PED hal. 9 butir 2 | Baseline |
| B-02 | R-02 | Selisih_Tahun > 2 | Tambah Alasan_Gugur | PED hal. 9 butir 2 | Baseline |
| B-03 | Tambahan / pemecahan baru | Selisih_Tahun < 0 | Tambah Alasan_Gugur | Derivasi teknis; tanpa kutipan langsung | V |
| B-04 | R-03 | Status seleksi PT = Tidak lulus | Tambah Alasan_Gugur | PED hal. 9 butir 1 | Baseline |
| B-05 | R-03 | Prodi_Terakreditasi = False | Tambah Alasan_Gugur | PED hal. 9 butir 1; PS Bab I huruf D angka 3c | Baseline |
| B-06 | Tambahan / pemecahan baru | Jenis kelas ∈ {Eksekutif, Khusus, Karyawan} | Tambah Alasan_Gugur | PS Bab I huruf D angka 3i | Baseline |
| B-07 | Tambahan / pemecahan baru | Sedang menerima beasiswa APBN/APBD/sumber lain | Tambah Alasan_Gugur | PS Bab I huruf D angka 3h | K04 |
| B-08 | R-01 | Tahun lulus terpenuhi DAN lulus seleksi DAN prodi terakreditasi DAN kelas reguler DAN tidak menerima beasiswa lain DAN tidak ada Alasan_Gugur | Status_Administrasi = Memenuhi_Syarat | PED hal. 9; PS Bab I huruf D angka 3 | V |
| B-09 | R-02/R-03 | Ada minimal satu Alasan_Gugur | Status_Administrasi = Tidak_Memenuhi_Syarat | Derivasi teknis; tanpa kutipan langsung | Baseline |
| C-01 | R-04 | Memiliki KIP SMA DAN kampus PTN | Memenuhi_Prioritas += 1 | PED hal. 10 butir 1 | Baseline |
| C-02 | R-05 | Penerima_Bansos DAN kampus PTN | Memenuhi_Prioritas += 2 | PED hal. 10 butir 2 | Baseline |
| C-03 | R-06 | Memiliki KIP SMA DAN kampus PTS | Memenuhi_Prioritas += 3 | PED hal. 10 butir 3 | Baseline |
| C-04 | R-07 | Penerima_Bansos DAN kampus PTS | Memenuhi_Prioritas += 4 | PED hal. 10 butir 4 | Baseline |
| C-05 | R-08 | Rentan_Miskin_P3KE DAN kampus PTN | Memenuhi_Prioritas += 5 | PED hal. 11 butir 5 | Baseline |
| C-06 | R-09 | Rentan_Miskin_P3KE DAN kampus PTS | Memenuhi_Prioritas += 6 | PED hal. 11 butir 6 | Baseline |
| C-07 | R-10 | Berasal dari panti sosial/asuhan (PTN atau PTS) | Memenuhi_Prioritas += 7 | PED hal. 11 butir 7 | Baseline |
| C-08 | R-11 | Miskin_Penghasilan ATAU Miskin_SKTM | Memenuhi_Prioritas += 8 | PED hal. 12 butir 8 | K02 |
| C-09 | Tambahan / pemecahan baru | Ada minimal satu prioritas yang cocok | Kategori_Ekonomi = Prioritas MIN(k) | PED hal. 10–12 (urutan prioritas) | Baseline |
| C-10 | R-12 | Tidak ada prioritas yang cocok | Kategori_Ekonomi = Tidak_Memenuhi_Syarat_Ekonomi | Derivasi teknis; tanpa kutipan langsung | V |
| D-01 | R-13 | 3T ATAU asli Papua ATAU anak TKI perbatasan ATAU bencana ATAU konflik ATAU korban kekerasan ATAU korban HAM | Status_Kondisi_Khusus = Ya | PS Bab I huruf C angka 1c–1f; PED hal. 5 | K03 |
| D-02 | R-14 | Semua flag kondisi khusus bernilai False | Status_Kondisi_Khusus = Tidak | Derivasi teknis; tanpa kutipan langsung | V |
| E-01 | R-15 | Status_Administrasi = Tidak_Memenuhi_Syarat | Keputusan_Akhir = Tidak_Layak | Derivasi teknis; tanpa kutipan langsung | Baseline |
| E-02 | R-16/R-17 | Administrasi memenuhi DAN kategori ekonomi Prioritas 1–8 | Keputusan_Akhir = Layak (jalur ekonomi) | PED hal. 9 butir 3 | Baseline |
| E-03 | R-19 | Administrasi memenuhi DAN tidak memenuhi syarat ekonomi DAN ada kondisi khusus | Keputusan_Akhir = Layak (pertimbangan khusus) | PS Bab I huruf C angka 1b (dan/atau pertimbangan khusus) | K03 |
| E-04 | R-18/R-20 | Administrasi memenuhi DAN tidak memenuhi syarat ekonomi DAN tidak ada kondisi khusus | Keputusan_Akhir = Tidak_Layak | Derivasi teknis; tanpa kutipan langsung | Baseline |
| F-00 | Tambahan / pemecahan baru | Keputusan = Layak | Wajib_Dokumen += DOK-AKUN | PED hal. 18; PS Bab I huruf D angka 3c | Baseline |
| F-01 | R-16 | Layak DAN Prioritas ∈ {1, 3} | Wajib_Dokumen += DOK-KIP | PED hal. 10 | Baseline |
| F-02 | R-16 | Layak DAN Prioritas ∈ {2, 4} | Wajib_Dokumen += DOK-BANSOS | PED hal. 10 | Baseline |
| F-03 | R-16 | Layak DAN Prioritas ∈ {5, 6} | Wajib_Dokumen += DOK-P3KE | PED hal. 11 | Baseline |
| F-04 | R-16 | Layak DAN Prioritas = 7 | Wajib_Dokumen += DOK-PANTI | PED hal. 11 | Baseline |
| F-05 | R-17 | Layak DAN Prioritas = 8 DAN Miskin_Penghasilan | Wajib_Dokumen += DOK-PENGHASILAN | PED hal. 12 butir 8a | K02 |
| F-06 | R-17 | Layak DAN Prioritas = 8 DAN Miskin_SKTM | Wajib_Dokumen += DOK-SKTM | PED hal. 12 butir 8b | K02 |
| F-09 | R-19 | Layak DAN Status_Kondisi_Khusus = Ya | Wajib_Dokumen += DOK-KHUSUS | PS Bab I huruf C angka 1c–1f | K03 |
| G-01 | R-21 | Layak DAN Tingkat_1 DAN prodi bukan Kedokteran | Beasiswa_Kuliah = maks Rp 8.000.000 / semester | PED hal. 8; PS Bab III, Komponen Pembiayaan angka 1b | K05, K06, V |
| G-02 | R-22 | Layak DAN Tingkat_1 DAN prodi Kedokteran | Beasiswa_Kuliah = maks Rp 12.000.000 / semester | PED hal. 8; PS Bab III, Komponen Pembiayaan angka 1b | K05, K06, V |
| G-03 | R-23 | Layak DAN Tingkat_2 | Beasiswa_Kuliah = maks Rp 4.000.000 / semester | PED hal. 8; PS Bab III, Komponen Pembiayaan angka 1b | V |
| G-04 | R-24 | Layak DAN Tingkat_3 | Beasiswa_Kuliah = maks Rp 2.400.000 / semester | PED hal. 8; PS Bab III, Komponen Pembiayaan angka 1b | V |
| G-05 | R-25 | Layak DAN zona kampus = A | Beasiswa_Biaya_Hidup = Rp 800.000 / bulan (Rp 4.800.000 / semester) | PED hal. 7 dan 14 | V |
| G-06 | R-26 | Layak DAN zona kampus = B | Beasiswa_Biaya_Hidup = Rp 950.000 / bulan (Rp 5.700.000 / semester) | PED hal. 7 dan 14 | V |
| G-07 | R-27 | Layak DAN zona kampus = C | Beasiswa_Biaya_Hidup = Rp 1.100.000 / bulan (Rp 6.600.000 / semester) | PED hal. 7 dan 14 | V |
| G-08 | R-28 | Layak DAN zona kampus = D | Beasiswa_Biaya_Hidup = Rp 1.250.000 / bulan (Rp 7.500.000 / semester) | PED hal. 7 dan 14 | V |
| G-09 | R-29 | Layak DAN zona kampus = E | Beasiswa_Biaya_Hidup = Rp 1.400.000 / bulan (Rp 8.400.000 / semester) | PED hal. 7 dan 14 | V |
| G-10 | R-30 | Layak DAN jenjang = Sarjana | Masa_Beasiswa_Maks = 8 semester | PED hal. 15 | V |
| G-11 | R-31 | Layak DAN jenjang = Diploma IV | Masa_Beasiswa_Maks = 8 semester | PED hal. 15 | V |
| G-12 | R-32 | Layak DAN jenjang = Diploma III | Masa_Beasiswa_Maks = 6 semester | PED hal. 15 | V |
| G-13 | R-33 | Layak DAN jenjang = Diploma II | Masa_Beasiswa_Maks = 4 semester | PED hal. 15 | V |
| G-14 | R-34 | Layak DAN jenjang = Diploma I | Masa_Beasiswa_Maks = 2 semester | PED hal. 15 | V |
| G-15 | Tambahan / pemecahan baru | Layak DAN jenjang Sarjana DAN rumpun prodi = Kedokteran | Dapat dilanjutkan ke Profesi Dokter, maks 4 semester | PED hal. 15; PS Bab I huruf D angka 3e | K06, V |
| G-16 | Tambahan / pemecahan baru | Layak DAN jenjang Sarjana DAN rumpun prodi = Kedokteran Gigi | Dapat dilanjutkan ke Profesi Dokter Gigi, maks 4 semester | PED hal. 15; PS Bab I huruf D angka 3e | K06, V |
| G-17 | Tambahan / pemecahan baru | Layak DAN jenjang Sarjana DAN rumpun prodi = Kedokteran Hewan | Dapat dilanjutkan ke Profesi Dokter Hewan, maks 4 semester | PED hal. 15; PS Bab I huruf D angka 3e | K06, V |
| G-18 | Tambahan / pemecahan baru | Layak DAN jenjang Sarjana DAN rumpun prodi = Keperawatan | Dapat dilanjutkan ke Profesi Ners, maks 2 semester | PED hal. 15; PS Bab I huruf D angka 3e | K06, V |
| G-19 | Tambahan / pemecahan baru | Layak DAN jenjang Sarjana DAN rumpun prodi = Farmasi | Dapat dilanjutkan ke Profesi Apoteker, maks 2 semester | PED hal. 15; PS Bab I huruf D angka 3e | K06, V |
| G-20 | Tambahan / pemecahan baru | Layak DAN jenjang Sarjana DAN rumpun prodi = Kebidanan | Dapat dilanjutkan ke Profesi Bidan, maks 2 semester | PED hal. 15; PS Bab I huruf D angka 3e | K06, V |
| G-21 | Tambahan / pemecahan baru | Layak DAN jenjang Sarjana DAN rumpun prodi = Kependidikan | Dapat dilanjutkan ke Pendidikan Profesi Guru, maks 2 semester | PED hal. 15; PS Bab I huruf D angka 3e | K06, V |

## Perubahan yang harus disebut dalam laporan

1. R-14 memakai OR pada flag false; D-02 memakai semua false.
2. R-16/R-17/R-18/R-19/R-20 dapat bertabrakan; E-01–E-04 memisahkan jalur ekonomi dan kondisi khusus.
3. R-12 memakai OR pada batas penolakan penghasilan sehingga bisa tumpang tindih dengan R-11; C-10 bergantung pada tidak adanya prioritas.
4. R-16 salah mengeja kategori prioritas 3 dan 6; implementasi memakai nomor prioritas.
5. B-03, B-06, B-07 menambah penanganan tahun tidak valid, kelas nonreguler, dan beasiswa lain.
6. Terdata_P3KE mengganti konvensi desil 0; C-09 memilih prioritas minimum.
7. A-09 dan F-06 menambah bukti SKTM; interpretasi alternatif penghasilan/SKTM masih K02.
8. G-10–G-14 selalu menampilkan batas durasi untuk yang layak; Jangka_Waktu_Kuliah tidak lagi dibutuhkan sebagai pemicu.
9. G-15–G-21 menambah kelanjutan profesi; nama prodi dan rumpun harus diselaraskan.
10. F-00 menambah daftar persiapan akun; F-01–F-06/F-09 memisahkan dokumen per jalur.
11. Mesin menyimpan banyak alasan gugur dan menjalankan lima strata sampai fixpoint.
12. Eksekusi aktif memakai Cypher/Neo4j. Turtle tersedia sebagai representasi/ekspor RDF; jangan menyebut mesin aktif menjalankan SPARQL atau OWL reasoner.

## Bukti yang perlu dilengkapi

Untuk setiap K02–K05, catat kutipan lengkap sumber, nomor halaman/pasal, edisi, penafsir/pakar yang meninjau, tanggal, dan keputusan. Sumber PM tercatat sebagai sumber umum tetapi tidak memiliki relasi langsung dari rule pada baseline. Jangan menambahkan relasi semata-mata untuk memenuhi hitungan.
