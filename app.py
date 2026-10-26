"""POKJA RISET Eko_Bang BRIDA NTB: pencari riset & inovasi pengembangan produk komoditas.

Jalankan:  streamlit run app.py
"""
import html
import io
import os
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict

import sys
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# Pastikan modul rk_*.py di folder yang sama selalu bisa diimpor (lokal maupun Streamlit Cloud).
sys.path.insert(0, str(Path(__file__).resolve().parent))
load_dotenv()

# Di Streamlit Cloud, kunci API diisi lewat Settings > Secrets (bukan file .env).
try:
    for _k, _v in st.secrets.items():
        if isinstance(_v, (str, int, float)):
            os.environ.setdefault(_k, str(_v))
except Exception:
    pass

from rk_gambar import gambar_produk  # noqa: E402
from rk_produk import ringkas_produk  # noqa: E402
from rk_search import cari  # noqa: E402
from rk_sources import SUMBER  # noqa: E402

JUDUL_APP = "POKJA RISET Eko_Bang BRIDA NTB"

st.set_page_config(page_title=JUDUL_APP, page_icon="🌱", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');

:root {
  --laut: #0b5d6b; --laut-tua: #073f4a; --hijau: #2f8f5b; --pasir: #f2c14e; --karang: #e8795a;
  --teks-redup: #5b6b62;
}
.stApp, .stApp input, .stApp textarea, .stApp button p, .stApp .stMarkdown {
  font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
}
.block-container {padding-top: 3.6rem;}

/* ---------- Banner judul ---------- */
.hero {
  position: relative; overflow: hidden; border-radius: 22px;
  padding: 34px 34px 40px; margin-bottom: 18px; color: #fff;
  background: linear-gradient(120deg, var(--laut-tua), var(--laut), var(--hijau), var(--laut));
  background-size: 300% 300%;
  animation: geserLatar 16s ease-in-out infinite;
  box-shadow: 0 14px 34px -18px rgba(7,63,74,.65);
}
.hero::before, .hero::after {           /* gelombang & cahaya matahari */
  content: ""; position: absolute; border-radius: 50%; pointer-events: none;
}
.hero::before {
  width: 260px; height: 260px; right: -60px; top: -90px;
  background: radial-gradient(circle, rgba(242,193,78,.55), rgba(242,193,78,0) 70%);
  animation: denyut 6s ease-in-out infinite;
}
.hero::after {
  width: 140%; height: 120px; left: -20%; bottom: -78px;
  background: rgba(255,255,255,.10);
  animation: ombak 9s ease-in-out infinite;
}
.hero .lencana {
  display: inline-flex; align-items: center; gap: 8px; font-size: .78rem; font-weight: 600;
  letter-spacing: .08em; text-transform: uppercase; padding: 5px 12px; border-radius: 999px;
  background: rgba(255,255,255,.14); border: 1px solid rgba(255,255,255,.25);
  opacity: 0; animation: muncul .7s ease-out .1s forwards;
}
.hero .titik {width: 8px; height: 8px; border-radius: 50%; background: var(--pasir);
  box-shadow: 0 0 0 0 rgba(242,193,78,.7); animation: kedip 2s infinite;}
.hero h1 {
  font-size: clamp(1.7rem, 4.2vw, 3rem); font-weight: 800; line-height: 1.12;
  margin: 14px 0 8px; padding: 0; color: #fff; letter-spacing: -.01em;
}
.hero h1 .kata {display: inline-block; opacity: 0; transform: translateY(18px);
  animation: naik .7s cubic-bezier(.2,.8,.2,1) forwards; margin-right: .28em;}
.hero h1 .kata:nth-child(1) {animation-delay: .15s;}
.hero h1 .kata:nth-child(2) {animation-delay: .30s;}
.hero h1 .kata:nth-child(3) {animation-delay: .45s;}
.hero h1 .kata:nth-child(4) {animation-delay: .60s;}
.hero h1 .kata:nth-child(5) {animation-delay: .75s;}
.hero h1 .kilau {               /* teks berkilau emas */
  background: linear-gradient(90deg, #fff 0%, var(--pasir) 25%, #fff 50%, var(--pasir) 75%, #fff 100%);
  background-size: 200% auto; -webkit-background-clip: text; background-clip: text;
  color: transparent; -webkit-text-fill-color: transparent;
  animation: naik .7s cubic-bezier(.2,.8,.2,1) forwards, kilau 4s linear 1.2s infinite;
}
.hero .garis {height: 4px; width: 0; border-radius: 4px; margin: 4px 0 14px;
  background: linear-gradient(90deg, var(--pasir), var(--karang));
  animation: tarik 1s ease-out .9s forwards;}
.hero p {color: rgba(255,255,255,.88); margin: 0; max-width: 760px; font-size: 1rem;
  opacity: 0; animation: muncul .8s ease-out 1.1s forwards;}
.hero .ikon {position: absolute; right: 34px; bottom: 26px; font-size: 3.2rem; opacity: .9;
  animation: apung 5s ease-in-out infinite;}

@keyframes naik {to {opacity: 1; transform: none;}}
@keyframes muncul {to {opacity: 1;}}
@keyframes tarik {to {width: 140px;}}
@keyframes kilau {to {background-position: -200% center;}}
@keyframes geserLatar {0%,100% {background-position: 0% 50%;} 50% {background-position: 100% 50%;}}
@keyframes denyut {0%,100% {transform: scale(1); opacity: .9;} 50% {transform: scale(1.12); opacity: 1;}}
@keyframes ombak {0%,100% {transform: translateX(0) rotate(-2deg);} 50% {transform: translateX(4%) rotate(1deg);}}
@keyframes apung {0%,100% {transform: translateY(0) rotate(-4deg);} 50% {transform: translateY(-10px) rotate(4deg);}}
@keyframes kedip {70% {box-shadow: 0 0 0 9px rgba(242,193,78,0);} 100% {box-shadow: 0 0 0 0 rgba(242,193,78,0);}}
@media (max-width: 640px) {.hero {padding: 24px 20px 32px;} .hero .ikon {display: none;}}
@media (prefers-reduced-motion: reduce) {
  .hero, .hero *, .hero::before, .hero::after {animation: none !important; opacity: 1 !important;
    transform: none !important;}
  .hero .garis {width: 140px;}
}

/* ---------- Form pencarian ---------- */
[data-testid="stForm"] {border: 1px solid rgba(11,93,107,.18); border-radius: 18px;
  padding: 18px 20px 6px; background: rgba(11,93,107,.03);
  box-shadow: 0 6px 22px -16px rgba(7,63,74,.5);}
[data-testid="stForm"] input {font-size: 1.05rem; border-radius: 12px !important;}
[data-testid="stFormSubmitButton"] button {width: 100%; border-radius: 12px; font-weight: 700;
  background: linear-gradient(90deg, var(--laut), var(--hijau)); border: none;
  transition: transform .15s ease, box-shadow .15s ease;}
[data-testid="stFormSubmitButton"] button:hover {transform: translateY(-1px);
  box-shadow: 0 8px 18px -8px rgba(11,93,107,.7);}

/* ---------- Metrik & tab ---------- */
[data-testid="stMetric"] {border-radius: 16px; padding: 14px 16px;
  background: linear-gradient(160deg, rgba(11,93,107,.07), rgba(47,143,91,.05));
  border: 1px solid rgba(11,93,107,.14);}
[data-testid="stMetricValue"] {color: var(--laut); font-weight: 800;}
.stTabs [data-baseweb="tab"] {font-weight: 600;}

/* ---------- Kartu produk ---------- */
.grid {display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 18px;}
.card {border: 1px solid rgba(120,140,128,.28); border-radius: 16px; overflow: hidden;
       background: rgba(250,252,250,.6); display: flex; flex-direction: column;
       opacity: 0; animation: naik .5s ease-out forwards;
       transition: transform .2s ease, box-shadow .2s ease;}
.card:hover {transform: translateY(-4px); box-shadow: 0 14px 28px -18px rgba(7,63,74,.6);}
.card img {width: 100%; height: 170px; object-fit: cover; display: block; background: #e9efe9;}
.noimg {height: 170px; display: flex; align-items: center; justify-content: center;
        background: linear-gradient(135deg,#d7ecec,#f4efe1); color: var(--laut);
        font-weight: 700; font-size: 1.05rem; padding: 0 12px; text-align: center;}
.body {padding: 12px 14px 14px; display: flex; flex-direction: column; gap: 6px; flex: 1;}
.nama {font-weight: 700; font-size: 1.05rem;}
.badge {display: inline-block; font-size: .72rem; padding: 2px 8px; border-radius: 999px;
        background: #e0f0ee; color: var(--laut); margin-right: 6px;}
.jml {font-size: .78rem; color: #6b7a70;}
.card ul {margin: 4px 0 0 1rem; padding: 0; font-size: .8rem;}
.card li {margin-bottom: 3px;}
.atrib {font-size: .66rem; color: #8a968e; margin-top: auto; padding-top: 6px;}
.kaki {text-align: center; color: #8a968e; font-size: .78rem; margin-top: 28px;}
@media (prefers-color-scheme: dark) {
  .card {background: rgba(30,36,32,.6);} .badge {background:#173f45; color:#bfe6e2;}
  .noimg {background: linear-gradient(135deg,#173f45,#3a3527); color:#bfe6e2;}
  [data-testid="stMetricValue"] {color: #7fd3c4;}
}
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="hero">'
    '<span class="lencana"><span class="titik"></span>Badan Riset dan Inovasi Daerah · NTB</span>'
    '<h1><span class="kata">POKJA</span><span class="kata">RISET</span>'
    '<span class="kata kilau">Eko_Bang</span><span class="kata">BRIDA</span>'
    '<span class="kata">NTB</span></h1>'
    '<div class="garis"></div>'
    "<p>Pencari riset &amp; inovasi pengembangan produk komoditas. Ketik satu komoditas atau tema; "
    "aplikasi menelusuri jurnal ilmiah, prosiding, dan paten, lalu merangkum bentuk-bentuk "
    "produk yang sudah dikembangkan.</p>"
    '<span class="ikon">🌾</span></div>',
    unsafe_allow_html=True,
)

# ---------------- Input (satu kolom) ----------------
ada_lens = bool(os.getenv("LENS_TOKEN"))
ada_s2 = bool(os.getenv("S2_API_KEY"))
pilihan_sumber = [s for s in SUMBER if s != "Lens (paten)" or ada_lens]
default_sumber = [s for s in pilihan_sumber if s != "Semantic Scholar" or ada_s2]

with st.form("cari"):
    k1, k2 = st.columns([5, 1])
    teks = k1.text_input("Komoditas atau tema", label_visibility="collapsed",
                         placeholder="Ketik komoditas atau tema, mis. kulit jagung, rumput laut, bioplastik")
    tombol = k2.form_submit_button("🔎 Cari", type="primary")
    with st.expander("Pengaturan lanjutan"):
        a1, a2 = st.columns(2)
        tahun_mulai = a1.number_input("Tahun terbit mulai", 1980, 2100, 2015, step=1)
        limit = a2.slider("Maks. hasil per kueri per sumber", 10, 100, 25, step=5)
        sumber = st.multiselect("Sumber data", pilihan_sumber, default=default_sumber,
                                help="Semantic Scholar lebih stabil bila S2_API_KEY diisi. "
                                     "Paten Lens.org muncul bila LENS_TOKEN diisi di file .env.")
        b1, b2 = st.columns(2)
        filter_rel = b1.checkbox("Hanya hasil yang relevan dengan kata kunci", value=True)
        tampil_gambar = b2.checkbox("Tampilkan gambar contoh produk", value=True)

@st.cache_data(ttl=3600, show_spinner=False)
def _cari(teks, tahun_mulai, sumber, limit, filter_rel):
    hasil, galat, kueri, info = cari(teks, tahun_mulai, list(sumber), limit, filter_rel)
    info = {**info, "grup": [sorted(g) for g in info["grup"]]}
    return [asdict(r) for r in hasil], galat, kueri, info


@st.cache_data(ttl=86400, show_spinner=False)
def _gambar_banyak(pasangan):
    with ThreadPoolExecutor(max_workers=6) as ex:
        return list(ex.map(lambda p: gambar_produk(p[0], p[1]), pasangan))


def _e(teks):
    return html.escape(str(teks or ""))


def kartu_produk(p, gbr):
    if gbr:
        gambar = f'<img src="{_e(gbr["url"])}" alt="{_e(p["nama"])}" loading="lazy">'
        atrib = (f'Gambar ilustrasi: <a href="{_e(gbr["halaman"])}" target="_blank">'
                 f'{_e(gbr["sumber"])}</a>'
                 + (f' · {_e(gbr["pembuat"])}' if gbr.get("pembuat") else "")
                 + (f' · {_e(gbr["lisensi"])}' if gbr.get("lisensi") else ""))
    else:
        gambar = f'<div class="noimg">{_e(p["nama"])}</div>'
        atrib = "Gambar tidak ditemukan"
    daftar = "".join(
        f'<li><a href="{_e(r.get("url"))}" target="_blank">{_e((r.get("judul") or "")[:90])}'
        f'{"…" if len(r.get("judul") or "") > 90 else ""}</a>'
        f' ({_e(r.get("tahun") or "-")})</li>'
        for r in p["riset"][:3]
    )
    return (
        f'<div class="card">{gambar}<div class="body">'
        f'<div class="nama">{_e(p["nama"])}</div>'
        f'<div><span class="badge">{_e(p["kategori"])}</span>'
        f'<span class="jml">{p["jumlah"]} riset</span></div>'
        f'<ul>{daftar}</ul><div class="atrib">{atrib}</div></div></div>'
    )


if tombol:
    st.session_state["param"] = (teks.strip(), int(tahun_mulai), tuple(sumber), limit, filter_rel)
    st.session_state["gambar"] = tampil_gambar

param = st.session_state.get("param")
if not param:
    st.info("Ketik **satu** komoditas atau tema di kolom atas, lalu klik **Cari**. "
            "Boleh bahasa Indonesia atau Inggris.\n\n"
            "Contoh: `kelapa` · `kulit jagung` · `limbah tulang ikan` · `rumput laut` · "
            "`bioplastik` · `edible film`")
    st.stop()
if not param[0]:
    st.warning("Isi komoditas atau tema terlebih dulu.")
    st.stop()
if not param[2]:
    st.warning("Pilih minimal satu sumber data di Pengaturan lanjutan.")
    st.stop()

with st.spinner("Menelusuri sumber riset… (biasanya 10–60 detik)"):
    data, galat, kueri, info = _cari(*param)

if info["inti_en"]:
    st.caption(f"Dicari sebagai: **{_e(info['inti_id'])}** (Indonesia) dan "
               f"**{_e(info['inti_en'])}** (Inggris)")

for n, e in galat.items():
    st.warning(f"**{n}** {e}")

if not data:
    st.info("Tidak ada hasil. Coba ketik dalam bahasa Inggris (mis. *corn husk*), "
            "mundurkan tahun mulai, atau matikan filter relevansi di Pengaturan lanjutan.")
    st.stop()

df = pd.DataFrame(data)
df["kategori_str"] = df["kategori"].apply("; ".join)
df["produk_str"] = df["produk"].apply("; ".join)
judul_subjek = info["inti_id"] or param[0]

with st.expander(f"Kueri yang dipakai ({len(kueri)})"):
    st.write(", ".join(f"`{q}`" for q in kueri))

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total hasil", f"{len(df):,}".replace(",", "."))
c2.metric("Bentuk produk terdeteksi", int(df["produk"].explode().dropna().nunique()))
c3.metric("Paten", int((df["jenis"] == "paten").sum()))
tahun_ok = df["tahun"].dropna()
c4.metric("Rentang tahun", f"{int(tahun_ok.min())}–{int(tahun_ok.max())}" if len(tahun_ok) else "-")

tab1, tab2, tab3 = st.tabs(["🧺 Contoh produk", "📊 Ringkasan", "📄 Daftar riset"])

# ---------------- Tab 1: galeri produk ----------------
with tab1:
    produk = ringkas_produk(data, info["inti_id"], info["inti_en"] or info["inti_id"], maks=16)
    if not produk:
        st.info("Belum ada nama produk yang terdeteksi dari judul riset. "
                "Lihat tab Daftar riset, atau tambahkan istilah produk di rk_produk.py.")
    else:
        st.caption(f"Bentuk produk dari **{_e(judul_subjek)}** yang paling banyak diteliti. "
                   "Gambar adalah ilustrasi berlisensi terbuka dan mungkin tidak persis sama "
                   "dengan produk dalam riset.")
        if st.session_state.get("gambar", True):
            with st.spinner("Mengambil gambar contoh produk…"):
                gbr = _gambar_banyak(tuple(
                    (p["nama_en"], p["kunci"]) for p in produk))
        else:
            gbr = [None] * len(produk)
        st.markdown('<div class="grid">' + "".join(
            kartu_produk(p, g).replace(
                '<div class="card">',
                f'<div class="card" style="animation-delay:{i * 0.06:.2f}s">', 1)
            for i, (p, g) in enumerate(zip(produk, gbr))) + "</div>",
            unsafe_allow_html=True)

# ---------------- Tab 2: ringkasan ----------------
with tab2:
    kat = df.explode("kategori")
    g1, g2 = st.columns(2)
    g1.subheader("Bentuk pengembangan produk")
    g1.bar_chart(kat["kategori"].value_counts(), horizontal=True)
    g2.subheader("Tren publikasi per tahun")
    g2.line_chart(df.dropna(subset=["tahun"]).astype({"tahun": int}).groupby("tahun").size())
    g3, g4 = st.columns(2)
    g3.subheader("Sumber data")
    g3.bar_chart(df["sumber"].value_counts())
    g4.subheader("Produk paling sering diteliti")
    prod = df.explode("produk").dropna(subset=["produk"])
    if len(prod):
        g4.bar_chart(prod["produk"].value_counts().head(15), horizontal=True)
    else:
        g4.write("Belum ada produk terdeteksi.")

# ---------------- Tab 3: tabel ----------------
with tab3:
    f1, f2, f3 = st.columns([2, 2, 1])
    pilih_kat = f1.multiselect("Saring kategori", sorted(kat["kategori"].unique()))
    semua_prod = sorted(df["produk"].explode().dropna().unique())
    pilih_prod = f2.multiselect("Saring produk", semua_prod)
    hanya_oa = f3.checkbox("Open access saja")
    kata = st.text_input("Cari kata dalam judul/abstrak")

    t = df
    if pilih_kat:
        t = t[t["kategori"].apply(lambda ks: any(k in ks for k in pilih_kat))]
    if pilih_prod:
        t = t[t["produk"].apply(lambda ps: any(p in ps for p in pilih_prod))]
    if hanya_oa:
        t = t[t["open_access"] == True]  # noqa: E712
    if kata:
        m = (t["judul"].str.contains(kata, case=False, na=False, regex=False)
             | t["abstrak"].str.contains(kata, case=False, na=False, regex=False))
        t = t[m]

    st.caption(f"{len(t)} hasil ditampilkan")
    kolom = ["tahun", "judul", "produk_str", "kategori_str", "jenis", "venue",
             "penulis", "sitasi", "sumber", "url"]
    st.dataframe(
        t[kolom].sort_values(["tahun", "sitasi"], ascending=False, na_position="last"),
        hide_index=True,
        column_config={
            "tahun": st.column_config.NumberColumn("Tahun", format="%d"),
            "judul": "Judul", "produk_str": "Produk", "kategori_str": "Kategori",
            "jenis": "Jenis", "venue": "Jurnal/Penerbit", "penulis": "Penulis",
            "sitasi": "Sitasi", "sumber": "Sumber",
            "url": st.column_config.LinkColumn("Tautan"),
        },
    )

    ekspor = t.drop(columns=["kategori", "produk"]).rename(
        columns={"kategori_str": "kategori", "produk_str": "produk"})
    nama_file = "riset_" + "".join(ch if ch.isalnum() else "_" for ch in judul_subjek.lower())[:40]
    d1, d2 = st.columns(2)
    d1.download_button("⬇️ Unduh CSV", ekspor.to_csv(index=False).encode("utf-8-sig"),
                       f"{nama_file}.csv", "text/csv")
    buf = io.BytesIO()
    ekspor.to_excel(buf, index=False, sheet_name="Riset")
    d2.download_button("⬇️ Unduh Excel", buf.getvalue(), f"{nama_file}.xlsx",
                       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

st.markdown(
    f'<div class="kaki"><b>{JUDUL_APP}</b><br>'
    "Sumber data: OpenAlex, Crossref, Semantic Scholar, Europe PMC, Lens.org (opsional) · "
    "Gambar: Wikimedia Commons / Openverse (lisensi terbuka)</div>",
    unsafe_allow_html=True)
