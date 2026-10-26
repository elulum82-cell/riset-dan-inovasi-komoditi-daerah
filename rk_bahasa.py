"""Mengurai satu input (komoditas atau tema) menjadi frasa Indonesia & Inggris.

Contoh: "olahan kulit jagung" -> inti "kulit jagung", Inggris "corn husk",
grup relevansi [{kulit, husk, peel, ...}, {jagung, corn, maize}].
"""
import re

import requests

from rk_config import SINONIM_KOMODITAS

# Kata yang tidak menentukan topik (diabaikan saat mencocokkan relevansi).
KATA_UMUM = {
    "olahan", "produk", "pengembangan", "inovasi", "pemanfaatan", "pengolahan",
    "dari", "dan", "untuk", "berbasis", "hasil", "turunan", "diversifikasi",
    "aplikasi", "penggunaan", "potensi", "riset", "penelitian", "teknologi",
    "the", "of", "and", "for", "from", "based", "product", "products",
    "development", "innovation", "utilization", "processing", "processed",
    "derivative", "derivatives", "value-added", "application", "use",
}

# Glosarium kata/frasa Indonesia -> padanan Inggris (padanan pertama dipakai untuk kueri).
GLOSARIUM = {
    # bagian tanaman / hasil samping
    "kulit": ["husk", "peel", "skin", "hull", "rind", "klobot"],
    "kulit buah": ["fruit peel", "peel"],
    "kulit ari": ["seed coat", "testa"],
    "tongkol": ["cob"],
    "klobot": ["corn husk", "husk"],
    "rambut": ["silk", "hair"],
    "limbah": ["waste", "by-product", "residue"],
    "ampas": ["bagasse", "pomace", "residue", "pulp"],
    "daun": ["leaf", "leaves"],
    "batang": ["stem", "stalk", "trunk"],
    "biji": ["seed", "bean", "kernel"],
    "buah": ["fruit"],
    "tempurung": ["shell"],
    "cangkang": ["shell"],
    "sabut": ["coir", "husk", "fiber"],
    "akar": ["root"],
    "bunga": ["flower"],
    "getah": ["latex", "sap", "resin"],
    "tandan kosong": ["empty fruit bunch"],
    "pelepah": ["frond", "midrib"],
    "jerami": ["straw"],
    "sekam": ["husk", "rice husk"],
    "dedak": ["bran"],
    "bekatul": ["rice bran", "bran"],
    "air": ["water"],
    "umbi": ["tuber"],
    "kayu": ["wood"],
    "serbuk gergaji": ["sawdust"],
    "nira": ["sap", "neera"],
    "bungkil": ["cake", "meal"],
    "molase": ["molasses"],
    "tetes tebu": ["molasses"],
    # hewani / perikanan
    "tulang": ["bone"],
    "sisik": ["scale"],
    "kepala": ["head"],
    "kotoran": ["manure", "dung"],
    "bulu": ["feather"],
    "darah": ["blood"],
    "jeroan": ["offal", "viscera"],
    "duri": ["bone", "spine"],
    "rumput": ["grass"],
    "laut": ["sea", "marine"],
    "minyak": ["oil"],
    "tepung": ["flour"],
    "gula": ["sugar"],
    "pati": ["starch"],
    "serat": ["fiber", "fibre"],
    "arang": ["charcoal"],
    # tema umum
    "bioplastik": ["bioplastic"],
    "kemasan": ["packaging"],
    "pangan fungsional": ["functional food"],
    "pangan": ["food"],
    "pakan": ["feed"],
    "pupuk": ["fertilizer"],
    "kompos": ["compost"],
    "energi terbarukan": ["renewable energy"],
    "bioenergi": ["bioenergy"],
    "kosmetik": ["cosmetic"],
    "obat": ["drug", "medicine"],
    "herbal": ["herbal"],
    "minuman": ["beverage", "drink"],
    "makanan ringan": ["snack"],
    "fermentasi": ["fermentation"],
    "karbon aktif": ["activated carbon"],
    "nanoselulosa": ["nanocellulose"],
    "biokomposit": ["biocomposite"],
    "biochar": ["biochar"],
    "briket": ["briquette"],
    "pewarna alami": ["natural dye", "natural colorant"],
    "minyak atsiri": ["essential oil"],
    "kerajinan": ["handicraft", "craft"],
    "tekstil": ["textile"],
    "sabun": ["soap"],
}

# Sinonim komoditas dari config ikut dipakai; tambahkan padanan kedua yang lazim.
_EKSTRA = {"jagung": ["corn", "maize"], "singkong": ["cassava", "manioc"],
           "kelapa sawit": ["oil palm", "palm"], "sawit": ["oil palm", "palm"],
           "kopi": ["coffee"], "kakao": ["cocoa", "cacao"], "padi": ["rice", "paddy"]}

KAMUS = dict(GLOSARIUM)
for _id, _en in SINONIM_KOMODITAS.items():
    KAMUS.setdefault(_id, [_en])
KAMUS.update(_EKSTRA)
_MAKS_KATA = max(len(k.split()) for k in KAMUS)


def _token(teks):
    return re.findall(r"[a-z0-9\-]+", teks.lower())


def urai(teks):
    """Pecah teks jadi frasa (pencocokan terpanjang dulu), buang kata umum.

    Hasil: daftar (frasa_id, [padanan_en]) — padanan kosong bila tidak dikenal.
    """
    kata = _token(teks)
    hasil, i = [], 0
    while i < len(kata):
        for n in range(min(_MAKS_KATA, len(kata) - i), 0, -1):
            frasa = " ".join(kata[i:i + n])
            if frasa in KAMUS:
                hasil.append((frasa, list(KAMUS[frasa])))
                i += n
                break
        else:
            if kata[i] not in KATA_UMUM:
                hasil.append((kata[i], []))
            i += 1
    return hasil


def _terjemah_daring(teks):
    """Cadangan untuk kata yang tidak ada di glosarium (MyMemory, gratis tanpa kunci)."""
    try:
        r = requests.get("https://api.mymemory.translated.net/get",
                         params={"q": teks, "langpair": "id|en"}, timeout=8)
        r.raise_for_status()
        t = (r.json().get("responseData") or {}).get("translatedText") or ""
        t = re.sub(r"\s+", " ", t).strip().lower()
        if t and t != teks.lower() and "mymemory" not in t and len(t) < 120:
            return t
    except Exception:
        pass
    return ""


def analisis(teks, daring=True):
    """Kembalikan dict: asli, inti_id, inti_en, grup (untuk relevansi)."""
    asli = teks.strip()
    bagian = urai(asli)
    inti_id = " ".join(f for f, _ in bagian) or asli.lower()
    tak_dikenal = [f for f, en in bagian if not en]

    if bagian and not tak_dikenal:
        # Bahasa Indonesia menaruh kata inti di depan; Inggris di belakang.
        inti_en = " ".join(en[0] for _, en in reversed(bagian))
    elif daring and tak_dikenal:
        inti_en = _terjemah_daring(inti_id)
    else:
        inti_en = ""
    if inti_en == inti_id:
        inti_en = ""

    grup = [{f, *en} for f, en in bagian]
    return {"asli": asli, "inti_id": inti_id, "inti_en": inti_en, "grup": grup}


def _ada(teks, kata):
    return re.search(rf"(?<![a-z]){re.escape(kata)}", teks) is not None


def cocok(teks, info):
    """True bila teks memuat semua grup kata inti, atau seluruh frasa Inggrisnya."""
    teks = teks.lower()
    grup = info.get("grup") or []
    if grup and all(any(_ada(teks, k) for k in g) for g in grup):
        return True
    kata_en = [k for k in _token(info.get("inti_en", "")) if k not in KATA_UMUM]
    return bool(kata_en) and all(_ada(teks, k) for k in kata_en)
