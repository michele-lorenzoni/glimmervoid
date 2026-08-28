"""Glimmervoid custom plugin: cache server-side dei risultati di ricerca.

Perche' serve
-------------
Ogni ricerca e' uno scraping verso engine che rate-limitano per IP. Ripetere
la stessa query a distanza di ore ripaga il costo (e il rischio di ban) per un
risultato che quasi sempre non e' cambiato. Questo plugin memorizza i risultati
di una ricerca e li riserve senza toccare gli engine, per ``TTL`` secondi
(default 7 giorni).

Come si aggancia
----------------
Sfrutta la coppia di hook upstream:

- ``pre_search()`` che ritorna ``False`` fa saltare l'intero giro di scraping;
- ``post_search()`` viene eseguito **comunque**, anche dopo un ``False``, e la
  lista che ritorna viene passata a ``ResultContainer.extend()``.

Quindi: cache hit -> ``pre_search`` ritorna ``False`` (nessuno scraping) e
``post_search`` inietta i risultati salvati. Cache miss -> lo scraping avviene
normalmente e ``post_search`` decide se valga la pena salvarlo.

I risultati re-iniettati ripassano da ``on_result``, quindi le blocklist
(``blocked_domains``, ``url_prefix_remover``) vengono riapplicate: una entry
vecchia non puo' resuscitare un dominio bloccato nel frattempo.

La guardia contro l'avvelenamento della cache
---------------------------------------------
Il rischio e' salvare una risposta degradata (engine sospesi, zero risultati) e
poi riservirla per giorni, impedendo il retry che avrebbe funzionato.

La guardia **non** puo' essere "salva solo se nessun engine e' fallito": su
un'istanza reale c'e' quasi sempre qualche engine cronicamente rotto
(duckduckgo e startpage, ad esempio, falliscono ad ogni ricerca), quindi
``unresponsive_engines`` non e' mai vuoto e non si salverebbe mai nulla.

La guardia e' invece sul **risultato**: si salva solo se ci sono almeno
``MIN_RESULTS`` risultati. Ne consegue che:

- una risposta degradata non lascia nessuna entry -> la ricerca successiva
  riprova davvero;
- **non esiste negative caching**: uno zero non viene mai memorizzato e non
  puo' bloccare i tentativi successivi.

Ordinamento
-----------
Si salva l'output di ``get_ordered_results()`` (ordine di visualizzazione) con
``positions``/``score`` azzerati su una copia: alla re-iniezione le posizioni
vengono riassegnate 1..N in quell'ordine, ricostruendo il ranking originale.
Chiamare ``get_ordered_results()`` chiude il container in anticipo, per cui
**questo plugin va registrato per ultimo** in ``settings.yml`` (vedi il
commento nel blocco ``plugins:``): un plugin registrato dopo di lui non
riuscirebbe piu' ad aggiungere risultati.

Privacy
-------
Le chiavi sono hash (``ExpireCache.secret_hash``, derivato da
``server.secret_key``): il file su disco non contiene le query in chiaro. I
**valori** sono pickle non cifrati e contengono i risultati, che restano
contenuto pubblico del web; la query originale non viene salvata.

Resta comunque una traccia su disco di cosa e' stato cercato, ed e' il motivo
per cui il plugin e' **inerte se non lo si abilita esplicitamente** con la
variabile d'ambiente ``GLIMMERVOID_RESULT_CACHE``: sull'istanza pubblica non
viene impostata e il plugin non crea nemmeno il database.

Configurazione (tutta via env, nessun rebuild per cambiarla)
------------------------------------------------------------
======================================== =========== =========================
variabile                                default     significato
======================================== =========== =========================
``GLIMMERVOID_RESULT_CACHE``             (assente)   ``1``/``true``/``yes``/
                                                     ``on`` per abilitare
``GLIMMERVOID_RESULT_CACHE_TTL``         ``604800``  durata entry, in secondi
``GLIMMERVOID_RESULT_CACHE_MIN_RESULTS`` ``5``       soglia "risposta sana"
``GLIMMERVOID_RESULT_CACHE_DB``          (vedi sotto) path del file SQLite
======================================== =========== =========================

Il default del database e' ``/var/cache/searxng/result_cache.db``, directory
creata dal ``Dockerfile``. Montarci sopra un volume Docker fa sopravvivere la
cache ai rebuild dell'immagine (senza volume si perde a ogni aggiornamento,
perche' l'auto-update ricrea il container). Se la directory non e' scrivibile
si ricade sul default upstream (``/tmp``), con un warning nei log.
"""

import copy
import logging
import os
import time
import typing as t

from flask import g
from flask_babel import gettext  # pyright: ignore[reportUnknownVariableType]

from searx.cache import ExpireCache, ExpireCacheCfg
from searx.plugins import Plugin, PluginInfo

if t.TYPE_CHECKING:
    from searx.plugins import PluginCfg
    from searx.result_types import Result
    from searx.search import SearchWithPlugins
    from searx.search.models import SearchQuery
    from searx.extended_types import SXNG_Request

log = logging.getLogger("searx.plugins.result_cache")

ENV_ENABLE = "GLIMMERVOID_RESULT_CACHE"
ENV_TTL = "GLIMMERVOID_RESULT_CACHE_TTL"
ENV_MIN_RESULTS = "GLIMMERVOID_RESULT_CACHE_MIN_RESULTS"
ENV_DB = "GLIMMERVOID_RESULT_CACHE_DB"

DEFAULT_TTL = 7 * 24 * 60 * 60
DEFAULT_MIN_RESULTS = 5
DEFAULT_DB = "/var/cache/searxng/result_cache.db"

# Una pagina di risultati pickled sta abbondantemente sotto questo tetto; il
# default upstream (10 KB) invece lo sforerebbe sempre. ExpireCache.set() non
# solleva se il valore e' troppo grande, ritorna False e logga.
MAX_VALUE_LEN = 8 * 1024 * 1024

# Nome del campo su flask.g usato per passare stato fra pre_search, post_search
# e il template (Flask espone `g` a Jinja).
G_FIELD = "glimmervoid_cache"

# Valori accettati come "vero" nelle env var booleane.
_TRUE = {"1", "true", "yes", "on"}


def _env_flag(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in _TRUE


def _env_int(name: str, default: int, minimum: int) -> int:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        value = int(raw)
    except ValueError:
        log.warning("result_cache: %s=%r non e' un intero, uso il default %d", name, raw, default)
        return default
    if value < minimum:
        log.warning("result_cache: %s=%d sotto il minimo %d, uso il minimo", name, value, minimum)
        return minimum
    return value


def _age_label(seconds: int) -> str:
    """Eta' di una entry in forma compatta per la UI ("3h", "2g", "45m")."""
    if seconds < 60:
        return "%ds" % seconds
    if seconds < 3600:
        return "%dm" % (seconds // 60)
    if seconds < 86400:
        return "%dh" % (seconds // 3600)
    return "%dg" % (seconds // 86400)


class SXNGPlugin(Plugin):
    """Serve i risultati da cache quando la stessa query e' gia' stata fatta."""

    id = "result_cache"

    def __init__(self, plg_cfg: "PluginCfg") -> None:
        super().__init__(plg_cfg)

        self.enabled = _env_flag(ENV_ENABLE)
        self.ttl = _env_int(ENV_TTL, DEFAULT_TTL, minimum=60)
        self.min_results = _env_int(ENV_MIN_RESULTS, DEFAULT_MIN_RESULTS, minimum=1)
        self.cache: "ExpireCache | None" = None

        if self.enabled:
            self.cache = self._build_cache()

        if self.cache is None:
            # Disabilitato (o costruzione fallita): gli hook escono subito.
            self.enabled = False
            log.info("result_cache: disattivo (%s non impostata o cache non inizializzabile)", ENV_ENABLE)
        else:
            log.info(
                "result_cache: attivo — ttl=%ds, soglia=%d risultati",
                self.ttl,
                self.min_results,
            )

        self.info = PluginInfo(
            id=self.id,
            name=gettext("Result cache"),
            description=gettext("Serve repeated searches from a local cache instead of querying the engines again"),
            preference_section="general",
        )

    def _build_cache(self) -> "ExpireCache | None":
        db_url = os.environ.get(ENV_DB, "").strip() or DEFAULT_DB
        directory = os.path.dirname(db_url)
        if directory:
            try:
                os.makedirs(directory, exist_ok=True)
                if not os.access(directory, os.W_OK):
                    raise OSError("directory non scrivibile")
            except OSError as exc:
                log.warning(
                    "result_cache: %s non utilizzabile (%s), ricado sul default upstream in /tmp",
                    directory,
                    exc,
                )
                db_url = ""
        try:
            return ExpireCache.build_cache(
                ExpireCacheCfg(
                    name="glimmervoid_results",
                    db_url=db_url,
                    MAX_VALUE_LEN=MAX_VALUE_LEN,
                    MAXHOLD_TIME=self.ttl,
                )
            )
        except Exception:  # pylint: disable=broad-except
            log.exception("result_cache: impossibile inizializzare la cache, resto disattivo")
            return None

    # ------------------------------------------------------------------ chiave

    def _cache_key(self, search_query: "SearchQuery") -> str:
        """Chiave hashata che identifica la ricerca.

        Deve includere tutto cio' che cambia i risultati: query, engine
        selezionati, lingua, safesearch, pagina, time range, bang esterno. Se
        si dimenticasse la selezione di engine, un utente con preferenze
        diverse riceverebbe i risultati di qualcun altro.
        """
        engines = sorted(
            "%s|%s" % (getattr(ref, "category", ""), getattr(ref, "name", ""))
            for ref in (search_query.engineref_list or [])
        )
        raw = "\x1f".join(
            [
                " ".join((search_query.query or "").split()).lower(),
                ",".join(engines),
                search_query.lang or "",
                str(search_query.safesearch),
                str(search_query.pageno),
                search_query.time_range or "",
                search_query.external_bang or "",
            ]
        )
        assert self.cache is not None
        return self.cache.secret_hash(raw)

    @staticmethod
    def _force_refresh(request: "SXNG_Request") -> bool:
        """``no_cache=1`` da form (POST) o query string (GET): salta la lettura."""
        for source in (request.form, request.args):
            value = source.get("no_cache")
            if value and value.strip().lower() in _TRUE:
                return True
        return False

    # ------------------------------------------------------------------- hooks

    def pre_search(self, request: "SXNG_Request", search: "SearchWithPlugins") -> bool:
        if not self.enabled or self.cache is None:
            return True

        state: "dict[str, t.Any]" = {"state": "miss", "key": None, "age_label": None, "stored": False}
        setattr(g, G_FIELD, state)

        try:
            key = self._cache_key(search.search_query)
        except Exception:  # pylint: disable=broad-except
            log.exception("result_cache: costruzione della chiave fallita, procedo senza cache")
            return True
        state["key"] = key

        if self._force_refresh(request):
            # Bypass in lettura, ma la entry verra' comunque riscritta in
            # post_search: "rescan" deve aggiornare la cache, non ignorarla.
            state["state"] = "bypass"
            return True

        try:
            entry = self.cache.get(key)
        except Exception:  # pylint: disable=broad-except
            log.exception("result_cache: lettura fallita, procedo con lo scraping")
            return True

        if not isinstance(entry, dict) or not entry.get("results"):
            return True

        age = max(0, int(time.time()) - int(entry.get("ts", 0)))
        state["state"] = "hit"
        state["age_label"] = _age_label(age)
        state["entry"] = entry
        log.info("result_cache: HIT — %d risultati, eta' %ds", len(entry["results"]), age)
        # False = niente scraping. post_search viene eseguito comunque.
        return False

    def post_search(
        self, request: "SXNG_Request", search: "SearchWithPlugins"
    ) -> "None | list[Result]":
        state = getattr(g, G_FIELD, None)
        if not state or self.cache is None:
            return None

        entry = state.pop("entry", None)
        if entry is not None:
            # Cache hit: i risultati salvati diventano quelli della ricerca.
            return list(entry["results"])

        key = state.get("key")
        if not key:
            return None

        container = getattr(search, "result_container", None)
        if container is None:
            return None

        try:
            results = container.get_ordered_results()
        except Exception:  # pylint: disable=broad-except
            log.exception("result_cache: lettura dei risultati fallita, non salvo nulla")
            return None

        if len(results) < self.min_results:
            # La guardia: una risposta degradata non lascia traccia, cosi' la
            # ricerca successiva riprova invece di riservire la spazzatura.
            log.info(
                "result_cache: %d risultati < soglia %d — NON salvo (la prossima ricerca riprovera')",
                len(results),
                self.min_results,
            )
            return None

        payload = {
            "v": 1,
            "ts": int(time.time()),
            "n": len(results),
            "engines": sorted({r.engine for r in results if getattr(r, "engine", None)}),
            "results": self._freeze(results),
        }
        try:
            stored = self.cache.set(key, payload, expire=self.ttl)
        except Exception:  # pylint: disable=broad-except
            log.exception("result_cache: scrittura fallita")
            return None

        state["stored"] = bool(stored)
        if stored:
            log.info("result_cache: salvati %d risultati (ttl %ds)", len(results), self.ttl)
        else:
            log.warning("result_cache: scrittura rifiutata (valore troppo grande?)")
        return None

    @staticmethod
    def _freeze(results: "list[t.Any]") -> "list[t.Any]":
        """Copia dei risultati pronta per la cache.

        Si lavora su una deepcopy perche' gli originali stanno per essere
        renderizzati e non vanno toccati. ``positions``/``score`` vengono
        azzerati: alla re-iniezione ``_merge_main_result`` riassegna le
        posizioni 1..N nell'ordine salvato, ricostruendo il ranking.
        """
        frozen = copy.deepcopy(results)
        for item in frozen:
            try:
                item.positions = []
                item.score = 0
            except Exception:  # pylint: disable=broad-except
                # LegacyResult e' un dict-like: se non ha questi campi pazienza,
                # l'ordine viene comunque dalla sequenza salvata.
                pass
        return frozen
