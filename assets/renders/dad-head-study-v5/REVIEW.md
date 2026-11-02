# Dad head study V5 — review (not approved)

**Status: NOT APPROVED.** These are real Blender WASM renders of the current scripted V5 scene, not a likeness approval. The official Blender Human Base Meshes v1.4.1 `GEO-head_stylized` remains the starting mesh; its source bundle was left untouched. This is generated geometry and materials, not manual sculpting.

## Render set

- `front.png` — 640 × 800
- `three-quarter.png` — 640 × 800
- `profile.png` — 640 × 800
- `face-closeup.png` — 640 × 640

## Front/profile review against the Dad turnaround

| Criterion | Result | Observation |
|---|---|---|
| Hair silhouette / no separate spherical cap | **Fail** | The scalp still reads as a smooth bald helmet. Its subtle lifted surface does not produce the short, swept-up hairstyle in the turnaround. |
| No spikes | **Pass for this render** | The experimental raised tube-locks were removed; no strand spikes are present. |
| Beard as convincing volume | **Fail** | The separate shell renders, but its cheek/top boundaries remain visibly angular and mask-like in front and three-quarter views. |
| Moustache | **Fail** | The two small raised curves still look like disconnected, crossing strokes instead of a soft integrated moustache. |
| Face / eyes / eyelids | **Partial** | The official stylized orbital forms and separate eyes render, but the overall eye scale and facial likeness still need comparison/refinement. |
| Nape / neck | **Partial** | The rear skull is rounded; the nape transition remains visibly irregular, and the neck-to-bust finish is not yet convincing. |
| Overall likeness | **Fail** | The front and profile do not yet match the supplied Dad turnaround closely enough. |

## Verification

- `python -m py_compile tools/blender-wasm-runtime/src/dad_head_study_v5.py` — passed.
- Rebuilt from a fresh copy of the official-base `.blend` in the Blender WASM harness — succeeded.
- Re-rendered all four views and inspected them — succeeded, with the failures above.

## Next iteration

Do not promote or reuse this as an approved Dad model. Replace the smooth cap appearance with non-spiky, swept volumetric hair forms; redesign the beard silhouette and moustache together as a softer, integrated shape; then inspect front and profile against the reference before making any approval claim. Keep this study separate from `character.json` and preserve the official base bundle.
