import { useEffect, useMemo, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { Check, Loader2, Sparkles, X } from "lucide-react";
import { api, Form, FORM_KOSONG, rupiah } from "../lib/api";
import { AKREDITASI, JENJANG, KELAS, KONDISI, label, RUMPUN, ZONA } from "../lib/opsi";

type Set_ = (k: keyof Form, v: any) => void;

const LANGKAH = ["Sekolah & kampus", "Program studi", "Ekonomi keluarga", "Kondisi khusus"];

function Kolom({ label: l, hint, children, ai }: { label: string; hint?: string; children: React.ReactNode; ai?: boolean }) {
  return (
    <label className="form-field">
      <span className="flex items-center gap-2 text-sm font-semibold">
        {l}
        {ai && <span className="rounded bg-stabilo px-1.5 text-[10px] font-bold text-tinta-tua">dari cerita</span>}
      </span>
      {children}
      {hint && <span className="text-xs text-redup">{hint}</span>}
    </label>
  );
}

const inputCls = (ai?: boolean) =>
  `form-input w-full rounded-xl border border-garis bg-white px-3 py-2.5 text-[15px] outline-none transition focus:border-tinta ${ai ? "field-ai" : ""}`;

function Pilihan({ value, onChange, opsi, ai }: { value: string; onChange: (v: string) => void; opsi: { v: string; l: string }[]; ai?: boolean }) {
  return (
    <div className="form-options" role="radiogroup">
      {opsi.map((o) => {
        const aktif = value === o.v;
        return (
          <button
            type="button"
            role="radio"
            aria-checked={aktif}
            key={o.v}
            onClick={() => onChange(o.v)}
            className={`rounded-xl border px-3.5 py-2 text-sm font-semibold transition ${
              aktif ? `border-tinta bg-tinta text-white ${ai ? "ring-2 ring-stabilo ring-offset-1" : ""}` : "border-garis bg-white text-tinta-muda hover:border-tinta-muda"
            }`}
          >
            {o.l}
          </button>
        );
      })}
    </div>
  );
}

function Centang({ checked, onChange, children, ai }: { checked: boolean; onChange: (v: boolean) => void; children: React.ReactNode; ai?: boolean }) {
  return (
    <label
      className={`flex cursor-pointer items-start gap-3 rounded-xl border px-3.5 py-3 text-[15px] transition ${
        checked ? "border-tinta bg-white" : "border-garis bg-white/60 hover:bg-white"
      } ${ai && checked ? "field-ai" : ""}`}
    >
      <input type="checkbox" checked={checked} onChange={(e) => onChange(e.target.checked)} className="peer sr-only" />
      <span
        className={`mt-0.5 grid size-5 shrink-0 place-items-center rounded-md border-2 peer-focus-visible:ring-2 peer-focus-visible:ring-stabilo ${
          checked ? "border-tinta bg-tinta text-white" : "border-garis"
        }`}
      >
        {checked && <Check className="size-3.5" strokeWidth={3} />}
      </span>
      <span>{children}</span>
    </label>
  );
}

function Langkah1({ f, set, ai }: { f: Form; set: Set_; ai: Set<string> }) {
  return (
    <div className="form-fields">
      <Kolom label="Nama" ai={ai.has("nama")}>
        <input className={inputCls(ai.has("nama"))} value={f.nama} onChange={(e) => set("nama", e.target.value)} placeholder="Nama lengkap" />
      </Kolom>
      <div className="field-row">
        <Kolom label="Tahun lulus SMA/SMK/MA" ai={ai.has("tahun_lulus")}>
          <input type="number" className={inputCls(ai.has("tahun_lulus"))} value={f.tahun_lulus} onChange={(e) => set("tahun_lulus", e.target.value ? +e.target.value : "")} placeholder="2025" />
        </Kolom>
        <Kolom label="Tahun mendaftar KIP Kuliah">
          <input type="number" className={inputCls()} value={f.tahun_daftar} onChange={(e) => set("tahun_daftar", +e.target.value)} />
        </Kolom>
      </div>
      <div className="field-row">
      <Kolom label="Hasil seleksi masuk perguruan tinggi" ai={ai.has("status_seleksi")}>
        <Pilihan ai={ai.has("status_seleksi")} value={f.status_seleksi} onChange={(v) => set("status_seleksi", v)} opsi={[{ v: "Lulus", l: "Sudah diterima" }, { v: "Tidak_Lulus", l: "Belum / tidak diterima" }]} />
      </Kolom>
      <Kolom label="Jenis perguruan tinggi" ai={ai.has("jenis_kampus")}>
        <Pilihan ai={ai.has("jenis_kampus")} value={f.jenis_kampus} onChange={(v) => set("jenis_kampus", v)} opsi={[{ v: "PTN", l: "Negeri (PTN)" }, { v: "PTS", l: "Swasta (PTS)" }]} />
      </Kolom>
      </div>
      <div className="field-row">
        <Kolom label="Nama kampus" ai={ai.has("nama_kampus")}>
          <input className={inputCls(ai.has("nama_kampus"))} value={f.nama_kampus} onChange={(e) => set("nama_kampus", e.target.value)} placeholder="Opsional" />
        </Kolom>
        <Kolom label="Zona biaya hidup kampus" hint="Lihat besaran per kota di laman resmi KIP Kuliah." ai={ai.has("zona")}>
          <select className={inputCls(ai.has("zona"))} value={f.zona} onChange={(e) => set("zona", e.target.value)}>
            {ZONA.map((z) => <option key={z.v} value={z.v}>{z.l}</option>)}
          </select>
        </Kolom>
      </div>
    </div>
  );
}

function Langkah2({ f, set, ai }: { f: Form; set: Set_; ai: Set<string> }) {
  return (
    <div className="form-fields">
      <div className="field-row">
        <Kolom label="Nama program studi" ai={ai.has("nama_prodi")}>
          <input className={inputCls(ai.has("nama_prodi"))} value={f.nama_prodi} onChange={(e) => set("nama_prodi", e.target.value)} placeholder="Contoh: Informatika" />
        </Kolom>
        <Kolom label="Rumpun prodi" hint="Menentukan batas biaya kedokteran dan program profesi." ai={ai.has("rumpun_prodi")}>
          <select className={inputCls(ai.has("rumpun_prodi"))} value={f.rumpun_prodi} onChange={(e) => set("rumpun_prodi", e.target.value)}>
            {RUMPUN.map((r) => <option key={r.v} value={r.v}>{r.l}</option>)}
          </select>
        </Kolom>
      </div>
      <Kolom label="Akreditasi program studi" ai={ai.has("akreditasi_prodi")}>
        <Pilihan ai={ai.has("akreditasi_prodi")} value={f.akreditasi_prodi} onChange={(v) => set("akreditasi_prodi", v)} opsi={AKREDITASI} />
      </Kolom>
      <Kolom label="Jenjang" ai={ai.has("jenjang")}>
        <Pilihan ai={ai.has("jenjang")} value={f.jenjang} onChange={(v) => set("jenjang", v)} opsi={JENJANG} />
      </Kolom>
      <Kolom label="Jenis kelas" ai={ai.has("jenis_kelas")}>
        <Pilihan ai={ai.has("jenis_kelas")} value={f.jenis_kelas} onChange={(v) => set("jenis_kelas", v)} opsi={KELAS} />
      </Kolom>
      <Centang ai={ai.has("beasiswa_lain")} checked={f.beasiswa_lain} onChange={(v) => set("beasiswa_lain", v)}>
        Saya sedang menerima beasiswa atau bantuan biaya pendidikan lain (APBN, APBD, atau sumber lain)
      </Centang>
    </div>
  );
}

function Langkah3({ f, set, ai }: { f: Form; set: Set_; ai: Set<string> }) {
  const perKapita = f.penghasilan !== "" && f.anggota_keluarga ? Math.round(+f.penghasilan / +f.anggota_keluarga) : null;
  return (
    <div className="grid gap-6">
      <div>
        <p className="mb-2.5 text-sm font-semibold">Kartu dan data bantuan sosial yang dimiliki</p>
        <div className="grid gap-2.5 sm:grid-cols-2">
          <Centang ai={ai.has("kip_sma")} checked={f.kip_sma} onChange={(v) => set("kip_sma", v)}>Punya KIP saat SMA/SMK/MA</Centang>
          <Centang ai={ai.has("dtks")} checked={f.dtks} onChange={(v) => set("dtks", v)}>Keluarga terdata DTKS</Centang>
          <Centang ai={ai.has("pkh")} checked={f.pkh} onChange={(v) => set("pkh", v)}>Keluarga penerima PKH</Centang>
          <Centang ai={ai.has("kks")} checked={f.kks} onChange={(v) => set("kks", v)}>Keluarga pemegang KKS</Centang>
          <Centang ai={ai.has("panti")} checked={f.panti} onChange={(v) => set("panti", v)}>Tinggal di panti sosial / panti asuhan</Centang>
          <Centang ai={ai.has("terdata_p3ke")} checked={f.terdata_p3ke} onChange={(v) => set("terdata_p3ke", v)}>Keluarga terdata P3KE</Centang>
        </div>
        {f.terdata_p3ke && (
          <div className="mt-3 max-w-xs">
            <Kolom label="Desil P3KE" ai={ai.has("desil_p3ke")}>
              <select className={inputCls(ai.has("desil_p3ke"))} value={f.desil_p3ke ?? ""} onChange={(e) => set("desil_p3ke", e.target.value ? +e.target.value : null)}>
                <option value="">Pilih desil</option>
                {Array.from({ length: 10 }, (_, i) => <option key={i + 1} value={i + 1}>Desil {i + 1}</option>)}
              </select>
            </Kolom>
          </div>
        )}
      </div>
      <div className="field-row">
        <Kolom label="Penghasilan kotor gabungan orang tua/wali per bulan" ai={ai.has("penghasilan")} hint={f.penghasilan !== "" ? rupiah(+f.penghasilan) : "Isi 0 jika tidak ada penghasilan"}>
          <input type="number" min={0} step={50000} className={inputCls(ai.has("penghasilan"))} value={f.penghasilan} onChange={(e) => set("penghasilan", e.target.value === "" ? "" : +e.target.value)} placeholder="2500000" />
        </Kolom>
        <Kolom label="Jumlah anggota keluarga" ai={ai.has("anggota_keluarga")} hint={perKapita !== null ? `Per kapita ${rupiah(perKapita)} per bulan` : "Sesuai kartu keluarga"}>
          <input type="number" min={1} className={inputCls(ai.has("anggota_keluarga"))} value={f.anggota_keluarga} onChange={(e) => set("anggota_keluarga", e.target.value === "" ? "" : +e.target.value)} placeholder="4" />
        </Kolom>
      </div>
      <div className="grid gap-2.5 sm:grid-cols-2">
        <Centang ai={ai.has("sktm")} checked={f.sktm} onChange={(v) => set("sktm", v)}>Punya Surat Keterangan Tidak Mampu (SKTM) dari desa/kelurahan</Centang>
        <Centang ai={ai.has("bukti_sktm")} checked={f.bukti_sktm} onChange={(v) => set("bukti_sktm", v)}>Punya rekening listrik dan foto rumah sebagai bukti dukung</Centang>
      </div>
    </div>
  );
}

function Langkah4({ f, set, ai }: { f: Form; set: Set_; ai: Set<string> }) {
  return (
    <div className="grid gap-2.5">
      <p className="mb-1 text-sm text-redup">Centang yang sesuai. Kondisi khusus bisa membuka jalur pertimbangan khusus meskipun syarat ekonomi tidak terpenuhi.</p>
      {KONDISI.map((k) => (
        <Centang key={k.k} ai={ai.has(k.k)} checked={f[k.k] as boolean} onChange={(v) => set(k.k, v)}>
          {k.l}
        </Centang>
      ))}
    </div>
  );
}

function kurang(f: Form): string[] {
  const m: string[] = [];
  if (f.tahun_lulus === "") m.push("Tahun lulus");
  if (!f.status_seleksi) m.push("Hasil seleksi");
  if (!f.jenis_kampus) m.push("Jenis perguruan tinggi");
  if (!f.akreditasi_prodi) m.push("Akreditasi prodi");
  if (f.penghasilan === "") m.push("Penghasilan orang tua");
  if (f.anggota_keluarga === "") m.push("Jumlah anggota keluarga");
  if (f.terdata_p3ke && !f.desil_p3ke) m.push("Desil P3KE");
  return m;
}

export default function Cek() {
  const nav = useNavigate();
  const [sp] = useSearchParams();
  const [f, setF] = useState<Form>(FORM_KOSONG);
  const [ai, setAi] = useState<Set<string>>(new Set());
  const [step, setStep] = useState(0);
  const [cerita, setCerita] = useState("");
  const [ekstrak, setEkstrak] = useState<{ status: "idle" | "load" | "ok" | "err"; pesan?: string; belum?: string[] }>({ status: "idle" });
  const [kirim, setKirim] = useState(false);
  const [galat, setGalat] = useState("");

  const set: Set_ = (k, v) => {
    setF((x) => ({ ...x, [k]: v }));
    setAi((s) => {
      if (!s.has(k as string)) return s;
      const n = new Set(s);
      n.delete(k as string);
      return n;
    });
  };

  const jalankanEkstrak = async (teks: string) => {
    setEkstrak({ status: "load" });
    try {
      const r = await api.ekstrak(teks);
      const kunci = Object.keys(r.fakta);
      setF((x) => ({ ...x, ...r.fakta }));
      setAi(new Set(kunci));
      setEkstrak({ status: "ok", pesan: `${kunci.length} isian terisi dari ceritamu. Periksa yang bertanda stabilo.`, belum: r.belum_diketahui });
    } catch (e: any) {
      setEkstrak({ status: "err", pesan: e.message });
    }
  };

  useEffect(() => {
    if (sp.get("mulai") === "cerita") {
      const t = sessionStorage.getItem("pk-cerita") || "";
      sessionStorage.removeItem("pk-cerita");
      if (t) {
        setCerita(t);
        jalankanEkstrak(t);
      }
    }
  }, []);

  const belumLengkap = useMemo(() => kurang(f), [f]);

  const submit = async () => {
    setKirim(true);
    setGalat("");
    try {
      const h = await api.evaluasi(f);
      nav(`/hasil/${h.id}`);
    } catch (e: any) {
      setGalat(e.message);
      setKirim(false);
    }
  };

  const ringkasan: [string, string][] = [
    ["Nama", f.nama || "–"],
    ["Lulus", f.tahun_lulus ? `${f.tahun_lulus} (daftar ${f.tahun_daftar})` : "–"],
    ["Seleksi", f.status_seleksi ? (f.status_seleksi === "Lulus" ? "Sudah diterima" : "Belum diterima") : "–"],
    ["Kampus", [f.jenis_kampus, f.nama_kampus].filter(Boolean).join(", ") || "–"],
    ["Prodi", [f.nama_prodi, f.akreditasi_prodi && label(AKREDITASI, f.akreditasi_prodi)].filter(Boolean).join(", ") || "–"],
    ["Kelas", f.jenis_kelas],
    ["Penghasilan", f.penghasilan !== "" ? `${rupiah(+f.penghasilan)} / ${f.anggota_keluarga || "?"} orang` : "–"],
    [
      "Kartu & data",
      [f.kip_sma && "KIP SMA", f.dtks && "DTKS", f.pkh && "PKH", f.kks && "KKS", f.terdata_p3ke && `P3KE desil ${f.desil_p3ke ?? "?"}`, f.panti && "Panti", f.sktm && "SKTM"]
        .filter(Boolean)
        .join(", ") || "Tidak ada",
    ],
    ["Kondisi khusus", KONDISI.filter((k) => f[k.k]).length ? `${KONDISI.filter((k) => f[k.k]).length} dipilih` : "Tidak ada"],
  ];

  return (
    <div className="wadah check-page py-10">
      <h1 className="text-3xl font-extrabold tracking-tight">Cek kelayakan KIP Kuliah</h1>
      <p className="mt-2 max-w-2xl text-redup">Isi empat bagian di bawah. Kamu bisa mulai dari cerita supaya sebagian besar isian terisi otomatis.</p>

      <section className="mt-8 rounded-2xl border border-garis bg-white p-4 sm:p-5">
        <div className="flex flex-wrap items-center gap-2">
          <Sparkles className="size-4 text-tinta" />
          <h2 className="font-bold">Mulai dari cerita</h2>
          <span className="text-sm text-redup">(diproses Gemini, keputusan tetap oleh mesin aturan)</span>
        </div>
        <textarea
          rows={3}
          value={cerita}
          onChange={(e) => setCerita(e.target.value)}
          placeholder="Ceritakan sekolahmu, kampus dan prodi tujuan, pekerjaan dan penghasilan orang tua, kartu bantuan yang dimiliki…"
          className="mt-3 w-full resize-none rounded-xl border border-garis px-3 py-2.5 text-[15px] leading-relaxed outline-none focus:border-tinta"
        />
        <div className="mt-2 flex flex-wrap items-center gap-3">
          <button
            onClick={() => jalankanEkstrak(cerita)}
            disabled={cerita.trim().length < 15 || ekstrak.status === "load"}
            className="inline-flex items-center gap-2 rounded-xl bg-tinta px-4 py-2 text-sm font-bold text-white hover:bg-tinta-tua disabled:opacity-40"
          >
            {ekstrak.status === "load" ? <Loader2 className="size-4 animate-spin" /> : <Sparkles className="size-4" />}
            {ekstrak.status === "load" ? "Membaca cerita…" : "Isi formulir dari cerita"}
          </button>
          {ekstrak.status === "ok" && <span className="text-sm font-medium text-layak">{ekstrak.pesan}</span>}
          {ekstrak.status === "err" && <span className="text-sm font-medium text-gagal">{ekstrak.pesan}</span>}
        </div>
        {ekstrak.status === "ok" && ekstrak.belum && ekstrak.belum.length > 0 && (
          <div className="mt-3 rounded-xl bg-kertas px-4 py-3 text-sm">
            <p className="font-semibold">Belum disebut di ceritamu, lengkapi di formulir:</p>
            <ul className="mt-1 list-disc pl-5 text-redup">
              {ekstrak.belum.map((b) => <li key={b}>{b}</li>)}
            </ul>
          </div>
        )}
      </section>

      <div className="mt-8 grid gap-8 lg:grid-cols-[1fr_320px]">
        <div>
          <ol className="form-steps" aria-label="Langkah formulir">
            {LANGKAH.map((l, i) => (
              <li key={l}>
                <button
                  onClick={() => setStep(i)}
                  aria-current={step === i ? "step" : undefined}
                  className={`flex items-center gap-2 rounded-xl px-3 py-2 text-sm font-semibold transition ${
                    step === i ? "bg-tinta text-white" : "bg-white text-tinta-muda hover:bg-white/70"
                  }`}
                >
                  <span className={`tnum grid size-5 place-items-center rounded-full text-[11px] ${step === i ? "bg-stabilo text-tinta-tua" : "bg-kertas"}`}>{i + 1}</span>
                  {l}
                </button>
              </li>
            ))}
          </ol>

          <div className="form-panel mt-5 rounded-2xl border border-garis bg-white p-5 sm:p-7">
            {step === 0 && <Langkah1 f={f} set={set} ai={ai} />}
            {step === 1 && <Langkah2 f={f} set={set} ai={ai} />}
            {step === 2 && <Langkah3 f={f} set={set} ai={ai} />}
            {step === 3 && <Langkah4 f={f} set={set} ai={ai} />}
          </div>

          <div className="mt-5 flex items-center justify-between gap-3">
            <button onClick={() => setStep((s) => Math.max(0, s - 1))} disabled={step === 0} className="rounded-xl px-4 py-2.5 text-sm font-semibold text-tinta-muda hover:bg-white disabled:invisible">
              Kembali
            </button>
            {step < 3 ? (
              <button onClick={() => setStep((s) => s + 1)} className="rounded-xl bg-tinta px-5 py-2.5 text-sm font-bold text-white hover:bg-tinta-tua">
                Lanjut ke {LANGKAH[step + 1].toLowerCase()}
              </button>
            ) : (
              <button onClick={submit} disabled={kirim || belumLengkap.length > 0} className="inline-flex items-center gap-2 rounded-xl bg-tinta px-5 py-2.5 text-sm font-bold text-white hover:bg-tinta-tua disabled:opacity-40">
                {kirim && <Loader2 className="size-4 animate-spin" />} Cek kelayakan
              </button>
            )}
          </div>
          {galat && <p className="mt-3 rounded-xl bg-gagal-muda px-4 py-3 text-sm text-gagal">{galat}</p>}
        </div>

        <aside className="lg:sticky lg:top-24 lg:self-start">
          <div className="rounded-2xl border border-garis bg-white p-5">
            <h2 className="font-bold">Ringkasan isian</h2>
            <dl className="mt-3 grid gap-2.5 text-sm">
              {ringkasan.map(([k, v]) => (
                <div key={k} className="grid grid-cols-[100px_1fr] gap-2">
                  <dt className="text-redup">{k}</dt>
                  <dd className="font-medium">{v}</dd>
                </div>
              ))}
            </dl>
            <div className="mt-4 border-t border-garis pt-4">
              {belumLengkap.length ? (
                <div className="text-sm">
                  <p className="font-semibold">Perlu dilengkapi sebelum dicek:</p>
                  <ul className="mt-1.5 grid gap-1">
                    {belumLengkap.map((m) => (
                      <li key={m} className="flex items-center gap-2 text-redup"><X className="size-3.5 text-gagal" /> {m}</li>
                    ))}
                  </ul>
                </div>
              ) : (
                <p className="flex items-center gap-2 text-sm font-semibold text-layak"><Check className="size-4" /> Siap dicek</p>
              )}
            </div>
            {belumLengkap.length === 0 && (
              <button onClick={submit} disabled={kirim} className="mt-4 inline-flex w-full items-center justify-center gap-2 rounded-xl bg-tinta px-4 py-2.5 text-sm font-bold text-white hover:bg-tinta-tua">
                {kirim && <Loader2 className="size-4 animate-spin" />} Cek kelayakan
              </button>
            )}
          </div>
        </aside>
      </div>
    </div>
  );
}
