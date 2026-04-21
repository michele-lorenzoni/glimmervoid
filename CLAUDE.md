# Project conventions

See `PROJECT_MAP.md` in the repo root for a structural map of the codebase (layout, templates, static assets, custom engines, scripts, dynamic features). Consult it before scanning files.

See `STYLE_GUIDE.md` for the visual conventions: neon palette (green=active, cyan=hover, pink=headings, amber=warn, red=danger), dashed vs solid borders, Lucide icon family, component patterns (nav, tabs, buttons, inputs, checkbox/radio), responsive rules, and CSS architecture. Always check it before adding UI so new elements match the existing language.

**Keep `STYLE_GUIDE.md` in sync.** Whenever you introduce, remove, or change a visual convention — new palette color, new component pattern, new responsive breakpoint, new icon family, new responsive rule, changes to border/radius/spacing, new CSS layer architecture — update the relevant section of `STYLE_GUIDE.md` in the same commit. Drift between code and guide defeats the purpose of having one. If a change is a one-off tweak that doesn't generalize, it can stay local; if it sets a new convention someone else should follow, it goes in the guide.

## Styling

- **Allowed shapes: rectangles with `border-radius: 2px`, and circles.** Nothing else — no pills (`999px` on non-square rectangles), no `0` to "flatten", no intermediate radii.
  - `2px` radius applies to every squared element in the repo: `--pref-radius*` tokens, buttons, inputs, cards, tooltips, dialogs, chips, tab pills, checkboxes.
  - Circles are fine via `border-radius: 50%` / `999px` on square elements or SVG `<circle>`. Use when circular geometry is intrinsic to the element (avatars, dots, circular icons/buttons).

## Git

- **Do not append `Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>` (or any Claude `Co-Authored-By` trailer) to commit messages.** Commit messages must end with the subject/body only, no Claude attribution trailer.
