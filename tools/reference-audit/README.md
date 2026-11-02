# Dad reference-audit utilities

`extract_silhouette_profiles.py` reads the alpha channels of the unchanged Dad front, three-quarter and side master crops and emits sampled outer silhouette coordinates. It does not alter the reference images and does not generate a model.

## Run

From the repository root:

```sh
python -m pip install -r tools/reference-audit/requirements.txt
python tools/reference-audit/extract_silhouette_profiles.py
```

Outputs are written to `assets/references/character-masters/characters/dad/derived/`:

- `dad-silhouette-profiles.csv` — 934 samples at a 2-pixel vertical step, alpha threshold 128.
- `dad-silhouette-profiles.manifest.json` — source image sizes and SHA-256 hashes, threshold, coordinate conventions and limitations.

The row envelope deliberately records only the outermost alpha-covered pixels; transparent interior gaps are collapsed. The three-quarter crop is a reference validation view, not assumed to be orthographic depth data. Treat these values as measured image-space constraints; do not infer unsupported hidden geometry or assign world units without a documented scale decision.
