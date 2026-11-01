# Imported references from `PandaGarry/docuflow`

These are direct, pixel-preserving copies of the character masters, view crops, and `character.json` files from the user's earlier project. They are **modeling references**, not finished Family Studio renders, textures, or approved final character designs.

- Source repository: <https://github.com/PandaGarry/docuflow>
- Source ref: `main`
- Source commit: `6c8023123ab8130b7a3b61b0c2b836b5b06a1de9`
- Source paths: `studio/characters/{dad,mom,son}/`
- Transfer date: 2026-11-01
- Integrity manifest: [`SHA256SUMS`](SHA256SUMS)
- Permission: the repository owner explicitly authorized reuse in this project. The source repository has no separate LICENSE file, so preserve this provenance and do not treat the files as third-party stock assets.

## Files

Each character folder contains the original `master/turnaround.png`, `master/face.png`, crops from `views/{front,three_quarter,side}.png`, and `character.json`. The directory layout is flattened only for convenience; the source file names and pixels are unchanged.

The turnarounds have a green reference background. Keep it as reference-plate background only: it is not part of the model or scene, must not be sampled into materials, and must not appear in a final render. The face/master and view files are likewise for visual comparison; inspect their alpha/background before any image processing.

The three `character.json` files preserve the source metadata as-is. They contain useful proportions, palette and identity constraints, but are not automatically validated modeling measurements. In particular, Dad's metadata calls the home top `hoodie_gray` while the visible turnaround reads as a light-gray crewneck with no visible hood; resolve this canon discrepancy with the author rather than silently changing the reference.

`motion/` contains three selected walk/run still sheets and one small run-rig MP4. The stills were inspected and show visible cropping/seam artifacts; use them only to study timing/pose, never as an approved visual target. The MP4 has not been reviewed. For the code/animation review and the decision not to treat the old procedural render as Blender output, see [`docs/series/docuflow-migration-review.md`](../../../docs/series/docuflow-migration-review.md).