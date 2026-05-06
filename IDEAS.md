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
  - Hetzner Cost Optimized — listino verificato (excl. VAT):

    | Plan | CPU | RAM | SSD | €/mese |
    |---|---|---|---|---|
    | **CX23** | 2× Intel/AMD | 4 GB | 40 GB | **€4.49** |
    | CAX11 | 2× ARM Ampere | 4 GB | 40 GB | €4.99 |
    | CX33 | 4× Intel/AMD | 8 GB | 80 GB | €6.99 |
    | CAX21 | 4× ARM | 8 GB | 80 GB | €8.49 |

    **Raccomandazione: CX23** (€4.49 excl. VAT, ~€5.48 IT con IVA 22%, + ~€0.50/mo IPv4 dedicato). Stesse specifiche di CAX11 ma €0.50 meno e x86 (zero rischio di edge case con tooling). Per SOCKS5 servono <100 MB RAM e CPU trascurabile, quindi è ampiamente sovradimensionato. Datacenter EU (Falkenstein/Norimberga/Helsinki).
  - **Caveat blocklist**: gli IP cloud Hetzner sono comunque marchiati come "datacenter" e potrebbero essere già bannati dagli stessi engine che bannano Render — meno aggressivamente, ma non risolto a priori. Test obbligatorio prima di impegnarsi: `curl --socks5 ...` verso l'engine target dal VPS appena montato. Se anche Hetzner viene rifiutato, l'unica via è static residential / ISP proxies (vedi voce successiva) o IP residenziale proprio (self-hosting).
- **Static residential / ISP proxies flat-rate** (es. Webshare): N IP residenziali fissi a costo fisso anziché a GB. Più IP del singolo VPS, niente sorprese in bolletta. Buon compromesso se il VPS singolo viene bannato troppo spesso.
- **Self-hosting su IP residenziale.** Mini-server a casa via DDNS: banda dell'abbonamento internet, IP residenziale "buono" agli occhi degli engine. Operativamente più lavoro (uptime, NAT, dynamic DNS) ma zero costi ricorrenti.
- **Migrare l'intera istanza fuori da Render.** Gli IP di Render sono cloud noti e finiscono in blocklist. Un VPS o un home-server può ospitare direttamente SearXNG **senza nessun proxy aggiuntivo**, a patto che l'IP non sia già contaminato. Più lavoro operativo, zero costi proxy.
- **Proxy residenziali pay-per-GB** (Bright Data, Smartproxy, IPRoyal): tenuti come opzione di emergenza per volumi bassissimi o test puntuali. **Non sostenibili** per uso continuo a questi volumi.
- **Engine via API** dove disponibile (Google CSE, SerpAPI, Bing API, …). Le API non hanno IP-ban ma hanno quote/costi.

## Engine custom

- I precedenti `brave_api.py` e `commoncrawl.py` sono stati rimossi perché non funzionavano. Reintrodurre solo se c'è una ragione concreta e una versione che funziona davvero.

## Architettura ricerca: allowlist + cache + API a pagamento

Cambio di paradigma rispetto al meta-search "su tutto il web": restringere la ricerca a una lista curata di domini affidabili. Risolve l'IP-ban *by design* (l'API a pagamento non banna per IP) e abbatte i costi tramite cache.

**Componenti:**

1. **Engine custom SearXNG** che chiama un'API di ricerca:
   - 🧠 Google Programmable Search Engine (CSE) — nasce per restringere a un set di domini, configurato server-side via dashboard Google. ~$5/1000 query oltre il free tier 100/giorno.
   - 🧠 Brave Search API — supporta operator `site:`, $3–9/1000 query.
   - *Prezzi da verificare al momento della scelta.*
2. **`allowed_domains.txt`** — gestito col pattern già consolidato di `blocked_domains.txt`: file di testo iniettato a build-time dal `Dockerfile` in `settings.yml` (o letto direttamente dall'engine custom).
3. **Cache aggressiva** delle response API:
   - Chiave: `(query_normalizzata, lingua, page)`.
   - TTL configurabile (es. default 7 giorni per evergreen, 1 giorno per query con keyword "news/oggi/ora").
   - Cache hit = zero spesa API.
4. **Pulsante "force refresh"** in UI sulla results page per saltare la cache su richiesta esplicita.

**Pro:**
- Risolve IP-ban *by design*.
- Costi API contenuti grazie alla cache.
- Risultati più puliti: niente junk SEO.

**Tradeoff onesti:**
- **Perdita di serendipità**: SearXNG nasce per scoprire fuori dai sentieri noti; l'allowlist taglia questa feature alla radice. Scelta filosofica, non solo tecnica.
- Manutenzione `allowed_domains.txt`: deve crescere col tempo o ricerche rare tornano vuote.
- Cache invalidation non banale: TTL lunghi → risultati obsoleti; troppo corti → cache inutile.
- 📂 Storage cache: il container Render ha disco effimero. Servono Redis (Render add-on) o volume persistente — costo o config aggiuntiva.

**Vincolo verificato:**
- 🌐 Il SearXNG `Hostnames` plugin **non** supporta nativamente una mode `keep_only`/allowlist ([dev/plugins/hostnames.html](https://docs.searxng.org/dev/plugins/hostnames.html)): solo `replace`, `remove`, `high_priority`, `low_priority`. Quindi l'allowlist richiede engine custom o filtro lato API (es. CSE configurato già allowlist-only nella dashboard Google).

**Sequenza di rollout consigliata:**
1. Decidere fra Google CSE (allowlist server-side, più qualità) e Brave API (operator `site:`, più semplice da prototipare).
2. PoC dell'engine custom con cache **in-memory** (dict) per validare flusso end-to-end.
3. Solo se PoC funziona: aggiungere persistenza cache (Redis su Render) e pulsante force-refresh in template.
4. Promuovere a engine "primario" solo se la qualità dei risultati è soddisfacente — altrimenti tenere come engine accessorio attivabile via cookie.

## Tuning outgoing

- Rivalutare i parametri in `settings.yml.template` `outgoing:` (linee ~185-200): `request_timeout`, `pool_connections`, `pool_maxsize`, `useragent_suffix`, `enable_http2`. I default attuali sono ragionevoli ma vanno tarati se cambia hosting o si introducono proxy lenti.

## UI / UX

_(vuoto)_

## Static / build

_(vuoto)_
