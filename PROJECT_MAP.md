# Glimmervoid — project map

Customized SearXNG fork with terminal-style UI. Python/Flask app comes from the upstream `searxng/searxng:latest` Docker image — **this repo contains only overrides** (templates, static assets, a couple of engines, config).

## Top-level layout

```
glimmervoid/
├── CLAUDE.md                    # conventions (radius 2px, no Claude co-author)
├── Dockerfile                   # builds on searxng/searxng:latest, injects overrides
├── package.json                 # Tailwind v4.1 (CLI, no tailwind.config.js)
├── requirements.txt             # pre-commit tooling only (djlint, jsbeautifier, …)
├── settings.yml.template        # instance config w/ {{BLOCKED_DOMAINS}} placeholder
├── blocked_domains.txt          # auto-sorted, injected into settings.yml on build
├── scripts/                     # sort_json.py, sort_txt.py, extract_palette.py
├── showcase/                    # screenshots (index/results, desktop/mobile)
└── searx/
    ├── engines/                 # custom engines only
    │   ├── brave_api.py
    │   └── commoncrawl.py
    └── templates/
        ├── simple/              # Jinja2 templates (override upstream)
        └── static/
            ├── custom/          # project-specific JS + JSON data
            └── themes/simple/   # compiled CSS, fonts, favicon
```

## Entry points

- **Not run directly here.** Built via `Dockerfile` on top of `searxng/searxng:latest`. Dockerfile stages:
  1. Format `blocked_domains.txt` → YAML list and inject into `/etc/searxng/settings.yml` via `{{BLOCKED_DOMAINS}}` placeholder.
  2. Copy `searx/templates/simple/*` → upstream template dir.
  3. Copy `searx/templates/static/{custom,themes/simple}` → upstream static dir.
  4. Copy `searx/engines/*.py` → upstream engines dir.
- Exposes port 8080.

## Templates (`searx/templates/simple/`)

Main files:

| File | Role |
|---|---|
| `base.html` | Shell: `<head>`, nav top bar (`prefs`, `donate`, `home`), favicon links, loads `active_article.js` + `dynamic_favicon.js`, block `stylesheets` attorno a `output.css`. Meta `favicon-seed` (block `favicon_seed`, default = `endpoint`). **Unico punto in cui vive la nav.** |
| `page_with_header.html` | Wrapper per la preferences page: estende `base.html`, aggiunge `preferences.css` via block `stylesheets`. |
| `index.html` | Homepage: blinking terminal caret + shortcuts grid. |
| `results.html` | Results page (`terminal-results` wrapper, counters via CSS `::before`). Override `favicon_seed` = `q or endpoint`. |
| `search.html`, `simple_search.html`, `_search_bar.html` | Search form + terminal-prompt macro. |
| `preferences.html` + `preferences/` | Preferences UI (estende `page_with_header.html`). |
| `macros.html` | `result_header` macro — favicon resolver for result domains (lines 22–29). |
| `icons.html`, `_icons/` | Icon macro + 10 custom SVG icons (claude, codeberg, fish, github, hackthebox, …). |
| `result_templates/`, `categories.html`, `messages/` | Upstream partials. |

### Terminal CSS system
- `.term-font` (Iosevka mono), `.term-accent` (green #7aff8f), `.term-dim`, `.term-prompt` (`>`), `.term-search`, `.term-nav-link`, `.term-meta`.
- Results numbered via `#urls article.result::before` counter.
- Italian comments in templates/CSS (e.g. "Struttura upstream: #urls > div > article.result").

## Static assets

### `searx/templates/static/custom/` — project-specific
| File | Purpose |
|---|---|
| `active_article.js` | Keyboard nav for results: arrows / `j` / `k` / Enter. Adds `border-sky-800` on active result. |
| `dynamic_favicon.js` | Legge `<meta name="favicon-seed">` e genera identicon 5×5 mirrored (FNV-1a → xorshift32). Colore pescato dal seed tra `--color-neon-{green,cyan,pink,blue}` via `getComputedStyle` (amber/red esclusi = warn/danger). Caricato da `base.html`, seed default = `endpoint`. |
| `urls_manager.js` | On load, fetches the 4 URL JSONs and stamps badges on matching `<article>` results. |
| `favorite_urls.json` | ~1800 "preferiti" URLs (badge). |
| `highlight_urls.json` | "visitati" URLs. |
| `unwanted_urls.json` | "indesiderati" URLs. |
| `ignored_urls.json` | "ignorati" URLs. |

All JSONs are alphabetically sorted by pre-commit hook (`scripts/sort_json.py`).

### `searx/templates/static/themes/simple/`
- `input.css` — Tailwind v4 entry: `@import "tailwindcss"` + `@theme` block (colors `--color-cust-*` + `--color-cust-{dim,chip-border,placeholder}` palette-aware per grigi secondari, fonts Fira Sans + Iosevka, fluid sizes via `clamp()`). **No tailwind.config.js.**
- `output.css` — compiled Tailwind (~21KB). Committed to repo, copied into Docker.
- `preferences.css`, `highlight.css` — preferences + code highlight styling.
- `img/favicon.{png,svg,svg.gz,svg.br}` — DiceBear identicon, static fallback. Pink `#d81b60`.
- `img/github-color.svg`, `fonts/` — assets.

### Build
```bash
npx @tailwindcss/cli -i input.css -o output.css
```
(No script shortcut in package.json — run manually.)

## Custom engines

- `searx/engines/brave_api.py` — Brave Search API.
- `searx/engines/commoncrawl.py` — Common Crawl.

All other engines come from the upstream image.

## Scripts

| Script | Purpose |
|---|---|
| `scripts/sort_json.py` | Pre-commit: sort JSON arrays/keys. |
| `scripts/sort_txt.py` | Pre-commit: sort `blocked_domains.txt`. |
| `scripts/extract_palette.py` | Utility to pull hex colors from Atlassian palette screenshots. |

## Conventions (reminders)

- **Border-radius always `2px`** — never `0`, never `999px`, never other values. Applies to CSS rules, `--pref-radius*` tokens, chips/pills/buttons/inputs/cards/tooltips/dialogs.
- **No `Co-Authored-By: Claude …` trailer** on commits.
- **Commit subjects** follow pattern `feat:` / `fix:` / `update:` / `polish:` (Italian body text is fine).
- Template comments in Italian are standard; keep them if editing existing files.
- Tailwind classes preferred over inline styles; `term-*` utilities already defined in output.css.
- Pre-commit hooks auto-sort JSON and `blocked_domains.txt` — don't fight them.

## Dynamic features worth remembering

- **Dynamic favicon** (`dynamic_favicon.js`, loaded by `base.html`): client-side JS hashes a seed (FNV-1a) → xorshift32 → 5×5 mirrored DiceBear-style identicon SVG → `data:` URI replaces `<link rel="icon">`. Colore pescato dal seed fra gli slot neon non-semantici (`--color-neon-{green,cyan,pink,blue}`, letti via `getComputedStyle` — amber/red esclusi perché riservati a warn/danger); segue automaticamente la palette attiva. Seed letto da `<meta name="favicon-seed">`, popolato via block Jinja `favicon_seed`: default = `endpoint` (index / preferences / … → identicon stabile per pagina), `results.html` lo sovrascrive con `q or endpoint` per variare in base alla query.
- **Result badges** via `urls_manager.js` — matches article `href` against the 4 JSON sets.
- **Keyboard nav** via `active_article.js` — `↑/↓/j/k` move active result, `Enter` opens it.

## What's NOT in this repo

- The Flask app / Python core (lives in upstream `searxng/searxng:latest`).
- Most engines (upstream).
- Upstream themes other than `simple`.
- Runtime settings — only `settings.yml.template` is tracked.
