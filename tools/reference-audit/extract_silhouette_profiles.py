#!/usr/bin/env python3
"""Extract transparent outer-silhouette samples from Dad's unchanged master crops.

Requires Pillow. This produces measurement aids only; it does not generate or
approve 3D geometry. Source pixels are read without modification.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
REFERENCE_DIR = ROOT / "assets/references/character-masters/characters/dad"
OUTPUT_DIR = REFERENCE_DIR / "derived"
VIEWS = ("front", "three_quarter", "side")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def extract_rows(view: str, path: Path, alpha_threshold: int, sample_step: int):
    image = Image.open(path).convert("RGBA")
    width, height = image.size
    alpha = image.getchannel("A")
    pix = alpha.load()
    rows = []
    for y in range(0, height, sample_step):
        occupied = [x for x in range(width) if pix[x, y] >= alpha_threshold]
        if not occupied:
            continue
        left, right = occupied[0], occupied[-1]
        center = (left + right) / 2.0
        rows.append({
            "view": view,
            "source": path.name,
            "source_sha256": sha256(path),
            "image_width_px": width,
            "image_height_px": height,
            "sample_y_px_from_top": y,
            "z_fraction_from_ground": f"{(height - 1 - y) / (height - 1):.6f}",
            "x_left_px": left,
            "x_right_px": right,
            "width_fraction_of_canvas_height": f"{(right - left + 1) / height:.6f}",
            "center_offset_fraction_of_canvas_height": f"{(center - (width - 1) / 2) / height:.6f}",
        })
    return image.size, rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--alpha-threshold", type=int, default=128)
    parser.add_argument("--sample-step", type=int, default=2)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()
    if not 0 <= args.alpha_threshold <= 255:
        parser.error("--alpha-threshold must be between 0 and 255")
    if args.sample_step < 1:
        parser.error("--sample-step must be at least 1")

    all_rows = []
    sources = {}
    for view in VIEWS:
        source = REFERENCE_DIR / f"{view}.png"
        size, rows = extract_rows(view, source, args.alpha_threshold, args.sample_step)
        sources[source.name] = {"size_px": list(size), "sha256": sha256(source)}
        all_rows.extend(rows)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = args.output_dir / "dad-silhouette-profiles.csv"
    fields = list(all_rows[0])
    with csv_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(all_rows)

    manifest = {
        "purpose": "measurement aid only; not a 3D model or approval",
        "source_assets_unchanged": True,
        "alpha_threshold_inclusive": args.alpha_threshold,
        "sample_step_px": args.sample_step,
        "origin_convention": "z_fraction_from_ground=0 at source canvas bottom and 1 at top; x is measured from source canvas center",
        "boundary_convention": "leftmost/rightmost pixels at or above alpha threshold for each sampled row; transparent holes are intentionally collapsed to the outer silhouette",
        "source_views": sources,
        "csv": csv_path.name,
        "sample_count": len(all_rows),
    }
    manifest_path = args.output_dir / "dad-silhouette-profiles.manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(all_rows)} silhouette samples to {csv_path}")
    print(f"Wrote source/hash manifest to {manifest_path}")


if __name__ == "__main__":
    main()
