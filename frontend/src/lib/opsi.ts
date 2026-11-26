export const AKREDITASI = [
  { v: "Unggul", l: "Unggul" },
  { v: "A", l: "A" },
  { v: "Internasional", l: "Internasional" },
  { v: "Baik_Sekali", l: "Baik Sekali" },
  { v: "B", l: "B" },
  { v: "Baik", l: "Baik" },
  { v: "C", l: "C" },
  { v: "Belum_Terakreditasi", l: "Belum terakreditasi" },
];

export const RUMPUN = [
  { v: "Lainnya", l: "Lainnya (umum)" },
  { v: "Kedokteran", l: "Kedokteran" },
  { v: "Kedokteran_Gigi", l: "Kedokteran Gigi" },
  { v: "Kedokteran_Hewan", l: "Kedokteran Hewan" },
  { v: "Keperawatan", l: "Keperawatan" },
  { v: "Farmasi", l: "Farmasi" },
  { v: "Kebidanan", l: "Kebidanan" },
  { v: "Kependidikan", l: "Kependidikan / keguruan" },
];

export const JENJANG = [
  { v: "Sarjana", l: "Sarjana (S1)" },
  { v: "Diploma_IV", l: "Diploma IV" },
  { v: "Diploma_III", l: "Diploma III" },
  { v: "Diploma_II", l: "Diploma II" },
  { v: "Diploma_I", l: "Diploma I" },
];

export const KELAS = [
  { v: "Reguler", l: "Reguler" },
  { v: "Eksekutif", l: "Eksekutif" },
  { v: "Khusus", l: "Khusus" },
  { v: "Karyawan", l: "Karyawan" },
];

export const ZONA = [
  { v: "A", l: "Zona A (Rp800 rb/bulan)" },
  { v: "B", l: "Zona B (Rp950 rb/bulan)" },
  { v: "C", l: "Zona C (Rp1,1 jt/bulan)" },
  { v: "D", l: "Zona D (Rp1,25 jt/bulan)" },
  { v: "E", l: "Zona E (Rp1,4 jt/bulan)" },
];

export const KONDISI = [
  { k: "asal_3t", l: "Berasal dari daerah 3T (terdepan, terluar, tertinggal)" },
  { k: "asli_papua", l: "Orang asli Papua" },
  { k: "anak_tki", l: "Anak TKI yang tinggal di daerah perbatasan" },
  { k: "bencana", l: "Terdampak bencana alam" },
  { k: "konflik", l: "Terdampak konflik sosial" },
  { k: "korban_kekerasan", l: "Korban kekerasan" },
  { k: "korban_ham", l: "Korban pelanggaran HAM berat" },
] as const;

export const label = (list: { v: string; l: string }[], v: string) => list.find((x) => x.v === v)?.l ?? v;
