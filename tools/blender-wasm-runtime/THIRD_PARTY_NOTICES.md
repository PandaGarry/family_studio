# Third-party notices

## `@volter/blender-engine` 0.1.148

- Package: `@volter/blender-engine@0.1.148`, pinned in `package.json` and `package-lock.json`.
- Upstream repository: <https://github.com/volter-ai/editor>, package directory `packages/blender-engine`.
- Runtime bundle/source metadata identifies the Blender source repository as <https://github.com/volter-ai/blender>; Blender version is 5.2.0 LTS.
- License: GNU General Public License, version 3 or later (GPL-3.0-or-later). Blender is identified in the package's license notice as GPL-2.0-or-later, conveyed under the package's GPL-3.0-or-later terms.
- Full package license: [`THIRD_PARTY_LICENSES/volter-blender-engine-0.1.148-LICENSE.txt`](THIRD_PARTY_LICENSES/volter-blender-engine-0.1.148-LICENSE.txt).
- Dependency attributions from the package's `wasm/DEPENDENCY-LICENSES.txt`: [`THIRD_PARTY_LICENSES/volter-blender-engine-dependency-licenses.txt`](THIRD_PARTY_LICENSES/volter-blender-engine-dependency-licenses.txt).

This harness imports the package as an npm dependency rather than copying its runtime modules into Family Studio. The package's compiled WebAssembly and JavaScript are served locally by the Vite development server. Do not strip or replace upstream copyright and license notices.
