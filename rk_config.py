"""Pengaturan yang boleh diedit: istilah pencarian, sinonim komoditas, kategori."""

# Istilah yang dipadukan dengan nama komoditas bila pengguna tidak mengisi tema.
ISTILAH_PENGEMBANGAN = [
    "product development",
    "value-added products",
    "derivative products",
    "processing innovation",
    "product diversification",
    "pengembangan produk",
    "produk turunan",
    "diversifikasi produk",
    "pengolahan",
]

# Sinonim Indonesia -> Inggris. Tambahkan bebas.
SINONIM_KOMODITAS = {
    "kelapa": "coconut", "rumput laut": "seaweed", "kopi": "coffee",
    "kakao": "cocoa", "jagung": "maize", "singkong": "cassava",
    "ubi kayu": "cassava", "ubi jalar": "sweet potato", "sawit": "oil palm",
    "kelapa sawit": "oil palm", "karet": "rubber", "pisang": "banana",
    "mete": "cashew", "jambu mete": "cashew", "vanili": "vanilla",
    "porang": "konjac", "tembakau": "tobacco", "bambu": "bamboo",
    "ikan": "fish", "udang": "shrimp", "madu": "honey", "cengkeh": "clove",
    "pala": "nutmeg", "lada": "pepper", "kunyit": "turmeric", "jahe": "ginger",
    "sagu": "sago", "beras": "rice", "padi": "rice", "kedelai": "soybean",
    "nanas": "pineapple", "mangga": "mango", "durian": "durian",
    "tebu": "sugarcane", "teh": "tea", "kapuk": "kapok", "nilam": "patchouli",
    "serai": "lemongrass", "kelor": "moringa", "sorgum": "sorghum",
    "bawang merah": "shallot", "cabai": "chili", "tomat": "tomato",
    "kentang": "potato", "talas": "taro", "sukun": "breadfruit",
    "aren": "sugar palm", "lontar": "palmyra palm", "gaharu": "agarwood",
    "kemiri": "candlenut", "sapi": "cattle", "susu": "milk",
    "telur": "egg", "ayam": "chicken", "kambing": "goat",
    "mutiara": "pearl", "teripang": "sea cucumber", "tuna": "tuna",
    "lobster": "lobster", "kepiting": "crab", "garam": "salt",
    "jamur": "mushroom", "alpukat": "avocado", "jeruk": "citrus",
    "markisa": "passion fruit", "salak": "snake fruit",
}

# Kategori bentuk pengembangan produk: nama -> kata kunci (huruf kecil, ID+EN).
KATEGORI = {
    "Pangan olahan & minuman": [
        "food", "beverage", "snack", "flour", "pangan", "minuman", "tepung",
        "makanan", "fermented", "fermentasi", "bakery", "noodle", "mie",
        "confectionery", "jam", "selai", "juice", "sari buah",
    ],
    "Pangan fungsional & nutrasetikal": [
        "functional food", "nutraceutical", "antioxidant", "probiotic",
        "prebiotic", "pangan fungsional", "antioksidan", "bioactive",
        "bioaktif", "dietary fiber", "supplement", "suplemen",
    ],
    "Farmasi & kesehatan": [
        "pharmaceutical", "drug", "antibacterial", "antimicrobial", "wound",
        "farmasi", "obat", "antibakteri", "anti-inflammatory", "antidiabetic",
        "herbal medicine", "jamu",
    ],
    "Kosmetik & perawatan": [
        "cosmetic", "skincare", "skin care", "lotion", "soap", "kosmetik",
        "sabun", "serum", "shampoo", "sunscreen", "perfume", "parfum",
    ],
    "Bioenergi & bahan bakar": [
        "biofuel", "biodiesel", "bioethanol", "biogas", "briquette", "pellet",
        "bioenergi", "bioenergy", "briket", "bioetanol", "biomass fuel",
    ],
    "Material & biokomposit": [
        "composite", "fiber", "fibre", "nanocellulose", "biocomposite",
        "komposit", "serat", "activated carbon", "karbon aktif", "board",
        "panel", "textile", "tekstil", "coir", "sabut",
    ],
    "Kemasan & bioplastik": [
        "packaging", "bioplastic", "edible film", "edible coating",
        "biodegradable", "kemasan", "bioplastik",
    ],
    "Pakan & pertanian": [
        "feed", "fertilizer", "fertiliser", "compost", "biochar", "pakan",
        "pupuk", "kompos", "biopesticide", "biopestisida", "silage", "silase",
    ],
    "Kimia & bahan industri": [
        "oleochemical", "enzyme", "extraction", "essential oil", "surfactant",
        "ekstraksi", "minyak atsiri", "enzim", "pectin", "pektin", "starch",
        "pati", "chitosan", "kitosan", "carrageenan", "karagenan", "alginate",
    ],
    "Teknologi proses & mesin": [
        "drying", "dryer", "machine", "equipment", "process optimization",
        "pengeringan", "mesin", "alat", "extrusion", "ekstrusi",
    ],
    "Bisnis, rantai nilai & pasar": [
        "value chain", "market", "business model", "supply chain",
        "rantai nilai", "pemasaran", "umkm", "hilirisasi", "downstream",
        "agroindustry", "agroindustri", "feasibility", "kelayakan",
    ],
}
