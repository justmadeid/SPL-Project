# Aturan dan kelengkapan data

Dokumen kerja ini menetapkan rancangan validasi dan daftar keputusan domain yang perlu diselesaikan sebelum implementasi. Status: **draf untuk ditinjau**, bukan perubahan aturan aktif dan bukan persetujuan pakar.

Baseline: commit `c776a7c`, tag `baseline-before-audit-fixes`. Branch: `work/rules-data-completeness`. Tanggal: 26 November 2026.

- [Kelengkapan data](kelengkapan-data.md): kontrak 31 field, status penilaian, dan penerimaan input.
- [Matriks aturan](matriks-aturan.md): inventaris 63 aturan aktif, pemetaan aturan lama, sumber tercatat, dan status tinjauan.
- [Rencana pengujian](rencana-pengujian.md): skenario dengan hasil yang diharapkan sebelum implementasi.

## Keputusan ruang lingkup

| ID | Pertanyaan | Posisi saat ini | Kriteria penyelesaian |
|---|---|---|---|
| K01 | Simulasi Pedoman 2025 atau layanan pendaftaran 2026? | **Diputuskan pengguna 26 November 2026: simulasi akademik berbasis Pedoman 2025**, dengan PS 2023 sebagai rujukan pendukung baseline | Tahun input digunakan untuk simulasi; tidak mengklaim aturan resmi pendaftaran 2026 |
| K02 | Penghasilan atau SKTM cukup secara alternatif? | A-09/C-08/F-06 mengikuti asumsi OR pada Rules-Revisi; belum ditetapkan sebagai kebenaran regulasi | Kutipan sumber lengkap beserta konteks dan konfirmasi dosen/pakar |
| K03 | Kondisi khusus cukup menghasilkan Layak tanpa memenuhi ekonomi? | E-03 mengikuti interpretasi baseline; beda antara kelayakan otomatis dan pertimbangan perlu ditegaskan | Konfirmasi redaksi serta jenis keluaran yang tepat |
| K04 | Semua beasiswa lain menggugurkan? | B-07 memakai satu boolean untuk APBN/APBD/sumber lain | Konfirmasi cakupan dan pengecualian, termasuk jenis bantuan yang dimaksud |
| K05 | Akreditasi Internasional dan program internasional setara? | Baseline memakai akreditasi Internasional; bukan flag program internasional | Konfirmasi bahwa kategori ini sesuai sumber, bukan sekadar bahasa pengantar/program |
| K06 | Pengelompokan prodi dan profesi | Implementasi memakai rumpun_prodi, dokumen revisi menyebut Program_Studi | Samakan kamus dan maknanya di laporan, UI, dan aturan |

Keputusan K02–K05 tidak boleh ditutup hanya karena pengujian perangkat lunak berhasil. Pengujian membuktikan implementasi terhadap spesifikasi, bukan keabsahan interpretasi regulasi.

## Urutan pekerjaan

1. Tinjau kontrak kelengkapan dengan acuan simulasi akademik Pedoman 2025 (K01 sudah diputuskan).
2. Lengkapi bukti dan tinjauan K02–K06.
3. Implementasikan validasi API, status input belum lengkap, lalu UI dan ekstraksi cerita dengan kontrak yang sama.
4. Jalankan kasus uji yang mencakup nilai batas, data kosong, tiap aturan, serta konflik keputusan.
5. Sinkronkan laporan, preset, panduan, dan ekspor ABox; sebutkan versi sumber.
6. Bandingkan perubahan terhadap baseline sebelum penggabungan branch.

## Catatan audit baseline

- Kode dan Neo4j memiliki 63 ID aturan yang sesuai dokumen revisi.
- Sepuluh preset memicu 41 aturan; 29 skenario tambahan sementara melengkapi aktivasi menjadi 63. Aktivasi bukan bukti semua kombinasi benar.
- API mengisi penghasilan yang tidak dikirim menjadi 0 dan anggota keluarga menjadi 1. Payload administratif minimal dapat menjadi Layak Prioritas 8.
- P3KE true tanpa desil masih diterima API.
- Snapshot RDF lolos validasi deklarasi predikat dan domain/range; ini tidak memverifikasi regulasi atau kebenaran input.
- T10 pada Rules-Revisi memakai zona C, sedangkan preset aplikasi memakai D. T1/T3/T7/T8 juga memiliki variasi input. Pilih fixture yang sama sebelum membandingkan jejak.

Sumber lokal: [Rules-Revisi](../../Expert%20Project%20/Rules-Revisi.md), [rules.py](../../backend/app/rules.py), [main.py](../../backend/app/main.py), [presets.py](../../backend/app/presets.py).
