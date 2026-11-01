# Blender WebAssembly runtime — Dad head study v1

This local harness runs the pinned `@volter/blender-engine@0.1.148` build of Blender 5.2.0 LTS in browser WebAssembly, authors an exploratory custom-mesh head study through Blender Python, renders native Cycles views, and saves an editable `.blend` file. Approved masters are packed as viewport guides, but the 934 measured silhouette samples have **not** yet been used numerically to drive this mesh. Scripted mesh authoring is not manual sculpting.

## Current result and quality gate

The script executed and saved the scene and four real Cycles renders. The first likeness pass **failed visual review**: the hair reads as spikes, the beard as a single mask, and the face does not sufficiently follow the approved master. It is an exploratory geometry diagnostic only—not a blockout promoted as a model, an approved likeness, or production work. Do not build body, topology, rig, or animation on this result. R3 and R4 remain rejected and are not used as a base.

- Blender scene: [`assets/models/dad/studies/dad-head-study-v1.blend`](../../assets/models/dad/studies/dad-head-study-v1.blend)
- iPhone-friendly review board: [`assets/renders/dad-head-study-v1/review-board.png`](../../assets/renders/dad-head-study-v1/review-board.png)
- Individual front / three-quarter / profile / close-up renders: [`assets/renders/dad-head-study-v1/`](../../assets/renders/dad-head-study-v1/)
- Source script: [`src/dad_head_study_v1.py`](src/dad_head_study_v1.py)
- Reference measurements: [`assets/references/character-masters/characters/dad/derived/dad-silhouette-profiles.csv`](../../assets/references/character-masters/characters/dad/derived/dad-silhouette-profiles.csv)

## Run the technical harness

Requirements: Node.js 20.19+ and npm. From the repository root:

```sh
cd tools/blender-wasm-runtime
npm ci
npm run dev
```

The page loads the saved review renders without starting Blender. Use the explicit button only when a fresh render is needed; it replaces the workspace scene with the current exploratory script and saves the new unapproved result. Native Cycles rendering takes several minutes in this browser runtime.

## Constraints

- Reviews use only approved Dad masters. The light crewneck/no hood lock remains unchanged; this iteration is head-only.
- Measured silhouette CSV rows are image-space observations, not approved 3D geometry.
- No paid cloud renderer is required. Browser cross-origin isolation is required for WebAssembly threads.
- A successful render or valid `.blend` proves technical execution only. The user’s visual assessment is the approval gate.
- The engine package and compiled Blender payload are GPL-3.0-or-later; retain the notices in [`THIRD_PARTY_LICENSES/`](THIRD_PARTY_LICENSES/) and [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).
