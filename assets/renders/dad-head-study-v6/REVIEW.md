# Dad head study V6 — review (not approved)

**Status: NOT APPROVED.** V6 is an iteration, not an approved character model or a likeness claim. It starts from a separate copy of the official Blender Human Base Meshes v1.4.1 `GEO-head_stylized`; the source bundle remains untouched. The generator uses scripted geometry, not manual sculpting.

## Render set

- `front.png` — 640 × 800
- `three-quarter.png` — 640 × 800
- `profile.png` — 640 × 800
- `face-closeup.png` — 640 × 640

These are native Cycles renders from the Blender WASM runtime using the shared bounds-based studio rig. The editable, unapproved scene is `assets/models/dad/studies/dad-head-study-v6-unapproved.blend`.

## Review against the Dad turnaround

| Criterion | Result | Observation |
|---|---|---|
| Hairstyle reads as hair rather than a bald dome | **Fail** | The cap is too smooth and helmet-like. The geometry relief is not yet convincing as the short, swept-up quiff in the reference. |
| No spikes | **Pass** | Experimental exposed tube/loft strands were removed. The current render avoids spike tips, but this leaves the hair too uniform. |
| Rounded occipital profile | **Partial** | The back remains rounded, but the complete scalp silhouette is still too uniform. |
| Beard is geometric and integrated | **Partial / fail** | A separate surface-conforming shell is present, and a UV feather helps soften the border. In the front/profile renders the beard still reads too much like a broad face mask. |
| Moustache | **Fail** | The volume patches are less wire-like than earlier curves but still read as a narrow bar, not the softly integrated moustache in the reference. |
| Eyes, eyelids, natural neck | **Partial** | The official orbital and eye geometry remains recognizable; adult likeness and the bust/neck transition still need refinement. |
| Overall front/profile likeness | **Fail** | Neither view matches the supplied turnaround closely enough for approval. |

## Verification

- `py_compile` passed for the V6 builder and shared render module.
- Executed the builder with the shared render module in Blender WASM from a fresh copy of the official-base scene — succeeded.
- Rendered and visually inspected all four views — succeeded; acceptance criteria remain unmet.

## Reusable renderer status

`tools/blender-wasm-runtime/src/studio_render_pipeline.py` now supplies bounds-derived orthographic front, three-quarter, profile, back and face-close-up cameras, plus a consistent Cycles/AgX studio-light baseline. It is integrated into the V6 harness and tested on this head/bust. It is a solid reusable starting point, **not yet validated as universal** across full-body characters, unusual proportions, or varied material styles.

## Next direction

Do not promote V6. Continue by replacing the smooth-cap appearance with broad, low-profile swept volumes that remain embedded and non-spiky; keep refining the beard/moustache as one coherent shape; compare front/profile directly to the turnaround. Apply the studio rig to a full-body character only after a separate framing/material check. Preserve the official source bundle and keep these studies separate from `character.json`.
