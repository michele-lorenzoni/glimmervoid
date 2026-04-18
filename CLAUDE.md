# Project conventions

See `PROJECT_MAP.md` in the repo root for a structural map of the codebase (layout, templates, static assets, custom engines, scripts, dynamic features). Consult it before scanning files.

## Styling

- **Border radius must always be `2px`.** Applies to every CSS rule in the repo (regular radii, `--pref-radius*` tokens, pill/chip shapes, buttons, inputs, cards, tooltips, dialogs). Do not use other radius values, do not use `999px` for pills, do not use `0` to "flatten" — always `2px`.

## Git

- **Do not append `Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>` (or any Claude `Co-Authored-By` trailer) to commit messages.** Commit messages must end with the subject/body only, no Claude attribution trailer.
