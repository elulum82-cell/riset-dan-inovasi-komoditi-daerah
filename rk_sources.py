"""Konektor ke sumber data riset resmi (API publik)."""
import html
import os
import re

import requests

from rk_models import Record

TIMEOUT = 25


def _email():
    return os.getenv("CONTACT_EMAIL", "").strip()


def _headers():
    return {"User-Agent": f"RisetKomoditi/1.0 (mailto:{_email() or 'unknown'})"}


def _bersih(teks):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", teks or ""))).strip()


def openalex(q, tahun_mulai, limit=25):
    params = {
        "search": q,
        "per-page": min(limit, 200),
        "filter": f"from_publication_date:{tahun_mulai}-01-01",
    }
    if _email():
        params["mailto"] = _email()
    if os.getenv("OPENALEX_API_KEY"):
        params["api_key"] = os.getenv("OPENALEX_API_KEY")
    r = requests.get("https://api.openalex.org/works", params=params,
                     headers=_headers(), timeout=TIMEOUT)
    r.raise_for_status()
    hasil = []
    for w in r.json().get("results", []):
        inv = w.get("abstract_inverted_index") or {}
        posisi = {i: kata for kata, idx in inv.items() for i in idx}
        sumber = (w.get("primary_location") or {}).get("source") or {}
        jenis = w.get("type") or "artikel"
        hasil.append(Record(
            sumber="OpenAlex",
            jenis="paten" if jenis == "patent" else jenis,
            judul=_bersih(w.get("display_name")),
            tahun=w.get("publication_year"),
            abstrak=" ".join(posisi[i] for i in sorted(posisi)),
            doi=(w.get("doi") or "").replace("https://doi.org/", ""),
            url=w.get("doi") or w.get("id", ""),
            venue=sumber.get("display_name") or "",
            penulis=", ".join(
                (a.get("author") or {}).get("display_name", "")
                for a in (w.get("authorships") or [])[:5]),
            sitasi=w.get("cited_by_count"),
            open_access=(w.get("open_access") or {}).get("is_oa"),
            kueri=q,
        ))
    return hasil


def crossref(q, tahun_mulai, limit=25):
    params = {"query": q, "rows": min(limit, 100),
              "filter": f"from-pub-date:{tahun_mulai}"}
    if _email():
        params["mailto"] = _email()
    r = requests.get("https://api.crossref.org/works", params=params,
                     headers=_headers(), timeout=TIMEOUT)
    r.raise_for_status()
    hasil = []
    for it in r.json().get("message", {}).get("items", []):
        dp = (it.get("issued") or {}).get("date-parts") or [[None]]
        tahun = dp[0][0] if dp and dp[0] else None
        hasil.append(Record(
            sumber="Crossref",
            jenis=it.get("type") or "artikel",
            judul=_bersih((it.get("title") or [""])[0]),
            tahun=tahun,
            abstrak=_bersih(it.get("abstract")),
            doi=it.get("DOI", ""),
            url=it.get("URL", ""),
            venue=(it.get("container-title") or [""])[0],
            penulis=", ".join(
                f"{a.get('given', '')} {a.get('family', '')}".strip()
                for a in (it.get("author") or [])[:5]),
            sitasi=it.get("is-referenced-by-count"),
            kueri=q,
        ))
    return hasil


def semantic_scholar(q, tahun_mulai, limit=25):
    headers = _headers()
    if os.getenv("S2_API_KEY"):
        headers["x-api-key"] = os.getenv("S2_API_KEY")
    params = {
        "query": q, "limit": min(limit, 100), "year": f"{tahun_mulai}-",
        "fields": "title,abstract,year,externalIds,venue,citationCount,url,isOpenAccess,authors",
    }
    r = requests.get("https://api.semanticscholar.org/graph/v1/paper/search",
                     params=params, headers=headers, timeout=TIMEOUT)
    r.raise_for_status()
    hasil = []
    for p in r.json().get("data") or []:
        hasil.append(Record(
            sumber="Semantic Scholar", jenis="artikel",
            judul=_bersih(p.get("title")), tahun=p.get("year"),
            abstrak=p.get("abstract") or "",
            doi=(p.get("externalIds") or {}).get("DOI", "") or "",
            url=p.get("url") or "", venue=p.get("venue") or "",
            penulis=", ".join(a.get("name", "") for a in (p.get("authors") or [])[:5]),
            sitasi=p.get("citationCount"), open_access=p.get("isOpenAccess"),
            kueri=q,
        ))
    return hasil


def europe_pmc(q, tahun_mulai, limit=25):
    params = {"query": f"({q}) AND PUB_YEAR:[{tahun_mulai} TO 3000]",
              "format": "json", "pageSize": min(limit, 100), "resultType": "core"}
    r = requests.get("https://www.ebi.ac.uk/europepmc/webservices/rest/search",
                     params=params, headers=_headers(), timeout=TIMEOUT)
    r.raise_for_status()
    hasil = []
    for it in r.json().get("resultList", {}).get("result", []):
        doi = it.get("doi", "") or ""
        tahun = str(it.get("pubYear", ""))
        hasil.append(Record(
            sumber="Europe PMC", jenis="artikel",
            judul=_bersih(it.get("title")),
            tahun=int(tahun) if tahun.isdigit() else None,
            abstrak=_bersih(it.get("abstractText")), doi=doi,
            url=(f"https://doi.org/{doi}" if doi else
                 f"https://europepmc.org/article/{it.get('source')}/{it.get('id')}"),
            venue=it.get("journalTitle", "") or "",
            penulis=it.get("authorString", "") or "",
            sitasi=it.get("citedByCount"),
            open_access=it.get("isOpenAccess") == "Y", kueri=q,
        ))
    return hasil


def lens_paten(q, tahun_mulai, limit=25):
    """Opsional: aktif hanya bila LENS_TOKEN diisi di .env."""
    token = os.getenv("LENS_TOKEN")
    if not token:
        return []
    body = {
        "query": {"query_string": {"query": q}},
        "size": min(limit, 100),
        "include": ["lens_id", "biblio.invention_title", "abstract",
                    "date_published", "jurisdiction"],
    }
    r = requests.post("https://api.lens.org/patent/search", json=body,
                      headers={"Authorization": f"Bearer {token}",
                               "Content-Type": "application/json"},
                      timeout=TIMEOUT)
    r.raise_for_status()

    def _teks(lst):
        if not lst:
            return ""
        if isinstance(lst, dict):
            lst = [lst]
        en = [x for x in lst if x.get("lang") == "en"]
        return (en or lst)[0].get("text", "")

    hasil = []
    for p in r.json().get("data", []):
        tgl = p.get("date_published") or ""
        tahun = int(tgl[:4]) if tgl[:4].isdigit() else None
        if tahun and tahun < tahun_mulai:
            continue
        hasil.append(Record(
            sumber="Lens (paten)", jenis="paten",
            judul=_bersih(_teks((p.get("biblio") or {}).get("invention_title"))),
            tahun=tahun, abstrak=_bersih(_teks(p.get("abstract"))),
            url=f"https://www.lens.org/lens/patent/{p.get('lens_id')}",
            venue=p.get("jurisdiction", "") or "", kueri=q,
        ))
    return hasil


SUMBER = {
    "OpenAlex": openalex,
    "Crossref": crossref,
    "Semantic Scholar": semantic_scholar,
    "Europe PMC": europe_pmc,
    "Lens (paten)": lens_paten,
}
