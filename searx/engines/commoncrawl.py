# SPDX-License-Identifier: AGPL-3.0-or-later
"""
CommonCrawl URL source.

Interroga il CDX Index Server di CommonCrawl per restituire le URL
crawlate che corrispondono al pattern/dominio indicato dalla query.
Non è un motore di ricerca full-text sui CONTENUTI: il CDX indicizza
URL. Con un filter regex possiamo però trovare URL che contengono
una certa stringa in host/path.

Docs: https://index.commoncrawl.org/
"""

from datetime import datetime
from json import loads
from urllib.parse import urlencode, urlparse

from searx.network import get as http_get

categories = ["general", "web"]
paging = True
safesearch = False
language_support = False
time_range_support = False

# Collezione CDX da interrogare (es. CC-MAIN-2026-12).
# Override possibile da settings.yml con la chiave 'index_name'.
# Aggiornare periodicamente tramite https://index.commoncrawl.org/collinfo.json
index_name = "CC-MAIN-2026-12"
base_url = "https://index.commoncrawl.org"

# Numero di risultati per pagina (per scope TLD).
page_size = 10

# Timeout di default (override possibile da settings.yml).
timeout = 15.0

# Per le query "parola singola" CDX richiede uno scope URL/SURT.
# Iteriamo su questi TLD + filter regex per coprire un bacino
# ragionevole. Override da settings.yml con `word_scope_tlds`.
word_scope_tlds = ["com", "org", "net", "io", "dev", "co"]


def _classify_query(query):
    """Ritorna un tipo tra: 'prefix' | 'exact' | 'domain' | 'word'.

    Accompagnato da valori utili a costruire le richieste CDX.

    - 'prefix' : query con '*' → un solo request, matchType=prefix.
    - 'exact'  : query URL http(s) → un solo request, matchType=exact.
    - 'domain' : query con '.' → un solo request, matchType=domain.
    - 'word'   : parola singola → N request (uno per TLD) con
                 matchType=prefix + filter=url:.*word.*
    """
    q = query.strip()

    if "*" in q:
        return "prefix", q, None

    if q.startswith("http://") or q.startswith("https://"):
        host = urlparse(q).netloc
        return "exact", (host or q), None

    if "." in q:
        return "domain", q, None

    return "word", q.lower(), None


def _cdx_url(url_arg, match_type, filter_str, page):
    args = {
        "url": url_arg,
        "output": "json",
        "matchType": match_type,
        "limit": page_size,
        "page": max(0, page),
    }
    if filter_str:
        args["filter"] = filter_str
    return f"{base_url}/{index_name}-index?{urlencode(args)}"


def request(query, params):
    qtype, value, _ = _classify_query(query)
    page = max(0, params["pageno"] - 1)

    if qtype == "word":
        # La singola request qui è solo un placeholder: usa il primo TLD.
        # Il resto dei TLD viene interrogato in response() via http_get.
        first_tld = word_scope_tlds[0]
        url = _cdx_url(f"{first_tld},)", "prefix", f"url:.*{value}.*", page)
    elif qtype == "prefix":
        url = _cdx_url(value, "prefix", None, page)
    elif qtype == "exact":
        url = _cdx_url(value, "exact", None, page)
    else:  # domain
        url = _cdx_url(value, "domain", None, page)

    params["url"] = url
    params["headers"] = {"Accept": "application/x-ndjson"}
    # Stash metadata per riusare in response()
    params["_cc_qtype"] = qtype
    params["_cc_value"] = value
    params["_cc_page"] = page
    return params


def _parse_cdx_lines(text):
    items = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entry = loads(line)
        except ValueError:
            continue

        url = entry.get("url")
        if not url:
            continue

        timestamp = entry.get("timestamp", "")
        mime = entry.get("mime", "")
        status = entry.get("status", "")

        published_dt = None
        if len(timestamp) >= 14:
            try:
                published_dt = datetime.strptime(timestamp[:14], "%Y%m%d%H%M%S")
            except ValueError:
                published_dt = None

        content_parts = []
        if status:
            content_parts.append(f"HTTP {status}")
        if mime:
            content_parts.append(mime)
        if published_dt:
            content_parts.append(f"crawled {published_dt.strftime('%Y-%m-%d')}")

        result_item = {
            "url": url,
            "title": url,
            "content": " · ".join(content_parts) or "CommonCrawl archive entry",
        }
        if published_dt:
            result_item["publishedDate"] = published_dt

        items.append(result_item)
    return items


def response(resp):
    # Parse della prima risposta (primo TLD o query non-word).
    results = _parse_cdx_lines(resp.text)

    # Per le query "word", interroga gli altri TLD in sequenza.
    qtype = getattr(resp, "search_params", {}).get("_cc_qtype")
    if qtype is None:
        # Compat: params non propagato come attributo su alcune versioni
        # di SearXNG. In quel caso la richiesta primaria basta.
        return results

    if qtype == "word":
        value = resp.search_params["_cc_value"]
        page = resp.search_params["_cc_page"]
        for tld in word_scope_tlds[1:]:
            extra_url = _cdx_url(f"{tld},)", "prefix", f"url:.*{value}.*", page)
            try:
                extra_resp = http_get(extra_url, timeout=timeout, headers={"Accept": "application/x-ndjson"})
                if extra_resp.status_code == 200:
                    results.extend(_parse_cdx_lines(extra_resp.text))
            except Exception:
                # Non interrompere per fallimenti su un singolo TLD.
                continue

    # Dedup per url mantenendo il primo
    seen = set()
    deduped = []
    for r in results:
        if r["url"] in seen:
            continue
        seen.add(r["url"])
        deduped.append(r)
    return deduped
