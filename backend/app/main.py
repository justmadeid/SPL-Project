from contextlib import asynccontextmanager
from typing import Literal, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, model_validator

from . import config, db, engine, llm, ontology, presets


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        ontology.seed()
        n = engine.inferensi_ulang_semua()
        print(f"[kipk] Ontologi & basis aturan dimuat ke Neo4j; inferensi ulang {n} pendaftar")
    except Exception as e:  # tetap jalan agar /api/health bisa memberi tahu masalahnya
        print(f"[kipk] Gagal memuat ontologi ke Neo4j: {e}")
    yield
    db.close()


app = FastAPI(title="Sistem Pakar KIP Kuliah", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


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
