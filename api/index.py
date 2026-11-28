"""Entry point Vercel Functions: aplikasi FastAPI di backend/app dijalankan sebagai fungsi Python.

vercel.json mengarahkan semua /api/* ke fungsi ini; path asli tetap diterima FastAPI.
Frontend dibangun Vercel ke frontend/dist dan disajikan sebagai berkas statis.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.main import app  # noqa: E402,F401
