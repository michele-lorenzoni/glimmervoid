"""Extract hex colors from Atlassian palette screenshots.

Each screenshot is a list of horizontal color bands with a text label.
Strategy: walk the image vertically at a fixed x (inside a swatch, far
enough right to avoid text) and detect contiguous color runs.
"""

import sys
from pathlib import Path

from PIL import Image


def hex_of(px):
    r, g, b = px[:3]
    return f"#{r:02X}{g:02X}{b:02X}"


def extract_bands(img: Image.Image, sample_x: int, min_band_height: int = 8):
    """Return list of (y_center, hex) for each contiguous color band."""
    w, h = img.size
    if sample_x >= w:
        return []
    prev = None
    bands = []
    run_start = 0
    for y in range(h):
        px = img.getpixel((sample_x, y))[:3]
        if prev is None:
            prev = px
            run_start = y
            continue
        # Consider same band if channel diff < 6
        if all(abs(a - b) <= 5 for a, b in zip(px, prev)):
            continue
        # Band break
        if y - run_start >= min_band_height:
            mid = (run_start + y) // 2
            bands.append((mid, hex_of(img.getpixel((sample_x, mid))[:3])))
        prev = px
        run_start = y
    # Final band
    if h - run_start >= min_band_height:
        mid = (run_start + h) // 2
        bands.append((mid, hex_of(img.getpixel((sample_x, mid))[:3])))
    return bands


def detect_columns(img: Image.Image):
    """Heuristic: find x positions where vertical slices contain many
    distinct swatch bands (i.e. not the page background).
    Returns a list of (column_name, sample_x).
    """
    w, h = img.size
    # Simple approach: try a few candidate x positions across the width
    # and pick those that produce > 5 distinct bands.
    results = []
    step = max(20, w // 40)
    for x in range(20, w - 20, step):
        bands = extract_bands(img, x)
        hexes = [b[1] for b in bands]
        distinct = len(set(hexes))
        if distinct >= 5:
            results.append((x, bands))
    return results


def main(paths):
    for p in paths:
        img = Image.open(p).convert("RGB")
        print(f"\n=== {Path(p).name}  ({img.size[0]}x{img.size[1]}) ===")
        # Try two sample_x: roughly left column (25% width) and right column (70% width)
        for label, frac in (("col1", 0.40), ("col2", 0.80)):
            x = int(img.size[0] * frac)
            bands = extract_bands(img, x)
            # filter page-background grays/near-pure-white/dark at extremities
            if not bands:
                continue
            print(f"-- {label} @ x={x} --")
            for y, hx in bands:
                print(f"  y={y:4d}  {hx}")


if __name__ == "__main__":
    main(sys.argv[1:])
