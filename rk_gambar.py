"""Mencari gambar ilustrasi produk berlisensi terbuka.

Urutan: Wikimedia Commons, lalu Openverse. Keduanya gratis tanpa kunci API.
Gambar hanya ilustrasi; atribusi pembuat dan lisensi selalu ditampilkan.
"""
import html
import os
import re

import requests

TIMEOUT = 15


def _headers():
    email = os.getenv("CONTACT_EMAIL", "").strip() or "unknown"
    return {"User-Agent": f"RisetKomoditi/1.0 (mailto:{email})"}


def _bersih(teks):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", teks or ""))).strip()


def _skor(judul, kata):
    judul = judul.lower()
    return sum(1 for k in kata if k in judul)


def gambar_commons(kueri):
    params = {
        "action": "query", "format": "json", "generator": "search",
        "gsrsearch": f"{kueri} filetype:bitmap", "gsrnamespace": 6,
        "gsrlimit": 8, "prop": "imageinfo",
        "iiprop": "url|extmetadata|mime", "iiurlwidth": 480,
    }
    r = requests.get("https://commons.wikimedia.org/w/api.php", params=params,
                     headers=_headers(), timeout=TIMEOUT)
    r.raise_for_status()
    halaman = list(((r.json().get("query") or {}).get("pages") or {}).values())
    if not halaman:
        return None
    kata = [k for k in kueri.lower().split() if len(k) > 2]
    halaman.sort(key=lambda p: (-_skor(p.get("title", ""), kata), p.get("index", 99)))
    for p in halaman:
        info = (p.get("imageinfo") or [{}])[0]
        if info.get("mime") not in ("image/jpeg", "image/png", "image/webp"):
            continue
        meta = info.get("extmetadata") or {}
        return {
            "url": info.get("thumburl") or info.get("url"),
            "halaman": info.get("descriptionurl", ""),
            "pembuat": _bersih((meta.get("Artist") or {}).get("value", ""))[:80],
            "lisensi": (meta.get("LicenseShortName") or {}).get("value", ""),
            "sumber": "Wikimedia Commons",
        }
    return None


def gambar_openverse(kueri):
    r = requests.get("https://api.openverse.org/v1/images/",
                     params={"q": kueri, "page_size": 5},
                     headers=_headers(), timeout=TIMEOUT)
    r.raise_for_status()
    for it in r.json().get("results", []):
        url = it.get("thumbnail") or it.get("url")
        if not url:
            continue
        lis = f"{it.get('license', '')} {it.get('license_version', '')}".strip().upper()
        return {
            "url": url,
            "halaman": it.get("foreign_landing_url", ""),
            "pembuat": (it.get("creator") or "")[:80],
            "lisensi": f"CC {lis}" if lis and not lis.startswith(("CC", "PDM")) else lis,
            "sumber": "Openverse",
        }
    return None


def gambar_produk(kueri, cadangan=None):
    """Coba beberapa kueri & sumber; kembalikan dict gambar atau None."""
    for q in [kueri] + ([cadangan] if cadangan and cadangan != kueri else []):
        for fn in (gambar_commons, gambar_openverse):
            try:
                hasil = fn(q)
            except Exception:
                hasil = None
            if hasil and hasil.get("url"):
                return hasil
    return None
