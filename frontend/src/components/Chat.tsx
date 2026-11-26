import { useEffect, useId, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { ArrowUp, Loader2 } from "lucide-react";
import { api } from "../lib/api";
import { RuleId } from "./Jejak";
import { Logo } from "./Layout";

type Msg = { role: "user" | "assistant"; content: string };

const SARAN_UMUM = [
  "Apa saja urutan prioritas penerima KIP Kuliah?",
  "Berapa batas penghasilan orang tua untuk KIP Kuliah?",
  "Kalau saya lulus 3 tahun lalu, masih bisa daftar?",
  "Dokumen apa yang perlu disiapkan kalau pakai SKTM?",
];
const SARAN_KASUS = ["Kenapa hasil saya seperti ini?", "Apa yang bisa saya lakukan agar layak?", "Berapa total bantuan yang saya terima per semester?"];

/** Merender jawaban asisten: chip [X-00] tertaut ke halaman aturan, tebal, miring, tautan, dan bullet. */
export function Isi({ t }: { t: string }) {
  return (
    <div className="grid gap-2 whitespace-pre-wrap">
      {t.split(/\n\s*\n/).map((p, i) => (
        <p key={i}>
          {p.split(/(\[[^\]]+\]\(https?:\/\/[^)\s]+\)|\[[A-G]-\d{2}(?:,\s*[A-G]-\d{2})*\]|\*\*[^*]+\*\*|(?<![*\w])\*[^*\s][^*\n]*\*(?![*\w]))/g).map((s, j) =>
            /^\[[^\]]+\]\(https?:\/\/[^)\s]+\)$/.test(s) ? (
              <a key={j} href={s.slice(s.indexOf("](") + 2, -1)} target="_blank" rel="noreferrer" className="font-semibold text-tinta underline decoration-stabilo decoration-2 underline-offset-2">
                {s.slice(1, s.indexOf("]("))}
              </a>
            ) : /^\[[A-G]-\d{2}(?:,\s*[A-G]-\d{2})*\]$/.test(s) ? (
              <span key={j}>
                {s.slice(1, -1).split(/,\s*/).map((id) => (
                  <Link key={id} to={`/aturan#${id}`} className="mx-0.5 align-[1px]"><RuleId id={id} /></Link>
                ))}
              </span>
            ) : /^\*\*.+\*\*$/.test(s) ? (
              <strong key={j}>{s.slice(2, -2)}</strong>
            ) : /^\*[^*\s][^*\n]*\*$/.test(s) ? (
              <em key={j} className="text-redup">{s.slice(1, -1)}</em>
            ) : (
              <span key={j}>{s.replace(/^[*-] /gm, "• ").replace(/^(\s+)[*-] /gm, "$1◦ ")}</span>
            )
          )}
        </p>
      ))}
    </div>
  );
}

/**
 * Chat asisten. `padat` dipakai di panel samping halaman hasil: area pesan bergulir sendiri
 * dan kotak tanya menempel di bawah panel. Tanpa `padat`, chat mengikuti gulir halaman.
 */
export default function Chat({ hasilId, padat = false, fokus = 0 }: { hasilId?: string; padat?: boolean; fokus?: number }) {
  const [pesan, setPesan] = useState<Msg[]>([]);
  const [teks, setTeks] = useState("");
  const [memuat, setMemuat] = useState(false);
  const [galat, setGalat] = useState("");
  const gulir = useRef<HTMLDivElement>(null);
  const bawah = useRef<HTMLDivElement>(null);
  const input = useRef<HTMLTextAreaElement>(null);
  const idInput = `tanya-${useId().replace(/:/g, "")}`;

  useEffect(() => {
    if (padat) {
      gulir.current?.scrollTo({ top: gulir.current.scrollHeight, behavior: "smooth" });
    } else if (pesan.length) {
      bawah.current?.scrollIntoView({ behavior: "smooth", block: "end" });
    }
  }, [pesan, memuat, padat]);

  useEffect(() => {
    if (fokus) input.current?.focus();
  }, [fokus]);

  const kirim = async (isi: string) => {
    const q = isi.trim();
    if (!q || memuat) return;
    const baru: Msg[] = [...pesan, { role: "user", content: q }];
    setPesan(baru);
    setTeks("");
    setMemuat(true);
    setGalat("");
    try {
      const r = await api.tanya(baru, hasilId);
      setPesan([...baru, { role: "assistant", content: r.teks }]);
    } catch (e: any) {
      setGalat(e.message);
    } finally {
      setMemuat(false);
    }
  };

  const saran = hasilId ? SARAN_KASUS : SARAN_UMUM;
  const ukuranTeks = padat ? "text-sm" : "text-[15px]";

  return (
    <div className={padat ? "flex min-h-0 flex-1 flex-col" : "flex flex-1 flex-col"}>
      <div ref={gulir} className={padat ? "min-h-0 flex-1 overflow-y-auto px-5 py-5" : "mt-8 flex-1"}>
        {pesan.length === 0 ? (
          <div>
            <p className="text-sm font-semibold text-redup">Contoh pertanyaan</p>
            <div className={`mt-3 grid gap-2 ${padat ? "" : "sm:grid-cols-2 xl:grid-cols-4"}`}>
              {saran.map((s) => (
                <button key={s} onClick={() => kirim(s)} className="rounded-xl border border-garis bg-white px-4 py-3 text-left text-sm font-medium hover:border-tinta">
                  {s}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <ul className={`grid ${padat ? "gap-4" : "gap-5"}`}>
            {pesan.map((m, i) =>
              m.role === "user" ? (
                <li key={i} className={`ml-auto rounded-2xl rounded-br-md bg-tinta px-4 py-2.5 text-white ${ukuranTeks} ${padat ? "max-w-[88%]" : "max-w-[min(85%,60ch)]"}`}>
                  {m.content}
                </li>
              ) : (
                <li key={i} className={`flex gap-2.5 ${padat ? "" : "max-w-[min(92%,80ch)] gap-3"}`}>
                  <Logo className={`mt-1 shrink-0 text-tinta ${padat ? "size-6" : "size-7"}`} />
                  <div className={`min-w-0 rounded-2xl rounded-tl-md border border-garis bg-white px-4 py-3 leading-relaxed ${ukuranTeks}`}><Isi t={m.content} /></div>
                </li>
              )
            )}
            {memuat && (
              <li className="flex items-center gap-3 text-sm text-redup"><Loader2 className="size-4 animate-spin" /> Mencari di basis aturan…</li>
            )}
          </ul>
        )}
        {galat && <p className="mt-4 rounded-xl bg-gagal-muda px-4 py-3 text-sm text-gagal">{galat}</p>}
        <div ref={bawah} />
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          kirim(teks);
        }}
        className={
          padat
            ? "flex items-end gap-2 border-t border-garis bg-white p-3"
            : "sticky bottom-4 mt-6 flex items-end gap-2 rounded-2xl border border-garis bg-white p-2 shadow-[0_10px_30px_-15px_rgba(16,26,69,.35)]"
        }
      >
        <label htmlFor={idInput} className="sr-only">Pertanyaan</label>
        <textarea
          ref={input}
          id={idInput}
          rows={1}
          value={teks}
          onChange={(e) => setTeks(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              kirim(teks);
            }
          }}
          placeholder={hasilId ? "Tanyakan soal hasil ini" : "Tulis pertanyaan tentang syarat, prioritas, atau manfaat KIP Kuliah"}
          className={`max-h-40 flex-1 resize-none px-3 py-2 outline-none ${ukuranTeks}`}
        />
        <button type="submit" disabled={!teks.trim() || memuat} aria-label="Kirim pertanyaan" className="grid size-10 shrink-0 place-items-center rounded-xl bg-tinta text-white disabled:opacity-30">
          <ArrowUp className="size-5" />
        </button>
      </form>
    </div>
  );
}
