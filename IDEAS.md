# Glimmervoid — idee e possibili migliorie

Scratchpad personale per cose da valutare/sperimentare. Non è una roadmap, non è un committment: ogni voce va validata prima di partire. Quando una voce viene completata, si rimuove (la storia vive nei commit).

## IP ban / blocchi sui motori

> Stato attuale: la build-arg `OUTGOING_PROXIES` è dichiarata e funzionante ma **intenzionalmente vuota** sull'env di Render — non c'è un servizio di proxy attivo. Il meccanismo è dormiente, non rotto.

- **Passare da `outgoing.proxies` globale a `outgoing.networks` per-engine.** Definire un network "proxied" e assegnarlo solo ai motori che bannano (Google, Bing, ecc.); gli altri (DuckDuckGo, Wikipedia, …) restano diretti. Riduce costo proxy e latenza media. Richiede modifica `settings.yml.template` + piccolo refactor della build-arg nel `Dockerfile`. Va fatto **insieme** alla scelta di un servizio proxy concreto, altrimenti è prematuro.
- **Tor su un network dedicato** (`using_tor_proxy: true`) per engine secondari. Sconsigliato per Google/Bing: gli exit node Tor sono quasi sempre già in blocklist, quindi "Tor on" spesso peggiora invece di migliorare. Sensato solo per engine minori.
- **Toggle Tor da UI senza redeploy.** SearXNG legge `settings.yml` solo all'avvio: un vero toggle a livello di config richiede restart container. Tre strade per ottenere comunque l'effetto "bottone":
  1. *Doppio engine* — dichiarare ogni motore due volte (`google` + `google-tor`, ecc.) con `network: default` vs `network: tor`. L'utente li attiva/disattiva dalla pagina **preferences** già esistente. Zero codice, ma toggle per-engine, non un singolo bottone. Persistito via cookie.
  2. *Plugin custom SearXNG* — `searx.plugins.*` che intercetta la preparazione richiesta e inietta `params['proxies']` leggendo un cookie/preference custom (`tor_enabled=1`). Permette un singolo bottone "Tor: ON/OFF". ~50 righe Python + template tweak. Redeploy solo all'installazione.
  3. *Bang syntax* — combinato con (1): scrivere `!gtor query` per forzare Tor solo su quella ricerca. Zero-effort ma non è un bottone.
  
  Prerequisito comune a tutte: serve un demone **Tor in ascolto** raggiungibile da SearXNG (default SOCKS5 `127.0.0.1:9050`). Su Render = un container un processo, quindi va aggiunto al `Dockerfile` (installare `tor`, lanciarlo via supervisord/entrypoint script), oppure tenuto in un service Render separato, oppure su un VPS esterno.
- **Proxy residenziali a rotazione** (Bright Data, Smartproxy, IPRoyal). Si infilano nel meccanismo `OUTGOING_PROXIES` esistente. Costo ricorrente, ma è la soluzione "che funziona sempre".
- **Cambiare hosting.** Gli IP di Render sono cloud noti e finiscono in blocklist. Un VPS Hetzner / OVH o un home-server con DDNS può bastare senza proxy aggiuntivi. Più lavoro operativo, zero costi proxy.
- **Engine via API** dove disponibile (Google CSE, SerpAPI, Bing API, …). Le API non hanno IP-ban ma hanno quote/costi.

## Engine custom

- I precedenti `brave_api.py` e `commoncrawl.py` sono stati rimossi perché non funzionavano. Reintrodurre solo se c'è una ragione concreta e una versione che funziona davvero.

## Tuning outgoing

- Rivalutare i parametri in `settings.yml.template` `outgoing:` (linee ~185-200): `request_timeout`, `pool_connections`, `pool_maxsize`, `useragent_suffix`, `enable_http2`. I default attuali sono ragionevoli ma vanno tarati se cambia hosting o si introducono proxy lenti.

## UI / UX

_(vuoto)_

## Static / build

_(vuoto)_
