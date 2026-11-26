import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { MessageCircle, X } from "lucide-react";
import Chat from "./Chat";

/** Kasus yang sedang dibuka (halaman hasil); asisten ikut membaca hasilnya. */
type Konteks = { id: string; nama: string } | null;

type AsistenApi = {
  buka: () => void;
  setKonteks: (k: Konteks) => void;
};

const Ctx = createContext<AsistenApi>({ buka: () => {}, setKonteks: () => {} });
export const useAsisten = () => useContext(Ctx);

/**
 * Asisten tersedia di semua halaman sebagai drawer kanan yang menimpa halaman (layout tidak bergeser),
 * dibuka lewat tombol melayang atau lewat useAsisten().buka() dari halaman.
 */
export function AsistenProvider({ children }: { children: React.ReactNode }) {
  const [terbuka, setTerbuka] = useState(false);
  const [fokus, setFokus] = useState(0);
  const [konteks, setKonteks] = useState<Konteks>(null);

  const buka = useCallback(() => {
    setTerbuka(true);
    setFokus((f) => f + 1);
  }, []);
  const api = useMemo(() => ({ buka, setKonteks }), [buka]);

  useEffect(() => {
    if (!terbuka) return;
    const esc = (e: KeyboardEvent) => e.key === "Escape" && setTerbuka(false);
    window.addEventListener("keydown", esc);
    return () => window.removeEventListener("keydown", esc);
  }, [terbuka]);

  return (
    <Ctx.Provider value={api}>
      {children}

      {!terbuka && (
        <button
          onClick={buka}
          aria-controls="drawer-asisten"
          className="fixed bottom-5 right-5 z-30 inline-flex items-center gap-2 rounded-full bg-tinta py-3 pl-4 pr-5 text-sm font-semibold text-white shadow-[0_12px_30px_-10px_rgba(16,26,69,.65)] hover:bg-tinta-tua"
        >
          <MessageCircle className="size-4" /> Tanya asisten
        </button>
      )}

      <div
        onClick={() => setTerbuka(false)}
        className={`fixed inset-0 z-40 bg-tinta-tua/25 transition-opacity duration-300 ${terbuka ? "opacity-100" : "pointer-events-none opacity-0"}`}
      />
      <aside
        id="drawer-asisten"
        role="dialog"
        aria-modal={terbuka}
        aria-label="Asisten KIP Kuliah"
        aria-hidden={!terbuka}
        {...(!terbuka ? ({ inert: "" } as any) : {})}
        className={`fixed inset-y-0 right-0 z-50 flex w-full flex-col bg-kertas shadow-[-24px_0_48px_-24px_rgba(16,26,69,.45)] transition-transform duration-300 sm:w-[440px] ${terbuka ? "translate-x-0" : "translate-x-full"}`}
      >
        <div className="flex items-start gap-3 border-b border-garis bg-white px-5 py-4">
          <div className="min-w-0 flex-1">
            <h2 className="font-extrabold tracking-tight">{konteks ? "Tanya soal hasil ini" : "Tanya asisten KIP Kuliah"}</h2>
            <p className="mt-0.5 text-xs text-redup">
              {konteks
                ? `Asisten membaca hasil ${konteks.nama || "pendaftar"} dan menjawab dari basis aturan.`
                : "Jawaban disusun Gemini hanya dari aturan di knowledge graph, lengkap dengan nomor aturannya."}
            </p>
          </div>
          <button onClick={() => setTerbuka(false)} aria-label="Tutup asisten" className="grid size-8 shrink-0 place-items-center rounded-lg text-tinta-muda hover:bg-kertas">
            <X className="size-5" />
          </button>
        </div>
        {/* key: percakapan baru tiap ganti kasus, riwayat tetap selama kasusnya sama */}
        <Chat key={konteks?.id ?? "umum"} hasilId={konteks?.id} padat fokus={fokus} />
      </aside>
    </Ctx.Provider>
  );
}
