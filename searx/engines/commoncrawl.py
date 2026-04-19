# SPDX-License-Identifier: AGPL-3.0-or-later
"""
CommonCrawl URL source.

Interroga il CDX Index Server di CommonCrawl per restituire le URL
crawlate che corrispondono al pattern/dominio indicato dalla query.
Non e' un motore di ricerca full-text: la query viene interpretata
come URL, dominio o pattern (supporta wildcard '*').

Docs: https://index.commoncrawl.org/
"""

from datetime import datetime
from json import loads
from urllib.parse import urlencode, urlparse

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

# Numero di risultati per pagina.
page_size = 20

# Timeout di default (override possibile da settings.yml).
timeout = 10.0


def _build_match(query):
    """Deduce (url, matchType, filter) da inviare al CDX server.

    CommonCrawl NON è un motore full-text: il CDX indicizza URL,
    non contenuto. Strategie:

    - URL completo (http/https)   -> matchType=exact
    - dominio nudo (contiene '.') -> matchType=domain
    - pattern con '*'             -> matchType=prefix
    - parola singola              -> scope .com (SURT prefix 'com,)')
                                     + filter=url:.*word.* per trovare
                                     tutti gli URL .com che contengono
                                     la parola in host o path.
    """
    q = query.strip()

    if "*" in q:
        return q, "prefix", None

    if q.startswith("http://") or q.startswith("https://"):
        host = urlparse(q).netloc
        return host or q, "exact", None

    if "." in q:
        return q, "domain", None

    # Parola singola: scansione .com con filtro regex sul url.
    return "com,)", "prefix", f"url:.*{q.lower()}.*"


def request(query, params):
    url_arg, match_type, filter_str = _build_match(query)

    args = {
        "url": url_arg,
        "output": "json",
        "matchType": match_type,
        "limit": page_size,
        "page": max(0, params["pageno"] - 1),
    }
    if filter_str:
        args["filter"] = filter_str

    params["url"] = f"{base_url}/{index_name}-index?{urlencode(args)}"
    params["headers"] = {"Accept": "application/x-ndjson"}
    return params


def response(resp):
    results = []

    # Il CDX server restituisce JSON Lines (una entry per riga).
    for line in resp.text.splitlines():
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

        # Timestamp CC: YYYYMMDDhhmmss → datetime per publishedDate.
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

        results.append(result_item)

    return results
