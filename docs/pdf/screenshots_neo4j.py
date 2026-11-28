"""Ambil screenshot Neo4j Browser untuk docs/PANDUAN.md (disimpan ke docs/img/).

Cara kerja:
1. Jika belum ada Chrome dengan port debug 9333, skrip membukanya (profil di docs/pdf/.chrome-neo4j,
   diabaikan git) ke Neo4j Browser di http://localhost:7474.
2. Login-lah sendiri di jendela itu (username neo4j + password instance). Skrip menunggu maksimal 10 menit.
3. Setelah terhubung, skrip menjalankan beberapa query dan memotret hasilnya. Jendela Chrome dibiarkan terbuka,
   jadi skrip bisa dijalankan ulang tanpa login lagi.

Pakai:  uv run --with playwright python docs/pdf/screenshots_neo4j.py
"""

import subprocess
import time
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "img"
OUT.mkdir(exist_ok=True)
PROFIL = HERE / ".chrome-neo4j"
PORT = 9333
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
URL = "http://localhost:7474/browser/?connectURL=neo4j://neo4j@127.0.0.1:7687"

GILANG = "MATCH (p:Pendaftar {nama: 'Gilang Permana'}) WITH p ORDER BY p.dibuat DESC LIMIT 1\n"

QUERIES = [
    ("13-neo4j-skema", "CALL db.schema.visualization()", 5000),
    ("14-neo4j-hierarki", "MATCH path = (:Kelas)-[:SUBKELAS_DARI*]->(:Kelas {nama: 'Entitas'})\nRETURN path", 5000),
    ("15-neo4j-pendaftar", GILANG + "MATCH (p)-[r]->(n) WHERE NOT n:Rule\nRETURN p, r, n", 6000),
    ("16-neo4j-jejak-graf", GILANG + "MATCH (p)-[m:MEMICU]->(r:Rule)-[b:BERDASARKAN]->(s:Sumber)\nRETURN p, m, r, b, s", 6000),
    ("17-neo4j-jejak-tabel",
     GILANG + "MATCH (p)-[m:MEMICU]->(r:Rule)\nRETURN m.urutan AS urutan, r.id AS aturan, r.nama AS nama, m.kesimpulan AS kesimpulan\nORDER BY urutan",
     3000),
    ("18-neo4j-aturan", "MATCH (r:Rule {id: 'C-02'})-[x]-(n) WHERE NOT n:Pendaftar\nRETURN r, x, n", 5000),
]


def cdp_aktif() -> bool:
    try:
        urllib.request.urlopen(f"http://localhost:{PORT}/json/version", timeout=1)
        return True
    except OSError:
        return False


def jalankan(page, query):
    editor = page.locator(".cm-content").first
    editor.click()
    page.keyboard.press("Meta+A")
    page.keyboard.press("Backspace")
    page.keyboard.insert_text(query)
    page.keyboard.press("Escape")  # tutup popup autocomplete
    page.keyboard.press("Meta+Enter")
    page.wait_for_timeout(300)
    page.mouse.click(100, 850)  # pindahkan fokus dari editor


# Teks (caption) node per label. Gaya ini disimpan Neo4j Browser di profil Chrome.
GAYA = [
    (GILANG + "MATCH (p)-[r]->(n) WHERE NOT n:Rule\nRETURN p, r, n",
     [("Pendaftar", "nama"), ("PendaftarLayak", "nama"), ("Kelas", "nama"), ("KategoriEkonomi", "kode"),
      ("Dokumen", "kode"), ("Keputusan", "kode"), ("ZonaBiayaHidup", "zona"), ("Jenjang", "kode"),
      ("BiayaPendidikan", "kode"), ("ProgramProfesi", "kode")]),
    (GILANG + "MATCH (p)-[m:MEMICU]->(r:Rule)-[b:BERDASARKAN]->(s:Sumber)\nRETURN p, m, r, b, s",
     [("Rule", "id"), ("Sumber", "kode")]),
]


LABEL = ["AlasanGugur", "BiayaPendidikan", "Dokumen", "Jenjang", "KategoriEkonomi", "Kelas", "Keputusan",
         "KondisiKhusus", "Pendaftar", "PendaftarLayak", "PendaftarTidakLayak", "ProgramProfesi", "Rule", "Sumber",
         "ZonaBiayaHidup"]


def atur_gaya(page, gaya=None):
    import re
    for query, daftar in (gaya or GAYA):
        jalankan(page, ":clear")
        page.wait_for_timeout(800)
        jalankan(page, query)
        page.wait_for_timeout(3000)
        for label, caption in daftar:
            chip = page.get_by_text(re.compile(rf"^{label} \(\d+\)$")).first
            if not chip.count():
                print("   (label tidak ada di hasil:", label, ")")
                continue
            chip.click()
            page.wait_for_timeout(400)
            portal = page.locator("[data-floating-ui-portal]").last
            portal.get_by_text(caption, exact=True).first.click()
            page.wait_for_timeout(300)
            page.mouse.click(100, 850)  # klik area kosong di panel kiri untuk menutup popover
            page.wait_for_timeout(300)


def main():
    if not cdp_aktif():
        subprocess.Popen([CHROME, f"--remote-debugging-port={PORT}", f"--user-data-dir={PROFIL}",
                          "--no-first-run", "--no-default-browser-check", "--window-size=1440,960", URL],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        while not cdp_aktif():
            time.sleep(0.5)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(f"http://localhost:{PORT}")
        pages = [p for c in browser.contexts for p in c.pages if "7474" in p.url]
        page = pages[0] if pages else browser.contexts[0].new_page()
        if not pages:
            page.goto(URL)

        print("Menunggu login di jendela Chrome (maks 10 menit)…", flush=True)
        for _ in range(1200):
            pw_field = page.locator("input[type=password]")
            if page.locator(".cm-content").count() and not (pw_field.count() and pw_field.first.is_visible()):
                break
            page.wait_for_timeout(500)
        else:
            raise SystemExit("Belum terhubung setelah 10 menit.")
        print("Terhubung.", flush=True)

        page.set_viewport_size({"width": 1440, "height": 900})
        page.wait_for_timeout(1000)
        for nama, query, jeda in QUERIES:
            if nama.startswith("13-"):
                # Node skema hanya punya properti `name`, jadi caption semua label diganti ke <type> (nama label)
                atur_gaya(page, [(query, [(l, "<type>") for l in LABEL])])
            elif nama.startswith("14-"):
                atur_gaya(page)  # caption data: nama, kode, id, ...
            jalankan(page, ":clear")
            page.wait_for_timeout(800)
            jalankan(page, query)
            page.wait_for_timeout(jeda)
            if nama.startswith("14-"):
                page.get_by_role("button", name="Zoom in").first.click()
                page.wait_for_timeout(800)
            page.mouse.move(700, 5)  # jauhkan kursor dari graf agar tidak ada tooltip
            page.wait_for_timeout(300)
            # Skema difoto utuh (panel kiri ikut berguna); sisanya dipotong ke area editor + hasil query
            clip = None if nama.startswith("13-") else {"x": 372, "y": 31, "width": 1068, "height": 729}
            page.screenshot(path=str(OUT / f"{nama}.jpg"), type="jpeg", quality=82, clip=clip)
            print("  ", nama, flush=True)
        # Chrome sengaja tidak ditutup supaya skrip bisa dijalankan ulang tanpa login.


if __name__ == "__main__":
    main()
