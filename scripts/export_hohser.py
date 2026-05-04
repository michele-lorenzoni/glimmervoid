#!/usr/bin/env python3
"""Convert glimmervoid URL/domain lists into a Hohser-compatible JSON import file.

Output schema (bare array):
    [
        {"domainName": "<host-or-url>", "display": "HIGHLIGHT|PARTIAL_HIDE|FULL_HIDE", "color": "COLOR_1|COLOR_2|COLOR_3"?},
        ...
    ]

Mapping:
    favorite_urls.json   -> HIGHLIGHT,    color COLOR_1
    highlight_urls.json  -> HIGHLIGHT,    color COLOR_2
    unwanted_urls.json   -> PARTIAL_HIDE
    ignored_urls.json    -> FULL_HIDE
    blocked_domains.txt  -> FULL_HIDE

Conflict resolution: stronger action wins (FULL_HIDE > PARTIAL_HIDE > HIGHLIGHT).
Within HIGHLIGHT, favorite (COLOR_1) wins over visited (COLOR_2).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CUSTOM = ROOT / "searx" / "templates" / "static" / "custom"

PRIORITY = {"FULL_HIDE": 3, "PARTIAL_HIDE": 2, "HIGHLIGHT": 1}


def load_json_array(path: Path) -> list[str]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_txt_lines(path: Path) -> list[str]:
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def merge(entry: dict, registry: dict[str, dict]) -> None:
    key = entry["domainName"]
    existing = registry.get(key)
    if existing is None:
        registry[key] = entry
        return
    if PRIORITY[entry["display"]] > PRIORITY[existing["display"]]:
        registry[key] = entry
    elif (
        entry["display"] == existing["display"] == "HIGHLIGHT"
        and entry.get("color") == "COLOR_1"
    ):
        registry[key] = entry


def main(out_path: Path) -> int:
    registry: dict[str, dict] = {}

    sources = [
        (CUSTOM / "favorite_urls.json", load_json_array, {"display": "HIGHLIGHT", "color": "COLOR_1"}),
        (CUSTOM / "highlight_urls.json", load_json_array, {"display": "HIGHLIGHT", "color": "COLOR_2"}),
        (CUSTOM / "unwanted_urls.json", load_json_array, {"display": "PARTIAL_HIDE"}),
        (CUSTOM / "ignored_urls.json", load_json_array, {"display": "FULL_HIDE"}),
        (ROOT / "blocked_domains.txt", load_txt_lines, {"display": "FULL_HIDE"}),
    ]

    counts = {}
    for path, loader, template in sources:
        items = loader(path)
        counts[path.name] = len(items)
        for value in items:
            entry = {"domainName": value, **template}
            merge(entry, registry)

    output = sorted(registry.values(), key=lambda e: e["domainName"].lower())
    out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Wrote {len(output)} entries to {out_path}")
    for name, n in counts.items():
        print(f"  {name}: {n}")
    return 0


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / "Desktop" / "hohser_import.json"
    raise SystemExit(main(target))
