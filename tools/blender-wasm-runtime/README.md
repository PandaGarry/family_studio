# Blender WebAssembly runtime — historical technical harness

This folder retains the pinned `@volter/blender-engine@0.1.148` package setup and technical verification notes. The earlier harness executed a procedural Dad blockout through Blender's Python API, rendered it in native Cycles, and saved a `.blend`; the user has since rejected **both** that R3 blockout as a model base and the later R4 procedural model. The current browser page is intentionally inert: it does not launch Blender, regenerate either rejected mesh, or present them as approved work.

## Run the status page locally

Requirements: Node.js 20.19+ and npm. From the repository root:

```sh
cd tools/blender-wasm-runtime
npm install
npm run dev
```

The static page explains that no Dad 3D model is currently approved. The pinned Blender WebAssembly package and project bridge remain in the repository as historical technical infrastructure, but no active modeling operation is connected to the page. This is not a production modeling app.

## Archived results

- R3 gray blockout `.blend`, Cycles previews, and generator are in explicitly named rejected/archive paths. The user had earlier rated it 9/10 as a proportion base, then clarified that the blockout itself is unsuitable and must not be used as the base.
- R4 procedural study was rated 1/10 and rejected; it is separately archived.
- No accepted Dad mesh, clean production topology, rig, animation, or final character render currently exists.
- The old renderer could establish that Blender WASM, Blender Python, native Cycles, and `.blend` save/reopen worked. That proves only technical execution—not likeness, professional quality, or an interactive sculpting workflow.

## Professional workflow constraints

The target is a faithful 2D/2.5D-to-3D transfer that preserves every visible feature and passes user-led side-by-side review. Python scripts may help set up aligned reference plates, cameras, measurement overlays, and repeatable renders; they must not substitute primitive assembly for hand-authored character modeling. Generic base meshes, text-to-3D, Subdivision, texture projection, and lighting are not shortcuts to the required likeness. The environment has not confirmed a native interactive Blender UI, so the next modeling stage must not be promised until an actual local sculpt/modeling path is verified.

No paid cloud renderer is required. The engine package and compiled Blender payload are GPL-3.0-or-later; retain the package and dependency notices in [`THIRD_PARTY_LICENSES/`](THIRD_PARTY_LICENSES/) and [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).
