"""Validasi request tanpa startup/seed atau akses database.

Jalankan: uv run python -m unittest discover -s tests -v
"""
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from app.main import app
from app.presets import BASE, daftar


class InputValidationTests(unittest.TestCase):
    def setUp(self):
        # Tanpa context manager: lifespan (seed/inferensi ulang) tidak dijalankan.
        self.client = TestClient(app)
        self.addCleanup(self.client.close)

    def test_invalid_input_rejected_before_engine(self):
        cases = []
        for field in ("penghasilan", "anggota_keluarga"):
            missing = dict(BASE)
            missing.pop(field)
            cases.append((field + " missing", missing))
            for value in (None, "", -1, True, 1.5):
                cases.append((f"{field}={value!r}", {**BASE, field: value}))
        cases.append(("zero family", {**BASE, "anggota_keluarga": 0}))
        for value in (None, 0, 11, True, 1.5):
            cases.append((f"P3KE desil={value!r}", {**BASE, "terdata_p3ke": True, "desil_p3ke": value}))
        with patch("app.main.engine.evaluasi") as evaluate:
            for name, data in cases:
                with self.subTest(name=name):
                    response = self.client.post("/api/evaluasi", json=data)
                    self.assertEqual(response.status_code, 422, response.text)
            evaluate.assert_not_called()

    def test_valid_inputs_keep_existing_contract(self):
        cases = [p["data"] for p in daftar()]
        cases += [{**BASE, "penghasilan": 0, "anggota_keluarga": 1}]
        cases += [{**BASE, "terdata_p3ke": True, "desil_p3ke": n} for n in (1, 3, 10)]
        with patch("app.main.engine.evaluasi", return_value={"ok": True}) as evaluate:
            for data in cases:
                with self.subTest(data=data.get("nama", "boundary")):
                    response = self.client.post("/api/evaluasi?pratinjau=true", json=data)
                    self.assertEqual(response.status_code, 200, response.text)
                    sent, preview = evaluate.call_args.args
                    self.assertEqual(sent["penghasilan"], data["penghasilan"])
                    self.assertEqual(sent["anggota_keluarga"], data["anggota_keluarga"])
                    self.assertTrue(preview)


if __name__ == "__main__":
    unittest.main()
