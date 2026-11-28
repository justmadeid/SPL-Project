"""Ambil screenshot aplikasi untuk docs/PANDUAN.md (disimpan ke docs/img/).

Syarat: backend (port 8000) dan frontend (port 5173) sedang berjalan, Neo4j aktif, dan Google Chrome terpasang.
Fitur Gemini (isi dari cerita, asisten) ikut difoto bila GEMINI_API_KEY aktif; jika gagal, gambar itu dilewati.

Pakai:  uv run --with playwright python docs/pdf/screenshots.py
"""

from pathlib import Path

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

URL = "http://localhost:5173"
OUT = Path(__file__).resolve().parent.parent / "img"
OUT.mkdir(exist_ok=True)


def foto(page, nama, **kw):
    path = OUT / f"{nama}.jpg"
    page.screenshot(path=str(path), type="jpeg", quality=82, **kw)
    print("  ", path.name)


def tunggu_tenang(page, ms=600):
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(ms)


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel="chrome")
        ctx = browser.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=1.5, locale="id-ID")
        page = ctx.new_page()

        # 1. Beranda
        page.goto(URL)
        tunggu_tenang(page, 1200)
        foto(page, "01-beranda")
        page.get_by_text("Coba dengan profil contoh").scroll_into_view_if_needed()
        page.evaluate("window.scrollBy(0, -40)")
        page.wait_for_timeout(400)
        foto(page, "02-profil-contoh")

        # 2. Cek kelayakan: isi dari cerita (Gemini)
        page.goto(URL + "/cek")
        tunggu_tenang(page)
        try:
            page.locator("textarea").first.fill(
                "Saya lulus SMA tahun 2025 dan diterima di Informatika UGM lewat SNBT. Keluarga saya terdata DTKS "
                "dan punya kartu KKS. Penghasilan ayah sekitar 3 juta per bulan untuk 5 orang. Kampus di Yogyakarta."
            )
            page.get_by_role("button", name="Isi formulir dari cerita").click()
            page.get_by_text("isian terisi dari ceritamu").wait_for(timeout=60_000)
            page.wait_for_timeout(500)
            foto(page, "04-cek-dari-cerita")
        except PWTimeout:
            print("   (lewati 04: Gemini tidak menjawab)")

        # langkah 3: ekonomi keluarga
        page.goto(URL + "/cek")
        tunggu_tenang(page)
        page.get_by_role("button", name="Ekonomi keluarga").first.click()
        page.wait_for_timeout(500)
        foto(page, "05-cek-ekonomi")

        # 3. Hasil T10 (Gilang) lewat profil contoh di beranda
        page.goto(URL)
        tunggu_tenang(page)
        page.locator("tr", has_text="Gilang, calon dokter").get_by_role("button", name="Nilai profil").click()
        page.wait_for_url("**/hasil/**")
        tunggu_tenang(page, 1000)
        foto(page, "06-hasil-kartu")
        hasil_url = page.url

        page.get_by_text("Biaya pendidikan (maks)").scroll_into_view_if_needed()
        page.evaluate("window.scrollBy(0, -120)")
        page.wait_for_timeout(300)
        page.get_by_text("Kenapa hasilnya begini").scroll_into_view_if_needed()
        page.locator("li button", has_text="Cocok dengan prioritas 2").first.click()
        page.wait_for_timeout(300)
        page.get_by_text("Kenapa hasilnya begini").evaluate("e => e.scrollIntoView({block: 'start'})")
        page.evaluate("window.scrollBy(0, -90)")
        page.wait_for_timeout(300)
        foto(page, "07-hasil-jejak")

        # graf penalaran
        page.get_by_role("tab", name="Graf penalaran").click()
        page.wait_for_timeout(3500)
        page.get_by_text("Kenapa hasilnya begini").evaluate("e => e.scrollIntoView({block: 'start'})")
        page.evaluate("window.scrollBy(0, -90)")
        page.wait_for_timeout(500)
        foto(page, "09-hasil-graf")

        # 4. Asisten di halaman hasil (Gemini)
        page.goto(hasil_url)
        tunggu_tenang(page, 800)
        page.get_by_role("button", name="Tanya asisten soal hasil ini").click()
        page.wait_for_timeout(600)
        try:
            page.get_by_role("button", name="Berapa total bantuan yang saya terima per semester?").click()
            page.get_by_text("Mencari di basis aturan").wait_for(state="detached", timeout=60_000)
            page.wait_for_timeout(600)
            foto(page, "10-asisten")
        except PWTimeout:
            print("   (lewati 10: Gemini tidak menjawab)")

        # 5. Kasus tidak layak (T4)
        page.goto(URL)
        tunggu_tenang(page)
        page.locator("tr", has_text="Dimas, kelas karyawan").get_by_role("button", name="Nilai profil").click()
        page.wait_for_url("**/hasil/**")
        tunggu_tenang(page, 1000)
        foto(page, "11-hasil-tidak-layak")

        # 6. Aturan & sumber
        page.goto(URL + "/aturan")
        tunggu_tenang(page, 2500)
        foto(page, "12-aturan")

        browser.close()


if __name__ == "__main__":
    main()
