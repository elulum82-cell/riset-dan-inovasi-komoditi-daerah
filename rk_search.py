"""Penyusunan kueri, pencarian bertahap per sumber, deduplikasi, klasifikasi."""
import re
import time
from concurrent.futures import ThreadPoolExecutor

import requests

from rk_bahasa import analisis, cocok
from rk_config import KATEGORI
from rk_produk import deteksi_produk
from rk_sources import SUMBER

# Jeda (detik) antar-permintaan ke sumber yang sama, supaya tidak kena batas laju (429).
JEDA = {"OpenAlex": 0.3, "Crossref": 1.0, "Semantic Scholar": 1.2,
        "Europe PMC": 0.4, "Lens (paten)": 1.0}
MAKS_COBA = 4


def bangun_kueri(info):
    """Maksimal 6 kueri: frasa Inggris + variasi, lalu frasa Indonesia + variasi."""
    id_, en = info["inti_id"], info["inti_en"]
    kueri = []
    if en:
        kueri += [en, f"{en} products", f"{en} utilization", f"{en} value-added"]
    kueri += [id_, f"pemanfaatan {id_}" if en else f"{id_} products"]
    if not en:
        kueri.append(f"{id_} utilization")
    return list(dict.fromkeys(q for q in kueri if q.strip()))


def _norm_judul(j):
    return re.sub(r"[^a-z0-9]", "", (j or "").lower())[:120]


def deduplikasi(records):
    lihat, hasil = set(), []
    for r in records:
        kunci = (r.doi or "").lower().strip() or _norm_judul(r.judul)
        kunci_judul = _norm_judul(r.judul)
        if not kunci or kunci in lihat or (kunci_judul and kunci_judul in lihat):
            continue
        lihat.add(kunci)
        if kunci_judul:
            lihat.add(kunci_judul)
        hasil.append(r)
    return hasil


def _ada(teks, kata):
    return re.search(rf"(?<![a-z]){re.escape(kata)}", teks) is not None


def klasifikasi(r):
    teks = f"{r.judul} {r.abstrak}".lower()
    r.kategori = [nama for nama, kata in KATEGORI.items()
                  if any(_ada(teks, k) for k in kata)] or ["Lainnya"]
    return r


def _tunggu_retry(err, percobaan):
    resp = getattr(err, "response", None)
    ra = resp.headers.get("Retry-After") if resp is not None else None
    if ra and str(ra).isdigit():
        return min(int(ra), 30)
    return 2 * (2 ** percobaan)          # 2, 4, 8 detik


def _panggil(fn, q, tahun_mulai, limit):
    """Panggil satu sumber; ulangi bila 429/5xx/koneksi putus."""
    for percobaan in range(MAKS_COBA):
        try:
            return fn(q, tahun_mulai, limit)
        except requests.HTTPError as e:
            kode = e.response.status_code if e.response is not None else 0
            if kode in (429, 500, 502, 503, 504) and percobaan < MAKS_COBA - 1:
                time.sleep(_tunggu_retry(e, percobaan))
                continue
            raise
        except (requests.ConnectionError, requests.Timeout):
            if percobaan < MAKS_COBA - 1:
                time.sleep(2 * (percobaan + 1))
                continue
            raise
    return []


def pesan_galat(err):
    """Ubah exception menjadi pesan singkat berbahasa Indonesia."""
    if isinstance(err, requests.HTTPError) and err.response is not None:
        kode = err.response.status_code
        if kode == 429:
            return "sedang membatasi jumlah permintaan (429). Coba lagi beberapa menit lagi."
        if kode in (401, 403):
            return f"menolak akses ({kode}). Periksa kunci API di file .env."
        if kode >= 500:
            return f"server sedang bermasalah ({kode})."
        return f"galat HTTP {kode}."
    if isinstance(err, requests.Timeout):
        return "tidak merespons (timeout)."
    if isinstance(err, requests.ConnectionError):
        return "tidak bisa dihubungi. Periksa koneksi internet."
    return str(err)[:150]


def _jalankan_sumber(nama, kueri, tahun_mulai, limit):
    """Kueri dijalankan berurutan untuk satu sumber, dengan jeda."""
    fn, hasil, galat = SUMBER[nama], [], None
    for i, q in enumerate(kueri):
        if i:
            time.sleep(JEDA.get(nama, 0.5))
        try:
            hasil.extend(_panggil(fn, q, tahun_mulai, limit))
        except Exception as e:
            galat = e
            if isinstance(e, requests.HTTPError) and e.response is not None \
                    and e.response.status_code in (401, 403):
                break
    return nama, hasil, galat


def cari(teks, tahun_mulai, sumber_dipilih, limit_per_kueri=25,
         filter_relevansi=True, info=None):
    """Kembalikan (records, galat{sumber: pesan}, kueri, info)."""
    info = info or analisis(teks)
    kueri = bangun_kueri(info)
    sumber_dipilih = [n for n in sumber_dipilih if n in SUMBER]
    semua, galat = [], {}
    with ThreadPoolExecutor(max_workers=max(1, len(sumber_dipilih))) as ex:
        for nama, hasil, err in ex.map(
                lambda n: _jalankan_sumber(n, kueri, tahun_mulai, limit_per_kueri),
                sumber_dipilih):
            semua.extend(hasil)
            # Peringatan hanya bila sumber itu gagal total (tidak ada hasil sama sekali).
            if err is not None and not hasil:
                galat[nama] = pesan_galat(err)

    subjek = sorted({k for g in info["grup"] for k in g} | ({info["inti_en"]} - {""}),
                    key=len, reverse=True)
    hasil = []
    for r in deduplikasi(semua):
        if not r.judul:
            continue
        if filter_relevansi and not cocok(f"{r.judul} {r.abstrak}", info):
            continue
        klasifikasi(r)
        r.produk = deteksi_produk(r, subjek)
        hasil.append(r)
    return hasil, galat, kueri, info
