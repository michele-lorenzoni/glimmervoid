# Glimmervoid

**English** | [Italiano](README.it.md)

Customized [SearXNG](https://github.com/searxng/searxng) fork with a terminal-style UI: monospace (Iosevka), neon palette, keyboard-driven results, dynamic per-page identicon favicon, badge overlay for favorite/visited/unwanted/ignored URLs.

The Python/Flask core comes from the upstream `searxng/searxng:latest` Docker image — **this repo only ships overrides** (Jinja templates, custom JS, compiled Tailwind CSS, `settings.yml.template`, blocked-domains list).

## Repo layout

```
glimmervoid/
├── Dockerfile                   # builds on searxng/searxng:latest, injects overrides
├── settings.yml.template        # instance config w/ {{BLOCKED_DOMAINS}} + {{OUTGOING_PROXIES}}
├── blocked_domains.txt          # auto-sorted, injected at build time
├── package.json                 # Tailwind v4.1 CLI (no tailwind.config.js)
├── requirements.txt             # pre-commit tooling (djlint, jsbeautifier, …)
├── scripts/                     # sort_json.py, sort_txt.py, extract_palette.py
└── searx/templates/
    ├── simple/                  # Jinja overrides (base, index, results, preferences, …)
    └── static/
        ├── custom/              # active_article.js, dynamic_favicon.js, urls_manager.js, *_urls.json
        └── themes/simple/       # input.css, compiled output.css, fonts, favicon
```

Detailed map in [`PROJECT_MAP.md`](PROJECT_MAP.md).

## Local dev

Pre-commit tooling lives in a Python venv; everything else is Node + Docker.

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

Pre-commit hooks auto-sort `blocked_domains.txt` and every `*.json` under `searx/templates/static/custom/`.

### Tailwind build

No npm script shortcut — run the CLI manually after editing `input.css`:

```bash
cd searx/templates/static/themes/simple
npx @tailwindcss/cli -i input.css -o output.css
```

`output.css` is committed and copied into the Docker image.

### Local Docker run

```bash
docker build -t glimmervoid .
docker run --rm -p 8080:8080 glimmervoid
```

Visit `http://localhost:8080`. Optional outgoing proxies:

```bash
docker build --build-arg OUTGOING_PROXIES="socks5://host:1080,http://host:3128" -t glimmervoid .
```

## Deployment

Deployed on [Render](https://render.com/). There is **no `render.yaml`** in the repo: service config (env vars, build settings) lives entirely in the Render dashboard.

- Dockerfile build-args (e.g. `OUTGOING_PROXIES`) are injected from the service's **Environment Variables**.
- `settings.yml` is generated at **build time** inside the image; changes to `settings.yml.template` or `blocked_domains.txt` require a rebuild, not just a container restart.
- Pushing to `main` triggers an automatic rebuild + redeploy on Render.

## Conventions

- **Border-radius is always `2px`** on squared elements (buttons, inputs, cards, chips, tooltips, dialogs); circles via `border-radius: 50%` are allowed. No `0`, no `999px` on non-square shapes, no intermediate radii.
- Commit subjects follow `feat:` / `fix:` / `update:` / `polish:`. Italian body text is fine.
- No `Co-Authored-By: Claude …` trailer on commits.

See [`CLAUDE.md`](CLAUDE.md) for full project conventions, [`STYLE_GUIDE.md`](STYLE_GUIDE.md) for the visual language, and [`IDEAS.md`](IDEAS.md) for non-committed design notes and tradeoffs.
