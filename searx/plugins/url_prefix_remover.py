"""Glimmervoid custom plugin: nasconde i risultati il cui URL inizia con un
*prefisso-URL* bloccato (host + path, opzionalmente + vincoli sulla query).

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

Vincoli sulla query string
--------------------------
Alcuni siti non mettono la lingua nel path ma in un parametro di query. Per
questi, la riga della lista puo' portarsi dietro una query string; in quel caso
il risultato viene scartato solo se **tutti** i parametri indicati sono
presenti nel suo URL (i parametri in piu' sul risultato sono ammessi)::

    support.google.com/youtube/answer/7174035?hl=ru   -> solo la variante russa
    support.google.com/youtube/answer/7174035         -> la pagina in ogni lingua
    support.google.com/youtube/answer/7174035?hl      -> solo se "hl" e' presente,
                                                        con qualunque valore

Piu' parametri si combinano in AND (``?hl=ru&foo=bar``). Se il risultato ripete
lo stesso parametro (``?hl=ru&hl=en``) basta che uno dei valori combaci.

Nomi e valori dei parametri sono confrontati **case-sensitive**, esattamente
come il path (in lista convivono infatti sia ``support.microsoft.com/fr-FR/``
sia ``support.microsoft.com/fr-fr/``): per coprire piu' grafie servono piu'
righe. Le sequenze percent-encoded e i ``+`` vengono decodificati da entrambi i
lati prima del confronto.

La lista viene letta una volta all'avvio (come i ``blocked_domains``, che sono
iniettati a build-time): per aggiornarla serve un rebuild dell'immagine.
"""

import logging
import os
import typing as t
from urllib.parse import parse_qs, parse_qsl, unquote_plus, urlparse

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

# Vincolo su un parametro di query: (nome, valore) con valore ``None`` = "il
# parametro deve esserci, qualunque sia il suo valore".
_Constraint = t.Tuple[str, t.Optional[str]]
# Voce caricata dalla lista: chiave host+path + vincoli di query (vuoti = nessuno).
_Prefix = t.Tuple[str, t.Tuple[_Constraint, ...]]


def _parse_constraints(raw_query: str) -> "tuple[_Constraint, ...]":
    """Vincoli ``(nome, valore)`` estratti dalla query di una riga della lista.

    ``hl=ru`` -> il parametro deve valere ``ru``; ``hl`` (senza ``=``) -> deve
    solo essere presente. Il decoding percent/``+`` e' delegato a
    :py:func:`urllib.parse.parse_qsl`, cosi' i due lati del confronto sono
    normalizzati allo stesso modo.
    """
    constraints: "list[_Constraint]" = []
    for part in raw_query.split("&"):
        part = part.strip()
        if not part:
            continue
        if "=" in part:
            # keep_blank_values: "?hl=" e' un vincolo legittimo (valore vuoto).
            constraints.extend(parse_qsl(part, keep_blank_values=True))
        else:
            constraints.append((unquote_plus(part), None))
    return tuple(constraints)


def _normalize(raw: str) -> "_Prefix | None":
    """Voce di lista -> chiave ``host+path`` (scheme/www-insensitive, senza slash
    finale) piu' i vincoli di query. ``None`` se la riga non e' utilizzabile."""
    raw = raw.strip()
    if not raw:
        return None
    # consenti voci senza scheme (es. "nvidia.com/pl-pl/")
    parsed = urlparse(raw if "//" in raw else "//" + raw)
    host = (parsed.hostname or "").lower()
    if host.startswith("www."):
        host = host[4:]
    if not host:
        # senza host il prefisso non puo' matchare nulla: meglio segnalarlo che
        # caricarlo silenziosamente.
        return None
    return host + parsed.path.rstrip("/"), _parse_constraints(parsed.query)


def _load_prefixes(path: str) -> "list[_Prefix]":
    prefixes: "list[_Prefix]" = []
    try:
        with open(path, "r", encoding="utf-8") as fh:
            for lineno, line in enumerate(fh, 1):
                line = line.split("#", 1)[0].strip()
                if not line:
                    continue
                entry = _normalize(line)
                if entry is None:
                    log.warning("url_prefix_remover: riga %d ignorata (host mancante): %r", lineno, line)
                    continue
                prefixes.append(entry)
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
        log.info(
            "url_prefix_remover: %d prefissi caricati da %s (%d con vincoli di query)",
            len(self.prefixes),
            list_path,
            sum(1 for _, constraints in self.prefixes if constraints),
        )
        self.info = PluginInfo(
            id=self.id,
            name=gettext("URL prefix remover"),
            description=gettext("Remove results whose URL starts with a blocked URL prefix"),
            preference_section="general",
        )

    @staticmethod
    def _params_match(params: "dict[str, list[str]]", constraints: "tuple[_Constraint, ...]") -> bool:
        for name, value in constraints:
            values = params.get(name)
            if values is None:
                return False
            if value is not None and value not in values:
                return False
        return True

    def _blocked(self, key: str, raw_query: str) -> bool:
        # La query del risultato viene parsata pigramente: le voci senza vincoli
        # (la stragrande maggioranza) non pagano nulla.
        params: "dict[str, list[str]] | None" = None
        for pfx, constraints in self.prefixes:
            # confine di path: match esatto sul prefisso o discendenti sotto "/"
            if key != pfx and not key.startswith(pfx + "/"):
                continue
            if not constraints:
                return True
            if params is None:
                params = parse_qs(raw_query, keep_blank_values=True)
            if self._params_match(params, constraints):
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
        return not self._blocked(key, parsed.query or "")
