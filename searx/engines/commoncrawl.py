# SPDX-License-Identifier: AGPL-3.0-or-later
"""
CommonCrawl URL source.

Interroga il CDX Index Server di CommonCrawl per restituire le URL
crawlate che corrispondono alla query.

ATTENZIONE: il CDX è un indice di URL, non di contenuti. Non c'è
full-text search sulle pagine. La query viene interpretata come
URL/dominio/pattern e — per parole nude — come regex filter
sull'URL su scope globale.

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
# Override da settings.yml con la chiave 'index_name'.
# Aggiornare periodicamente tramite https://index.commoncrawl.org/collinfo.json
index_name = "CC-MAIN-2026-12"
base_url = "https://index.commoncrawl.org"

page_size = 20
timeout = 15.0


def _build_match(query):
    """Ritorna (url, matchType, filter).

    Il CDX Server è un INDICE SHARDED di URL: ogni request RICHIEDE
    uno scope URL/SURT che identifichi una slice dell'indice. Non si
    può fare un "full-index scan" — url=* viene rifiutato. Il
    parametro filter=url:REGEX funziona solo DENTRO lo scope.

    - URL completo (http/https)   -> matchType=exact
    - dominio nudo (contiene '.') -> matchType=domain
    - pattern con '*'             -> matchType=prefix
    - parola nuda                 -> scope = TLD .com (SURT 'com,)')
                                     + filter=url:.*word.* → tutti
                                     gli URL .com contenenti la parola
                                     in host o path. Limitato al TLD
                                     .com per costruzione dell'API.

    Per cercare altri TLD, specifica la query come dominio nudo
    (es. "hello.org") o URL pieno.
    """
    q = query.strip()

    if "*" in q:
        return q, "prefix", None

    if q.startswith("http://") or q.startswith("https://"):
        host = urlparse(q).netloc
        return host or q, "exact", None

    if "." in q:
        return q, "domain", None

    # Parola nuda: scope .com + regex filter sull'URL (unica slice
    # che CDX accetta come singolo scope "ampio"; vedi docstring).
    # SURT prefix "com," (senza `)`) matcha tutto ciò che sta sotto
    # .com — "com,)" invece matcherebbe solo un dominio che si
    # chiama letteralmente "com" (nulla).
    return "com,", "prefix", f"url:.*{q.lower()}.*"


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
