import { useState } from "react";
import { ChevronDown } from "lucide-react";
import { Jejak as JejakT } from "../lib/api";

const LAPIS_URUT = ["A", "B", "C", "D", "E", "F", "G"];

export function RuleId({ id }: { id: string }) {
  return (
    <span className="tnum inline-flex shrink-0 items-center rounded-md bg-tinta px-1.5 py-0.5 font-mono text-[11px] font-semibold text-white">
      {id}
    </span>
  );
}

function Item({ t }: { t: JejakT }) {
  const [buka, setBuka] = useState(false);
  return (
    <li className="relative pl-7">
      <span className="absolute left-[7px] top-2 size-2.5 rounded-full border-2 border-tinta bg-white" aria-hidden />
      <button
        onClick={() => setBuka(!buka)}
        className="flex w-full items-start gap-2.5 rounded-lg py-1.5 text-left hover:bg-kertas"
        aria-expanded={buka}
      >
        <RuleId id={t.id} />
        <span className="flex-1 text-[15px] leading-snug">
          <span className="stabilo">{t.kesimpulan}</span>
        </span>
        <ChevronDown className={`mt-0.5 size-4 shrink-0 text-redup transition-transform ${buka ? "rotate-180" : ""}`} />
      </button>
      {buka && (
        <div className="mb-2 ml-1 mt-1 grid gap-2 rounded-xl border border-garis bg-white p-3 text-sm">
          <p className="font-semibold">{t.nama}</p>
          <p>
            <span className="font-semibold text-tinta-muda">Jika</span> {t.jika}
          </p>
          <p>
            <span className="font-semibold text-tinta-muda">Maka</span> {t.maka}
          </p>
          {t.sumber.length > 0 && (
            <p className="text-redup">
              Sumber: {t.sumber.map((s) => `${s.judul} (${s.bagian})`).join("; ")}
            </p>
          )}
          {t.sumber.length === 0 && t.turunan && <p className="text-redup">Asal: {t.turunan}</p>}
        </div>
      )}
    </li>
  );
}

export default function Jejak({ trace }: { trace: JejakT[] }) {
  const grup = LAPIS_URUT.map((l) => ({ l, items: trace.filter((t) => t.lapis === l) })).filter((g) => g.items.length);
  return (
    <ol className="grid gap-6">
      {grup.map((g, i) => (
        <li key={g.l}>
          <h4 className="mb-2 flex items-baseline gap-2 text-sm font-bold text-tinta">
            <span className="tnum text-redup">{i + 1}.</span> {g.items[0].lapis_nama}
          </h4>
          <ul className="relative grid gap-0.5 before:absolute before:bottom-3 before:left-[11px] before:top-3 before:w-px before:bg-garis">
            {g.items.map((t) => (
              <Item key={t.id} t={t} />
            ))}
          </ul>
        </li>
      ))}
    </ol>
  );
}
