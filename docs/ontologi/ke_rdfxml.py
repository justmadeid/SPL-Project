"""Buat versi RDF/XML (.rdf) dari tbox.ttl dan abox.ttl.

Isi triple sama persis; hanya formatnya berbeda, untuk alat yang lebih nyaman dengan RDF/XML (mis. Protégé).

Pakai (dari akar proyek):
  uv run --with rdflib python docs/ontologi/ke_rdfxml.py
"""

from pathlib import Path

from rdflib import Graph

HERE = Path(__file__).resolve().parent

for nama in ("tbox", "abox"):
    g = Graph().parse(HERE / f"{nama}.ttl")
    keluar = HERE / f"{nama}.rdf"
    g.serialize(keluar, format="pretty-xml", encoding="utf-8")
    cek = Graph().parse(keluar, format="xml")
    assert len(cek) == len(g), f"{nama}: jumlah triple berbeda setelah konversi"
    print(f"{keluar.name}: {len(g)} triple")
