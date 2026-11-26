import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { AlertTriangle, Check, Loader2, MessageCircle, Sparkles } from "lucide-react";
import { api, Graf, Hasil as HasilT, rupiah } from "../lib/api";
import KartuHasil from "../components/KartuHasil";
import Jejak, { RuleId } from "../components/Jejak";
import GrafView from "../components/GrafView";
import { useAsisten } from "../components/AsistenDrawer";

function renderTeks(t: string) {
  // Tandai rujukan rule [X-00] di teks penjelasan
  return t.split(/(\[[A-G]-\d{2}\])/g).map((s, i) =>
    /^\[[A-G]-\d{2}\]$/.test(s) ? <RuleId key={i} id={s.slice(1, -1)} /> : <span key={i}>{s}</span>
  );
}

function Penjelasan({ id }: { id: string }) {
  const [st, setSt] = useState<{ s: "idle" | "load" | "ok" | "err"; t?: string }>({ s: "idle" });
  const minta = async () => {
    setSt({ s: "load" });
    try {
      const r = await api.penjelasan(id);
      setSt({ s: "ok", t: r.teks });
    } catch (e: any) {
      setSt({ s: "err", t: e.message });
    }
  };
  return (
    <div className="rounded-2xl border border-garis bg-white p-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h3 className="flex items-center gap-2 font-bold"><Sparkles className="size-4" /> Penjelasan dalam bahasa sehari-hari</h3>
        {st.s !== "ok" && (
          <button onClick={minta} disabled={st.s === "load"} className="inline-flex items-center gap-2 rounded-xl bg-tinta px-3.5 py-2 text-sm font-bold text-white hover:bg-tinta-tua disabled:opacity-50">
            {st.s === "load" && <Loader2 className="size-4 animate-spin" />} {st.s === "load" ? "Menyusun penjelasan…" : "Jelaskan hasil ini"}
          </button>
        )}
      </div>
      {st.s === "idle" && <p className="mt-2 text-sm text-redup">Gemini merangkum jejak aturan di bawah menjadi penjelasan singkat. Keputusannya tidak berubah.</p>}
      {st.s === "err" && <p className="mt-3 rounded-xl bg-gagal-muda px-4 py-3 text-sm text-gagal">{st.t}</p>}
      {st.s === "ok" && (
        <div className="mt-3 grid gap-3 text-[15px] leading-relaxed">
          {st.t!.split(/\n\s*\n/).map((p, i) => <p key={i}>{renderTeks(p)}</p>)}
        </div>
      )}
    </div>
  );
}

export default function Hasil() {
  const { id } = useParams();
  const [h, setH] = useState<HasilT | null>(null);
  const [graf, setGraf] = useState<Graf | null>(null);
  const [tab, setTab] = useState<"jejak" | "graf">("jejak");
  const [galat, setGalat] = useState("");
  const [cek, setCek] = useState<Record<string, boolean>>({});
  const asisten = useAsisten();

  // drawer asisten global ikut membaca kasus ini selama halaman hasil terbuka
  useEffect(() => {
    if (h) asisten.setKonteks({ id: h.id, nama: h.input.nama });
    return () => asisten.setKonteks(null);
  }, [h, asisten]);

  useEffect(() => {
    api.hasil(id!).then(setH).catch((e) => setGalat(e.message));
  }, [id]);
  useEffect(() => {
    if (tab === "graf" && !graf) api.grafHasil(id!).then(setGraf);
  }, [tab]);

  if (galat) return <p className="wadah py-16 text-gagal">{galat}</p>;
  if (!h) return <div className="wadah flex justify-center py-24"><Loader2 className="size-6 animate-spin text-tinta" /></div>;

  const layak = h.keputusan === "Layak";
  const m = h.manfaat;
  const selesai = h.dokumen.filter((d) => cek[d.kode]).length;

  return (
    <div className="wadah py-10">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <Link to="/cek" className="text-sm font-semibold text-tinta-muda hover:underline">Kembali ke formulir</Link>
      </div>

      <div className="mt-6 grid items-start gap-8 lg:grid-cols-[minmax(0,34rem)_minmax(0,1fr)] lg:gap-12">
        <div className="max-w-[34rem] pt-8">
          <KartuHasil
            h={h}
            besar
            aksi={
              <button
                onClick={asisten.buka}
                aria-controls="drawer-asisten"
                className="inline-flex items-center gap-2 rounded-full bg-stabilo px-3.5 py-2 text-sm font-semibold text-tinta-tua transition-colors hover:bg-white"
              >
                <MessageCircle className="size-4" /> Tanya asisten soal hasil ini
              </button>
            }
          />
        </div>

        <div className="grid content-start gap-4 lg:pt-8">
          <h2 className="text-2xl font-extrabold tracking-tight">
            {layak ? "Kamu memenuhi syarat KIP Kuliah." : "Kamu belum memenuhi syarat KIP Kuliah."}
          </h2>
          {layak ? (
            <p className="text-redup">
              {h.kategori
                ? `Masuk prioritas ${h.kategori.prioritas} (${h.kategori.nama}).`
                : "Lolos melalui pertimbangan khusus karena kondisi yang kamu pilih."}{" "}
              Penetapan akhir tetap melalui verifikasi perguruan tinggi.
            </p>
          ) : h.alasan_gugur.length ? (
            <div className="rounded-2xl bg-gagal-muda p-4">
              <p className="flex items-center gap-2 font-bold text-gagal"><AlertTriangle className="size-4" /> Gugur di syarat administrasi</p>
              <ul className="mt-2 grid gap-1.5 text-sm">
                {h.alasan_gugur.map((a) => (
                  <li key={a.kode} className="flex gap-2"><RuleId id={a.kode} /> {a.teks}</li>
                ))}
              </ul>
            </div>
          ) : (
            <p className="text-redup">Syarat administrasi terpenuhi, tetapi tidak ada kriteria ekonomi maupun kondisi khusus yang cocok.</p>
          )}
          {h.cocok_prioritas.length > 1 && (
            <p className="text-sm text-redup">
              Cocok dengan prioritas {h.cocok_prioritas.map((c) => c.prioritas).join(", ")}; yang dipakai adalah prioritas tertinggi.
            </p>
          )}
          <div className="mt-2 grid gap-4">
          <div className="rounded-2xl border border-garis bg-white p-5">
            <div className="flex items-baseline justify-between">
              <h2 className="font-bold">Dokumen yang perlu disiapkan</h2>
              {h.dokumen.length > 0 && <span className="tnum text-sm text-redup">{selesai}/{h.dokumen.length}</span>}
            </div>
            {h.dokumen.length ? (
              <ul className="mt-3 grid gap-2">
                {h.dokumen.map((d) => (
                  <li key={d.kode}>
                    <label className="flex cursor-pointer gap-3 rounded-xl border border-garis p-3 text-sm hover:bg-kertas">
                      <input type="checkbox" className="peer sr-only" checked={!!cek[d.kode]} onChange={(e) => setCek({ ...cek, [d.kode]: e.target.checked })} />
                      <span className={`mt-0.5 grid size-5 shrink-0 place-items-center rounded-md border-2 peer-focus-visible:ring-2 peer-focus-visible:ring-stabilo ${cek[d.kode] ? "border-layak bg-layak text-white" : "border-garis"}`}>
                        {cek[d.kode] && <Check className="size-3.5" strokeWidth={3} />}
                      </span>
                      <span>
                        <span className={`font-semibold ${cek[d.kode] ? "text-redup line-through" : ""}`}>{d.nama}</span>
                        <span className="block text-xs text-redup">{d.keterangan}</span>
                      </span>
                    </label>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="mt-2 text-sm text-redup">
                Tidak ada dokumen karena hasilnya belum layak. Perbaiki syarat yang menjadi alasan, atau{" "}
                <button onClick={asisten.buka} className="font-semibold text-tinta underline">tanyakan alternatifnya ke asisten</button>.
              </p>
            )}
          </div>
          {h.kondisi_khusus.length > 0 && (
            <div className="mt-4 rounded-2xl border border-garis bg-white p-5 text-sm">
              <h2 className="font-bold">Kondisi khusus tercatat</h2>
              <ul className="mt-2 list-disc pl-5 text-redup">{h.kondisi_khusus.map((k) => <li key={k.kode}>{k.nama}</li>)}</ul>
            </div>
          )}
          </div>
        </div>
      </div>

      {layak && (
        <section className="mt-12 grid gap-px overflow-hidden rounded-2xl border border-garis bg-garis sm:grid-cols-2 lg:grid-cols-4">
          {[
            ["Biaya pendidikan (maks)", m.ukt ? rupiah(m.ukt.maks) : "–", "per semester, dibayar langsung ke kampus"],
            ["Biaya hidup", m.biaya_hidup ? rupiah(m.biaya_hidup.per_bulan) : "–", m.biaya_hidup ? `per bulan, cair ${rupiah(m.biaya_hidup.per_semester)} tiap semester (zona ${m.biaya_hidup.zona})` : ""],
            ["Masa beasiswa", m.jenjang ? `${m.jenjang.maks_semester} semester` : "–", m.jenjang?.nama ?? ""],
            ["Lanjut profesi", m.profesi ? `${m.profesi.maks_semester} semester` : "Tidak ada", m.profesi ? m.profesi.nama : "Prodi ini tidak berlanjut ke program profesi"],
          ].map(([k, v, d]) => (
            <div key={k} className="bg-white p-5">
              <p className="text-sm font-semibold text-redup">{k}</p>
              <p className="tnum mt-1 text-2xl font-extrabold tracking-tight">{v}</p>
              <p className="mt-1 text-xs leading-relaxed text-redup">{d}</p>
            </div>
          ))}
        </section>
      )}

        <section className="mt-14">
          <div className="flex flex-wrap items-end justify-between gap-3">
            <div>
              <h2 className="text-xl font-extrabold tracking-tight">Kenapa hasilnya begini</h2>
              <p className="mt-1 text-sm text-redup">{h.trace.length} aturan menyala, berurutan dari fakta dasar sampai keputusan. Klik aturan untuk melihat syarat dan sumbernya.</p>
            </div>
            <div className="flex rounded-xl bg-white p-1 text-sm font-semibold" role="tablist">
              {(["jejak", "graf"] as const).map((t) => (
                <button key={t} role="tab" aria-selected={tab === t} onClick={() => setTab(t)} className={`rounded-lg px-3 py-1.5 ${tab === t ? "bg-tinta text-white" : "text-tinta-muda"}`}>
                  {t === "jejak" ? "Jejak aturan" : "Graf penalaran"}
                </button>
              ))}
            </div>
          </div>
          <div className="mt-5">
            {tab === "jejak" ? (
              <div className="grid gap-6">
                <Penjelasan id={h.id} />
                <Jejak trace={h.trace} />
              </div>
            ) : graf ? (
              <div>
                <GrafView data={graf} tinggi={560} />
                <p className="mt-2 text-sm text-redup">Subgraf Neo4j untuk kasus ini: pendaftar, konsep yang disimpulkan, aturan yang menyala, dan regulasi sumbernya.</p>
              </div>
            ) : (
              <div className="flex h-60 items-center justify-center"><Loader2 className="size-6 animate-spin text-tinta" /></div>
            )}
          </div>
        </section>
    </div>
  );
}
