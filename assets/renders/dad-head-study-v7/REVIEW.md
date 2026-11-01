# Dad head study V7 — review (not approved)

**Status: NOT APPROVED.** This is a procedural geometry experiment and an unapproved likeness study, not a production character or claim that the Dad reference has been matched. Do not promote it into `character.json`, the approved-model path, a rig, or the shared rendering baseline.

## Evidence

- `front.png` — 640 × 800
- `three-quarter.png` — 640 × 800
- `profile.png` — 640 × 800
- `face-closeup.png` — 640 × 640
- Editable scene: `assets/models/dad/studies/dad-head-study-v7-unapproved.blend`
- Builder: `tools/blender-wasm-runtime/src/dad_head_study_v7.py`

The scene was rebuilt from a fresh copy of the official Blender Human Base Meshes v1.4.1 scene; the source bundle was not modified. The renders were produced with Cycles in the Blender WASM runtime and the shared bounds-based studio render pipeline. All four generated images were visually inspected after the final build.

## Review against the Dad turnaround

| Criterion | Result | Observation |
|---|---|---|
| Eye size, exposure and fit | **Partial / fail** | The sclera meshes are scaled to 70% of their V6 dimensions and moved forward from the first V7 trial; the iris and official orbital forms remain. Both eyes are more exposed than in the earlier V7 render, but the sockets still read too dark and the eyes remain oversized relative to the Dad reference. No eyelid ribbons are used because the prior ribbon test created conspicuous concentric rings. |
| Nose bridge and tip | **Partial** | The bridge and rounded tip are larger than V6 and more legible in profile, but the overall likeness still needs reference-led proportion work. |
| Hair silhouette and detail | **Fail** | Hair is a separate, shallow raised scalp mesh with low-profile geometric relief. It still reads as a smooth cap/helmet; the hairline is visibly uneven, and the cap lacks the reference's grouped, swept-up clumps. |
| Beard and moustache | **Fail** | A separate raised, surface-conforming shell and moustache mesh replace the face shader mask. The volume is technically geometric, but the dark, sharply bounded surface still reads as a patch rather than integrated facial hair. |
| Ears and bust | **Partial** | Ears are clear of the cap and the facial hair no longer paints over them. The bust remains a study, not approved body geometry. |
| Overall likeness | **Fail** | Front, three-quarter and profile do not yet match the supplied turnaround closely enough. The study is not accepted. |

## Technical verification

- `python -m py_compile tools/blender-wasm-runtime/src/dad_head_study_v7.py` — passed.
- Rebuilt from a fresh official bundle copy in Blender WASM — passed.
- Builder output: `source_mesh_faces: 4134`, `hair_cap_faces: 330`, `beard_shell_faces: 8640`.
- Four Cycles renders completed and were visually inspected — passed as a render-workflow check only; artistic acceptance criteria remain unmet.

## MPFB2 source/license and runtime check

Reviewed the `makehumancommunity/mpfb2` repository snapshot at commit [`6ff1eb358f6c1959ced77e79e6dd2406d9a71f49`](https://github.com/makehumancommunity/mpfb2/tree/6ff1eb358f6c1959ced77e79e6dd2406d9a71f49):

- [`LICENSE.md`](https://github.com/makehumancommunity/mpfb2/blob/6ff1eb358f6c1959ced77e79e6dd2406d9a71f49/LICENSE.md) identifies MPFB program code as GPLv3 and bundled graphical assets as CC0 1.0; the repository supplies separate `LICENSE.CODE.md` and `LICENSE.ASSETS.md` files.
- The [`base.obj` header](https://github.com/makehumancommunity/mpfb2/blob/6ff1eb358f6c1959ced77e79e6dd2406d9a71f49/src/mpfb/data/3dobjs/base.obj) also explicitly says the base mesh was released as CC0 in September 2020.
- The [`README`](https://github.com/makehumancommunity/mpfb2/blob/6ff1eb358f6c1959ced77e79e6dd2406d9a71f49/README.md) states that version 2.x requires Blender 4.2 or newer. The add-on itself has **not** been installed or tested in this Blender-WASM renderer.
- Hair/facial-hair names in the add-on are asset presets, while the hair-asset editor expects separately installed asset-pack data. No hairstyle or beard asset pack was imported; its exact license and WASM behavior would need separate verification.

This investigation verifies a license path for the repository's bundled base assets, not for every third-party asset pack, and does not establish add-on compatibility with the current renderer. No MPFB2 mesh or code is included in this V7 study.

## Next direction

Do not approve or promote V7. Rework the hair silhouette with broader, better-grouped geometry rather than a smooth scalp cap; soften and reshape the beard edge so it reads as hair, not a facial mask; continue tuning eye exposure against the face reference. If evaluating MPFB2 hair/facial-hair assets, first obtain and verify the license for the specific pack and test the resulting geometry in the WASM runtime. Keep the Dad and shared renderer unapproved until visual evidence supports acceptance.
