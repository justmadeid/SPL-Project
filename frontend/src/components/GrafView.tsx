import { useEffect, useMemo, useRef, useState } from "react";
import ForceGraph2D from "react-force-graph-2d";
import { Graf } from "../lib/api";

export const WARNA: Record<string, string> = {
  Pendaftar: "#FFE14D",
  Rule: "#1B2A6B",
  Sumber: "#7A5AF8",
  KategoriEkonomi: "#0E8A5E",
  KondisiKhusus: "#E07A1F",
  AlasanGugur: "#C23B3B",
  Keputusan: "#101A45",
  Dokumen: "#2F7FD8",
  Manfaat: "#14A3A3",
  Kelas: "#9AA3BD",
  Lain: "#9AA3BD",
};

export const NAMA_GRUP: Record<string, string> = {
  Pendaftar: "Pendaftar",
  Rule: "Rule",
  Sumber: "Sumber regulasi",
  KategoriEkonomi: "Kategori ekonomi",
  KondisiKhusus: "Kondisi khusus",
  AlasanGugur: "Alasan gugur",
  Keputusan: "Keputusan",
  Dokumen: "Dokumen",
  Manfaat: "Manfaat",
  Kelas: "Kelas ontologi",
};

export default function GrafView({ data, tinggi = 520, labelSemua = true }: { data: Graf; tinggi?: number; labelSemua?: boolean }) {
  const wrap = useRef<HTMLDivElement>(null);
  const fg = useRef<any>(null);
  const [lebar, setLebar] = useState(800);
  const [hover, setHover] = useState<any>(null);

  useEffect(() => {
    if (!wrap.current) return;
    const ro = new ResizeObserver(([e]) => setLebar(e.contentRect.width));
    ro.observe(wrap.current);
    return () => ro.disconnect();
  }, []);

  const graph = useMemo(() => ({ nodes: data.nodes.map((n) => ({ ...n })), links: data.links.map((l) => ({ ...l })) }), [data]);
  const grup = useMemo(() => Array.from(new Set(data.nodes.map((n) => n.group))), [data]);

  useEffect(() => {
    const t = setTimeout(() => fg.current?.zoomToFit(400, 40), 900);
    return () => clearTimeout(t);
  }, [graph, lebar]);

  return (
    <div ref={wrap} className="relative overflow-hidden rounded-2xl border border-garis bg-white">
      <ForceGraph2D
        ref={fg}
        graphData={graph}
        width={lebar}
        height={tinggi}
        backgroundColor="#ffffff"
        cooldownTicks={120}
        onEngineStop={() => fg.current?.zoomToFit(400, 50)}
        linkColor={() => "rgba(27,42,107,0.18)"}
        linkDirectionalArrowLength={4}
        linkDirectionalArrowRelPos={1}
        onNodeHover={setHover}
        nodeLabel={(n: any) => `${NAMA_GRUP[n.group] ?? n.group}: ${n.label}`}
        nodeCanvasObject={(n: any, ctx, scale) => {
          const r = n.group === "Pendaftar" ? 9 : n.group === "Rule" ? 5 : 6;
          ctx.beginPath();
          ctx.arc(n.x, n.y, r, 0, 2 * Math.PI);
          ctx.fillStyle = WARNA[n.group] ?? "#999";
          ctx.fill();
          if (n.group === "Pendaftar") {
            ctx.lineWidth = 2 / scale;
            ctx.strokeStyle = "#1B2A6B";
            ctx.stroke();
          }
          const tampil = labelSemua ? scale > 0.9 || n.group === "Pendaftar" || n.group === "Keputusan" : hover?.id === n.id || scale > 2.2;
          if (tampil) {
            const teks = n.label.length > 34 ? n.label.slice(0, 32) + "…" : n.label;
            const fs = Math.max(10 / scale, 2.5);
            ctx.font = `${n.group === "Pendaftar" ? 700 : 500} ${fs}px "Plus Jakarta Sans", sans-serif`;
            ctx.textAlign = "center";
            ctx.textBaseline = "top";
            ctx.fillStyle = "#101A45";
            ctx.fillText(teks, n.x, n.y + r + 2 / scale);
          }
        }}
        nodePointerAreaPaint={(n: any, color, ctx) => {
          ctx.fillStyle = color;
          ctx.beginPath();
          ctx.arc(n.x, n.y, 9, 0, 2 * Math.PI);
          ctx.fill();
        }}
      />
      <div className="pointer-events-none absolute left-3 top-3 flex max-w-[70%] flex-wrap gap-x-3 gap-y-1 rounded-xl bg-white/90 px-3 py-2 text-[11px] text-redup">
        {grup.map((g) => (
          <span key={g} className="flex items-center gap-1.5">
            <span className="size-2.5 rounded-full" style={{ background: WARNA[g] ?? "#999" }} />
            {NAMA_GRUP[g] ?? g}
          </span>
        ))}
      </div>
      <p className="pointer-events-none absolute bottom-3 right-3 text-[11px] text-redup">Seret untuk menggeser, gulir untuk memperbesar</p>
    </div>
  );
}
