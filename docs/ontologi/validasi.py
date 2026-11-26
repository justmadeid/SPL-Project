"""Validasi abox.ttl terhadap tbox.ttl dan jalankan closure RDFS.

Yang dicek:
  1. setiap predikat kip: di ABox dideklarasikan di TBox;
  2. domain (rdfs2) dan range (rdfs3): subjek/objek sudah bertipe kelas yang benar
     (memperhitungkan subkelas), SEBELUM reasoner menambah tipe baru;
  3. closure RDFS (owlrl): berapa triple yang diturunkan, dan tipe satu pendaftar setelahnya.

Pakai (dari akar proyek):
  uv run --with rdflib --with owlrl python docs/ontologi/validasi.py ["Nama Pendaftar"]
"""

import sys
from pathlib import Path

import owlrl
from rdflib import Graph, Namespace
from rdflib.namespace import RDF, RDFS

HERE = Path(__file__).resolve().parent
KIP = Namespace("http://pintukuliah.local/ontologi#")


def lokal(iri) -> str:
    return str(iri).split("#")[-1]


def main():
    nama = sys.argv[1] if len(sys.argv) > 1 else "Gilang Permana"
    tbox = Graph().parse(HERE / "tbox.ttl")
    abox = Graph().parse(HERE / "abox.ttl")
    g = tbox + abox
    print(f"TBox {len(tbox)} triple, ABox {len(abox)} triple")

    props = set(tbox.subjects(RDF.type, RDF.Property))
    asing = sorted(lokal(p) for p in set(abox.predicates()) - props if str(p).startswith(str(KIP)))
    print("1. Predikat tanpa deklarasi:", asing or "tidak ada")

    def subkelas(c):
        return {c} | set(tbox.transitive_subjects(RDFS.subClassOf, c))

    def bertipe(x, c):
        return any((x, RDF.type, k) in g for k in subkelas(c))

    langgar = 0
    for p in sorted(props):
        for aksioma, posisi in ((RDFS.domain, 0), (RDFS.range, 2)):
            for c in tbox.objects(p, aksioma):
                if not str(c).startswith(str(KIP)):
                    continue  # range xsd:* / rdfs:Class / rdf:Statement tidak dicek di sini
                salah = {t[posisi] for t in abox.triples((None, p, None)) if not bertipe(t[posisi], c)}
                if salah:
                    langgar += len(salah)
                    print(f"   {lokal(aksioma)} {lokal(p)} dilanggar oleh", [lokal(x) for x in list(salah)[:3]])
    print("2. Pelanggaran domain/range:", langgar)

    n0 = len(g)
    owlrl.DeductiveClosure(owlrl.RDFS_Semantics).expand(g)
    print(f"3. Closure RDFS: {n0} -> {len(g)} triple (+{len(g) - n0})")
    s = KIP["pendaftar_" + "_".join(nama.split())]
    tipe_awal = sorted(lokal(o) for o in abox.objects(s, RDF.type))
    tipe_akhir = sorted(lokal(o) for o in g.objects(s, RDF.type) if str(o).startswith(str(KIP)))
    print(f"   {nama}: tipe di ABox {tipe_awal} -> setelah closure {tipe_akhir}")


if __name__ == "__main__":
    main()
