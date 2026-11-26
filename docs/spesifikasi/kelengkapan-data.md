# Definisi kelengkapan data

Status: **rancangan**, belum diimplementasikan. Tujuannya mencegah informasi yang belum diketahui menjadi fakta negatif atau nilai nol, serta menyamakan kontrak UI dan API.

## Makna nilai

- Field tidak dikirim, null, dan string kosong setelah trim berarti belum diketahui, bukan jawaban negatif.
- Angka 0 hanya sah sebagai penghasilan nol yang dinyatakan pengguna. Anggota keluarga 0 tidak sah.
- Boolean memiliki tiga keadaan saat pengisian: belum dijawab, ya, tidak. Penyimpanan draft boleh memakai null; inferensi negatif tidak boleh menggunakan null sebagai false.
- Ekstraksi cerita hanya mengisi fakta yang dinyatakan jelas. Informasi yang tidak disebut tetap belum diketahui. Pengguna meninjau hasil ekstraksi sebelum penilaian.
- Nilai bawaan yang memengaruhi keputusan/manfaat harus dikonfirmasi. Tidak ada default tersembunyi untuk penghasilan, anggota keluarga, kelas, beasiswa, jenjang, rumpun, atau zona.

## Kontrak field

Wajib penilaian berarti diperlukan untuk penilaian lengkap pada versi pertama kontrak ini, walaupun suatu jalur tertentu mungkin dapat diputuskan lebih awal. Pemangkasan pertanyaan berdasarkan jalur belum termasuk rancangan tahap pertama. Semua boolean wajib dapat dikonfirmasi lewat jawaban per item atau tindakan eksplisit untuk satu kelompok; tidak otomatis dari checkbox yang belum disentuh.

| Field | Kewajiban | Nilai dan validasi | Jika belum diketahui |
|---|---|---|---|
| nama | Opsional | Teks, trim; bukan penentu kelayakan | Gunakan label Tanpa nama |
| tahun_daftar | Wajib penilaian | Integer positif, tahun kalender empat digit; acuan sumber ditampilkan | Perlu dilengkapi |
| tahun_lulus | Wajib penilaian | Integer positif, tahun kalender empat digit | Perlu dilengkapi |
| status_seleksi | Wajib penilaian | Lulus / Tidak_Lulus; belum ada hasil bukan otomatis Tidak_Lulus | Perlu dilengkapi |
| jenis_kampus | Wajib penilaian | PTN / PTS | Perlu dilengkapi |
| nama_kampus | Opsional | Teks, trim; tidak menentukan zona otomatis | Tetap boleh menilai |
| akreditasi_prodi | Wajib penilaian | Unggul, A, Internasional, Baik_Sekali, B, Baik, C, Belum_Terakreditasi | Perlu dilengkapi; tidak disamakan dengan belum terakreditasi |
| jenis_kelas | Wajib penilaian | Reguler, Eksekutif, Khusus, Karyawan | Perlu dilengkapi |
| beasiswa_lain | Wajib penilaian | Boolean eksplisit; semantik mengikuti K04 | Perlu dilengkapi |
| kip_sma | Wajib penilaian | Boolean eksplisit | Perlu dilengkapi |
| dtks | Wajib penilaian | Boolean eksplisit | Perlu dilengkapi |
| pkh | Wajib penilaian | Boolean eksplisit | Perlu dilengkapi |
| kks | Wajib penilaian | Boolean eksplisit | Perlu dilengkapi |
| terdata_p3ke | Wajib penilaian | Boolean eksplisit | Perlu dilengkapi |
| desil_p3ke | Wajib jika terdata_p3ke=true | Integer 1–10 | Perlu dilengkapi jika terdata; null jika tidak terdata |
| panti | Wajib penilaian | Boolean eksplisit | Perlu dilengkapi |
| penghasilan | Wajib penilaian | Integer rupiah per bulan ≥0; gabungan orang tua/wali | Perlu dilengkapi, bukan Rp0 |
| anggota_keluarga | Wajib penilaian | Integer ≥1 | Perlu dilengkapi, bukan 1 |
| sktm | Wajib penilaian | Boolean eksplisit | Perlu dilengkapi |
| bukti_sktm | Wajib jika sktm=true | Boolean eksplisit; rekening listrik DAN foto rumah | Perlu dilengkapi jika punya SKTM; tidak relevan jika sktm=false |
| asal_3t | Wajib penilaian | Boolean eksplisit | Perlu dilengkapi |
| asli_papua | Wajib penilaian | Boolean eksplisit | Perlu dilengkapi |
| anak_tki | Wajib penilaian | Boolean eksplisit sesuai definisi perbatasan | Perlu dilengkapi |
| bencana | Wajib penilaian | Boolean eksplisit | Perlu dilengkapi |
| konflik | Wajib penilaian | Boolean eksplisit | Perlu dilengkapi |
| korban_kekerasan | Wajib penilaian | Boolean eksplisit | Perlu dilengkapi |
| korban_ham | Wajib penilaian | Boolean eksplisit | Perlu dilengkapi |
| nama_prodi | Opsional | Teks, trim; bukan pengganti rumpun_prodi | Tetap boleh menilai |
| rumpun_prodi | Wajib untuk informasi UKT/profesi | Kedokteran, Kedokteran_Gigi, Kedokteran_Hewan, Keperawatan, Farmasi, Kebidanan, Kependidikan, Lainnya | Kelayakan dapat dihitung; UKT/profesi ditandai belum lengkap |
| jenjang | Wajib untuk durasi/profesi | Sarjana, Diploma_IV, Diploma_III, Diploma_II, Diploma_I | Kelayakan dapat dihitung; durasi/profesi belum lengkap |
| zona | Wajib untuk biaya hidup | A–E, dipilih/dikonfirmasi pengguna | Kelayakan dapat dihitung; biaya hidup belum lengkap |

Akreditasi mengikuti enum baseline sementara K05 terbuka. K01 sudah menetapkan simulasi akademik Pedoman 2025. Tahun input merupakan parameter simulasi, bukan penanda bahwa regulasi tahun tersebut sudah diverifikasi. Label versi yang diusulkan: sim-ped2025-v1; label ini belum ditulis ke hasil aplikasi.

## Validasi lintas field

1. terdata_p3ke=true memerlukan desil. Jika false tetapi desil terisi, minta koreksi atau konfirmasi penghapusan; API tidak diam-diam membuang data bertentangan.
2. sktm=true memerlukan jawaban bukti_sktm. Jawaban false adalah data lengkap dan berarti jalur SKTM belum memenuhi A-09; jalur penghasilan tetap dievaluasi sesuai baseline K02.
3. sktm=false dan bukti_sktm=true dapat berarti pengguna memiliki rekening/foto tanpa SKTM. Ini tidak kontradiktif, tetapi tidak mengaktifkan A-09.
4. tahun_lulus > tahun_daftar diperlakukan sebagai input tidak valid yang harus dikoreksi, bukan keputusan Tidak_Layak. Ini usulan perubahan perilaku B-03 dan membutuhkan pembaruan kasus T6 serta laporan.
5. penghasilan negatif, anggota keluarga <1, desil di luar 1–10, tipe salah, atau enum tidak dikenal ditolak di API. Jangan menerima boolean sebagai integer atau membulatkan pecahan rupiah/anggota keluarga secara diam-diam.
6. Nama prodi tidak otomatis memaksa rumpun melalui pencocokan teks. UI meminta pengguna mengonfirmasi rumpun; pemeriksaan terhadap master resmi belum tersedia.
7. Data kosong tidak dikirim ke mesin aturan. Rule C-10, D-02, dan keputusan negatif baru berjalan setelah prasyarat kelengkapan dipenuhi.

## Status keluaran

Status kelengkapan berbeda dari keputusan domain. Rancangan respons mencakup status_input, keputusan, field_belum_lengkap, kesalahan_field, status_manfaat, dan versi_aturan.

| Situasi | status_input | keputusan | Perilaku |
|---|---|---|---|
| Field wajib belum diketahui | Perlu_Dilengkapi | null | Daftar field dan pesan perbaikan; tidak menjalankan inferensi atau menyimpan hasil final |
| Tipe/rentang/kombinasi tidak valid | Tidak_Valid | null | Kesalahan per field; tidak menjalankan inferensi |
| Field keputusan lengkap, data manfaat kurang | Lengkap | Hasil mesin aturan | Bagian manfaat yang bergantung pada data kosong tidak disimpulkan |
| Semua data yang relevan lengkap | Lengkap | Hasil mesin aturan | Penjelasan, dokumen, dan manfaat yang relevan |
| Tidak layak | Lengkap | Tidak_Layak | Manfaat Tidak_Berlaku, bukan Perlu_Dilengkapi |

Usulan HTTP: 422 untuk input tidak valid, 200 untuk respons terstruktur Perlu_Dilengkapi dan hasil lengkap. Kegagalan layanan tetap 5xx dan tidak dipetakan menjadi keputusan domain. Kontrak final API harus ditinjau bersama perubahan frontend sebelum diterapkan.

## Dampak implementasi yang direncanakan

- Model input mendukung draft, tetapi gerbang validasi memblokir inferensi sebelum data siap.
- A-07/C-05/C-06 tidak boleh memakai desil null. A-08 tidak boleh memakai penghasilan default.
- G-01 tidak boleh menganggap rumpun kosong sebagai non-kedokteran; G-01/G-02 dan G-15–G-21 memerlukan rumpun yang diketahui.
- G-05–G-09 memerlukan zona diketahui; G-10–G-21 memerlukan jenjang diketahui sesuai aturan masing-masing.
- Hasil lama yang berasal dari default tidak otomatis dianggap sudah dikonfirmasi. Tinjau migrasi terlebih dahulu; jangan mengubah atau menghapus riwayat secara massal.
- Backend saat start menjalankan seed dan inferensi ulang semua profil. Sebelum perubahan domain diaktifkan, tambahkan strategi versi/backup database agar hasil historis tidak berubah diam-diam. Tag Git saja bukan backup Neo4j.

## Batas cakupan

Sistem menguji input pengguna, tidak memverifikasi dokumen atau terhubung ke Dapodik. NIK/NISN/NPSN/email tetap informasi persiapan pada F-00, bukan syarat baru yang dikumpulkan. Tidak ada integrasi master kampus/prodi atau pengecekan bansos otomatis pada tahap ini.
