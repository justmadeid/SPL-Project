# Deploy demo Pintu Kuliah ke Render

Deploy menggunakan branch `deploy/render-demo`, satu layanan Docker Render, dan satu Neo4j AuraDB khusus demo. Frontend dan API menggunakan origin yang sama. Database lokal tidak disalin atau dibuka ke internet.

## Buat database Aura

1. Daftar atau masuk di https://console.neo4j.io/.
2. Buat instance **AuraDB Free**, beri nama `pintukuliah-demo`. Pilih Free secara eksplisit, bukan paket trial berbayar.
3. Unduh file credentials dan simpan secara pribadi. Password yang dibuat tidak dapat ditampilkan kembali.
4. Tunggu status Running. Catat URI `neo4j+s://....databases.neo4j.io`, username, password, dan nama database dari credentials.
5. Gunakan database kosong khusus proyek ini. Startup pertama membangun ontologi dan 63 aturan; tidak perlu mengimpor ABox lokal atau profil pengguna.

## Buat layanan Render

1. Daftar/masuk di https://dashboard.render.com/ dengan akun GitHub.
2. Pilih **New → Blueprint**, hubungkan repository `justmadeid/SPL-Project`.
3. Pilih branch **deploy/render-demo**, Blueprint Path `render.yaml` di root repository.
4. Review layanan `pintu-kuliah-demo`, runtime Docker, paket Free. Jangan isi root directory `backend`; Docker memerlukan frontend dan backend dari root.
5. Masukkan NEO4J_URI dan NEO4J_PASSWORD dari Aura pada isian secret Render. NEO4J_USER dan NEO4J_DATABASE sudah `neo4j`; sesuaikan bila credentials berbeda.
6. Deploy dan tunggu build serta health check berhasil. URL publik diberikan Render setelah layanan dibuat.

Alternatif tombol deploy: https://render.com/deploy?repo=https://github.com/justmadeid/SPL-Project/tree/deploy/render-demo

## Konfigurasi demo

| Variabel | Nilai |
|---|---|
| PUBLIC_DEMO | true |
| ENABLE_SEED_ENDPOINT | false |
| NEO4J_URI | URI terenkripsi dari Aura |
| NEO4J_USER | neo4j, atau username pada credentials |
| NEO4J_PASSWORD | Password Aura, hanya di Environment Render |
| NEO4J_DATABASE | neo4j, atau nama database pada credentials |

Jangan menambahkan Gemini API key pada deployment awal. PUBLIC_DEMO menonaktifkan panggilan Gemini sekalipun key ada. Formulir manual dan preset tetap aktif. Pengaktifan AI untuk publik memerlukan pembatasan pemakaian tersendiri; demo AI lokal tetap dapat dipakai saat presentasi.

Endpoint reset `/api/seed` menolak request publik. Dalam mode demo, startup hanya melakukan seed saat belum ada rule, dan tidak menghitung ulang seluruh profil saat cold start. Versi ini mengasumsikan satu instance aplikasi dan database Aura khusus demo; pembaruan isi aturan memerlukan prosedur terpisah, bukan reset dari browser.

## Pemeriksaan setelah deploy

- `/api/ready`: 200 dan `{"ok":true}` jika database berisi jumlah aturan yang sesuai.
- `/api/health`: koneksi Neo4j sehat, rules 63, AI tidak aktif.
- Buka `/`, `/cek`, `/aturan`, lalu refresh masing-masing halaman.
- Uji Rina (T1), Dimas (T4), Yohana (T3); buka hasil dan graf.
- Gunakan data fiktif. Demo publik tidak memiliki akun pengguna; hasil yang URL-nya diketahui dapat dibuka oleh orang lain.

Jika deploy gagal: lihat log Render, periksa URI `neo4j+s://`, password, nama database, dan status Aura Running. Jangan menyalin kredensial ke issue atau chat. Jika jumlah rule tidak 63, periksa database yang dipilih; jangan gunakan database yang berisi pekerjaan lain.

Render Free tidur setelah 15 menit tidak aktif dan memerlukan sekitar satu menit untuk aktif kembali. Buka dan uji URL sebelum sesi. Aura Free dapat pause setelah 72 jam tidak aktif; cek konsol dan Resume sebelum presentasi. Hapus layanan demo ketika tidak diperlukan. Simpan backup yang diperlukan sebelum menghapus database.

## Referensi

- https://render.com/docs/blueprint-spec
- https://render.com/docs/deploy-to-render
- https://render.com/docs/free
- https://neo4j.com/docs/aura/getting-started/create-instance/
- https://neo4j.com/docs/aura/getting-started/connect-instance/
- https://neo4j.com/docs/aura/managing-instances/instance-actions/
