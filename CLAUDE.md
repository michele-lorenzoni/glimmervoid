# Project conventions

See `PROJECT_MAP.md` in the repo root for a structural map of the codebase (layout, templates, static assets, custom engines, scripts, dynamic features). Consult it before scanning files.

See `STYLE_GUIDE.md` for the visual conventions: neon palette (green=active, cyan=hover, pink=headings, amber=warn, red=danger), dashed vs solid borders, Lucide icon family, component patterns (nav, tabs, buttons, inputs, checkbox/radio), responsive rules, and CSS architecture. Always check it before adding UI so new elements match the existing language.

See `IDEAS.md` per le idee, possibili migliorie e tradeoff non ancora implementati. Non è una roadmap né un committment: è il taccuino dove vivono i ragionamenti su evoluzioni future del progetto.

**Keep `STYLE_GUIDE.md` in sync.** Whenever you introduce, remove, or change a visual convention — new palette color, new component pattern, new responsive breakpoint, new icon family, new responsive rule, changes to border/radius/spacing, new CSS layer architecture — update the relevant section of `STYLE_GUIDE.md` in the same commit. Drift between code and guide defeats the purpose of having one. If a change is a one-off tweak that doesn't generalize, it can stay local; if it sets a new convention someone else should follow, it goes in the guide.

**Keep `IDEAS.md` aggiornato.** Ogni volta che in conversazione emerge una nuova idea, un'analisi di tradeoff o una possibile direzione di sviluppo non banale (anche senza richiesta esplicita dell'utente), aggiungerla a `IDEAS.md` nello stesso commit del lavoro che l'ha generata. Quando una voce viene completata si rimuove (la storia vive nei commit). Non duplicare voci esistenti — preferire arricchirle.

## Styling

- **Allowed shapes: rectangles with `border-radius: 2px`, and circles.** Nothing else — no pills (`999px` on non-square rectangles), no `0` to "flatten", no intermediate radii.
  - `2px` radius applies to every squared element in the repo: `--pref-radius*` tokens, buttons, inputs, cards, tooltips, dialogs, chips, tab pills, checkboxes.
  - Circles are fine via `border-radius: 50%` / `999px` on square elements or SVG `<circle>`. Use when circular geometry is intrinsic to the element (avatars, dots, circular icons/buttons).

## Git

- **Do not append `Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>` (or any Claude `Co-Authored-By` trailer) to commit messages.** Commit messages must end with the subject/body only, no Claude attribution trailer.

## Deployment

- **The project is deployed on Render.** There is no `render.yaml` in the repo: service config (env vars, build settings) lives only in the Render dashboard.
- Dockerfile build-args (e.g. `OUTGOING_PROXIES`) are injected by Render from the service's **Environment Variables**. To change/disable one, edit it in the Render dashboard → tab Environment → save (triggers automatic rebuild + redeploy).
- `settings.yml` is generated **at build-time** inside the image by the Dockerfile. Runtime changes to its content require a **rebuild**, not just a container restart.
- Default assumption when the user mentions "variables" or "config" of the project: they live on Render, not in local files.
