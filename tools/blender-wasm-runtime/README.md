# Blender WebAssembly runtime probe

This is a small browser harness for the pinned `@volter/blender-engine@0.1.148` package. It boots Blender 5.2.0 LTS in a worker, executes the Dad R4 hero-model script through Blender's Python API, asks Blender's native Cycles renderer for full-body front/¾/profile/back and face-closeup previews, then flushes the project as a real `.blend` file.

## Run locally

Requirements: Node.js 20.19+ (tested with Node 22.22.3), a modern browser with `SharedArrayBuffer`, and a secure browser context. From the repository root:

```sh
cd tools/blender-wasm-runtime
npm install
npm run dev
```

Open the Vite address printed in the terminal. The page starts the test automatically only when `crossOriginIsolated` is true; otherwise the log explains that the preview host did not preserve the required COOP/COEP headers. The server listens on `0.0.0.0` for the Arena preview proxy. It is a development harness, not an internet-facing production service.

## What it serves and saves

- The Vite middleware serves the pinned engine's Brotli assets at `/__editor/blender-wasm/*` with the required MIME and `Content-Encoding` headers.
- The project bridge stages the preserved Dad reference images in an ignored local workspace and persists the Blender document there while the session runs.
- Browser writes are limited to the preserved R3 blockout outputs and the R4 hero-model v1 PNGs/`.blend` in the explicit artifact allowlist.
- R4 outputs, once a browser session successfully completes, are written to `assets/renders/dad-hero-v1/` and `assets/models/dad/dad-hero-v1.blend`; the approved R3 blockout remains preserved separately.
- R4 v1 is a complete colored static figure for likeness/lookdev review, not yet a production topology, UV-ready, rigged or animated final asset. Its approval gates and known next steps live in [`docs/series/roadmap.md`](../../docs/series/roadmap.md).

The workspace under `tools/blender-wasm-runtime/workspace/` and `node_modules/` are ignored. No paid render service is required. Engine bytes are served from the installed package, not downloaded by the browser from a cloud renderer.

## Licensing

The engine package and compiled Blender payload are GPL-3.0-or-later. The package's complete license text, including its Blender notice and dependency-license references, is retained in [`THIRD_PARTY_LICENSES/volter-blender-engine-0.1.148-LICENSE.txt`](THIRD_PARTY_LICENSES/volter-blender-engine-0.1.148-LICENSE.txt). See [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md). Keep those notices with any redistribution of the runtime or its Blender artifacts.
