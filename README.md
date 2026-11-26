# Pintu Kuliah: Sistem Pakar Kelayakan KIP Kuliah

Proyek akhir mata kuliah Sistem Pakar Lanjut (MIK226410), Magister Kecerdasan Artifisial UGM.

Pintu Kuliah menilai apakah seorang calon mahasiswa layak menerima KIP Kuliah, menentukan jalur prioritasnya, dokumen yang harus disiapkan, serta besaran biaya pendidikan, biaya hidup, dan masa beasiswa. Setiap keputusan disertai jejak aturan (*rule trace*) beserta sumber regulasinya.

| Komponen wajib | Implementasi |
|---|---|
| Knowledge representation (ontologi + KG) | Ontologi KIP Kuliah di **Neo4j**: hierarki `:Kelas` dengan `SUBKELAS_DARI`, instance `KategoriEkonomi`, `Dokumen`, `KondisiKhusus`, `BiayaPendidikan`, `ZonaBiayaHidup`, `Jenjang`, `ProgramProfesi`, `Sumber` |
| Rules IF–THEN dari pakar/sumber | 63 node `:Rule` (lapis A–G) yang disusun dari Pedoman KIP Kuliah 2025, Persesjen Kemendikbudristek 13/2023, dan Permendikbud 10/2020. Lihat [Expert Project/Rules-Revisi.md](Expert%20Project%20/Rules-Revisi.md) |
| Reasoning + penjelasan | Mesin inferensi **forward chaining** berstrata: setiap rule adalah query Cypher yang dijalankan sampai fixpoint. Setiap rule yang menyala meninggalkan relasi `(:Pendaftar)-[:MEMICU {urutan, kesimpulan}]->(:Rule)` sebagai jejak penjelasan |
| Nilai tambah NLP/LLM | **Gemini**: (1) mengisi formulir dari cerita bebas, (2) menjelaskan jejak aturan dalam bahasa sehari-hari, (3) asisten tanya-jawab yang hanya berpijak pada aturan di knowledge graph. LLM tidak pernah mengambil keputusan |

Panduan penggunaan dan penjelasan teori tersedia di [docs/PANDUAN.md](docs/PANDUAN.md).

Ontologi juga tersedia sebagai RDF/Turtle di [docs/ontologi/](docs/ontologi): `tbox.ttl` (kelas, domain/range, subproperti) dan `abox.ttl` (instance referensi, aturan, dan pendaftar yang diekspor dari Neo4j). Penjelasannya ada di PANDUAN bagian 6.6.

```bash
uv run --directory backend --with rdflib python ../docs/ontologi/ekspor_abox.py   # ekspor ulang ABox
uv run --with rdflib --with owlrl python docs/ontologi/validasi.py                # cek domain/range + closure RDFS
```

## Resource pengumpulan tugas

- **T-Box:** [docs/ontologi/tbox.ttl](docs/ontologi/tbox.ttl)
- **A-Box:** [docs/ontologi/abox.ttl](docs/ontologi/abox.ttl), snapshot hasil ekspor yang tersimpan; tidak otomatis mengikuti database lokal.
- **Apps:** [backend/](backend/) dan [frontend/](frontend/)

Konfigurasi rahasia tidak disimpan di Git. Gunakan `backend/.env.example` sebagai template.

## Arsitektur

```
React + Vite + Tailwind (frontend/)  ──/api──▶  FastAPI (backend/)  ──Bolt──▶  Neo4j
                                                    │
                                                    └──▶ Gemini API (opsional)
```

- `backend/app/ontology.py`: TBox dan instance referensi, dimuat ke Neo4j saat server start.
- `backend/app/rules.py`: basis aturan IF–THEN (bagian IF = `WHERE` Cypher, bagian THEN = `SET`/`MERGE`).
- `backend/app/engine.py`: forward chaining per strata (stratifikasi untuk negasi `NOT` dan agregat `MIN`), perakitan hasil, dan subgraf penjelasan.
- `backend/app/llm.py`: ekstraksi fakta (structured output), penjelasan, dan asisten berbasis Gemini.
- `frontend/src/pages`: Beranda, Cek kelayakan (wizard + isi dari cerita), Hasil (kartu hasil, manfaat, dokumen, jejak aturan, graf penalaran), Aturan & sumber (daftar aturan + graf ontologi). Asisten tanya-jawab tersedia di semua halaman sebagai drawer (`components/AsistenDrawer.tsx`); di halaman hasil, asisten ikut membaca kasus yang sedang dibuka.

## Menjalankan

### Prasyarat
- Python 3.11+ dan [uv](https://docs.astral.sh/uv/)
- Node.js 18+
- Neo4j 5 (Neo4j Desktop, atau Docker)

### 1. Siapkan Neo4j

**Neo4j Desktop:** buat instance baru (atau pakai yang sudah ada), jalankan (*Start*), lalu catat password-nya. Pakai `bolt://127.0.0.1:7687` (bukan `localhost`, yang di macOS bisa mengarah ke IPv6 dan ditolak).

**Alternatif Docker:**
```bash
docker run -d --name kipk-neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password-anda neo4j:5
```

### 2. Backend
```bash
cd backend
cp .env.example .env
```
Isi `NEO4J_PASSWORD` (dan `NEO4J_URI` bila berbeda). Untuk fitur AI, isi `GEMINI_API_KEY` dari [Google AI Studio](https://aistudio.google.com/apikey). Tanpa key, sistem pakar tetap berjalan penuh; hanya tiga fitur AI yang nonaktif.

```bash
uv sync
uv run uvicorn app.main:app --port 8000 --reload
```
Saat start, backend otomatis memuat ontologi dan 63 aturan ke Neo4j. Cek status di http://localhost:8000/api/health.

### 3. Frontend
```bash
cd frontend
npm install
npm run dev
```
Buka http://localhost:5173.

## Mencoba
- Beranda → **Coba dengan profil contoh**: 10 kasus uji (T1–T10) yang mencakup semua jalur keputusan.
- Beranda → tulis cerita → **Isi formulir dari cerita** (butuh Gemini). Field yang diisi AI ditandai stabilo kuning.
- Halaman hasil → tab **Graf penalaran** untuk melihat subgraf Neo4j kasus tersebut.
- Neo4j Browser (http://localhost:7474), contoh query:

```cypher
// Jejak penalaran seorang pendaftar
MATCH (p:Pendaftar {nama: 'Gilang Permana'})-[m:MEMICU]->(r:Rule)-[:BERDASARKAN]->(s:Sumber)
RETURN m.urutan, r.id, m.kesimpulan, s.kode ORDER BY m.urutan;

// Hierarki kelas ontologi
MATCH path = (:Kelas)-[:SUBKELAS_DARI*]->(:Kelas {nama: 'Entitas'}) RETURN path;

// Semua pendaftar layak beserta kategorinya
MATCH (p:PendaftarLayak)-[:BERKATEGORI]->(k:KategoriEkonomi) RETURN p.nama, k.nama;
```

## API ringkas

| Method | Endpoint | Fungsi |
|---|---|---|
| GET | `/api/health` | Status Neo4j dan Gemini |
| GET | `/api/presets` | Profil contoh T1–T10 |
| POST | `/api/evaluasi` | Jalankan inferensi untuk satu pendaftar |
| GET | `/api/hasil/{id}` / `/api/hasil/{id}/graf` | Hasil dan subgraf penjelasan |
| GET | `/api/aturan` / `/api/ontologi/graf` | Basis aturan dan graf ontologi |
| POST | `/api/llm/ekstrak` / `/api/llm/penjelasan/{id}` / `/api/llm/tanya` | Fitur Gemini |
| POST | `/api/seed` | Muat ulang ontologi + aturan, lalu jalankan ulang inferensi semua pendaftar |

## Catatan
Aplikasi ini adalah alat bantu pembelajaran, bukan layanan resmi. Penetapan penerima KIP Kuliah dilakukan perguruan tinggi dan Kemdiktisaintek melalui https://kip-kuliah.kemdiktisaintek.go.id.
