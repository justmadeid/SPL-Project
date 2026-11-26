import { AsistenProvider } from "./AsistenDrawer";
import { useEffect, useState } from "react";
import { Link, NavLink, Outlet } from "react-router-dom";
import { api, Health } from "../lib/api";

export function Logo({ className = "" }: { className?: string }) {
  return (
    <svg viewBox="0 0 32 32" className={className} aria-hidden>
      <rect x="2" y="6" width="28" height="20" rx="4.5" fill="currentColor" />
      <rect x="2" y="11.5" width="28" height="4.5" fill="#FFE14D" />
      <rect x="6" y="19.5" width="9" height="2.6" rx="1.3" fill="#fff" opacity=".7" />
    </svg>
  );
}

function Status() {
  const [h, setH] = useState<Health | null>(null);
  const [err, setErr] = useState(false);
  useEffect(() => {
    api.health().then(setH).catch(() => setErr(true));
  }, []);
  const dot = (ok: boolean) => <span className={`inline-block size-2 rounded-full ${ok ? "bg-layak" : "bg-gagal"}`} />;
  if (err)
    return <span className="flex items-center gap-1.5 text-xs text-gagal">{dot(false)} Backend belum berjalan</span>;
  if (!h) return null;
  return (
    <span className="hidden items-center gap-3 text-xs text-redup lg:flex" title={h.neo4j.ok ? `${h.neo4j.nodes} node, ${h.neo4j.rels} relasi di ${h.neo4j.uri}` : h.neo4j.error}>
      <span className="flex items-center gap-1.5">{dot(h.neo4j.ok)} Neo4j</span>
      <span className="flex items-center gap-1.5" title={h.llm.aktif ? h.llm.model : "Isi GEMINI_API_KEY di backend/.env"}>
        {dot(h.llm.aktif)} Gemini
      </span>
    </span>
  );
}

const nav = [
  { to: "/cek", l: "Cek kelayakan", s: "Cek" },
  { to: "/aturan", l: "Aturan & sumber", s: "Aturan" },
];

export default function Layout() {
  return (
    <div className="flex min-h-screen flex-col">
      <header className="sticky top-0 z-30 border-b border-garis bg-kertas/90 backdrop-blur">
        <div className="wadah flex h-16 items-center gap-3 sm:gap-6">
          <Link to="/" aria-label="Pintu Kuliah, beranda" className="flex shrink-0 items-center gap-2.5 text-tinta">
            <Logo className="size-8" />
            <span className="hidden text-[17px] font-extrabold tracking-tight sm:inline">Pintu Kuliah</span>
          </Link>
          <nav className="ml-auto flex items-center gap-1 sm:ml-6">
            {nav.map((n) => (
              <NavLink
                key={n.to}
                to={n.to}
                className={({ isActive }) =>
                  `whitespace-nowrap rounded-lg px-2.5 py-1.5 text-sm font-semibold transition-colors sm:px-3 ${
                    isActive ? "bg-tinta text-white" : "text-tinta-muda hover:bg-white"
                  }`
                }
              >
                <span className="sm:hidden">{n.s}</span>
                <span className="hidden sm:inline">{n.l}</span>
              </NavLink>
            ))}
          </nav>
          <div className="ml-auto hidden lg:block">
            <Status />
          </div>
        </div>
      </header>
      <main className="flex-1">
        <AsistenProvider>
          <Outlet />
        </AsistenProvider>
      </main>
      <footer className="border-t border-garis">
        <div className="wadah flex flex-col gap-2 py-6 text-sm text-redup sm:flex-row sm:justify-between">
          <p>
            Proyek akhir Sistem Pakar Lanjut, Magister Kecerdasan Artifisial UGM. Bukan situs resmi KIP Kuliah.
          </p>
          <p>
            Keputusan resmi ditetapkan perguruan tinggi dan Kemdiktisaintek melalui{" "}
            <a className="font-semibold text-tinta underline-offset-2 hover:underline" href="https://kip-kuliah.kemdiktisaintek.go.id" target="_blank" rel="noreferrer">
              kip-kuliah.kemdiktisaintek.go.id
            </a>
            .
          </p>
        </div>
      </footer>
    </div>
  );
}
