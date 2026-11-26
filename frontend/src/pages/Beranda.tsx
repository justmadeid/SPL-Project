import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Loader2, Sparkles, BookOpen, GraduationCap, HeartHandshake, ClipboardCheck } from "lucide-react";
import { api, Hasil, Preset } from "../lib/api";
import KartuHasil from "../components/KartuHasil";

const CONTOH_CERITA =
  "Nama saya Rina, lulus SMA tahun 2025. Saya diterima SNBT di Informatika UGM (akreditasi Unggul). Waktu SMA saya punya KIP. Ayah buruh bangunan, penghasilannya sekitar 2,5 juta sebulan, kami berempat di rumah.";

const LANGKAH = [
  { j: "Syarat administrasi", d: "Tahun lulus, hasil seleksi, akreditasi prodi, jenis kelas, dan beasiswa lain.", r: "B-01 sampai B-09", icon: ClipboardCheck },
  { j: "Prioritas ekonomi", d: "Delapan urutan prioritas resmi, dari pemegang KIP SMA sampai bukti SKTM.", r: "C-01 sampai C-10", icon: HeartHandshake },
  { j: "Kondisi khusus", d: "3T, orang asli Papua, anak TKI, bencana, konflik, dan korban kekerasan.", r: "D-01, D-02", icon: BookOpen },
  { j: "Hasil & manfaat", d: "Hasil pemeriksaan, dokumen pendukung, serta informasi bantuan biaya kuliah dan biaya hidup.", r: "E, F, G", icon: GraduationCap },
];

export default function Beranda() {
  const nav = useNavigate();
  const [cerita, setCerita] = useState("");
  const [presets, setPresets] = useState<Preset[]>([]);
  const [contoh, setContoh] = useState<Hasil | null>(null);
  const [memuat, setMemuat] = useState<string | null>(null);
  const [galat, setGalat] = useState("");

  useEffect(() => {
    api.presets().then((p) => {
      setPresets(p);
      api.evaluasi(p[0].data, true).then(setContoh).catch(() => {});
    }).catch(() => setGalat("Layanan penilaian belum dapat dihubungi. Coba muat ulang halaman beberapa saat lagi."));
  }, []);

  const lanjutCerita = () => {
    sessionStorage.setItem("pk-cerita", cerita.trim());
    nav("/cek?mulai=cerita");
  };

  const cobaPreset = async (p: Preset) => {
    setMemuat(p.kode);
    try {
      const h = await api.evaluasi(p.data);
      nav(`/hasil/${h.id}`);
    } catch (e: any) {
      setGalat(e.message);
      setMemuat(null);
    }
  };

  return (
    <div className="beranda">
      <section className="wadah hero-kuliah grid items-center gap-10 pb-16 pt-10 lg:grid-cols-[1.05fr_.95fr] lg:pt-14">
        <div>
          <p className="hero-invitation"><GraduationCap size={18} /> Langkah kecil, mimpi besar.</p>
          <h1 className="max-w-xl text-4xl font-extrabold leading-[1.08] tracking-tight text-tinta-tua sm:text-5xl">
            Kenali kelayakanmu untuk KIP Kuliah.
          </h1>
          <p className="mt-5 max-w-lg text-lg leading-relaxed text-redup">
            Ceritakan pendidikan dan kondisi keluargamu. Kami bantu memeriksa syarat yang sesuai, memahami alasan hasilnya, dan mengetahui dokumen yang perlu disiapkan.
          </p>

          <div className="cerita-panel mt-7 max-w-xl rounded-2xl border border-garis bg-white">
            <label htmlFor="cerita" className="cerita-label">
              Mulai dari ceritamu
            </label>
            <textarea
              id="cerita"
              rows={3}
              value={cerita}
              onChange={(e) => setCerita(e.target.value)}
              placeholder="Contoh: Saya lulus SMA 2025, diterima di Informatika UGM lewat SNBT. Ayah buruh dengan penghasilan 2,5 juta, kami berempat…"
              className="cerita-input w-full rounded-xl text-[15px] leading-relaxed placeholder:text-redup/70"
            />
            <div className="cerita-actions">
              <button onClick={() => setCerita(CONTOH_CERITA)} className="rounded-lg px-2 py-1.5 text-sm font-semibold text-tinta-muda hover:bg-kertas">
                Pakai contoh cerita
              </button>
              <button
                onClick={lanjutCerita}
                disabled={cerita.trim().length < 15}
                className="inline-flex items-center gap-2 rounded-xl bg-tinta px-4 py-2.5 text-sm font-bold text-white transition hover:bg-tinta-tua disabled:cursor-not-allowed disabled:opacity-40"
              >
                <Sparkles className="size-4" /> Isi formulir dari cerita
              </button>
            </div>
          </div>
          <p className="mt-3 text-sm text-redup">
            Lebih suka mengisi sendiri?{" "}
            <button onClick={() => nav("/cek")} className="font-semibold text-tinta underline decoration-stabilo decoration-[3px] underline-offset-4">
              Isi formulir langkah demi langkah
            </button>
          </p>
          <p className="mt-4 max-w-lg text-xs leading-relaxed text-redup">Pemeriksaan awal ini bukan keputusan penerimaan KIP Kuliah. Penetapan penerima tetap melalui proses seleksi resmi.</p>
          {galat && <p className="mt-4 rounded-xl bg-gagal-muda px-4 py-3 text-sm font-medium text-gagal">{galat}</p>}
        </div>

        <div className="hero-visual relative mx-auto w-full max-w-md lg:max-w-none">
          <div className="student-scene">
            <div className="student-backdrop" aria-hidden="true" />
            <div className="student-message">Mimpi kuliah?<br /><strong>Yuk, mulai di sini!</strong></div>
            <img className="student-character student-character-male" src="/images/mahasiswa-pria-3d.png" alt="Mahasiswa dengan kemeja mint dan ransel kuning memberi jempol" width="1024" height="1536" fetchPriority="high" />
            <img className="student-character student-character-female" src="/images/mahasiswa-3d.png" alt="Mahasiswi dengan hijab biru dan sweater kuning melambaikan tangan sambil membawa buku" width="1024" height="1536" fetchPriority="high" />
            <span className="scene-star star-one" aria-hidden="true">✦</span>
            <span className="scene-star star-two" aria-hidden="true">✦</span>
            <span className="student-note"><BookOpen size={17} /> Cerita kamu, langkah pertamamu</span>
          </div>
          <div className="preview-card">
          {contoh ? (
            <div className="rotate-[-2deg]">
              <KartuHasil h={contoh} />
            </div>
          ) : (
            <div className="h-64 animate-pulse rounded-[22px] bg-tinta/10" />
          )}
          </div>
          <p className="mt-8 text-center text-xs text-redup">Contoh hasil penilaian Rina, pemegang KIP SMA.</p>
        </div>
      </section>

      <section className="border-y border-garis bg-white">
        <div className="wadah py-14">
          <h2 className="text-2xl font-extrabold tracking-tight">Apa saja yang diperiksa?</h2>
          <p className="mt-2 max-w-2xl text-redup">
            Jawabanmu dicocokkan dengan aturan dalam Pedoman KIP Kuliah 2025 dan Persesjen 13/2023.
            Setiap hasil dilengkapi alasan dan rujukan aturan agar bisa kamu telusuri.
          </p>
          <ol className="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {LANGKAH.map((l, i) => (
              <li key={l.j} className={`step-kuliah step-kuliah-${i + 1}`}>
                <div className="step-heading"><l.icon size={24} strokeWidth={1.8} /><span className="tnum">{i + 1}</span></div>
                <h3 className="mt-1 font-bold">{l.j}</h3>
                <p className="mt-1.5 text-sm leading-relaxed text-redup">{l.d}</p>
                <p className="mt-3 font-mono text-xs text-tinta-muda">{l.r}</p>
              </li>
            ))}
          </ol>
        </div>
      </section>

      <section className="wadah py-14">
        <div className="flex flex-wrap items-end justify-between gap-3">
          <div>
            <h2 className="text-2xl font-extrabold tracking-tight">Coba dengan profil contoh</h2>
            <p className="mt-2 text-redup">Lihat bagaimana kondisi yang berbeda menghasilkan penilaian yang berbeda. Profil berikut hanya untuk simulasi.</p>
          </div>
        </div>
        <div className="mt-6 overflow-hidden rounded-2xl border border-garis bg-white">
          <table className="w-full text-left text-sm">
            <thead className="bg-kertas text-redup">
              <tr>
                <th className="px-4 py-2.5 font-semibold">Kasus</th>
                <th className="px-4 py-2.5 font-semibold">Profil</th>
                <th className="hidden px-4 py-2.5 font-semibold md:table-cell">Keadaan</th>
                <th className="px-4 py-2.5" />
              </tr>
            </thead>
            <tbody>
              {presets.map((p) => (
                <tr key={p.kode} className="border-t border-garis">
                  <td className="tnum px-4 py-3 font-mono text-xs text-redup">{p.kode}</td>
                  <td className="px-4 py-3 font-semibold">{p.judul}</td>
                  <td className="hidden px-4 py-3 text-redup md:table-cell">{p.deskripsi}</td>
                  <td className="px-4 py-3 text-right">
                    <button
                      onClick={() => cobaPreset(p)}
                      disabled={!!memuat}
                      className="inline-flex items-center gap-1.5 rounded-lg border border-garis px-3 py-1.5 font-semibold text-tinta hover:border-tinta disabled:opacity-50"
                    >
                      {memuat === p.kode && <Loader2 className="size-3.5 animate-spin" />} Nilai profil
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
