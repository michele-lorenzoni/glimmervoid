# SPDX-License-Identifier: AGPL-3.0-or-later
"""
CommonCrawl URL source — DISABILITATO.

Il CDX Server di CommonCrawl è un indice di URL, non un motore
full-text: non può scansionare l'intero indice per trovare URL che
contengono una stringa. Richiede sempre uno scope URL/host/dominio
specifico. Per un uso generalista non è adatto.

Tutto il codice è commentato di sotto. Per riattivarlo:
1. togliere il blocco string letterale `\"\"\"...\"\"\"` qui sotto
2. riattivare l'entry in settings.yml.template
3. riattivare la COPY nel Dockerfile
"""

_DISABLED = """
from datetime import datetime
from json import loads
from urllib.parse import urlencode, urlparse

categories = ["general", "web"]
paging = True
safesearch = False
language_support = False
time_range_support = False

index_name = "CC-MAIN-2026-12"
base_url = "https://index.commoncrawl.org"

page_size = 20
timeout = 15.0


def _build_match(query):
    q = query.strip()

    if "*" in q:
        return q, "prefix", None

    if q.startswith("http://") or q.startswith("https://"):
        host = urlparse(q).netloc
        return host or q, "exact", None

    if "." in q:
        return q, "domain", None

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
"""
