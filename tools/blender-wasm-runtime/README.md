# Blender WebAssembly runtime — Dad head studies

This local harness runs the pinned `@volter/blender-engine@0.1.148` build of Blender 5.2.0 LTS in browser WebAssembly, creates custom exploratory meshes through Blender Python, renders native Cycles views and saves editable `.blend` files. Scripted mesh authoring is not manual sculpting.

## Latest: V2 — still not approved

V2 attempted the feedback-driven changes: broader skull/cheeks, smaller and more seated eyes, a stronger nose profile, a beard surface fitted to face-section estimates, and broad swept hair ribbons. Real Cycles renders show that the beard still reads as a hard mask, the quiff as spikes, and the profile likeness remains weak. This pass **failed**; it is not a usable production base.

- Blender scene: [`assets/models/dad/studies/dad-head-study-v2.blend`](../../assets/models/dad/studies/dad-head-study-v2.blend)
- iPhone-friendly review board: [`assets/renders/dad-head-study-v2/review-board.png`](../../assets/renders/dad-head-study-v2/review-board.png)
- Individual front / three-quarter / profile / close-up renders: [`assets/renders/dad-head-study-v2/`](../../assets/renders/dad-head-study-v2/)
- Source script: [`src/dad_head_study_v2.py`](src/dad_head_study_v2.py)
- [V2 visual review record](../../docs/series/dad-head-study-v2-review.md)

## Archived: V1 — failed first pass

- [V1 scene](../../assets/models/dad/studies/dad-head-study-v1.blend)
- [V1 review board](../../assets/renders/dad-head-study-v1/review-board.png)
- [V1 source script](src/dad_head_study_v1.py)

Neither V1 nor V2 is a clean, unified, production-topology base mesh, and neither represents "80% of the work." They are separate editable objects and surfaces authored procedurally. R3 and R4 remain rejected and are not used as a base.

## Run the technical harness

Requirements: Node.js 20.19+ and npm. From the repository root:

```sh
cd tools/blender-wasm-runtime
npm ci
npm run dev
```

The page loads V2's saved renders without starting Blender. Use the explicit button only when a fresh diagnostic render is wanted. It regenerates the unapproved V2 scene and takes several minutes in this browser runtime.

## Constraints and limits

- Approved Dad masters remain the source of truth; light crewneck/no hood is unchanged. This iteration is head-only.
- The 934 measured silhouette samples have **not** yet been applied numerically to V1 or V2. The available scene guides and custom profiles do not make these a verified likeness transfer.
- Do not proceed to body, production topology, rig or animation from V1/V2. User review is the approval gate.
- No paid cloud renderer is required. Browser cross-origin isolation is required for WebAssembly threads.
- The engine package and compiled Blender payload are GPL-3.0-or-later; retain notices in [`THIRD_PARTY_LICENSES/`](THIRD_PARTY_LICENSES/) and [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).
