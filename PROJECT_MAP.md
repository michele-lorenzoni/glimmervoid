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
├── blocked_domains.txt          # auto-sorted, injected into settings.yml on build (hostname filter)
├── blocked_url_prefixes.txt     # auto-sorted, host+path prefixes hidden by custom plugin
├── scripts/                     # sort_json.py, sort_txt.py, extract_palette.py
├── showcase/                    # screenshots (index/results, desktop/mobile)
└── searx/
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
| `icons.html`, `_icons/` | Icon macro + 11 custom SVG icons (claude, codeberg, fish, github, globe, hackthebox, …). |
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

None — all engines come from the upstream image.

## Custom plugins

- `searx/plugins/url_prefix_remover.py` — server-side `SXNGPlugin`. Hides any result whose URL **starts with** a prefix listed in `blocked_url_prefixes.txt` (host+path, scheme/`www.`-insensitive, path-boundary aware — `/pl-pl` won't match `/pl-plaza`). Complements `blocked_domains.txt`, which the upstream `hostnames` plugin matches on hostname (`netloc`) only and so can't express a path. Registered in `settings.yml.template` under `plugins:` (`active: true`); the Dockerfile copies both the module and the list into `/usr/local/searxng/searx/plugins/`. List read once at startup → rebuild to apply (same as `blocked_domains`).
  - **Query-string constraints.** A list entry may carry a query string, for sites that put the language in a parameter instead of the path: `support.google.com/youtube/answer/7174035?hl=ru` blocks only the Russian variant, while the same line without `?hl=ru` blocks the page in every language. Semantics: all listed parameters must be present on the result URL (AND); extra parameters on the result are allowed; a repeated parameter matches if any of its values does; a bare name (`?hl`, no `=`) means "present with any value"; `?q=` means "present and empty". Names/values are compared **case-sensitively**, like the path — hence the list carries both `support.microsoft.com/fr-FR/` and `.../fr-fr/`. Percent-encoding and `+` are decoded on both sides before comparing. Entries **without** a query string ignore the result's query entirely (unchanged behaviour), and the result query is parsed lazily so they cost nothing.
  - **Gotcha:** a trailing `/` after the query (`google.com/?hl=ar-AE/`) lands *inside the parameter value*, not the path — the entry then matches nothing. Before the query support existed, such lines silently normalised to the bare host and blocked the **whole domain**.

## Scripts

| Script | Purpose |
|---|---|
| `scripts/sort_json.py` | Pre-commit: sort JSON arrays/keys. |
| `scripts/sort_txt.py` | Pre-commit: sort `blocked_domains.txt`. |
| `scripts/extract_palette.py` | Utility to pull hex colors from Atlassian palette screenshots. |
| `scripts/selfhost/auto-update.ps1` | Selfhost: polls `origin/main`, rebuilds image + restarts container if HEAD moved. Logs to `<repo>/auto-update.log`. |
| `scripts/selfhost/register-task.ps1` | Selfhost: registers `auto-update.ps1` as a Windows Scheduled Task (every 2 min). Run once as Administrator. |

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
