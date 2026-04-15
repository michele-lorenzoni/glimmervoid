# SPDX-License-Identifier: AGPL-3.0-or-later
"""
CommonCrawl URL source.

Interroga il CDX Index Server di CommonCrawl per restituire le URL
crawlate che corrispondono al pattern/dominio indicato dalla query.
Non e' un motore di ricerca full-text: la query viene interpretata
come URL, dominio o pattern (supporta wildcard '*').

Docs: https://index.commoncrawl.org/
"""

from json import loads
from urllib.parse import urlencode, urlparse

categories = ["general", "web"]
paging = True
safesearch = False
language_support = False
time_range_support = False

# Collezione CDX da interrogare (es. CC-MAIN-2025-05).
# Override possibile da settings.yml con la chiave 'index_name'.
index_name = "CC-MAIN-2025-05"
base_url = "https://index.commoncrawl.org"

# Numero di risultati per pagina.
page_size = 20

# Timeout di default (override possibile da settings.yml).
timeout = 10.0


def _build_match(query):
    """Deduce matchType e url da inviare al CDX server.

    - URL completo (http/https)  -> matchType=exact
    - dominio nudo (contiene '.') -> matchType=domain
    - parola singola              -> matchType=domain, trattata come dominio .com
    - pattern con '*'             -> matchType=prefix
    """
    q = query.strip()

    if "*" in q:
        return q, "prefix"

    if q.startswith("http://") or q.startswith("https://"):
        host = urlparse(q).netloc
        return host or q, "exact"

    if "." in q:
        return q, "domain"

    return q, "domain"


def request(query, params):
    url_arg, match_type = _build_match(query)

    args = {
        "url": url_arg,
        "output": "json",
        "matchType": match_type,
        "limit": page_size,
        "page": max(0, params["pageno"] - 1),
    }

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

        # Formatta timestamp CC (YYYYMMDDhhmmss) in ISO.
        published = ""
        if len(timestamp) >= 8:
            published = f"{timestamp[0:4]}-{timestamp[4:6]}-{timestamp[6:8]}"

        content_parts = []
        if status:
            content_parts.append(f"HTTP {status}")
        if mime:
            content_parts.append(mime)
        if published:
            content_parts.append(f"crawled {published}")

        results.append(
            {
                "url": url,
                "title": url,
                "content": " · ".join(content_parts) or "CommonCrawl archive entry",
                "publishedDate": published,
            }
        )

    return results
