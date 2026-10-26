"""Mendeteksi contoh produk dari judul/abstrak hasil riset.

Setiap entri leksikon: (istilah Inggris, istilah Indonesia, kategori).
Istilah Indonesia boleh berisi beberapa varian dipisah "|".
Tambahkan entri baru sesuai kebutuhan.
"""
import re
from collections import defaultdict

LEKSIKON = [
    # Pangan olahan & minuman
    ("flour", "tepung", "Pangan olahan & minuman"),
    ("sugar", "gula", "Pangan olahan & minuman"),
    ("milk", "susu", "Pangan olahan & minuman"),
    ("chips", "keripik|kripik", "Pangan olahan & minuman"),
    ("crackers", "kerupuk", "Pangan olahan & minuman"),
    ("noodles", "mie|mi", "Pangan olahan & minuman"),
    ("bread", "roti", "Pangan olahan & minuman"),
    ("cookies", "kue kering|cookies", "Pangan olahan & minuman"),
    ("biscuit", "biskuit", "Pangan olahan & minuman"),
    ("cake", "bolu|cake", "Pangan olahan & minuman"),
    ("fruit jam", "selai|marmalade", "Pangan olahan & minuman"),
    ("candy", "permen", "Pangan olahan & minuman"),
    ("syrup", "sirup", "Pangan olahan & minuman"),
    ("vinegar", "cuka", "Pangan olahan & minuman"),
    ("juice", "jus|sari buah", "Pangan olahan & minuman"),
    ("beverage", "minuman", "Pangan olahan & minuman"),
    ("tea", "teh", "Pangan olahan & minuman"),
    ("wine", "wine|anggur buah", "Pangan olahan & minuman"),
    ("yogurt", "yoghurt|yogurt", "Pangan olahan & minuman"),
    ("ice cream", "es krim", "Pangan olahan & minuman"),
    ("chocolate", "cokelat|coklat", "Pangan olahan & minuman"),
    ("sauce", "saus", "Pangan olahan & minuman"),
    ("nata de coco", "nata de coco", "Pangan olahan & minuman"),
    ("dodol", "dodol", "Pangan olahan & minuman"),
    ("snack", "camilan|snack", "Pangan olahan & minuman"),
    ("pasta", "pasta", "Pangan olahan & minuman"),
    ("sausage", "sosis", "Pangan olahan & minuman"),
    ("nuggets", "nugget", "Pangan olahan & minuman"),
    ("jelly", "jeli|jelly", "Pangan olahan & minuman"),
    ("powder", "bubuk", "Pangan olahan & minuman"),
    ("instant drink", "minuman instan", "Pangan olahan & minuman"),
    ("kombucha", "kombucha", "Pangan olahan & minuman"),
    ("meat analogue", "daging analog", "Pangan olahan & minuman"),
    # Pangan fungsional
    ("dietary supplement", "suplemen", "Pangan fungsional & nutrasetikal"),
    ("probiotic", "probiotik", "Pangan fungsional & nutrasetikal"),
    ("protein isolate", "isolat protein", "Pangan fungsional & nutrasetikal"),
    ("dietary fiber", "serat pangan", "Pangan fungsional & nutrasetikal"),
    ("extract", "ekstrak", "Pangan fungsional & nutrasetikal"),
    ("herbal tea", "teh herbal", "Pangan fungsional & nutrasetikal"),
    # Farmasi
    ("capsule", "kapsul", "Farmasi & kesehatan"),
    ("ointment", "salep", "Farmasi & kesehatan"),
    ("wound dressing", "pembalut luka", "Farmasi & kesehatan"),
    ("hydrogel", "hidrogel", "Farmasi & kesehatan"),
    ("tablet", "tablet", "Farmasi & kesehatan"),
    # Kosmetik
    ("soap", "sabun", "Kosmetik & perawatan"),
    ("lotion", "losion|lotion", "Kosmetik & perawatan"),
    ("cream", "krim", "Kosmetik & perawatan"),
    ("shampoo", "sampo|shampo", "Kosmetik & perawatan"),
    ("sunscreen", "tabir surya", "Kosmetik & perawatan"),
    ("face mask", "masker wajah|masker", "Kosmetik & perawatan"),
    ("lip balm", "lip balm", "Kosmetik & perawatan"),
    ("perfume", "parfum", "Kosmetik & perawatan"),
    ("serum", "serum", "Kosmetik & perawatan"),
    ("aromatherapy", "aromaterapi", "Kosmetik & perawatan"),
    # Bioenergi
    ("briquette", "briket", "Bioenergi & bahan bakar"),
    ("charcoal", "arang", "Bioenergi & bahan bakar"),
    ("biodiesel", "biodiesel", "Bioenergi & bahan bakar"),
    ("bioethanol", "bioetanol", "Bioenergi & bahan bakar"),
    ("biogas", "biogas", "Bioenergi & bahan bakar"),
    ("pellet", "pelet", "Bioenergi & bahan bakar"),
    ("bio-oil", "bio-oil|minyak pirolisis", "Bioenergi & bahan bakar"),
    # Material
    ("activated carbon", "karbon aktif|arang aktif", "Material & biokomposit"),
    ("nanocellulose", "nanoselulosa", "Material & biokomposit"),
    ("biocomposite", "biokomposit", "Material & biokomposit"),
    ("composite", "komposit", "Material & biokomposit"),
    ("particleboard", "papan partikel", "Material & biokomposit"),
    ("fiberboard", "papan serat", "Material & biokomposit"),
    ("fiber", "serat|fibre", "Material & biokomposit"),
    ("coir", "sabut", "Material & biokomposit"),
    ("yarn", "benang", "Material & biokomposit"),
    ("fabric", "kain", "Material & biokomposit"),
    ("paper", "kertas", "Material & biokomposit"),
    ("pulp", "pulp", "Material & biokomposit"),
    ("brick", "bata", "Material & biokomposit"),
    ("concrete", "beton", "Material & biokomposit"),
    ("handicraft", "kerajinan", "Material & biokomposit"),
    ("furniture", "mebel|furnitur", "Material & biokomposit"),
    ("membrane", "membran", "Material & biokomposit"),
    ("adsorbent", "adsorben", "Material & biokomposit"),
    ("aerogel", "aerogel", "Material & biokomposit"),
    # Kemasan
    ("bioplastic", "bioplastik", "Kemasan & bioplastik"),
    ("edible film", "edible film|film edibel", "Kemasan & bioplastik"),
    ("edible coating", "edible coating|pelapis edibel", "Kemasan & bioplastik"),
    ("packaging", "kemasan", "Kemasan & bioplastik"),
    ("straw", "sedotan", "Kemasan & bioplastik"),
    ("biodegradable plate", "piring biodegradable", "Kemasan & bioplastik"),
    # Pakan & pertanian
    ("animal feed", "pakan", "Pakan & pertanian"),
    ("fish feed", "pakan ikan", "Pakan & pertanian"),
    ("fertilizer", "pupuk", "Pakan & pertanian"),
    ("compost", "kompos", "Pakan & pertanian"),
    ("biochar", "biochar|bioarang", "Pakan & pertanian"),
    ("biopesticide", "biopestisida|pestisida nabati", "Pakan & pertanian"),
    ("silage", "silase", "Pakan & pertanian"),
    ("growing media", "media tanam", "Pakan & pertanian"),
    ("liquid smoke", "asap cair", "Pakan & pertanian"),
    # Kimia & bahan industri
    ("essential oil", "minyak atsiri", "Kimia & bahan industri"),
    ("virgin oil", "minyak murni|vco", "Kimia & bahan industri"),
    ("oil", "minyak", "Kimia & bahan industri"),
    ("starch", "pati", "Kimia & bahan industri"),
    ("modified starch", "pati termodifikasi", "Kimia & bahan industri"),
    ("pectin", "pektin", "Kimia & bahan industri"),
    ("chitosan", "kitosan", "Kimia & bahan industri"),
    ("collagen", "kolagen", "Kimia & bahan industri"),
    ("gelatin", "gelatin", "Kimia & bahan industri"),
    ("carrageenan", "karagenan|karaginan", "Kimia & bahan industri"),
    ("agar-agar", "agar-agar|agarose", "Kimia & bahan industri"),
    ("alginate", "alginat", "Kimia & bahan industri"),
    ("enzyme", "enzim", "Kimia & bahan industri"),
    ("surfactant", "surfaktan", "Kimia & bahan industri"),
    ("natural dye", "pewarna alami", "Kimia & bahan industri"),
    ("wax", "lilin", "Kimia & bahan industri"),
    ("resin", "resin", "Kimia & bahan industri"),
    ("adhesive", "perekat", "Kimia & bahan industri"),
    ("silica", "silika", "Kimia & bahan industri"),
    ("xylitol", "xilitol", "Kimia & bahan industri"),
    ("oleoresin", "oleoresin", "Kimia & bahan industri"),
]


def _pola(varian):
    alt = "|".join(re.escape(v.strip()).replace(r"\ ", r"\s+")
                   for v in varian if v.strip())
    return re.compile(rf"(?<![a-z])(?:{alt})(?:e?s)?(?![a-z])")


# Urutkan istilah terpanjang dulu agar "essential oil" didahulukan dari "oil".
_ENTRI = []
for en, idn, kat in LEKSIKON:
    varian = [en] + idn.split("|")
    _ENTRI.append((max(len(v) for v in varian), en, idn.split("|")[0], kat, _pola(varian)))
_ENTRI.sort(key=lambda x: -x[0])

INFO_PRODUK = {en: {"id": idn, "kategori": kat} for _, en, idn, kat, _ in _ENTRI}


def _hapus_subjek(teks, subjek):
    for s in sorted(subjek, key=len, reverse=True):
        teks = re.sub(rf"(?<![a-z]){re.escape(s)}(?![a-z])", " ", teks)
    return teks


def deteksi_produk(record, subjek=()):
    """Kembalikan daftar kunci produk (istilah Inggris) yang disebut di judul.

    Bila judul tidak memuat satu pun produk, abstrak (300 karakter awal) dipakai.
    Nama komoditas dihapus dulu agar "oil palm" tidak terbaca sebagai "oil".
    """
    for teks in (record.judul, (record.abstrak or "")[:300]):
        t = _hapus_subjek((teks or "").lower(), subjek)
        ketemu = []
        for _, en, _, _, pola in _ENTRI:
            if pola.search(t):
                ketemu.append(en)
                t = pola.sub(" | ", t)
        if ketemu:
            return ketemu
    return []


# Nama tampilan khusus bila urutan kata Indonesia berbeda ({k} = komoditas).
NAMA_KHUSUS = {"virgin oil": "minyak {k} murni", "essential oil": "minyak atsiri {k}"}


def nama_tampil(en, komoditas=""):
    idn = INFO_PRODUK.get(en, {}).get("id", en)
    k = komoditas.strip().lower()
    if k and en in NAMA_KHUSUS:
        return NAMA_KHUSUS[en].format(k=k).capitalize()
    return f"{idn} {k}".strip().capitalize() if k else idn.capitalize()


def ringkas_produk(records, komoditas="", komoditas_en="", maks=12):
    """Kelompokkan riset per produk -> daftar dict siap tampil, terurut terbanyak."""
    grup = defaultdict(list)
    for r in records:
        for p in r.get("produk", []) if isinstance(r, dict) else r.produk:
            grup[p].append(r)
    hasil = []
    for en, rs in grup.items():
        rs = sorted(rs, key=lambda x: (x.get("sitasi") or 0), reverse=True)
        subjek_en = (komoditas_en or komoditas).strip()
        hasil.append({
            "kunci": en,
            "nama": nama_tampil(en, komoditas),
            "nama_en": f"{subjek_en} {en}".strip(),
            "kategori": INFO_PRODUK.get(en, {}).get("kategori", "Lainnya"),
            "jumlah": len(rs),
            "riset": rs[:5],
        })
    hasil.sort(key=lambda x: -x["jumlah"])
    return hasil[:maks]
