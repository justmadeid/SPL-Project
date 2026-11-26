"""Integrasi LLM (Gemini) sebagai pendukung sistem pakar.

LLM TIDAK mengambil keputusan. Perannya:
  1. ekstrak()    : NLP — ubah cerita bebas pendaftar menjadi fakta terstruktur (mengisi formulir).
  2. jelaskan()   : ubah jejak rule (hasil mesin inferensi) menjadi narasi yang mudah dipahami.
  3. tanya()      : asisten tanya-jawab yang hanya berpijak pada basis aturan di knowledge graph.
"""

import json
import time

from typing import Optional

from google import genai
from google.genai import errors as genai_errors
from google.genai import types
from pydantic import BaseModel, Field

from . import config

_client = None


class LLMNonaktif(Exception):
    pass


def client():
    global _client
    if not config.LLM_ENABLED:
        raise LLMNonaktif("GEMINI_API_KEY belum diisi di backend/.env")
    if _client is None:
        _client = genai.Client(api_key=config.GEMINI_API_KEY)
    return _client


class LLMSibuk(Exception):
    pass


def _cfg(model: str, system: str, **kw) -> types.GenerateContentConfig:
    extra = {}
    # Keputusan dibuat mesin aturan; Gemini hanya merangkai bahasa, jadi mode berpikir dimatikan/diminimalkan
    if "2.5" in model and "pro" not in model:
        extra["thinking_config"] = types.ThinkingConfig(thinking_budget=0)
    elif model.startswith("gemini-3"):
        extra["thinking_config"] = types.ThinkingConfig(thinking_level="minimal")
    return types.GenerateContentConfig(system_instruction=system, **extra, **kw)


_MODEL_MATI: set[str] = set()  # model yang membalas 404 untuk key ini; tidak dicoba lagi selama server hidup
BATAS_PANGGILAN_MS = 25_000  # batas waktu satu panggilan Gemini
BATAS_TOTAL_S = 45  # batas waktu seluruh percobaan (termasuk model cadangan)


def _generate(contents, system: str, **kw):
    """Panggil Gemini dengan batas waktu. Bila model sibuk, lambat, atau tidak tersedia, pindah ke model cadangan."""
    models = [config.GEMINI_MODEL] + [m for m in config.GEMINI_FALLBACK_MODELS if m != config.GEMINI_MODEL]
    mulai = time.monotonic()
    for model in models:
        if model in _MODEL_MATI:
            continue
        for percobaan in range(2):
            if time.monotonic() - mulai > BATAS_TOTAL_S:
                raise LLMSibuk("Layanan Gemini sedang lambat. Coba lagi beberapa saat lagi.")
            try:
                cfg = _cfg(model, system, http_options=types.HttpOptions(timeout=BATAS_PANGGILAN_MS), **kw)
                return client().models.generate_content(model=model, contents=contents, config=cfg)
            except genai_errors.APIError as e:
                if e.code == 404:
                    print(f"[kipk] Gemini {model} tidak tersedia (404), tidak dicoba lagi")
                    _MODEL_MATI.add(model)
                    break
                if e.code == 504:  # habis waktu di sisi Google: langsung pindah model
                    print(f"[kipk] Gemini {model} habis waktu (504), pindah model")
                    break
                if e.code not in (429, 500, 503):
                    raise
                print(f"[kipk] Gemini {model} sibuk ({e.code}), percobaan {percobaan + 1}")
                time.sleep(1.5 * (percobaan + 1))
            except Exception as e:
                # timeout dari klien HTTP (httpx/httpx2): kenali lewat nama kelasnya
                if not any("Timeout" in c.__name__ for c in type(e).__mro__):
                    raise
                print(f"[kipk] Gemini {model} tidak menjawab dalam {BATAS_PANGGILAN_MS // 1000} detik, pindah model")
                break
    raise LLMSibuk("Layanan Gemini sedang sibuk. Coba lagi beberapa saat lagi.")


# ------------------------------------------------------------------ 1. Ekstraksi fakta
class FaktaEkstraksi(BaseModel):
    nama: Optional[str] = Field(None, description="Nama pendaftar")
    tahun_lulus: Optional[int] = Field(None, description="Tahun lulus SMA/SMK/MA")
    status_seleksi: Optional[str] = Field(None, description="'Lulus' jika sudah diterima di perguruan tinggi, 'Tidak_Lulus' jika tidak")
    jenis_kampus: Optional[str] = Field(None, description="'PTN' atau 'PTS'")
    nama_kampus: Optional[str] = None
    nama_prodi: Optional[str] = Field(None, description="Nama program studi")
    rumpun_prodi: Optional[str] = Field(None, description="Salah satu: Kedokteran, Kedokteran_Gigi, Kedokteran_Hewan, Keperawatan, Farmasi, Kebidanan, Kependidikan, Lainnya")
    akreditasi_prodi: Optional[str] = Field(None, description="Salah satu: Unggul, A, Internasional, Baik_Sekali, B, Baik, C, Belum_Terakreditasi")
    jenjang: Optional[str] = Field(None, description="Salah satu: Sarjana, Diploma_IV, Diploma_III, Diploma_II, Diploma_I")
    jenis_kelas: Optional[str] = Field(None, description="Salah satu: Reguler, Eksekutif, Khusus, Karyawan")
    beasiswa_lain: Optional[bool] = Field(None, description="Sedang menerima beasiswa lain dari APBN/APBD/sumber lain")
    kip_sma: Optional[bool] = Field(None, description="Punya Kartu Indonesia Pintar saat SMA")
    dtks: Optional[bool] = Field(None, description="Keluarga terdata DTKS")
    pkh: Optional[bool] = Field(None, description="Keluarga penerima PKH")
    kks: Optional[bool] = Field(None, description="Keluarga pemegang KKS")
    terdata_p3ke: Optional[bool] = None
    desil_p3ke: Optional[int] = Field(None, description="Desil P3KE 1-10")
    panti: Optional[bool] = Field(None, description="Tinggal di panti asuhan / panti sosial")
    penghasilan: Optional[int] = Field(None, description="Penghasilan kotor gabungan orang tua/wali per bulan dalam rupiah (angka penuh, mis. 3 juta = 3000000)")
    anggota_keluarga: Optional[int] = Field(None, description="Jumlah anggota keluarga dalam satu KK")
    sktm: Optional[bool] = Field(None, description="Punya Surat Keterangan Tidak Mampu")
    bukti_sktm: Optional[bool] = Field(None, description="Punya rekening listrik dan foto rumah sebagai bukti dukung SKTM")
    asal_3t: Optional[bool] = Field(None, description="Berasal dari daerah terdepan, terluar, tertinggal")
    asli_papua: Optional[bool] = None
    anak_tki: Optional[bool] = Field(None, description="Anak TKI yang tinggal di daerah perbatasan")
    bencana: Optional[bool] = Field(None, description="Terdampak bencana alam")
    konflik: Optional[bool] = Field(None, description="Terdampak konflik sosial")
    korban_kekerasan: Optional[bool] = None
    korban_ham: Optional[bool] = Field(None, description="Korban pelanggaran HAM berat")
    zona: Optional[str] = Field(None, description="Zona biaya hidup A-E jika disebut eksplisit")


class HasilEkstraksi(BaseModel):
    fakta: FaktaEkstraksi
    belum_diketahui: list[str] = Field(default_factory=list, description="Informasi penting yang belum disebut pengguna, dalam kalimat pendek bahasa Indonesia")


SYS_EKSTRAK = """Kamu adalah modul NLP pada sistem pakar kelayakan KIP Kuliah.
Tugasmu HANYA mengekstrak fakta dari cerita pengguna ke skema JSON. Jangan menilai kelayakan.
Aturan:
- Isi field hanya jika informasinya disebut atau tersirat sangat jelas. Selain itu biarkan null.
- Uang ditulis dalam rupiah penuh (contoh: "3,5 juta" -> 3500000; "800 ribu" -> 800000).
- Jika ayah dan ibu sama-sama berpenghasilan, jumlahkan sebagai penghasilan gabungan.
- Universitas negeri (UI, UGM, ITB, Unair, Undip, UNY, dsb.) -> PTN; universitas swasta -> PTS.
- "Diterima/lolos SNBP/SNBT/mandiri" -> status_seleksi 'Lulus'.
- Program studi pendidikan/keguruan -> rumpun_prodi 'Kependidikan'. S1 -> 'Sarjana'. D3 -> 'Diploma_III'.
- Daftar di belum_diketahui maksimal 5 hal terpenting yang belum disebut (mis. akreditasi prodi, penghasilan orang tua)."""

ENUMS = {
    "status_seleksi": {"Lulus", "Tidak_Lulus"},
    "jenis_kampus": {"PTN", "PTS"},
    "rumpun_prodi": {"Kedokteran", "Kedokteran_Gigi", "Kedokteran_Hewan", "Keperawatan", "Farmasi", "Kebidanan", "Kependidikan", "Lainnya"},
    "akreditasi_prodi": {"Unggul", "A", "Internasional", "Baik_Sekali", "B", "Baik", "C", "Belum_Terakreditasi"},
    "jenjang": {"Sarjana", "Diploma_IV", "Diploma_III", "Diploma_II", "Diploma_I"},
    "jenis_kelas": {"Reguler", "Eksekutif", "Khusus", "Karyawan"},
    "zona": {"A", "B", "C", "D", "E"},
}


def ekstrak(teks: str) -> dict:
    resp = _generate(teks, SYS_EKSTRAK, response_mime_type="application/json", response_schema=HasilEkstraksi, temperature=0.1)
    parsed: HasilEkstraksi = resp.parsed or HasilEkstraksi.model_validate_json(resp.text)
    fakta = {k: v for k, v in parsed.fakta.model_dump().items() if v is not None}
    for k, allowed in ENUMS.items():
        if k in fakta and fakta[k] not in allowed:
            fakta.pop(k)
    if fakta.get("desil_p3ke") is not None:
        fakta["terdata_p3ke"] = True
    return {"fakta": fakta, "belum_diketahui": parsed.belum_diketahui[:5]}


# ------------------------------------------------------------------ 2. Penjelasan keputusan
SYS_JELASKAN = """Kamu menjelaskan hasil sistem pakar KIP Kuliah kepada calon mahasiswa (usia ~18 tahun).
Keputusan SUDAH dibuat oleh mesin inferensi berbasis aturan. Jangan mengubah, meragukan, atau menambah keputusan.
Tulis dalam bahasa Indonesia yang hangat, jelas, dan ringkas (maksimal 170 kata), dengan struktur:
1. Satu kalimat inti hasilnya.
2. Satu paragraf alasan: rangkai rule yang menyala, sebut ID rule dalam kurung siku, mis. [C-01].
3. Satu paragraf langkah berikutnya (dokumen yang perlu disiapkan, atau apa yang bisa dilakukan jika tidak layak).
Jangan memakai heading atau bullet. Jangan menyebut dirimu AI."""


def jelaskan(hasil: dict) -> str:
    ringkas = {
        "nama": hasil["input"].get("nama"),
        "keputusan": hasil["keputusan"],
        "jalur": hasil["jalur"],
        "kategori": hasil["kategori"],
        "alasan_gugur": [a["teks"] for a in hasil["alasan_gugur"]],
        "kondisi_khusus": [k["nama"] for k in hasil["kondisi_khusus"]],
        "dokumen": [d["nama"] for d in hasil["dokumen"]],
        "manfaat": hasil["manfaat"],
        "jejak_rule": [{"id": t["id"], "kesimpulan": t["kesimpulan"]} for t in hasil["trace"]],
    }
    resp = _generate("Hasil sistem pakar (JSON):\n" + json.dumps(ringkas, ensure_ascii=False), SYS_JELASKAN, temperature=0.4)
    return (resp.text or "").strip()


# ------------------------------------------------------------------ 3. Asisten tanya-jawab (grounded)
SYS_TANYA = """Kamu adalah asisten informasi KIP Kuliah di dalam sebuah sistem pakar.
Jawab HANYA berdasarkan BASIS PENGETAHUAN di bawah (aturan dari knowledge graph Neo4j beserta sumber regulasinya).
- Sebut ID rule yang relevan dalam kurung siku, mis. [A-08], dan sumbernya bila membantu.
- Jika pertanyaan di luar basis pengetahuan, katakan bahwa informasinya tidak ada di basis aturan dan sarankan cek
  laman resmi kip-kuliah.kemdiktisaintek.go.id.
- Jika pengguna bertanya apakah dirinya layak, arahkan untuk memakai fitur "Cek kelayakan" agar dinilai mesin aturan.
- Bahasa Indonesia, ramah, ringkas (maksimal 150 kata), boleh memakai daftar pendek.

BASIS PENGETAHUAN:
{kb}
{kasus}"""


def tanya(pesan: list[dict], aturan: list[dict], hasil: dict | None = None) -> str:
    kb = "\n".join(
        f"[{r['id']}] {r['nama']} | JIKA {r['jika']} | MAKA {r['maka']} | Sumber: "
        + "; ".join(f"{s['kode']} {s['bagian']}" for s in r["sumber"])
        for r in aturan
    )
    kb += ("\nSumber: PED = Pedoman Pendaftaran KIP Kuliah 2025; PS = Persesjen Kemendikbudristek No. 13/2023; "
           "PM = Permendikbud No. 10/2020.")
    kasus = ""
    if hasil:
        kasus = "\nKASUS PENGGUNA SAAT INI (hasil mesin inferensi):\n" + json.dumps(
            {"keputusan": hasil["keputusan"], "jalur": hasil["jalur"], "jejak": [t["id"] + ": " + t["kesimpulan"] for t in hasil["trace"]]},
            ensure_ascii=False,
        )
    contents = [
        types.Content(role="user" if m["role"] == "user" else "model", parts=[types.Part(text=m["content"])])
        for m in pesan[-12:]
    ]
    resp = _generate(contents, SYS_TANYA.format(kb=kb, kasus=kasus), temperature=0.3)
    return (resp.text or "").strip()
