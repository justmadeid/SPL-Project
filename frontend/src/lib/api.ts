export type Form = {
  nama: string;
  tahun_daftar: number;
  tahun_lulus: number | "";
  status_seleksi: "Lulus" | "Tidak_Lulus" | "";
  jenis_kampus: "PTN" | "PTS" | "";
  nama_kampus: string;
  akreditasi_prodi: string;
  jenis_kelas: string;
  beasiswa_lain: boolean;
  kip_sma: boolean;
  dtks: boolean;
  pkh: boolean;
  kks: boolean;
  terdata_p3ke: boolean;
  desil_p3ke: number | null;
  panti: boolean;
  penghasilan: number | "";
  anggota_keluarga: number | "";
  sktm: boolean;
  bukti_sktm: boolean;
  asal_3t: boolean;
  asli_papua: boolean;
  anak_tki: boolean;
  bencana: boolean;
  konflik: boolean;
  korban_kekerasan: boolean;
  korban_ham: boolean;
  nama_prodi: string;
  rumpun_prodi: string;
  jenjang: string;
  zona: string;
};

export const FORM_KOSONG: Form = {
  nama: "",
  tahun_daftar: 2026,
  tahun_lulus: "",
  status_seleksi: "",
  jenis_kampus: "",
  nama_kampus: "",
  akreditasi_prodi: "",
  jenis_kelas: "Reguler",
  beasiswa_lain: false,
  kip_sma: false,
  dtks: false,
  pkh: false,
  kks: false,
  terdata_p3ke: false,
  desil_p3ke: null,
  panti: false,
  penghasilan: "",
  anggota_keluarga: "",
  sktm: false,
  bukti_sktm: false,
  asal_3t: false,
  asli_papua: false,
  anak_tki: false,
  bencana: false,
  konflik: false,
  korban_kekerasan: false,
  korban_ham: false,
  nama_prodi: "",
  rumpun_prodi: "Lainnya",
  jenjang: "Sarjana",
  zona: "C",
};

export type Sumber = { kode: string; judul: string; bagian: string };
export type Jejak = {
  urutan: number;
  id: string;
  lapis: string;
  lapis_nama: string;
  nama: string;
  jika: string;
  maka: string;
  kesimpulan: string;
  sumber: Sumber[];
  /** Keterangan asal untuk aturan turunan/negasi yang tidak merujuk regulasi langsung. */
  turunan?: string | null;
};
export type Hasil = {
  id: string;
  input: Form;
  keputusan: "Layak" | "Tidak_Layak" | null;
  jalur: string | null;
  status_administrasi: string | null;
  prioritas: number | null;
  kategori: { kode: string; nama: string; prioritas: number } | null;
  cocok_prioritas: { kode: string; nama: string; prioritas: number }[];
  alasan_gugur: { kode: string; teks: string }[];
  kondisi_khusus: { kode: string; nama: string }[];
  dokumen: { kode: string; nama: string; keterangan: string }[];
  manfaat: {
    ukt: { kode: string; nama: string; maks: number } | null;
    biaya_hidup: { zona: string; per_bulan: number; per_semester: number } | null;
    jenjang: { nama: string; maks_semester: number } | null;
    profesi: { nama: string; maks_semester: number } | null;
  };
  trace: Jejak[];
};
export type Aturan = Omit<Jejak, "urutan" | "kesimpulan"> & { strata: number };
export type Graf = { nodes: { id: string; label: string; group: string }[]; links: { source: string; target: string; label: string }[] };
export type Preset = { kode: string; judul: string; deskripsi: string; data: Form };
export type Health = {
  neo4j: { ok: boolean; uri: string; nodes?: number; rels?: number; rules?: number; pendaftar?: number; error?: string };
  llm: { aktif: boolean; model: string };
};

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`/api${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    let msg = `Permintaan gagal (${res.status})`;
    try {
      const body = await res.json();
      if (body?.detail) msg = typeof body.detail === "string" ? body.detail : "Data belum lengkap atau tidak valid.";
    } catch {}
    throw new Error(msg);
  }
  return res.json();
}

export const api = {
  health: () => req<Health>("/health"),
  presets: () => req<Preset[]>("/presets"),
  evaluasi: (f: Form, pratinjau = false) =>
    req<Hasil>(`/evaluasi${pratinjau ? "?pratinjau=true" : ""}`, { method: "POST", body: JSON.stringify(f) }),
  hasil: (id: string) => req<Hasil>(`/hasil/${id}`),
  grafHasil: (id: string) => req<Graf>(`/hasil/${id}/graf`),
  aturan: () => req<{ lapis: Record<string, string>; aturan: Aturan[] }>("/aturan"),
  grafOntologi: () => req<Graf>("/ontologi/graf"),
  ekstrak: (teks: string) =>
    req<{ fakta: Partial<Form>; belum_diketahui: string[] }>("/llm/ekstrak", { method: "POST", body: JSON.stringify({ teks }) }),
  penjelasan: (id: string) => req<{ teks: string }>(`/llm/penjelasan/${id}`, { method: "POST" }),
  tanya: (pesan: { role: "user" | "assistant"; content: string }[], hasil_id?: string) =>
    req<{ teks: string }>("/llm/tanya", { method: "POST", body: JSON.stringify({ pesan, hasil_id }) }),
};

export const rupiah = (n: number) => "Rp" + n.toLocaleString("id-ID");
export const rupiahRingkas = (n: number) =>
  n >= 1_000_000 ? `Rp${(n / 1_000_000).toLocaleString("id-ID", { maximumFractionDigits: 2 })} jt` : `Rp${Math.round(n / 1000)} rb`;
