from contextlib import asynccontextmanager
import threading
import time
from typing import Literal, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from neo4j.exceptions import Neo4jError
from pydantic import BaseModel, Field, model_validator

from . import config, db, engine, llm, ontology, presets


_siap = False
_kunci = threading.Lock()


def siapkan_database():
    """Muat ontologi + aturan ke Neo4j. Dipanggil saat startup, atau saat request pertama
    di lingkungan serverless (Vercel) yang tidak menjalankan lifespan secara andal."""
    global _siap
    with _kunci:
        if _siap:
            return
        if config.PUBLIC_DEMO:
            _seed_demo()
        else:
            ontology.seed()
            n = engine.inferensi_ulang_semua()
            print(f"[kipk] Ontologi & basis aturan dimuat ke Neo4j; inferensi ulang {n} pendaftar")
        _siap = True


def _seed_demo(tunggu_maks: float = 50.0):
    """Seed database demo tepat sekali, walau beberapa instance serverless menyala bersamaan.

    Kunci disimpan di database sebagai node (:SeedKunci {id: 1}) dengan constraint unik:
    hanya instance yang berhasil membuatnya yang menjalankan seed; instance lain menunggu
    sampai statusnya 'selesai'. Kunci 'berjalan' yang berumur > 2 menit dianggap macet.
    """
    try:
        db.run("CREATE CONSTRAINT seed_kunci IF NOT EXISTS FOR (s:SeedKunci) REQUIRE s.id IS UNIQUE")
    except Neo4jError:
        pass  # dibuat bersamaan oleh instance lain
    batas = time.monotonic() + tunggu_maks
    while True:
        st = db.run("MATCH (s:SeedKunci {id: 1}) RETURN s.status AS status, timestamp() - s.mulai AS umur")
        if st and st[0]["status"] == "selesai":
            n = db.run("MATCH (r:Rule) RETURN count(r) AS n")[0]["n"]
            if n != len(engine.RULES):
                raise RuntimeError("Jumlah aturan database demo tidak sesuai versi aplikasi")
            return
        if not st or st[0]["umur"] > 120_000:
            if st:
                db.run("MATCH (s:SeedKunci {id: 1}) WHERE s.status = 'berjalan' DELETE s")
            try:
                db.run("CREATE (:SeedKunci {id: 1, status: 'berjalan', mulai: timestamp()})")
            except Neo4jError:
                continue  # instance lain lebih dulu mengambil kunci
            try:
                ontology.seed()
            except Exception:
                db.run("MATCH (s:SeedKunci {id: 1}) DELETE s")
                raise
            db.run("MATCH (s:SeedKunci {id: 1}) SET s.status = 'selesai', s.selesai = timestamp()")
            print("[kipk] Seed database demo selesai")
            return
        if time.monotonic() > batas:
            raise RuntimeError("Seed database demo sedang dijalankan instance lain")
        time.sleep(1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        siapkan_database()
    except Exception as e:  # tetap jalan agar /api/health bisa memberi tahu masalahnya
        print(f"[kipk] Gagal memuat ontologi ke Neo4j: {e}")
    yield
    db.close()


app = FastAPI(title="Sistem Pakar KIP Kuliah", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.middleware("http")
async def pastikan_siap(request: Request, call_next):
    # Seed malas untuk demo serverless: request /api pertama memastikan basis aturan sudah ada.
    # Di mode lokal seed penuh hanya dijalankan lifespan saat server start.
    if (config.PUBLIC_DEMO and not _siap and request.url.path.startswith("/api/")
            and request.url.path != "/api/health"):
        try:
            await run_in_threadpool(siapkan_database)
        except Exception as e:
            print(f"[kipk] Gagal memuat ontologi ke Neo4j: {e}")
    return await call_next(request)


class FormInput(BaseModel):
    nama: str = ""
    tahun_daftar: int = 2026
    tahun_lulus: int
    status_seleksi: Literal["Lulus", "Tidak_Lulus"]
    jenis_kampus: Literal["PTN", "PTS"]
    nama_kampus: str = ""
    akreditasi_prodi: Literal["Unggul", "A", "Internasional", "Baik_Sekali", "B", "Baik", "C", "Belum_Terakreditasi"]
    jenis_kelas: Literal["Reguler", "Eksekutif", "Khusus", "Karyawan"] = "Reguler"
    beasiswa_lain: bool = False
    kip_sma: bool = False
    dtks: bool = False
    pkh: bool = False
    kks: bool = False
    terdata_p3ke: bool = False
    desil_p3ke: Optional[int] = Field(None, ge=1, le=10, strict=True)
    panti: bool = False
    penghasilan: int = Field(..., ge=0, strict=True)
    anggota_keluarga: int = Field(..., ge=1, strict=True)
    sktm: bool = False
    bukti_sktm: bool = False
    asal_3t: bool = False
    asli_papua: bool = False
    anak_tki: bool = False
    bencana: bool = False
    konflik: bool = False
    korban_kekerasan: bool = False
    korban_ham: bool = False
    nama_prodi: str = ""
    rumpun_prodi: str = "Lainnya"
    jenjang: Literal["Sarjana", "Diploma_IV", "Diploma_III", "Diploma_II", "Diploma_I"] = "Sarjana"
    zona: Literal["A", "B", "C", "D", "E"] = "C"


    @model_validator(mode="after")
    def validasi_desil_p3ke(self):
        if self.terdata_p3ke and self.desil_p3ke is None:
            raise ValueError("Desil P3KE wajib diisi jika terdata P3KE.")
        return self


class TeksInput(BaseModel):
    teks: str = Field(min_length=10, max_length=4000)


class Pesan(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class TanyaInput(BaseModel):
    pesan: list[Pesan]
    hasil_id: Optional[str] = None


def _llm(fn, *a):
    if not config.LLM_ENABLED:
        raise HTTPException(503, "Fitur AI tidak aktif pada demo publik. Gunakan formulir atau profil contoh.")
    try:
        return fn(*a)
    except llm.LLMNonaktif as e:
        raise HTTPException(503, str(e))
    except llm.LLMSibuk as e:
        raise HTTPException(503, str(e))
    except Exception as e:
        raise HTTPException(502, f"Gemini gagal merespons: {e}")


@app.get("/api/health")
def health():
    try:
        stat = engine.statistik()
        neo = {"ok": True, "uri": config.NEO4J_URI, **stat}
    except Exception as e:
        neo = {"ok": False, "uri": config.NEO4J_URI, "error": str(e)}
    return {"neo4j": neo, "llm": {"aktif": config.LLM_ENABLED, "model": config.GEMINI_MODEL}}


@app.post("/api/seed")
def seed():
    if config.PUBLIC_DEMO or not config.ENABLE_SEED_ENDPOINT:
        raise HTTPException(403, "Reset basis pengetahuan tidak diizinkan.")
    ontology.seed()
    engine.inferensi_ulang_semua()
    return engine.statistik()


@app.get("/api/presets")
def get_presets():
    return presets.daftar()


@app.post("/api/evaluasi")
def evaluasi(data: FormInput, pratinjau: bool = False):
    return engine.evaluasi(data.model_dump(), pratinjau)


@app.get("/api/hasil/{pid}")
def get_hasil(pid: str):
    h = engine.hasil(pid)
    if not h:
        raise HTTPException(404, "Hasil tidak ditemukan")
    return h


@app.get("/api/hasil/{pid}/graf")
def get_graf(pid: str):
    return engine.graf_pendaftar(pid)


@app.get("/api/aturan")
def get_aturan():
    return {"lapis": engine.lapis(), "aturan": engine.daftar_aturan()}


@app.get("/api/ontologi/graf")
def get_ontologi():
    return engine.graf_ontologi()


@app.post("/api/llm/ekstrak")
def llm_ekstrak(body: TeksInput):
    return _llm(llm.ekstrak, body.teks)


@app.post("/api/llm/penjelasan/{pid}")
def llm_penjelasan(pid: str):
    h = engine.hasil(pid)
    if not h:
        raise HTTPException(404, "Hasil tidak ditemukan")
    return {"teks": _llm(llm.jelaskan, h)}


@app.post("/api/llm/tanya")
def llm_tanya(body: TanyaInput):
    h = engine.hasil(body.hasil_id) if body.hasil_id else None
    jawab = _llm(llm.tanya, [m.model_dump() for m in body.pesan], engine.daftar_aturan(), h)
    return {"teks": jawab}


@app.get("/api/ready")
def ready():
    try:
        count = db.run("MATCH (r:Rule) RETURN count(r) AS n")[0]["n"]
        if count != len(engine.RULES):
            raise RuntimeError("Basis aturan belum siap")
    except Exception:
        raise HTTPException(503, "Database demo belum siap")
    return {"ok": True}


# Hasil build React dilayani dari origin yang sama dengan /api.
FRONTEND_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if (FRONTEND_DIST / "index.html").is_file():
    for folder in ("assets", "images"):
        if (FRONTEND_DIST / folder).is_dir():
            app.mount(f"/{folder}", StaticFiles(directory=FRONTEND_DIST / folder), name=folder)

    @app.get("/", include_in_schema=False)
    @app.get("/cek", include_in_schema=False)
    @app.get("/aturan", include_in_schema=False)
    @app.get("/hasil/{pid}", include_in_schema=False)
    def frontend(pid: str = ""):
        return FileResponse(FRONTEND_DIST / "index.html")
