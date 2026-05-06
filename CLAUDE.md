# Project conventions

See `PROJECT_MAP.md` in the repo root for a structural map of the codebase (layout, templates, static assets, custom engines, scripts, dynamic features). Consult it before scanning files.

See `STYLE_GUIDE.md` for the visual conventions: neon palette (green=active, cyan=hover, pink=headings, amber=warn, red=danger), dashed vs solid borders, Lucide icon family, component patterns (nav, tabs, buttons, inputs, checkbox/radio), responsive rules, and CSS architecture. Always check it before adding UI so new elements match the existing language.

See `IDEAS.md` per le idee, possibili migliorie e tradeoff non ancora implementati. Non è una roadmap né un committment: è il taccuino dove vivono i ragionamenti su evoluzioni future del progetto.

**Keep `STYLE_GUIDE.md` in sync.** Whenever you introduce, remove, or change a visual convention — new palette color, new component pattern, new responsive breakpoint, new icon family, new responsive rule, changes to border/radius/spacing, new CSS layer architecture — update the relevant section of `STYLE_GUIDE.md` in the same commit. Drift between code and guide defeats the purpose of having one. If a change is a one-off tweak that doesn't generalize, it can stay local; if it sets a new convention someone else should follow, it goes in the guide.

**Keep `IDEAS.md` aggiornato — azione automatica, no permission-asking.** Ogni volta che in conversazione emerge una nuova idea, un'analisi di tradeoff o una possibile direzione di sviluppo non banale, aggiungerla a `IDEAS.md` **direttamente, senza chiedere conferma**. Niente "vuoi che aggiorni IDEAS.md?" alla fine dei messaggi: l'utente ha già dato l'ok permanente. Vale anche per gli auto-commit/push (vedi `feedback_auto_push.md`). Quando una voce viene completata si rimuove (la storia vive nei commit). Non duplicare voci esistenti — preferire arricchirle.

## Styling

- **Allowed shapes: rectangles with `border-radius: 2px`, and circles.** Nothing else — no pills (`999px` on non-square rectangles), no `0` to "flatten", no intermediate radii.
  - `2px` radius applies to every squared element in the repo: `--pref-radius*` tokens, buttons, inputs, cards, tooltips, dialogs, chips, tab pills, checkboxes.
  - Circles are fine via `border-radius: 50%` / `999px` on square elements or SVG `<circle>`. Use when circular geometry is intrinsic to the element (avatars, dots, circular icons/buttons).

## Git

- **Do not append `Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>` (or any Claude `Co-Authored-By` trailer) to commit messages.** Commit messages must end with the subject/body only, no Claude attribution trailer.

## Source markers

Ogni asserzione fattuale sul progetto, su SearXNG o su comportamento esterno va preceduta da **uno dei tre marker**, a inizio bullet/frase, in modo che la fonte sia individuabile a colpo d'occhio:

- 🧠 **memoria di training**, non verificato — è un'ipotesi, va trattata come tale
- 🌐 **web** — WebFetch fatto in questa sessione, includere il link a supporto
- 📂 **repo locale** — file letto in questa sessione, citare `path:linea`

Regole:

- I marker vanno **a inizio frase o bullet**, mai a metà — devono saltare all'occhio durante lo scroll.
- Per paragrafi che mescolano più fatti, **spezzare in bullet** così che ogni asserzione abbia il suo marker.
- Asserzione mista (training + verifica successiva) → marker in sequenza (es. 🧠→📂) per mostrare il flusso.
- Frasi discorsive (consigli, opinioni, domande, riassunti del lavoro fatto) **non** si marcano — i marker sono solo per asserzioni fattuali, altrimenti diventano rumore.
- L'assenza di marker su un'asserzione fattuale = errore, l'utente può contestare immediatamente.
- **Caveat 🌐**: WebFetch su pagine **JS-rendered** (SPA, listini con tabelle dinamiche, dashboard) può restituire contenuto generato dal modello dietro il tool, non estratto realmente. Considerare 🌐 affidabile solo se il fatto è citato verbatim dal testo statico della pagina (doc, articoli, markdown, README). Se la response WebFetch sembra "troppo pulita" su una pagina che in realtà è SPA, downgrade ad 🧠 e verifica con l'utente.

## SearXNG reference

- **Qualsiasi informazione su SearXNG (engine, `settings.yml`, plugin, network, comportamento upstream) va recuperata dalla doc ufficiale o dal codice sorgente upstream, non dalla memoria di training.** La memoria di training su SearXNG ha già prodotto hallucination su nomi di key e blocchi YAML inesistenti — non è autorevole.
  - Doc ufficiale: <https://docs.searxng.org/>
  - Sorgente upstream: <https://github.com/searxng/searxng> (il container parte da `searxng/searxng:latest`)
- **Particolarmente critico per `settings.yml.template`**: prima di proporre una nuova key, un nuovo blocco o un refactor della config, verificare la sintassi nella doc o nel `settings.yml` di default upstream e citare la fonte (link) nella risposta/commit.
- La memoria di training si usa **solo come ultima spiaggia**, ed esplicitando che l'asserzione non è verificata.

## Deployment

- **The project is deployed on Render.** There is no `render.yaml` in the repo: service config (env vars, build settings) lives only in the Render dashboard.
- Dockerfile build-args (e.g. `OUTGOING_PROXIES`) are injected by Render from the service's **Environment Variables**. To change/disable one, edit it in the Render dashboard → tab Environment → save (triggers automatic rebuild + redeploy).
- `settings.yml` is generated **at build-time** inside the image by the Dockerfile. Runtime changes to its content require a **rebuild**, not just a container restart.
- Default assumption when the user mentions "variables" or "config" of the project: they live on Render, not in local files.
