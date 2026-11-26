# BAB III (Revisi): Aturan / Rules Sistem Pakar Kelayakan KIP Kuliah

Dokumen ini menggantikan BAB III pada *Expert System Report.docx*. Rule disusun **berlapis**: tiap lapis menghasilkan fakta antara yang dipakai lapis berikutnya. Susunan ini cocok untuk *forward chaining* sampai *fixpoint* (SPARQL `INSERT … WHERE`), dan setiap fakta turunan bisa ditandai dengan rule yang menghasilkannya (`:derivedBy`) untuk fasilitas penjelasan.

## Sumber pengetahuan (kode referensi)

| Kode | Sumber |
|---|---|
| **[PED]** | Pedoman Pendaftaran KIP Kuliah 2025 v1.0, Kemdiktisaintek (nomor halaman = nomor di kaki halaman pedoman) |
| **[PS]** | Persesjen Kemendikbudristek No. 13 Tahun 2023, Lampiran (Petunjuk Pelaksanaan PIP Pendidikan Tinggi) |
| **[PM]** | Permendikbud No. 10 Tahun 2020 tentang Program Indonesia Pintar |

---

## 0. Fakta masukan (input pengguna)

| Variabel | Tipe / nilai | Keterangan |
|---|---|---|
| `Tahun_Daftar` | integer | Tahun pendaftaran KIP Kuliah |
| `Tahun_Lulus_SMA` | integer | Tahun lulus SMA/SMK/MA/sederajat |
| `Status_Seleksi_PT` | `Lulus` / `Tidak_Lulus` | Hasil seleksi masuk PT (SNBP/SNBT/Mandiri) |
| `Jenis_Kampus` | `PTN` / `PTS` | |
| `Akreditasi_Prodi` | `Unggul`, `A`, `Internasional`, `Baik_Sekali`, `B`, `Baik`, `C`, `Belum_Terakreditasi` | **Satu variabel**, menggantikan `Status_Akreditasi_Prodi` + `Akreditasi_Prodi` yang dulu tumpang tindih |
| `Jenis_Kelas` | `Reguler`, `Eksekutif`, `Khusus`, `Karyawan` | |
| `Menerima_Beasiswa_Lain` | boolean | Beasiswa/bantuan biaya pendidikan dari APBN, APBD, atau sumber lain |
| `Memiliki_KIP_Menengah` | boolean | KIP SMA |
| `Terdata_DTKS`, `Penerima_PKH`, `Pemegang_KKS` | boolean | |
| `Terdata_P3KE` | boolean | **Baru**: menggantikan konvensi `Desil_P3KE == 0` |
| `Desil_P3KE` | integer 1–10 | Diisi hanya jika `Terdata_P3KE == True` |
| `Asal_Panti_Asuhan` | boolean | Panti sosial / panti asuhan |
| `Penghasilan_Gabungan_Ortu` | integer (Rp/bulan) | Pendapatan kotor gabungan orang tua/wali |
| `Jumlah_Anggota_Keluarga` | integer ≥ 1 | |
| `Memiliki_SKTM` | boolean | **Baru**: SKTM minimal tingkat desa/kelurahan |
| `Bukti_Dukung_SKTM` | boolean | **Baru**: rekening listrik dan foto rumah tersedia |
| `Asal_3T`, `Asli_Papua`, `Anak_TKI_Perbatasan`, `Bencana_Alam`, `Konflik_Sosial`, `Korban_Kekerasan`, `Korban_Pelanggaran_HAM` | boolean | Kondisi khusus |
| `Program_Studi` | string | Mis. `Kedokteran`, `Kedokteran_Gigi`, `Keperawatan`, `Informatika`, … |
| `Jenjang` | `Sarjana`, `Diploma_IV`, `Diploma_III`, `Diploma_II`, `Diploma_I` | |
| `Zona_Kampus` | `A`–`E` | Klaster biaya hidup wilayah kampus |

Ruang lingkup: sistem menilai **calon mahasiswa baru** lulusan SMA/sederajat (sasaran Program KIP Kuliah, [PS] Bab I huruf D angka 3a). Program profesi dibahas sebagai kelanjutan (Lapis G).

---

## Lapis A: Fakta turunan pembantu

**Rule A-01 (Selisih tahun lulus)**
IF `Tahun_Daftar` dan `Tahun_Lulus_SMA` diketahui
THEN `Selisih_Tahun = Tahun_Daftar − Tahun_Lulus_SMA`

**Rule A-02 (Peringkat akreditasi tingkat 1)**
IF `Akreditasi_Prodi ∈ {Unggul, A, Internasional}`
THEN `Peringkat_Akreditasi = Tingkat_1` AND `Prodi_Terakreditasi = True` — [PED] hal. 8

**Rule A-03 (Peringkat akreditasi tingkat 2)**
IF `Akreditasi_Prodi ∈ {Baik_Sekali, B}`
THEN `Peringkat_Akreditasi = Tingkat_2` AND `Prodi_Terakreditasi = True` — [PED] hal. 8

**Rule A-04 (Peringkat akreditasi tingkat 3)**
IF `Akreditasi_Prodi ∈ {Baik, C}`
THEN `Peringkat_Akreditasi = Tingkat_3` AND `Prodi_Terakreditasi = True` — [PED] hal. 8

**Rule A-05 (Prodi belum terakreditasi)**
IF `Akreditasi_Prodi == Belum_Terakreditasi`
THEN `Prodi_Terakreditasi = False`

**Rule A-06 (Penerima bansos Kemensos)**
IF `Terdata_DTKS == True` OR `Penerima_PKH == True` OR `Pemegang_KKS == True`
THEN `Penerima_Bansos = True` — [PS] Bab I huruf C angka 1b(1)–(3)

**Rule A-07 (Rentan miskin P3KE)**
IF `Terdata_P3KE == True` AND `Desil_P3KE <= 3`
THEN `Rentan_Miskin_P3KE = True` — [PED] hal. 11; [PS] Bab I huruf C angka 1b(4)

**Rule A-08 (Miskin berdasarkan penghasilan)**
IF `Penghasilan_Gabungan_Ortu <= 4.000.000`
OR (`Jumlah_Anggota_Keluarga >= 1` AND `Penghasilan_Gabungan_Ortu / Jumlah_Anggota_Keluarga <= 750.000`)
THEN `Miskin_Penghasilan = True` — [PED] hal. 12 butir 8a; [PS] Bab I huruf C angka 1b(6)

**Rule A-09 (Miskin berdasarkan SKTM)**
IF `Memiliki_SKTM == True` AND `Bukti_Dukung_SKTM == True`
THEN `Miskin_SKTM = True` — [PED] hal. 12 butir 8b

> **Asumsi interpretasi:** butir 8 Pedoman menyebut dua bentuk bukti (a. penghasilan, b. SKTM). Sistem menganggap **salah satu bukti cukup** (OR). Verifikasi akhir tetap dilakukan perguruan tinggi ([PED] hal. 12).

---

## Lapis B: Validasi administrasi

Setiap rule gugur menambahkan satu `Alasan_Gugur`. Satu pendaftar bisa punya **lebih dari satu** alasan, dan semuanya ditampilkan di penjelasan.

**Rule B-01 (Tahun lulus memenuhi)**
IF `0 <= Selisih_Tahun <= 2`
THEN `Syarat_Tahun_Lulus = Terpenuhi` — [PED] hal. 9 butir 2

**Rule B-02 (Gugur: melebihi batas tahun lulus)**
IF `Selisih_Tahun > 2`
THEN `Alasan_Gugur += "Lulus lebih dari 2 tahun sebelum tahun pendaftaran"` — [PED] hal. 9 butir 2

**Rule B-03 (Gugur: data tahun tidak valid)**
IF `Selisih_Tahun < 0`
THEN `Alasan_Gugur += "Tahun lulus setelah tahun pendaftaran (data tidak valid)"`

**Rule B-04 (Gugur: tidak lulus seleksi PT)**
IF `Status_Seleksi_PT == Tidak_Lulus`
THEN `Alasan_Gugur += "Belum/tidak lulus seleksi masuk perguruan tinggi"` — [PED] hal. 9 butir 1

**Rule B-05 (Gugur: prodi belum terakreditasi)**
IF `Prodi_Terakreditasi == False`
THEN `Alasan_Gugur += "Program studi belum terakreditasi"` — [PED] hal. 9 butir 1; [PS] Bab I huruf D angka 3c

**Rule B-06 (Gugur: bukan kelas reguler)**
IF `Jenis_Kelas ∈ {Eksekutif, Khusus, Karyawan}`
THEN `Alasan_Gugur += "Diterima di kelas eksekutif/khusus/karyawan"` — [PS] Bab I huruf D angka 3i

**Rule B-07 (Gugur: menerima beasiswa lain)**
IF `Menerima_Beasiswa_Lain == True`
THEN `Alasan_Gugur += "Sedang menerima beasiswa/bantuan biaya pendidikan lain (APBN/APBD/sumber lain)"` — [PS] Bab I huruf D angka 3h

**Rule B-08 (Administrasi memenuhi syarat)**
IF `Syarat_Tahun_Lulus == Terpenuhi` AND `Status_Seleksi_PT == Lulus` AND `Prodi_Terakreditasi == True`
AND `Jenis_Kelas == Reguler` AND `Menerima_Beasiswa_Lain == False`
AND **tidak ada** `Alasan_Gugur`
THEN `Status_Administrasi = Memenuhi_Syarat`

**Rule B-09 (Administrasi tidak memenuhi syarat)**
IF ada minimal satu `Alasan_Gugur`
THEN `Status_Administrasi = Tidak_Memenuhi_Syarat`

---

## Lapis C: Klasifikasi prioritas ekonomi

Rule C-01 sampai C-08 **masing-masing** menandai prioritas yang dipenuhi pendaftar (`Memenuhi_Prioritas += k`). Rule C-09 lalu memilih **nomor prioritas terkecil** (prioritas tertinggi). Dengan cara ini rule tidak perlu mengulang rantai negasi panjang seperti versi lama, dan tidak ada kombinasi yang lolos tanpa kategori.

**Rule C-01 (Prioritas 1: KIP SMA di PTN)**
IF `Memiliki_KIP_Menengah == True` AND `Jenis_Kampus == PTN`
THEN `Memenuhi_Prioritas += 1` — [PED] hal. 10 butir 1

**Rule C-02 (Prioritas 2: DTKS/bansos di PTN)**
IF `Penerima_Bansos == True` AND `Jenis_Kampus == PTN`
THEN `Memenuhi_Prioritas += 2` — [PED] hal. 10 butir 2

**Rule C-03 (Prioritas 3: KIP SMA di PTS)**
IF `Memiliki_KIP_Menengah == True` AND `Jenis_Kampus == PTS`
THEN `Memenuhi_Prioritas += 3` — [PED] hal. 10 butir 3

**Rule C-04 (Prioritas 4: DTKS/bansos di PTS)**
IF `Penerima_Bansos == True` AND `Jenis_Kampus == PTS`
THEN `Memenuhi_Prioritas += 4` — [PED] hal. 10 butir 4

**Rule C-05 (Prioritas 5: P3KE desil ≤ 3 di PTN)**
IF `Rentan_Miskin_P3KE == True` AND `Jenis_Kampus == PTN`
THEN `Memenuhi_Prioritas += 5` — [PED] hal. 11 butir 5

**Rule C-06 (Prioritas 6: P3KE desil ≤ 3 di PTS)**
IF `Rentan_Miskin_P3KE == True` AND `Jenis_Kampus == PTS`
THEN `Memenuhi_Prioritas += 6` — [PED] hal. 11 butir 6

**Rule C-07 (Prioritas 7: panti sosial/asuhan, PTN atau PTS)**
IF `Asal_Panti_Asuhan == True`
THEN `Memenuhi_Prioritas += 7` — [PED] hal. 11 butir 7

**Rule C-08 (Prioritas 8: miskin/rentan miskin terbukti)**
IF `Miskin_Penghasilan == True` OR `Miskin_SKTM == True`
THEN `Memenuhi_Prioritas += 8` — [PED] hal. 12 butir 8

**Rule C-09 (Tetapkan kategori ekonomi = prioritas tertinggi)**
IF ada minimal satu `Memenuhi_Prioritas`
THEN `Kategori_Ekonomi = Prioritas_k` dengan `k = MIN(Memenuhi_Prioritas)`
*(Resolusi konflik: urutan prioritas resmi [PED] hal. 10–12.)*

**Rule C-10 (Tidak memenuhi syarat ekonomi)**
IF **tidak ada** `Memenuhi_Prioritas`
THEN `Kategori_Ekonomi = Tidak_Memenuhi_Syarat_Ekonomi`

---

## Lapis D: Kondisi khusus (pertimbangan afirmasi)

**Rule D-01 (Ada kondisi khusus)**
IF `Asal_3T` OR `Asli_Papua` OR `Anak_TKI_Perbatasan` OR `Bencana_Alam` OR `Konflik_Sosial` OR `Korban_Kekerasan` OR `Korban_Pelanggaran_HAM` bernilai `True`
THEN `Status_Kondisi_Khusus = Ya` AND `Daftar_Kondisi_Khusus` = semua flag yang `True` — [PS] Bab I huruf C angka 1c–1f; [PED] hal. 5

**Rule D-02 (Tidak ada kondisi khusus)**
IF **semua** flag kondisi khusus bernilai `False` *(perbaikan: dulu memakai OR)*
THEN `Status_Kondisi_Khusus = Tidak`

---

## Lapis E: Keputusan akhir

Kondisi khusus menjadi **jalur tambahan** (OR), bukan syarat wajib, sesuai frasa "miskin/rentan miskin **dan/atau** dengan pertimbangan khusus" ([PS] Bab I huruf C angka 1b; [PED] hal. 9 butir 3).

**Rule E-01 (Tidak layak: gugur administrasi)**
IF `Status_Administrasi == Tidak_Memenuhi_Syarat`
THEN `Keputusan_Akhir = Tidak_Layak` AND `Alasan_Keputusan` = semua `Alasan_Gugur`

**Rule E-02 (Layak: jalur ekonomi)**
IF `Status_Administrasi == Memenuhi_Syarat` AND `Kategori_Ekonomi ∈ {Prioritas_1 … Prioritas_8}`
THEN `Keputusan_Akhir = Layak` AND `Jalur = Ekonomi_Prioritas_k`

**Rule E-03 (Layak: jalur kondisi khusus)**
IF `Status_Administrasi == Memenuhi_Syarat` AND `Kategori_Ekonomi == Tidak_Memenuhi_Syarat_Ekonomi` AND `Status_Kondisi_Khusus == Ya`
THEN `Keputusan_Akhir = Layak` AND `Jalur = Pertimbangan_Khusus`

**Rule E-04 (Tidak layak: tidak memenuhi syarat ekonomi maupun kondisi khusus)**
IF `Status_Administrasi == Memenuhi_Syarat` AND `Kategori_Ekonomi == Tidak_Memenuhi_Syarat_Ekonomi` AND `Status_Kondisi_Khusus == Tidak`
THEN `Keputusan_Akhir = Tidak_Layak` AND `Alasan_Keputusan = "Tidak memenuhi kriteria ekonomi maupun kondisi khusus"`

> Pendaftar yang memenuhi prioritas ekonomi **dan** punya kondisi khusus tetap masuk jalur ekonomi (E-02). Kondisi khususnya ikut dicatat dan menambah dokumen (F-09).

---

## Lapis F: Dokumen wajib

**Rule F-00 (Data pendaftaran akun, semua yang layak)**
IF `Keputusan_Akhir == Layak`
THEN `Wajib_Dokumen += "NIK, NISN, NPSN valid di Dapodik dan email aktif"` — [PED] hal. 18; [PS] Bab I huruf D angka 3c

**Rule F-01 (Prioritas 1 / 3)**
IF `Keputusan_Akhir == Layak` AND `Kategori_Ekonomi ∈ {Prioritas_1, Prioritas_3}`
THEN `Wajib_Dokumen += "Kartu KIP Pendidikan Menengah (KIP SMA)"`

**Rule F-02 (Prioritas 2 / 4)**
IF `Keputusan_Akhir == Layak` AND `Kategori_Ekonomi ∈ {Prioritas_2, Prioritas_4}`
THEN `Wajib_Dokumen += "Bukti terdata DTKS / kartu KKS / bukti kepesertaan PKH"`

**Rule F-03 (Prioritas 5 / 6)**
IF `Keputusan_Akhir == Layak` AND `Kategori_Ekonomi ∈ {Prioritas_5, Prioritas_6}`
THEN `Wajib_Dokumen += "Bukti terdata P3KE desil 1–3"`

**Rule F-04 (Prioritas 7)**
IF `Keputusan_Akhir == Layak` AND `Kategori_Ekonomi == Prioritas_7`
THEN `Wajib_Dokumen += "Surat keterangan dari panti sosial/panti asuhan"`

**Rule F-05 (Prioritas 8, bukti penghasilan)**
IF `Keputusan_Akhir == Layak` AND `Kategori_Ekonomi == Prioritas_8` AND `Miskin_Penghasilan == True`
THEN `Wajib_Dokumen += "Slip gaji / surat keterangan penghasilan orang tua/wali, kartu keluarga"` — [PED] hal. 12 butir 8a

**Rule F-06 (Prioritas 8, bukti SKTM)**
IF `Keputusan_Akhir == Layak` AND `Kategori_Ekonomi == Prioritas_8` AND `Miskin_SKTM == True`
THEN `Wajib_Dokumen += "SKTM desa/kelurahan, rekening listrik, foto rumah"` — [PED] hal. 12 butir 8b

**Rule F-09 (Kondisi khusus)**
IF `Keputusan_Akhir == Layak` AND `Status_Kondisi_Khusus == Ya`
THEN `Wajib_Dokumen += "Surat keterangan dari pemerintah daerah/instansi berwenang sesuai kondisi (3T, orang asli Papua, anak TKI di perbatasan, terdampak bencana/konflik, korban kekerasan/pelanggaran HAM)"`

---

## Lapis G: Besaran dan jangka waktu beasiswa

### Biaya pendidikan (UKT/SPP, dibayar ke perguruan tinggi)

**Rule G-01** IF `Layak` AND `Peringkat_Akreditasi == Tingkat_1` AND `Program_Studi != Kedokteran`
THEN `Beasiswa_Kuliah = "Maks Rp 8.000.000 / semester"` — [PED] hal. 8

**Rule G-02** IF `Layak` AND `Peringkat_Akreditasi == Tingkat_1` AND `Program_Studi == Kedokteran`
THEN `Beasiswa_Kuliah = "Maks Rp 12.000.000 / semester"` — [PED] hal. 8

**Rule G-03** IF `Layak` AND `Peringkat_Akreditasi == Tingkat_2`
THEN `Beasiswa_Kuliah = "Maks Rp 4.000.000 / semester"` — [PED] hal. 8

**Rule G-04** IF `Layak` AND `Peringkat_Akreditasi == Tingkat_3`
THEN `Beasiswa_Kuliah = "Maks Rp 2.400.000 / semester"` — [PED] hal. 8; [PS] Bab III

> Catatan G-01–G-04: angka di atas adalah **batas atas**. Besaran riil diusulkan perguruan tinggi, paling banyak sebesar rata-rata biaya pendidikan mahasiswa non-KIP di prodi tersebut ([PS] Bab III, Komponen Pembiayaan angka 1b).

### Bantuan biaya hidup (ditransfer ke mahasiswa, sekali per semester)

| Rule | Kondisi | Per bulan | Per semester (×6) |
|---|---|---|---|
| G-05 | `Layak` AND `Zona_Kampus == A` | Rp 800.000 | Rp 4.800.000 |
| G-06 | `Layak` AND `Zona_Kampus == B` | Rp 950.000 | Rp 5.700.000 |
| G-07 | `Layak` AND `Zona_Kampus == C` | Rp 1.100.000 | Rp 6.600.000 |
| G-08 | `Layak` AND `Zona_Kampus == D` | Rp 1.250.000 | Rp 7.500.000 |
| G-09 | `Layak` AND `Zona_Kampus == E` | Rp 1.400.000 | Rp 8.400.000 |

Sumber: [PED] hal. 7 dan 14 (besaran 5 klaster, diberikan satu kali setiap semester).

### Jangka waktu pemberian (selalu ditampilkan bila layak)

*(Perbaikan: versi lama hanya menyala jika `Jangka_Waktu_Kuliah > batas`, sehingga sebagian besar pendaftar layak tidak mendapat informasi masa beasiswa.)*

| Rule | Kondisi | Hasil `Masa_Beasiswa_Maks` |
|---|---|---|
| G-10 | `Layak` AND `Jenjang == Sarjana` | 8 semester |
| G-11 | `Layak` AND `Jenjang == Diploma_IV` | 8 semester |
| G-12 | `Layak` AND `Jenjang == Diploma_III` | 6 semester |
| G-13 | `Layak` AND `Jenjang == Diploma_II` | 4 semester |
| G-14 | `Layak` AND `Jenjang == Diploma_I` | 2 semester |

Sumber: [PED] hal. 15.

### Kelanjutan ke program profesi (baru)

Syarat: tetap tercatat sebagai penerima KIP Kuliah pada jenjang sarjana ([PS] Bab I huruf D angka 3e).

| Rule | Kondisi (`Layak` AND `Jenjang == Sarjana` AND …) | `Keterangan_Profesi` |
|---|---|---|
| G-15 | `Program_Studi == Kedokteran` | Dapat dilanjutkan ke Profesi Dokter, maks 4 semester |
| G-16 | `Program_Studi == Kedokteran_Gigi` | Profesi Dokter Gigi, maks 4 semester |
| G-17 | `Program_Studi == Kedokteran_Hewan` | Profesi Dokter Hewan, maks 4 semester |
| G-18 | `Program_Studi == Keperawatan` | Profesi Ners, maks 2 semester |
| G-19 | `Program_Studi == Farmasi` | Profesi Apoteker, maks 2 semester |
| G-20 | `Program_Studi == Kebidanan` | Profesi Bidan, maks 2 semester |
| G-21 | `Program_Studi` termasuk kependidikan (keguruan) | Pendidikan Profesi Guru, maks 2 semester |

Sumber: [PED] hal. 15.

---

## Urutan eksekusi (stratifikasi)

Rule yang memakai negasi ("tidak ada …", `NOT EXISTS`) atau agregat (`MIN`) baru boleh dijalankan **setelah** semua rule yang bisa menghasilkan fakta yang dinegasikan sudah selesai. Urutan stratanya:

1. **Strata 1:** A-01 … A-09 (fakta pembantu)
2. **Strata 2:** B-01 … B-07, C-01 … C-08, D-01
3. **Strata 3:** B-08, B-09, C-09, C-10, D-02 (memakai negasi/agregat dari strata 2)
4. **Strata 4:** E-01 … E-04
5. **Strata 5:** F-00 … F-09, G-01 … G-21

Tiap strata dijalankan sampai *fixpoint* sebelum pindah ke strata berikutnya. Dengan urutan ini, rule default tidak menghasilkan kesimpulan basi (lihat materi *SPARQL-Reasoning*, "Pitfalls of SPARQL rules").

---

## Daftar perubahan dari versi lama

| # | Masalah di versi lama | Perbaikan |
|---|---|---|
| 1 | **R-14 memakai `OR`.** Siapa pun yang punya satu flag `False` dianggap "bukan kondisi khusus", termasuk yang memenuhi R-13 sehingga hasilnya kontradiktif. | D-02 memakai **semua flag `False`** (AND / NOT EXISTS). |
| 2 | **R-19/R-20 bertabrakan dengan R-16/R-17/R-18.** Prioritas 1 tanpa kondisi khusus menghasilkan Layak (R-16) sekaligus Tidak_Layak (R-20). | Kondisi khusus jadi jalur tambahan (E-03), hanya dipakai jika tidak lolos jalur ekonomi. |
| 3 | **Salah ketik di R-16:** `"Prioritas_3_KIP_SM A_PTS"` dan `"Prioritas_6_P3K E_PTS"` tidak cocok dengan keluaran R-06/R-09, sehingga pendaftar Prioritas 3 dan 6 tidak pernah dinyatakan layak. | Kategori memakai pola tetap `Prioritas_k`, dicocokkan dengan nomor. |
| 4 | Syarat [PS] belum dijadikan rule: **kelas non-reguler** dan **penerima beasiswa lain**. | Ditambah B-06 dan B-07. |
| 5 | **SKTM** (butir 8b) tidak dimodelkan, hanya penghasilan. | Ditambah A-09, C-08, dan F-06. |
| 6 | `Tahun_Daftar < Tahun_Lulus_SMA` tidak tertangani, sehingga status administrasi kosong dan tidak ada keputusan. | Ditambah B-03. |
| 7 | Konvensi `Desil_P3KE == 0` untuk "tidak terdata" rawan salah; rantai negasi panjang di R-08…R-12 sulit dirawat. | Ditambah `Terdata_P3KE`, prioritas ditandai per rule lalu dipilih dengan `MIN` (C-09). |
| 8 | Pembagian `Penghasilan / Jumlah_Anggota_Keluarga` bisa membagi dengan nol. | A-08 mensyaratkan `Jumlah_Anggota_Keluarga >= 1`. |
| 9 | `Status_Akreditasi_Prodi` dan `Akreditasi_Prodi` tumpang tindih; peringkat "Baik Sekali/Baik" belum dikenali. | Satu variabel `Akreditasi_Prodi` dipetakan ke tiga tingkat (A-02…A-05). |
| 10 | Jangka waktu hanya ditampilkan jika masa studi melebihi batas. | G-10…G-14 selalu menyala bila layak. |
| 11 | Program profesi tidak dicakup. | Ditambah G-15…G-21. |
| 12 | Dokumen wajib digabung untuk semua jalur, dan R-17 tidak membedakan bukti penghasilan dari SKTM. | Dokumen dipecah per jalur (F-00…F-09). |
| 13 | Hanya satu `Alasan_Gugur` yang tersimpan. | Semua alasan gugur dikumpulkan untuk penjelasan. |

---

## Kasus uji (versi lama vs revisi)

Profil dasar semua kasus (kecuali disebut lain): lulus 2025, daftar 2026, lulus seleksi PTN, prodi Informatika akreditasi A, kelas reguler, tidak menerima beasiswa lain, penghasilan orang tua Rp 9 juta / 4 orang, Sarjana, Zona C, tanpa kondisi khusus.

| # | Perbedaan dari profil dasar | Kesimpulan versi lama | Kesimpulan revisi | Rule yang menyala (revisi) |
|---|---|---|---|---|
| T1 | Punya KIP SMA | **Konflik:** R-16 Layak + R-20 Tidak_Layak | Layak, Prioritas 1 | A-01, A-02, B-01, B-08, C-01, C-09, D-02, E-02, F-00, F-01, G-01, G-07, G-10 |
| T2 | PTS, KIP SMA, prodi B | Hanya R-20 Tidak_Layak (R-16 tidak cocok karena salah ketik) | Layak, Prioritas 3 | A-03, B-08, C-03, C-09, D-02, E-02, F-00, F-01, G-03, G-07, G-10 |
| T3 | Asli Papua | **Konflik:** R-18 Tidak_Layak + R-19 Layak + R-20 Tidak_Layak | Layak, jalur Pertimbangan Khusus | B-08, C-10, D-01, E-03, F-00, F-09, G-01, G-07, G-10 |
| T4 | Kelas karyawan, pemegang KKS | **Konflik:** R-16 Layak + R-20 Tidak_Layak | Tidak layak (kelas non-reguler) | A-06, B-06, B-09, C-02, C-09, E-01 |
| T5 | Penerima beasiswa APBD, KIP SMA | **Konflik:** R-16 Layak + R-20 Tidak_Layak | Tidak layak (beasiswa lain) | B-07, B-09, C-01, C-09, E-01 |
| T6 | Lulus 2027 (salah input) | Tidak ada keputusan | Tidak layak (data tahun tidak valid) | B-03, B-09, C-10, E-01 |
| T7 | PTS, penghasilan Rp 5 juta / 5 orang (Rp 1 juta per kapita), punya SKTM + bukti dukung | R-18 + R-20 Tidak_Layak | Layak, Prioritas 8 (SKTM) | A-09, B-08, C-08, C-09, E-02, F-00, F-06 |
| T8 | P3KE desil 2 dan dari panti asuhan | **Konflik:** R-16 Layak + R-20 Tidak_Layak | Layak, Prioritas 5 (cocok 5 dan 7, MIN = 5) | A-07, C-05, C-07, C-09, E-02, F-00, F-03 |
| T9 | Lulus 2022, KIP SMA | R-15 Tidak_Layak | Tidak layak (lebih dari 2 tahun) | B-02, B-09, C-01, C-09, E-01 |
| T10 | Kedokteran (Unggul), terdata DTKS | **Konflik:** R-16 Layak + R-20 Tidak_Layak | Layak, Prioritas 2: maks Rp 12 juta/semester, biaya hidup Rp 1,1 juta/bulan, 8 semester + profesi dokter 4 semester | A-06, C-02, C-09, E-02, F-00, F-02, G-02, G-07, G-10, G-15 |

Hasil tabel ini dihasilkan dengan simulasi Python yang menerjemahkan rule lama dan rule revisi apa adanya. Di versi lama, R-20 menyala pada **setiap** pendaftar tanpa kondisi khusus yang lolos administrasi (akibat bug #1 dan #2), sehingga hampir semua kasus layak berakhir konflik.
