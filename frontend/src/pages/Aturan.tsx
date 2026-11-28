import { useEffect, useMemo, useState } from "react";
import { Loader2, Search } from "lucide-react";
import { api, Aturan as AturanT, Graf } from "../lib/api";
import { RuleId } from "../components/Jejak";
import GrafView from "../components/GrafView";

const SUMBER = [
  { k: "PED", j: "Pedoman Pendaftaran KIP Kuliah 2025 v1.0", p: "Kemdiktisaintek" },
  { k: "PS", j: "Persesjen Kemendikbudristek No. 13 Tahun 2023", p: "Petunjuk pelaksanaan PIP Pendidikan Tinggi" },
  { k: "PM", j: "Permendikbud No. 10 Tahun 2020", p: "Program Indonesia Pintar" },
];

export default function Aturan() {
  const [data, setData] = useState<{ lapis: Record<string, string>; aturan: AturanT[] } | null>(null);
  const [graf, setGraf] = useState<Graf | null>(null);
  const [tab, setTab] = useState<"daftar" | "graf">("daftar");
  const [lapis, setLapis] = useState<string>("semua");
  const [cari, setCari] = useState("");

  useEffect(() => {
    api.aturan().then(setData);
  }, []);
  useEffect(() => {
    if (tab === "graf" && !graf) api.grafOntologi().then(setGraf);
  }, [tab]);

  const tampil = useMemo(() => {
    if (!data) return [];
    const c = cari.toLowerCase();
    return data.aturan.filter(
      (a) => (lapis === "semua" || a.lapis === lapis) && (!c || `${a.id} ${a.nama} ${a.jika} ${a.maka}`.toLowerCase().includes(c))
    );
  }, [data, lapis, cari]);

  return (
    <div className="wadah py-10">
      <h1 className="text-3xl font-extrabold tracking-tight">Aturan dan sumber pengetahuan</h1>
      <p className="mt-2 max-w-2xl text-redup">
        Basis pengetahuan sistem pakar: aturan IF–THEN yang disusun dari regulasi resmi, disimpan sebagai node <code className="rounded bg-white px-1 text-sm">:Rule</code> di Neo4j
        bersama ontologi KIP Kuliah.
      </p>

      <div className="mt-6 grid gap-3 sm:grid-cols-3">
        {SUMBER.map((s) => (
          <div key={s.k} className="rounded-2xl border border-garis bg-white p-4">
            <p className="font-mono text-xs font-semibold text-tinta-muda">{s.k}</p>
            <p className="mt-1 font-semibold leading-snug">{s.j}</p>
            <p className="text-sm text-redup">{s.p}</p>
          </div>
        ))}
      </div>

      <div className="mt-10 flex flex-wrap items-center justify-between gap-3">
        <div className="flex rounded-xl bg-white p-1 text-sm font-semibold" role="tablist">
          {(["daftar", "graf"] as const).map((t) => (
            <button key={t} role="tab" aria-selected={tab === t} onClick={() => setTab(t)} className={`rounded-lg px-3 py-1.5 ${tab === t ? "bg-tinta text-white" : "text-tinta-muda"}`}>
              {t === "daftar" ? "Daftar aturan" : "Graf ontologi"}
            </button>
          ))}
        </div>
        {tab === "daftar" && (
          <label className="relative w-full sm:w-72">
            <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-redup" />
            <input value={cari} onChange={(e) => setCari(e.target.value)} placeholder="Cari aturan, mis. SKTM" className="w-full rounded-xl border border-garis bg-white py-2 pl-9 pr-3 text-sm outline-none focus:border-tinta" />
          </label>
        )}
      </div>

      {tab === "graf" ? (
        <div className="mt-5">
          {graf ? <GrafView data={graf} tinggi={640} labelSemua={false} /> : <div className="flex h-80 items-center justify-center"><Loader2 className="size-6 animate-spin text-tinta" /></div>}
          <p className="mt-2 text-sm text-redup">
            Kelas ontologi (abu-abu) membentuk hierarki <code>SUBKELAS_DARI</code>; aturan (biru tua) terhubung ke konsep yang disimpulkannya dan regulasi sumbernya. Arahkan kursor ke node untuk melihat namanya.
          </p>
        </div>
      ) : !data ? (
        <div className="flex h-60 items-center justify-center"><Loader2 className="size-6 animate-spin text-tinta" /></div>
      ) : (
        <div className="mt-5 grid gap-8 lg:grid-cols-[220px_1fr]">
          <nav className="flex gap-1 overflow-x-auto lg:flex-col" aria-label="Filter lapis">
            {[["semua", "Semua lapis"], ...Object.entries(data.lapis)].map(([k, v]) => {
              const n = k === "semua" ? data.aturan.length : data.aturan.filter((a) => a.lapis === k).length;
              return (
                <button key={k} onClick={() => setLapis(k)} className={`flex shrink-0 items-center justify-between gap-3 rounded-xl px-3 py-2 text-left text-sm font-semibold ${lapis === k ? "bg-tinta text-white" : "text-tinta-muda hover:bg-white"}`}>
                  <span>{k !== "semua" && <span className="mr-1.5 font-mono">{k}</span>}{v}</span>
                  <span className={`tnum text-xs ${lapis === k ? "text-white/70" : "text-redup"}`}>{n}</span>
                </button>
              );
            })}
          </nav>
          <div className="overflow-hidden rounded-2xl border border-garis bg-white">
            {tampil.length === 0 && <p className="p-6 text-sm text-redup">Tidak ada aturan yang cocok dengan pencarian “{cari}”.</p>}
            {tampil.map((a) => (
              <article key={a.id} id={a.id} className="grid gap-2 border-b border-garis p-4 last:border-b-0 sm:grid-cols-[64px_1fr]">
                <div><RuleId id={a.id} /></div>
                <div className="min-w-0">
                  <h3 className="font-bold">{a.nama}</h3>
                  <p className="mt-1.5 text-sm"><span className="font-semibold text-tinta-muda">Jika</span> {a.jika}</p>
                  <p className="text-sm"><span className="font-semibold text-tinta-muda">Maka</span> {a.maka}</p>
                  <p className="mt-1.5 text-xs text-redup">
                    Strata {a.strata}
                    {a.sumber.length > 0 && <>; sumber: {a.sumber.map((s) => `${s.kode} ${s.bagian}`).join("; ")}</>}
                    {a.sumber.length === 0 && a.turunan && <>; asal: {a.turunan}</>}
                  </p>
                </div>
              </article>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
