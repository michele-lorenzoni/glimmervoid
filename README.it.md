# Glimmervoid

[English](README.md) | **Italiano**

Fork personalizzato di [SearXNG](https://github.com/searxng/searxng) con UI in stile terminale: monospace (Iosevka), palette neon, navigazione risultati da tastiera, favicon identicon dinamico per pagina, badge overlay per URL preferiti/visitati/indesiderati/ignorati.

Il core Python/Flask arriva dall'immagine Docker upstream `searxng/searxng:latest` — **questo repo contiene solo override** (template Jinja, JS custom, CSS Tailwind compilato, `settings.yml.template`, lista domini bloccati).

## Struttura del repo

```
glimmervoid/
├── Dockerfile                   # build su searxng/searxng:latest, inietta gli override
├── settings.yml.template        # config istanza con {{BLOCKED_DOMAINS}} + {{OUTGOING_PROXIES}}
├── blocked_domains.txt          # auto-ordinato, iniettato a build time
├── package.json                 # Tailwind v4.1 CLI (nessun tailwind.config.js)
├── requirements.txt             # tooling pre-commit (djlint, jsbeautifier, …)
├── scripts/                     # sort_json.py, sort_txt.py, extract_palette.py
└── searx/templates/
    ├── simple/                  # override Jinja (base, index, results, preferences, …)
    └── static/
        ├── custom/              # active_article.js, dynamic_favicon.js, urls_manager.js, *_urls.json
        └── themes/simple/       # input.css, output.css compilato, font, favicon
```

Mappa dettagliata in [`PROJECT_MAP.md`](PROJECT_MAP.md).

## Sviluppo locale

Il tooling pre-commit vive in un venv Python; tutto il resto è Node + Docker.

```powershell
# Windows / PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
pre-commit install
```

```bash
# Linux / macOS
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pre-commit install
```

Gli hook di pre-commit ordinano automaticamente `blocked_domains.txt` e ogni `*.json` sotto `searx/templates/static/custom/`.

### Build di Tailwind

Nessuno script npm di shortcut — esegui la CLI manualmente dopo aver modificato `input.css`:

```bash
cd searx/templates/static/themes/simple
npx @tailwindcss/cli -i input.css -o output.css
```

`output.css` è committato e copiato dentro l'immagine Docker.

### Esecuzione locale con Docker

```bash
docker build -t glimmervoid .
docker run --rm -p 8080:8080 glimmervoid
```

Apri `http://localhost:8080`. Proxy uscenti opzionali:

```bash
docker build --build-arg OUTGOING_PROXIES="socks5://host:1080,http://host:3128" -t glimmervoid .
```

## Deploy

Deployato su [Render](https://render.com/). **Non c'è alcun `render.yaml`** nel repo: la config del servizio (env vars, build settings) vive interamente nel dashboard Render.

- I build-arg del Dockerfile (es. `OUTGOING_PROXIES`) sono iniettati dalle **Environment Variables** del servizio.
- `settings.yml` è generato a **build time** dentro l'immagine; modifiche a `settings.yml.template` o `blocked_domains.txt` richiedono una rebuild, non solo un restart del container.
- Push su `main` triggera rebuild + redeploy automatici su Render.

## Convenzioni

- **Il `border-radius` è sempre `2px`** sugli elementi squadrati (bottoni, input, card, chip, tooltip, dialog); i cerchi via `border-radius: 50%` sono ammessi. No `0`, no `999px` su forme non quadrate, no valori intermedi.
- Subject dei commit con prefisso `feat:` / `fix:` / `update:` / `polish:`. Body in italiano è ok.
- Nessun trailer `Co-Authored-By: Claude …` nei commit.

Vedi [`CLAUDE.md`](CLAUDE.md) per le convenzioni complete del progetto, [`STYLE_GUIDE.md`](STYLE_GUIDE.md) per il linguaggio visuale, e [`IDEAS.md`](IDEAS.md) per note di design e tradeoff non ancora implementati.
