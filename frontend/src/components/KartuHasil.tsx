import { useId } from "react";
import { Hasil, rupiahRingkas } from "../lib/api";
import { AKREDITASI, JENJANG, label } from "../lib/opsi";

export function Stempel({ layak, besar = false }: { layak: boolean; besar?: boolean }) {
  const warna = layak ? "#0E8A5E" : "#C23B3B";
  const ukuran = besar ? "size-32 sm:size-36" : "size-24";
  const id = useId().replace(/:/g, "");
  const busur = { fontSize: 7.6, fontWeight: 800, letterSpacing: 1.5, fill: warna, fontFamily: '"Plus Jakarta Sans", sans-serif' } as const;
  return (
    <div className={`stempel ${ukuran} pointer-events-none select-none`} role="img" aria-label={layak ? "Layak" : "Belum layak"}>
      <svg viewBox="0 0 120 120" className="size-full drop-shadow-sm">
        <defs>
          {/* busur atas: baseline r=45, huruf menghadap keluar */}
          <path id={`${id}-atas`} d="M15,60 A45,45 0 0 1 105,60" />
          {/* busur bawah: digambar kiri ke kanan lewat bawah agar huruf tetap tegak; baseline r=51.5 */}
          <path id={`${id}-bawah`} d="M8.5,60 A51.5,51.5 0 0 0 111.5,60" />
        </defs>
        <circle cx="60" cy="60" r="56" fill="#fff" stroke={warna} strokeWidth="4" />
        <circle cx="60" cy="60" r="40" fill="none" stroke={warna} strokeWidth="1.2" />
        <circle cx="11.5" cy="60" r="1.6" fill={warna} />
        <circle cx="108.5" cy="60" r="1.6" fill={warna} />
        <text {...busur}>
          <textPath href={`#${id}-atas`} startOffset="50%" textAnchor="middle">HASIL SISTEM PAKAR</textPath>
        </text>
        <text {...busur}>
          <textPath href={`#${id}-bawah`} startOffset="50%" textAnchor="middle">KIP KULIAH</textPath>
        </text>
        {layak ? (
          <text x="60" y="68.5" textAnchor="middle" fontSize="23" fontWeight="800" fill={warna}>Layak</text>
        ) : (
          <>
            <text x="60" y="58" textAnchor="middle" fontSize="17" fontWeight="800" fill={warna}>Belum</text>
            <text x="60" y="76" textAnchor="middle" fontSize="17" fontWeight="800" fill={warna}>layak</text>
          </>
        )}
      </svg>
    </div>
  );
}

function Baris({ k, v }: { k: string; v: React.ReactNode }) {
  return (
    <div className="min-w-0">
      <dt className="text-[11px] font-medium text-white/60">{k}</dt>
      <dd className="text-sm font-semibold leading-snug text-white sm:truncate">{v}</dd>
    </div>
  );
}

export default function KartuHasil({ h, besar = false, aksi }: { h: Hasil; besar?: boolean; aksi?: React.ReactNode }) {
  const layak = h.keputusan === "Layak";
  const inp = h.input;
  const m = h.manfaat;
  return (
    <div className="relative">
      <div className={`pola-kartu relative overflow-hidden rounded-[22px] bg-tinta text-white shadow-[0_18px_40px_-18px_rgba(16,26,69,.55)] ${besar ? "p-6 sm:p-8" : "p-5"}`}>
        <div className="absolute inset-x-0 top-[62px] h-3 bg-stabilo sm:top-[70px]" aria-hidden />
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-xs font-semibold text-white/70">Kartu hasil penilaian</p>
            <p className="text-sm font-bold">KIP Kuliah {inp.tahun_daftar}</p>
          </div>
          {/* di kartu besar stempel menempati pojok kanan atas, jadi nomor kartu pindah ke bawah */}
          {!besar && <p className="tnum rounded-md bg-white/10 px-2 py-1 font-mono text-[11px] text-white/80">#{h.id.slice(0, 8)}</p>}
        </div>

        <div className={besar ? "mt-10" : "mt-8"}>
          <p className={`${besar ? "text-2xl sm:text-3xl" : "text-xl"} font-extrabold tracking-tight`}>{inp.nama || "Tanpa nama"}</p>
          <p className="mt-1 text-sm text-white/75">
            {[inp.nama_prodi, label(JENJANG, inp.jenjang)].filter(Boolean).join(", ")}
            {inp.nama_kampus ? ` di ${inp.nama_kampus}` : ""} ({inp.jenis_kampus}, akreditasi {label(AKREDITASI, inp.akreditasi_prodi)})
          </p>
        </div>

        <dl className={`grid gap-x-6 gap-y-3 ${besar ? "mt-7 grid-cols-2 sm:pr-24" : "mt-5 grid-cols-2 pr-20"}`}>
          <Baris k="Jalur" v={h.jalur ?? "Belum dapat diputuskan"} />
          <Baris k="Kategori" v={h.kategori ? `Prioritas ${h.kategori.prioritas}` : layak ? "Pertimbangan khusus" : "–"} />
          <Baris k="Biaya pendidikan" v={m.ukt ? `maks ${rupiahRingkas(m.ukt.maks)}/semester` : "–"} />
          <Baris k="Biaya hidup" v={m.biaya_hidup ? `${rupiahRingkas(m.biaya_hidup.per_bulan)}/bulan` : "–"} />
        </dl>
        {besar && (
          <div className="mt-6 flex flex-wrap items-center justify-between gap-3">
            <p className="tnum font-mono text-[11px] text-white/45">No. kartu {h.id.slice(0, 8)}</p>
            {aksi}
          </div>
        )}
      </div>
      <div className={`absolute ${besar ? "-right-3 -top-8 sm:-right-6" : "-bottom-5 -right-3"}`}>
        <Stempel layak={layak} besar={besar} />
      </div>
    </div>
  );
}
