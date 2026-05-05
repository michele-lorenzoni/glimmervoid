# Glimmervoid — idee e possibili migliorie

Scratchpad personale per cose da valutare/sperimentare. Non è una roadmap, non è un committment: ogni voce va validata prima di partire. Quando una voce viene completata, si rimuove (la storia vive nei commit).

## IP ban / blocchi sui motori

- **Capire perché `OUTGOING_PROXIES` non viene usata.** Possibili cause: variabile vuota su Render, proxy non raggiungibili, sintassi del valore non valida. Step zero prima di toccare il meccanismo.
- **Passare da `outgoing.proxies` globale a `outgoing.networks` per-engine.** Definire un network "proxied" e assegnarlo solo ai motori che bannano (Google, Bing, ecc.); gli altri (DuckDuckGo, Wikipedia, …) restano diretti. Riduce costo proxy e latenza media. Richiede modifica `settings.yml.template` + piccolo refactor della build-arg nel `Dockerfile`.
- **Tor su un network dedicato** (`using_tor_proxy: true`) per engine secondari. Sconsigliato per Google: gli exit node Tor sono quasi sempre già in blocklist.
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
