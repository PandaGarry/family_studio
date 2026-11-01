# Blender WebAssembly runtime probe

This is a small browser harness for the pinned `@volter/blender-engine@0.1.148` package. It boots Blender 5.2.0 LTS in a worker, executes the Dad blockout through Blender's Python API, asks Blender's native Cycles renderer for three previews, then flushes the project as a real `.blend` file.

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
- Browser writes are limited to the three preview PNGs and one `.blend` file in the explicit artifact allowlist.
- Outputs, once a browser session successfully completes, are written to `assets/renders/dad-blockout/` and `assets/models/dad/`.
- The active harness rebuilds the R3 neutral Dad blockout, which the user rated 9/10 as a proportion base; it is not a production model/rig/animation.
- The later full-figure procedural R4 study was rejected by the user at 1/10. It is archived separately and is not run by this harness or used as the next modeling base.

The workspace under `tools/blender-wasm-runtime/workspace/` and `node_modules/` are ignored. No paid render service is required. Engine bytes are served from the installed package, not downloaded by the browser from a cloud renderer.

## Licensing

The engine package and compiled Blender payload are GPL-3.0-or-later. The package's complete license text, including its Blender notice and dependency-license references, is retained in [`THIRD_PARTY_LICENSES/volter-blender-engine-0.1.148-LICENSE.txt`](THIRD_PARTY_LICENSES/volter-blender-engine-0.1.148-LICENSE.txt). See [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md). Keep those notices with any redistribution of the runtime or its Blender artifacts.
