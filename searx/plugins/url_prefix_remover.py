"""Glimmervoid custom plugin: nasconde i risultati il cui URL inizia con un
*prefisso-URL* bloccato (host + path).

Perche' serve
-------------
Il plugin upstream ``hostnames`` (dove finiscono i ``blocked_domains``) filtra
solo sull'hostname (``parsed_url.netloc``) e non sa esprimere un blocco per
path. Questo plugin colma il buco: scarta ogni risultato il cui URL *inizia*
con uno dei prefissi elencati in ``blocked_url_prefixes.txt``.

Esempio: il prefisso ``https://www.nvidia.com/pl-pl/`` nasconde quell'URL
stesso e tutto cio' che sta sotto quel path (``.../pl-pl/geforce`` ...), ma NON
``https://www.nvidia.com/en-us/``.

Il match e' insensibile allo scheme (http/https) e a un eventuale ``www.``
iniziale, e rispetta i confini di path (``/pl-pl`` non matcha ``/pl-plaza``).

La lista viene letta una volta all'avvio (come i ``blocked_domains``, che sono
iniettati a build-time): per aggiornarla serve un rebuild dell'immagine.
"""

import logging
import os
import typing as t
from urllib.parse import urlparse

from flask_babel import gettext  # pyright: ignore[reportUnknownVariableType]

from searx.plugins import Plugin, PluginInfo

if t.TYPE_CHECKING:
    from searx.plugins import PluginCfg
    from searx.result_types import Result
    from searx.search import SearchWithPlugins
    from searx.extended_types import SXNG_Request

log = logging.getLogger("searx.plugins.url_prefix_remover")

# La lista sta accanto al modulo (il Dockerfile ce la copia). Override opzionale
# via env per test locali.
_DEFAULT_LIST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "blocked_url_prefixes.txt")


def _normalize(raw: str) -> str:
    """Chiave di confronto ``host+path``, scheme/www-insensitive, senza slash finale."""
    raw = raw.strip()
    if not raw:
        return ""
    # consenti voci senza scheme (es. "nvidia.com/pl-pl/")
    parsed = urlparse(raw if "//" in raw else "//" + raw)
    host = (parsed.hostname or "").lower()
    if host.startswith("www."):
        host = host[4:]
    return host + parsed.path.rstrip("/")


def _load_prefixes(path: str) -> "list[str]":
    prefixes: "list[str]" = []
    try:
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.split("#", 1)[0].strip()
                if not line:
                    continue
                key = _normalize(line)
                if key:
                    prefixes.append(key)
    except FileNotFoundError:
        log.warning("url_prefix_remover: lista non trovata: %s", path)
    except OSError as exc:
        log.warning("url_prefix_remover: impossibile leggere %s: %s", path, exc)
    return prefixes


class SXNGPlugin(Plugin):
    """Rimuove i risultati il cui URL inizia con un prefisso bloccato."""

    id = "url_prefix_remover"

    def __init__(self, plg_cfg: "PluginCfg") -> None:
        super().__init__(plg_cfg)
        list_path = os.environ.get("GLIMMERVOID_URL_PREFIXES_FILE", _DEFAULT_LIST)
        self.prefixes = _load_prefixes(list_path)
        log.info("url_prefix_remover: %d prefissi caricati da %s", len(self.prefixes), list_path)
        self.info = PluginInfo(
            id=self.id,
            name=gettext("URL prefix remover"),
            description=gettext("Remove results whose URL starts with a blocked URL prefix"),
            preference_section="general",
        )

    def _blocked(self, key: str) -> bool:
        for pfx in self.prefixes:
            # confine di path: match esatto sul prefisso o discendenti sotto "/"
            if key == pfx or key.startswith(pfx + "/"):
                return True
        return False

    def on_result(self, request: "SXNG_Request", search: "SearchWithPlugins", result: "Result") -> bool:
        parsed = getattr(result, "parsed_url", None)
        if not parsed:
            return True
        host = (parsed.hostname or "").lower()
        if host.startswith("www."):
            host = host[4:]
        key = host + parsed.path.rstrip("/")
        # return False => il risultato viene scartato dalla lista
        return not self._blocked(key)
