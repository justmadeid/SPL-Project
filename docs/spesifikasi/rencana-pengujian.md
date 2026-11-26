# Rencana pengujian aturan dan kelengkapan

Status: rancangan penerimaan sebelum implementasi. Tabel ini belum merupakan hasil pengujian otomatis. Kasus domain menggunakan interpretasi baseline, kecuali ditandai bergantung keputusan K02–K05.

## Fixture dasar

Tahun daftar 2026, lulus 2025, sudah diterima PTN, akreditasi A, reguler, semua boolean dijawab false, desil null, penghasilan Rp9.000.000, 4 anggota keluarga, rumpun Lainnya, Sarjana, zona C. Nama, nama kampus, nama prodi opsional. Pada baseline, hasilnya Tidak_Layak melalui E-04. Penggunaan tahun 2026 dalam fixture tidak membuktikan regulasi 2026 telah diverifikasi.

Setiap kasus memakai fixture baru, bukan hasil mutasi kasus sebelumnya. Hanya perubahan terhadap fixture yang ditulis di tabel.

## Kelengkapan dan validasi

| ID | Perubahan | Hasil yang diharapkan |
|---|---|---|
| V01 | penghasilan tidak dikirim | Perlu_Dilengkapi, keputusan null, tidak ada inferensi |
| V02 | penghasilan null / string kosong | Perlu_Dilengkapi, bukan Rp0 |
| V03 | penghasilan eksplisit 0 | Input lengkap, prioritas 8 sesuai baseline |
| V04 | anggota_keluarga tidak dikirim | Perlu_Dilengkapi, bukan nilai default 1 |
| V05 | anggota_keluarga 0 atau negatif | Tidak_Valid |
| V06 | penghasilan negatif | Tidak_Valid |
| V07 | terdata_p3ke true, desil null | Perlu_Dilengkapi |
| V08 | desil 0 atau 11 | Tidak_Valid |
| V09 | terdata_p3ke false, desil 2 | Tidak_Valid; koreksi konflik, bukan hapus diam-diam |
| V10 | sktm true, bukti_sktm null | Perlu_Dilengkapi |
| V11 | sktm true, bukti_sktm false | Lengkap; A-09 tidak menyala |
| V12 | satu boolean syarat tidak dijawab | Perlu_Dilengkapi; tidak menggunakan false default |
| V13 | tahun_lulus 2027, tahun_daftar 2026 | Tidak_Valid, keputusan null; perubahan terhadap B-03/T6 lama |
| V14 | status_seleksi belum diketahui | Perlu_Dilengkapi, bukan Tidak_Lulus |
| V15 | akreditasi tidak diketahui | Perlu_Dilengkapi, bukan Belum_Terakreditasi |
| V16 | enum rumpun tidak dikenal, boolean dipakai sebagai angka, angka pecahan untuk jumlah anggota | Tidak_Valid |
| V17 | kip_sma true, zona null | Layak P1; biaya hidup belum lengkap, tidak memakai C default |
| V18 | kip_sma true, rumpun null | Layak P1; UKT/profesi belum lengkap, G-01 tidak menyala |
| V19 | kip_sma true, jenjang null | Layak P1; masa bantuan/profesi belum lengkap |
| V20 | nama/nama_kampus/nama_prodi kosong | Tidak menghalangi penilaian |
| V21 | cerita tidak menyebut beasiswa/kondisi khusus | Ekstraksi tetap null; perlu konfirmasi pengguna |
| V22 | cerita menyebut tahun daftar berbeda | Ekstraksi menangkap tahun, meminta tinjauan; tidak mengganti dengan default |
| V23 | input gagal validasi atau belum lengkap | Tidak membuat profil final atau trace baru di Neo4j |
| V24 | layanan/database gagal | Error layanan, bukan Tidak_Layak |

## Jalur domain dan batas

| ID | Perubahan | Harapan berdasarkan baseline |
|---|---|---|
| D01 | kip_sma true | Layak P1; E-02 saja; D-02 bukan alasan penolakan |
| D02 | dtks true | Layak P2; uji terpisah juga pkh dan kks |
| D03 | PTS + kip_sma true | Layak P3 |
| D04 | PTS + dtks true | Layak P4 |
| D05 | P3KE true + desil 3 | Layak P5; desil 4 tidak cukup |
| D06 | PTS + P3KE true + desil 2 | Layak P6 |
| D07 | panti true | Layak P7; F-04 |
| D08 | penghasilan 4.000.000 | Layak P8; F-05 |
| D09 | penghasilan 4.500.000 + anggota 6 | Layak P8 pada batas per kapita 750.000 |
| D10 | penghasilan 4.500.001 + anggota 6 | Tidak_Layak E-04 |
| D11 | sktm true + bukti true | Layak P8/F-06 bila K02 mempertahankan OR |
| D12 | hanya asli_papua true | E-03 saja bila K03 disepakati; D-02 tidak menyala |
| D13 | kip_sma true + asli_papua true | E-02 saja, kondisi tetap tercatat, F-09 |
| D14 | KIP + bansos + P3KE desil 2 + panti | P1; seluruh kecocokan dicatat; satu kategori final |
| D15 | tahun_lulus 2024 | Syarat tahun terpenuhi |
| D16 | tahun_lulus 2023 | B-02, Tidak_Layak E-01 |
| D17 | status_seleksi Tidak_Lulus | B-04/E-01 |
| D18 | akreditasi Belum_Terakreditasi | A-05/B-05/E-01 |
| D19 | kip_sma true + kelas Karyawan | B-06/E-01; ulang untuk Eksekutif dan Khusus |
| D20 | kip_sma true + beasiswa_lain true | B-07/E-01 jika K04 mempertahankan cakupan |
| D21 | tahun_lulus 2022 + Tidak_Lulus + belum terakreditasi + Karyawan + beasiswa_lain true | Lima alasan B-02/B-04/B-05/B-06/B-07, satu keputusan E-01 |
| D22 | masing-masing tujuh kondisi khusus true secara terpisah | D-01 merekam kondisi yang sesuai; D-02 tidak menyala |

## Manfaat dan dokumen

Semua kasus manfaat memakai kip_sma=true. Periksa nilai, bukan hanya keberadaan ID rule.

- A/Unggul/Internasional nonkedokteran: G-01 maksimum 8 juta; Kedokteran: G-02 maksimum 12 juta. Internasional menunggu K05.
- B/Baik_Sekali: G-03 maksimum 4 juta. C/Baik: G-04 maksimum 2,4 juta.
- Zona A–E: masing-masing 800.000, 950.000, 1.100.000, 1.250.000, 1.400.000 per bulan; nilai semester tepat enam kali.
- S1/D4/D3/D2/D1: masing-masing 8/8/6/4/2 semester; G-10–G-14.
- Tujuh rumpun profesi: dokter/dokter gigi/dokter hewan 4 semester; ners/apoteker/bidan/PPG 2 semester; G-15–G-21. Non-Sarjana tidak mendapat profesi dari aturan tersebut.
- F-00 ada pada semua hasil Layak; F-01–F-06 mengikuti prioritas terpilih dan bukti, F-09 mengikuti kondisi khusus.
- Tidak_Layak tidak mempunyai manfaat atau dokumen yang hanya berlaku untuk hasil Layak.

## Kriteria penerimaan

1. Semua 31 field memiliki kebijakan konsisten di UI, API, ekstraksi, dan penyimpanan.
2. Seluruh 63 rule baseline dipetakan ke pengujian, atau dicatat digantikan/dihentikan beserta alasannya. Jika B-03 dipindahkan ke validasi, jangan mempertahankan angka 63 sebagai target palsu.
3. Tepat satu rule E menyala untuk setiap input lengkap yang dapat diputuskan, dan nol untuk input belum lengkap/tidak valid.
4. Jejak menunjukkan alasan dan sumber yang tersedia; angka manfaat dan daftar dokumen sesuai fixture.
5. Pengujian tidak menyimpan profil percobaan ke data pengguna; gunakan database uji terpisah untuk pengujian otomatis.
6. Pengujian ulang baseline dan versi baru melaporkan perbedaan yang disengaja, bukan sekadar lulus/gagal.
7. Laporan, preset dan panduan memakai fixture yang sama. Tinjau semua variasi T1/T3/T7/T8/T10 sebelum menetapkan ekspektasi.
8. Migrasi atau restart tidak mengubah hasil historis tanpa versi dan strategi pemulihan database yang terdokumentasi.
