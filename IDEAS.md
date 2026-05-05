# Glimmervoid — idee e possibili migliorie

Scratchpad personale per cose da valutare/sperimentare. Non è una roadmap, non è un committment: ogni voce va validata prima di partire. Quando una voce viene completata, si rimuove (la storia vive nei commit).

## IP ban / blocchi sui motori

> Stato attuale: la build-arg `OUTGOING_PROXIES` è dichiarata e funzionante ma **intenzionalmente vuota** sull'env di Render — non c'è un servizio di proxy attivo. Il meccanismo è dormiente, non rotto.

- **Spostare il proxy da `outgoing:` globale a per-engine.** SearXNG supporta nativamente le keys `proxies`, `using_tor_proxy`, `enable_http2`, `timeout`, ecc. *direttamente sull'entry dell'engine* in `settings.yml` (override di `outgoing:`). Inoltre la key `network: <nome-engine>` permette a un engine di **ereditare** la configurazione di un altro: utile per non duplicare il blocco proxy. Pattern: settare `proxies: …` su Google/Bing/altri ban-sensible e lasciare gli altri diretti, oppure configurare un engine "carrier" e usare `network:` su quelli che devono condividere lo stesso proxy. Ref: [settings_engines.html](https://docs.searxng.org/admin/settings/settings_engines.html). Va fatto **insieme** alla scelta di un servizio proxy concreto, altrimenti è prematuro.
- **Tor su un network dedicato** (`using_tor_proxy: true`) per engine secondari. Sconsigliato per Google/Bing: gli exit node Tor sono quasi sempre già in blocklist, quindi "Tor on" spesso peggiora invece di migliorare. Sensato solo per engine minori.
- **Toggle Tor da UI senza redeploy.** SearXNG legge `settings.yml` solo all'avvio: un vero toggle a livello di config richiede restart container. Tre strade per ottenere comunque l'effetto "bottone":
  1. *Doppio engine* — dichiarare ogni motore due volte (`google` + `google-tor`, ecc.) con `network: default` vs `network: tor`. L'utente li attiva/disattiva dalla pagina **preferences** già esistente. Zero codice, ma toggle per-engine, non un singolo bottone. Persistito via cookie.
  2. *Plugin custom SearXNG* — `searx.plugins.*` che intercetta la preparazione richiesta e inietta `params['proxies']` leggendo un cookie/preference custom (`tor_enabled=1`). Permette un singolo bottone "Tor: ON/OFF". ~50 righe Python + template tweak. Redeploy solo all'installazione.
  3. *Bang syntax* — combinato con (1): scrivere `!gtor query` per forzare Tor solo su quella ricerca. Zero-effort ma non è un bottone.
  
  Prerequisito comune a tutte: serve un demone **Tor in ascolto** raggiungibile da SearXNG (default SOCKS5 `127.0.0.1:9050`). Su Render = un container un processo, quindi va aggiunto al `Dockerfile` (installare `tor`, lanciarlo via supervisord/entrypoint script), oppure tenuto in un service Render separato, oppure su un VPS esterno.
- **Volume atteso e modello tariffario.** Una ricerca SearXNG ban-routed = ~1–3 MB (3–5 engine ban-sensible × 200–700 KB di response, di più per verticali immagini/video). Uso moderato (~150 ricerche/giorno) → 6–15 GB/mese; uso intenso → ≥30 GB/mese. Conseguenza: il **pay-per-GB è la scelta sbagliata** a questi volumi (Bright Data ~€8/GB → €240+/mese in scenario heavy; anche IPRoyal ~$2/GB pesa). La banda **deve** essere flat-rate. *Stime e prezzi indicativi, da verificare al momento della scelta.*
- **VPS come SOCKS5 (raccomandato per uso personale).** VPS economico (Hetzner / Contabo / OVH-Kimsufi sui €4–5/mese) con banda inclusa generosa, configurato come proxy SOCKS5 (`dante`, `3proxy`, tunnel SSH). Costo fisso prevedibile, banda non un problema. Limite: un solo IP — quando viene bannato si cambia server. Si combina col pattern per-engine sopra (`proxies:` solo su Google/Bing/etc.) per ridurre l'esposizione del singolo IP.
- **Static residential / ISP proxies flat-rate** (es. Webshare): N IP residenziali fissi a costo fisso anziché a GB. Più IP del singolo VPS, niente sorprese in bolletta. Buon compromesso se il VPS singolo viene bannato troppo spesso.
- **Self-hosting su IP residenziale.** Mini-server a casa via DDNS: banda dell'abbonamento internet, IP residenziale "buono" agli occhi degli engine. Operativamente più lavoro (uptime, NAT, dynamic DNS) ma zero costi ricorrenti.
- **Migrare l'intera istanza fuori da Render.** Gli IP di Render sono cloud noti e finiscono in blocklist. Un VPS o un home-server può ospitare direttamente SearXNG **senza nessun proxy aggiuntivo**, a patto che l'IP non sia già contaminato. Più lavoro operativo, zero costi proxy.
- **Proxy residenziali pay-per-GB** (Bright Data, Smartproxy, IPRoyal): tenuti come opzione di emergenza per volumi bassissimi o test puntuali. **Non sostenibili** per uso continuo a questi volumi.
- **Engine via API** dove disponibile (Google CSE, SerpAPI, Bing API, …). Le API non hanno IP-ban ma hanno quote/costi.

## Engine custom

- I precedenti `brave_api.py` e `commoncrawl.py` sono stati rimossi perché non funzionavano. Reintrodurre solo se c'è una ragione concreta e una versione che funziona davvero.

## Tuning outgoing

- Rivalutare i parametri in `settings.yml.template` `outgoing:` (linee ~185-200): `request_timeout`, `pool_connections`, `pool_maxsize`, `useragent_suffix`, `enable_http2`. I default attuali sono ragionevoli ma vanno tarati se cambia hosting o si introducono proxy lenti.

## UI / UX

_(vuoto)_

## Static / build

_(vuoto)_
