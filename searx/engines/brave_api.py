# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Brave Search API
"""

from json import loads
from urllib.parse import urlencode

# Engine metadata
categories = ["general", "web"]
paging = True
safesearch = True
language_support = True

# API configuration
api_key = "TUA_API_KEY_QUI"  # Sostituisci con la tua chiave
base_url = "https://api.search.brave.com/res/v1/web/search"


# Search function
def request(query, params):
    """Build the search request"""

    # Safesearch mapping
    safesearch_map = {
        0: "off",  # None
        1: "moderate",  # Moderate
        2: "strict",  # Strict
    }

    # Build query parameters
    args = {
        "q": query,
        "count": 20,
        "offset": (params["pageno"] - 1) * 20,
        "safesearch": safesearch_map.get(params["safesearch"], "moderate"),
    }

    # Add language if available
    if params.get("language"):
        # Brave uses 'country' parameter (e.g., 'IT', 'US')
        lang_code = params["language"].split("-")[0].upper()
        if len(lang_code) == 2:
            args["country"] = lang_code

    # Build the URL
    params["url"] = f"{base_url}?{urlencode(args)}"

    # Add API key header
    params["headers"] = {"Accept": "application/json", "X-Subscription-Token": api_key}

    return params


def response(resp):
    """Parse the API response"""

    results = []

    try:
        json_data = loads(resp.text)
    except Exception:
        return results

    # Parse web results
    web_results = json_data.get("web", {}).get("results", [])

    for result in web_results:
        item = {
            "url": result.get("url", ""),
            "title": result.get("title", ""),
            "content": result.get("description", ""),
        }

        # Add thumbnail if available
        if result.get("thumbnail"):
            item["thumbnail"] = result["thumbnail"].get("src")

        # Add age/date if available
        if result.get("age"):
            item["publishedDate"] = result["age"]

        results.append(item)

    # Optionally add news results
    news_results = json_data.get("news", {}).get("results", [])
    for result in news_results:
        item = {
            "url": result.get("url", ""),
            "title": result.get("title", ""),
            "content": result.get("description", ""),
            "publishedDate": result.get("age"),
        }

        if result.get("thumbnail"):
            item["thumbnail"] = result["thumbnail"].get("src")

        results.append(item)

    return results
