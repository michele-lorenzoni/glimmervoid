# Glimmervoid — style guide

Tema **`terminal`**: background scuro, font monospace, palette neon differenziata per funzione. È l'unico tema del progetto, impostato come default e hardcoded — non c'è un selettore di tema nella preferences. Questa guida raccoglie le decisioni prese nel repo — consultala prima di aggiungere UI per mantenere coerenza.

> **Mantenere aggiornata.** Ogni modifica allo stile che introduce, cambia o rimuove una convenzione (nuovo colore in palette, nuovo pattern componente, cambio di border/radius/spacing, nuovo breakpoint responsive, nuova regola sulle icone o sull'architettura CSS) va riflessa in questa guida **nello stesso commit**. Tweak una tantum che non generalizzano restano locali; tutto ciò che qualcun altro deve seguire va qui.

### Theme naming
- La `<html>` ha sempre classe `theme-terminal` (hardcoded in `base.html`). Oggi è l'unico tema; altri arriveranno.
- Il valore di `simple_style` in `settings.yml.template` è lasciato a `auto` solo per compatibilità con upstream: il nostro CSS non ne dipende.
- Il selettore "Theme" nel tab UI della preferences è presente (override locale in `preferences/theme.html`) ma mostra solo l'opzione "Terminal" — resta visibile per quando aggiungeremo nuovi temi.

### Palette
Nel tab UI c'è un secondo fieldset "Palette" che gestisce la variante cromatica. La scelta è salvata in `localStorage['palette']` ed esposta come `html[data-palette="…"]`. Un inline script in `base.html` legge localStorage al boot e imposta l'attributo prima del render (no FOUC).

Le 6 `--color-neon-*` sono **slot funzionali**: il nome (`green`, `cyan`, `pink`, ecc.) identifica la FUNZIONE (attivo, hover, heading, warn, danger, info), il VALORE dipende dalla palette attiva.

| Valore | Label | Concept |
|---|---|---|
| `neon` (default) | Neon | Palette originale: verde/ciano/rosa/ambra/rosso/blu su gray-950 |
| `amber-crt` | Amber CRT | Terminale vintage ambra/arancio, mono-amber con rosso soft per danger |
| `mono-green` | Mono green | Terminale classico verde fosforescente, con amber/rosso per warn/danger |
| `cyberpunk` | Cyberpunk | Magenta/ciano/giallo ad alta saturazione, vibe synth-wave |
| `high-contrast` | High contrast | **Accessibilità** — palette WCAG AAA-like su sfondo nero puro (#000), bordi bianchi, colori saturi (green/yellow/red). Override anche `--color-cust-*` per superfici (text bianco, border bianco) |

Le superfici palette-aware passano tutte da `--color-cust-*` (body/element/border/default/url/description/title). In `preferences.css`, le vars `--pref-*` sono alias che puntano a queste globali — niente hex duplicati.

Per aggiungere una palette:
1. `<option value="my-palette">My palette</option>` in `preferences/palette.html`
2. Blocco `html[data-palette="my-palette"] { --color-neon-*: …; (opzionalmente --color-cust-*: …) }` in `input.css` E `output.css`
3. Documentarla nella tabella qui sopra.

---

## 1. Palette

### Superfici & testo
| Token | Hex | Uso |
|---|---|---|
| `--color-cust-body` / `--pref-body` | `#030712` | Background pagina (gray-950) |
| `--color-cust-element` / `--pref-element` | `#111827` | Background di input / searchbar / bottoni / checkbox / card interattive (gray-900) |
| `--color-cust-border` / `--pref-border` | `#374151` | Border default (gray-700) |
| `--pref-border-strong` | `#4b5563` | Border emphasis, hover-border di input disabled (gray-600) |
| `--color-cust-default` / `--pref-text` | `#fafafa` | Testo principale (neutral-50) |
| `--pref-text-muted` | `#d4d4d4` | Testo secondario (neutral-300) |
| `--pref-text-dim` / `term-dim` | `#6b7280` | Label dim, nav link idle (gray-500) |

### Palette neon funzionale
Il tema **non è monocromatico**: ogni colore neon indica una funzione precisa. Non scambiarli.

Sorgente di verità: `@theme` in `input.css` → `:root` in `output.css`. Tutti i riferimenti nel CSS usano `var(...)`, mai gli hex. Per cambiare un colore si modifica in un solo posto (la definizione nel `@theme`); per creare una palette alternativa si overrideano queste vars in un selettore `html[data-palette="…"]`.

| Token (globale) | Hex default | Funzione |
|---|---|---|
| `--color-neon-green` | `#7aff8f` | **Stato attivo / current / checked / success**. Tab selezionato, pagina corrente (`.term-nav-link.active`), checkbox checked, prompt `>`, search lens, chevron dropdown, caret homepage. |
| `--color-neon-cyan` | `#22d3ee` | **Hover interattivo**. Link hover (`.term-nav-link:hover`), tab hover, bottoni hover (border + bg tint), focus input/select, chip hover, category hover, keyboard-nav active result. |
| `--color-neon-pink` | `#f472b6` | **Decorazioni: heading / section label**. Prefissi `//` di h1/h4/pref-group, brackets `[ LEGEND ]` dei `<legend>`, colore del testo dei legend. |
| `--color-neon-amber` | `#fbbf24` | **Warning**. Reliability 50-80%, `rate80` bar, `.warning` td, `dialog-warning` border. |
| `--color-neon-red` | `#ef4444` | **Danger / error**. Reliability <50%, `rate95` bar, `.danger` td, `dialog-error` border. |
| `--color-neon-blue` | `#60a5fa` | **Info / neutrale**. Badge `ignored` URL. |

In `preferences.css` esistono anche alias locali `--neon-*` → `var(--color-neon-*)` per continuità storica; usa indifferentemente i due nomi, il risultato è identico.

### URL badges (results page)
Allineati alla palette neon:
| Badge | Fill | Border |
|---|---|---|
| `.url-badge-favorite` (verde) | `#7aff8f` (neon-green) | `#166534` (green-800) |
| `.url-badge-highlight` (ambra) | `#fbbf24` (neon-amber) | `#92400e` (amber-800) |
| `.url-badge-unwanted` (rosso) | `#ef4444` (neon-red) | `#991b1b` (red-800) |
| `.url-badge-ignored` (blu) | `#60a5fa` (blue-400) | `#1e40af` (blue-800) |

### Result attivo (keyboard nav)
`.term-result-active` applicata da `active_article.js` sull'`<article>` correntemente selezionato con `↑/↓/j/k`: border-top cyan `#22d3ee` (stesso hover-color della palette, coerente col concetto di "interactive focus"). Sostituisce il vecchio `border-sky-800`.

---

## 2. Border & radius

- **`border-radius: 2px` sempre**, ovunque. No `0`, no `999px`, no pill-shape. `--pref-radius = 2px`, `--radius-xs = 0.125rem`. Vale per card, button, input, checkbox, chip, tooltip, tab pill, dialog.
- **Dashed vs solid:**
  - `dashed` = *rule / separatore orizzontale*. Es: `h1` bottom, fieldset top, footer top, `td` bottom (riga tabella), `.tab-buttons` bottom, underline hover su anchor di contenuto.
  - `solid` = *contenitore / elemento interattivo*. Es: input, select, textarea, checkbox, radio, button, `.preferences_back`, `.bang`, `.category`, `.tabs > label`, dialog, `.selectable_url pre`, `.engine-tooltip`, table header.

Non mischiare: un input ha border solido. Una linea separatrice tra sezioni è dashed.

---

## 3. Tipografia

### Font family
- **`term-font` / `--pref-font`** → **Iosevka** (monospace). Tema terminale: homepage, results, preferences, qualunque `.term-*`.
  ```css
  font-family: "Iosevka", ui-monospace, SFMono-Regular, Menlo, Consolas, "Courier New", monospace;
  font-feature-settings: "liga" 0, "calt" 0;
  ```
- **`font-default` / `--font-fira`** → **Fira Sans**. Default body text, fallback dove l'estetica terminale non è richiesta.

### Size & weight
- **h1 preferences**: `clamp(1.25rem, 1vw + 1rem, 1.75rem)`, weight 500, `lowercase`.
- **h2/h3/legend/h4**: 0.72rem, weight 500, `uppercase`, `letter-spacing: 0.06-0.08em`.
- **Body preferences**: 14px (13px su ≤480px), `line-height: 1.55`, `letter-spacing: 0.01em` — **ma azzerato (`letter-spacing: normal`) sui `<select>`** perché falsa il calcolo di `width: max-content` e tronca il testo.
- **Tabs / bottoni / chip**: 0.72-0.78rem, `uppercase` o `lowercase`, `letter-spacing: 0.04-0.08em`.
- **Nav top**: 11px, `tracking-widest` (0.1em), `lowercase`.

---

## 4. Icone — stile Lucide

Tutte le icone SVG custom seguono la famiglia **Lucide** per coerenza:
```
fill: none
stroke: #7aff8f  (o colore funzionale)
stroke-width: 2  (3 per icone piccole dentro checkbox)
stroke-linecap: round
stroke-linejoin: round
viewBox: 0 0 24 24
```

Usi già nel repo (inline SVG o data-URI):
- **Search lens** (`_search_bar.html`): magnifier `circle(11 11 r=8) + path m21 21 -4.34 -4.34`.
- **Select chevron**: `path m6 9 6 6 6-6` — data-URI in `input.css`/`output.css`, posizionato `right 0.65rem center` con `padding-right: 2.75rem` sul select.
- **Checkbox check**: `path M20 6 9 17 l-5 -5`, `stroke-width: 3`, `background-size: 0.8rem 0.8rem` centrato.

Per icone esterne, usa SVG da [lucide.dev](https://lucide.dev) senza modifiche di stile di base.

---

## 5. Pattern componenti

### Nav top (`base.html`)
Vive **in un unico posto** (base.html) con 3 link `[ prefs ] [ donate ] [ home ]`. Non duplicare.
```html
<a class="term-nav-link{% if endpoint == 'X' %} active{% endif %}"
   href="..."
   {% if endpoint == 'X' %}aria-current="page"{% endif %}>
  <span class="bracket">[</span>&nbsp;label&nbsp;<span class="bracket">]</span>
</a>
```
- Idle: colore `#6b7280`, bracket `#374151`.
- Hover: cyan.
- `.active`: verde + `cursor: default`. L'`aria-current="page"` è obbligatorio.

### Tab buttons (top-level preferences)
Pseudo-elementi `::before '[' ::after ']'` per le brackets. Idle = dim, hover = cyan, active = green.

### Tab pills nested (engine categories)
`<label>` con bordo solido `--pref-border`, border-radius 2px, min-height 2.5rem, inline-flex. Hover = cyan, `:checked` = green.

### Bottoni
- Bg `--pref-element`, border solid `--pref-border`, radius 2px, min-height 2.5rem, lowercase, `letter-spacing: 0.08em`.
- Hover: bordo + testo cyan, bg `rgba(34, 211, 238, 0.08)`.
- Active state on "current page" link (non sui submit) = verde.

### Input / select / textarea
- Bg `--pref-element`, border solid, radius 2px.
- Focus: border cyan.
- `<select>`: `appearance: none` + chevron Lucide via data-URI, `width: max-content` con `max-width: 100%`, `letter-spacing: normal`, cap a `100%` sotto 640px.

### Checkbox / radio (globali, unlayered + !important)
- 1rem × 1rem box, radius 2px.
- `appearance: none`, bg `#111827`, border `#374151`.
- `:checked`: border verde + checkmark SVG Lucide al centro (`::after`).
- Radio: `:checked::after` quadrato verde 8px (radius 2px — non cerchio, coerenza col repo).
- `.checkbox-onoff` (toggle upstream) attualmente viene ristilizzato come checkbox standard.

### Dialog / alert
- `dialog-error`: border solid `--pref-danger-border` (#b91c1c), padding 0.8rem 1rem.
- `dialog-warning-block`: border solid `--pref-warning-border` (#a16207).

### Heading markers
- `h1::before = '//'` pink.
- `h4::before = '// '` pink con opacity 0.55.
- `legend::before = '[ '` / `legend::after = ' ]'` pink 0.55 opacity, testo del legend pink.
- `tr.pref-group th::before = '// '` pink 0.55 + testo pink.

---

## 6. Layout / spacing

- Body padding: `p-8` desktop, `1.25rem 1rem` sotto 720px, `0.85rem 0.75rem` sotto 480px (override da preferences.css su `body.preferences_endpoint`).
- **Min-height uniforme 2.5rem** su: `th/td` (come `height: 2.5rem`), button / submit / reset / `.preferences_back`, `.tabs > label`.
- `.tab-buttons`: NO border-bottom dashed (l'h1 sopra già separa; doppia linea sembra "puntini").
- Fieldset: flat, no card. Solo `border-top: 1px dashed` come separatore di sezione; `:first-of-type` in un tabpanel non ha il top border per evitare doppie linee dopo l'h1.

---

## 7. Responsive

Due breakpoint:
- **≤720px** (tablet/phone large): font ridotto, input full-width, fieldset più snello, tap target su tabs.
- **≤640px / ≤480px** (smartphone): layout a **card** per tabelle con `data-label` sui `<td>`, body padding ridotto, chip compatti, dropdown cap a 100%.

Tabelle a molte colonne (Special Queries answerers, engines) su ≤640px diventano card verticali. Ogni riga dati = blocco con pseudo-label `::before { content: attr(data-label); }`, uppercase dim 0.62rem. Classe `.header-row` sulla `<tr>` di intestazione per nasconderla su mobile.

Footer bottoni (Save / Reset / Back): `flex-wrap: wrap`, `white-space: nowrap`, larghezza naturale — **non forzare `flex: 1 1 0`** (rompe l'altezza quando Reset defaults va a capo).

---

## 8. Architettura CSS

- `searx/templates/static/input.css` → sorgente Tailwind v4 (`@import "tailwindcss"` + `@theme` + `@layer components` per `term-*` + regole unlayered per checkbox/radio/select).
- `searx/templates/static/output.css` → compilato. **Alcune regole critiche (checkbox, radio, select) sono UNLAYERED** per vincere sul cascade anche contro CSS upstream non layered.
- `searx/templates/static/preferences.css` → caricata dopo output.css via `page_with_header.html` `{% block stylesheets %}`. Contiene tutto lo styling specifico della preferences page, scoped con `body.preferences_endpoint` per non toccare altre pagine.

Regola d'oro: se una primitiva serve a più pagine → `input.css` (poi rebuilda o replica in output.css). Se serve solo alla preferences → `preferences.css`.

---

## 9. Git

- Commit style: `feat: / fix: / update: / polish: / refactor:` + riga vuota + body esplicativo se serve.
- **Niente trailer `Co-Authored-By: Claude`** (vedi `CLAUDE.md`).
- Pre-commit: `sort_json.py` e `sort_txt.py` tengono allineati `favorite_urls.json`, `blocked_domains.txt` ecc. Non combattere i hook.

---

## 10. Quando servono aggiunte

- **Nuovo elemento interattivo?** Bg `--pref-element`, border solid `--pref-border`, radius 2px, hover cyan.
- **Nuova sezione / heading?** Prefisso `//` pink o brackets `[ label ]` pink.
- **Nuovo stato attivo?** Green.
- **Nuovo feedback success/warning/error?** Green / amber / red dalla palette neon — non inventare nuovi colori.
- **Nuova icona?** SVG stile Lucide, `stroke: --neon-green` o colore funzionale, linecap round.
- **Nuovo override upstream?** Clona il file in `searx/templates/simple/...`, aggiungi riga `COPY` al Dockerfile, modifica con minimo diff rispetto all'upstream.
