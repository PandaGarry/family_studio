# Blender WebAssembly runtime — Dad head studies

This local harness runs the pinned `@volter/blender-engine@0.1.148` build of Blender 5.2.0 LTS in browser WebAssembly, creates exploratory characters through Blender Python, renders native Cycles views and saves editable `.blend` files. Scripted mesh authoring is not manual sculpting.

## Current study: V8 — MPFB2 works, likeness not approved

MPFB2 v2.0.18 was registered and exercised in Blender 5.2 WASM: it created the Human base mesh, accepted measured eye and cheek/jaw targets, assigned a layered skin material, saved a `.blend`, and rendered four views. Actual CC0 proxies from the HumanGenWeb/MakeHuman system-assets set were fitted for eyes, brows, hair, clothes and shoes. The short-hair candidates still have scalp/fit defects; no beard proxy was found; the best outfit proxy is a short-sleeve T-shirt rather than the requested crewneck sweater, and the shoe proxies expose toes. WASM compatibility is confirmed, but likeness and clothing are not approved; no Plan B was needed.

- [V8 interim side-by-side review and license/access notes](../../assets/renders/dad-head-study-v8/REVIEW_V8.md)
- [V8 reference-vs-MPFB2 face board](../../assets/renders/dad-head-study-v8/REVIEW_BOARD.png)
- [V8 diagnostic renders](../../assets/renders/dad-head-study-v8/)
- [Self-contained unapproved V8 MPFB2 scene](../../assets/models/dad/studies/dad-head-study-v8-mpfb-unapproved.blend) (11 MB, packed textures; diagnostic only)
- Working WASM scene: `workspace/models/dad-head-study-v8-mpfb.blend`

## Earlier study: V6 — still not approved

V6 is a separate study from the official Blender Human Base Meshes v1.4.1 `GEO-head_stylized` source. The cap and beard are geometry, not texture-only, but visual review still finds the hair too smooth/helmet-like and the beard too mask-like for the Dad turnaround. It is a diagnostic study, not a production base.

- [V6 unapproved editable Blender scene](../../assets/models/dad/studies/dad-head-study-v6-unapproved.blend)
- [V6 visual review and acceptance notes](../../assets/renders/dad-head-study-v6/REVIEW.md)
- [V6 front / three-quarter / profile / close-up renders](../../assets/renders/dad-head-study-v6/)
- [V6 scripted geometry builder](src/dad_head_study_v6.py)

## Shared studio render rig

[`src/studio_render_pipeline.py`](src/studio_render_pipeline.py) provides `setup_studio_review_rig(...)`: it derives world-space bounds from subject geometry, creates a consistent Cycles/AgX lighting setup, and names predictable orthographic front, three-quarter, profile, back and close-up cameras. Pass the character's renderable objects and a short prefix; resolution, samples, frame margin and studio colors are configurable. V6's browser/WASM harness executes this shared module with its builder and successfully rendered the four principal review views.

This is a reusable **starting point**, not yet a validated universal production renderer: it has been tested on a head/bust study, not yet across the project's full-body characters or different material/lighting styles. Future characters should use the same camera/light baseline, then get reference-specific framing and material checks before approval.

- Shared rig: [`src/studio_render_pipeline.py`](src/studio_render_pipeline.py)
- V6 WASM render harness: [`_v6_render.html`](./_v6_render.html)

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

- Approved Dad masters remain the source of truth; light crewneck/no hood is unchanged. V8 now contains a diagnostic full-body proxy assembly, not an approved body, outfit, or likeness.
- The 934 measured silhouette samples have **not** yet been applied numerically to V1 or V2. The available scene guides and custom profiles do not make these a verified likeness transfer.
- Do not proceed to body, production topology, rig or animation from V1/V2. User review is the approval gate.
- No paid cloud renderer is required. Browser cross-origin isolation is required for WebAssembly threads.
- The engine package and compiled Blender payload are GPL-3.0-or-later; retain notices in [`THIRD_PARTY_LICENSES/`](THIRD_PARTY_LICENSES/) and [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).
