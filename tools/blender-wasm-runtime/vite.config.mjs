import { defineConfig } from 'vite';
import { createHash } from 'node:crypto';
import { copyFile, mkdir, readdir, readFile, stat, utimes, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const toolRoot = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(toolRoot, '../..');
const workspace = path.join(toolRoot, 'workspace');
const engineWasm = path.join(toolRoot, 'node_modules/@volter/blender-engine/wasm');
const references = path.join(repoRoot, 'assets/references/character-masters/characters/dad');
const pendingDocuments = new Map();
const documentChunks = new Map();

const archivedArtifacts = {
  'dad-blockout-r3-rejected.blend': path.join(repoRoot, 'assets/models/dad/rejected/dad-blockout-r3-rejected.blend'),
  'dad-blockout-r3-rejected-front.png': path.join(repoRoot, 'assets/renders/dad-blockout-r3-rejected/front.png'),
  'dad-blockout-r3-rejected-three-quarter.png': path.join(repoRoot, 'assets/renders/dad-blockout-r3-rejected/three-quarter.png'),
  'dad-blockout-r3-rejected-side.png': path.join(repoRoot, 'assets/renders/dad-blockout-r3-rejected/side.png'),
};

const candidateArtifacts = {
  'dad-head-study-v1.blend': path.join(repoRoot, 'assets/models/dad/studies/dad-head-study-v1.blend'),
  'dad-head-study-v1-front.png': path.join(repoRoot, 'assets/renders/dad-head-study-v1/front.png'),
  'dad-head-study-v1-three-quarter.png': path.join(repoRoot, 'assets/renders/dad-head-study-v1/three-quarter.png'),
  'dad-head-study-v1-profile.png': path.join(repoRoot, 'assets/renders/dad-head-study-v1/profile.png'),
  'dad-head-study-v1-face-closeup.png': path.join(repoRoot, 'assets/renders/dad-head-study-v1/face-closeup.png'),
  'dad-head-study-v1-review-board.png': path.join(repoRoot, 'assets/renders/dad-head-study-v1/review-board.png'),
  'dad-head-study-v2.blend': path.join(repoRoot, 'assets/models/dad/studies/dad-head-study-v2.blend'),
  'dad-head-study-v2-front.png': path.join(repoRoot, 'assets/renders/dad-head-study-v2/front.png'),
  'dad-head-study-v2-three-quarter.png': path.join(repoRoot, 'assets/renders/dad-head-study-v2/three-quarter.png'),
  'dad-head-study-v2-profile.png': path.join(repoRoot, 'assets/renders/dad-head-study-v2/profile.png'),
  'dad-head-study-v2-face-closeup.png': path.join(repoRoot, 'assets/renders/dad-head-study-v2/face-closeup.png'),
  'dad-head-study-v2-review-board.png': path.join(repoRoot, 'assets/renders/dad-head-study-v2/review-board.png'),
  'dad-head-study-v4-front.png': path.join(repoRoot, 'assets/renders/dad-head-study-v4/front.png'),
  'dad-head-study-v4-three-quarter.png': path.join(repoRoot, 'assets/renders/dad-head-study-v4/three-quarter.png'),
  'dad-head-study-v4-profile.png': path.join(repoRoot, 'assets/renders/dad-head-study-v4/profile.png'),
  'dad-head-study-v4-face-closeup.png': path.join(repoRoot, 'assets/renders/dad-head-study-v4/face-closeup.png'),
};

function json(res, status, value) {
  res.statusCode = status;
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  res.end(JSON.stringify(value));
}

function safeRelative(input) {
  if (typeof input !== 'string' || !input || input.includes('\\')) return null;
  const parts = input.split('/');
  if (parts.some((part) => !part || part === '.' || part === '..')) return null;
  return parts.join('/');
}

async function bodyBytes(req, maxBytes = 256 * 1024 * 1024) {
  const chunks = [];
  let size = 0;
  for await (const chunk of req) {
    size += chunk.length;
    if (size > maxBytes) throw new Error(`Request body exceeds ${maxBytes} bytes`);
    chunks.push(chunk);
  }
  return Buffer.concat(chunks, size);
}

async function listWorkspace(dir = workspace, prefix = '') {
  const entries = [];
  for (const name of await readdir(dir)) {
    const full = path.join(dir, name);
    const relative = prefix ? `${prefix}/${name}` : name;
    const info = await stat(full);
    if (info.isDirectory()) entries.push(...await listWorkspace(full, relative));
    else if (info.isFile()) entries.push({ path: relative, size: info.size, mtime: Math.floor(info.mtimeMs) });
  }
  return entries;
}

async function ensureWorkspace() {
  await mkdir(path.join(workspace, 'models'), { recursive: true });
  await mkdir(path.join(workspace, 'references'), { recursive: true });
  for (const name of ['front.png', 'three_quarter.png', 'side.png', 'face.png', 'turnaround.png']) {
    const source = path.join(references, name);
    const destination = path.join(workspace, 'references', `dad-${name}`);
    let sourceStat;
    try {
      sourceStat = await stat(source);
    } catch (error) {
      if (error.code === 'ENOENT') continue;
      throw error;
    }
    let destinationStat = null;
    try {
      destinationStat = await stat(destination);
    } catch (error) {
      if (error.code !== 'ENOENT') throw error;
    }
    if (!destinationStat || destinationStat.size !== sourceStat.size || Math.floor(destinationStat.mtimeMs) !== Math.floor(sourceStat.mtimeMs)) {
      await copyFile(source, destination);
      await utimes(destination, sourceStat.atime, sourceStat.mtime);
    }
  }
}

async function projectFileIndex() {
  await ensureWorkspace();
  return listWorkspace();
}

async function blenderStatus() {
  const [bundleText, essentialsText, essentialsStat] = await Promise.all([
    readFile(path.join(engineWasm, 'BUNDLE.json'), 'utf8'),
    readFile(path.join(engineWasm, 'essentials.json'), 'utf8'),
    stat(path.join(engineWasm, 'essentials.json')),
  ]);
  const bundle = JSON.parse(bundleText);
  const essentials = JSON.parse(essentialsText);
  return {
    available: true,
    skew: 'emscripten',
    dir: '/__editor/blender-wasm',
    sizes: {
      'blender_browser.js': bundle.rawFiles['blender_browser.js'].bytes,
      'blender_browser.wasm': bundle.rawFiles['blender_browser.wasm'].bytes,
      'blender_browser.data': bundle.rawFiles['blender_browser.data'].bytes,
      'essentials.json': essentialsStat.size,
      'essentials.bin': essentials.bytes,
    },
    encoded: {
      'blender_browser.wasm': 'br',
      'blender_browser.data': 'br',
      'essentials.bin': 'br',
    },
    missing: [],
  };
}

async function handle(req, res, next) {
  for (const [name, value] of Object.entries(isolationHeaders)) res.setHeader(name, value);
  const url = new URL(req.url ?? '/', 'http://family-studio.local');
  const pathname = url.pathname;
  try {
    if (pathname === '/api/config' && req.method === 'GET') {
      await ensureWorkspace();
      return json(res, 200, { projectRoot: workspace, blender: 'Blender 5.2.0 LTS / Emscripten WebAssembly' });
    }

    if (pathname === '/api/runtime-event' && req.method === 'POST') {
      const event = JSON.parse((await bodyBytes(req, 1024 * 1024)).toString('utf8'));
      const summary = String(event.message ?? '').split(String.fromCharCode(10)).join(' ').split(String.fromCharCode(13)).join(' ').slice(0, 1200);
      console.log(`[blender-wasm:${String(event.type ?? 'event')}] ${summary}`);
      res.statusCode = 204;
      res.end();
      return;
    }

    if (pathname === '/__editor/blender-wasm/status' && req.method === 'GET') {
      return json(res, 200, await blenderStatus());
    }

    if (pathname.startsWith('/__editor/blender-wasm/') && req.method === 'GET') {
      const requested = pathname.slice('/__editor/blender-wasm/'.length);
      const fileMap = {
        'blender_browser.js': ['blender_browser.js', 'text/javascript; charset=utf-8', false],
        'blender_browser.wasm': ['blender_browser.wasm.br', 'application/wasm', true],
        'blender_browser.data': ['blender_browser.data.br', 'application/octet-stream', true],
        'essentials.json': ['essentials.json', 'application/json; charset=utf-8', false],
        'essentials.bin': ['essentials.bin.br', 'application/octet-stream', true],
      };
      const entry = fileMap[requested];
      if (!entry) return json(res, 404, { error: 'Unknown Blender WebAssembly asset' });
      const bytes = await readFile(path.join(engineWasm, entry[0]));
      res.statusCode = 200;
      res.setHeader('Content-Type', entry[1]);
      res.setHeader('Content-Length', bytes.length);
      res.setHeader('Cache-Control', 'public, max-age=3600, immutable');
      if (entry[2]) res.setHeader('Content-Encoding', 'br');
      res.end(bytes);
      return;
    }

    if (pathname === '/__editor/blender-project-index' && req.method === 'GET') {
      return json(res, 200, { root: workspace, files: await projectFileIndex() });
    }

    if (pathname === '/__editor/blender-project-file' && req.method === 'GET') {
      const relative = safeRelative(url.searchParams.get('path'));
      if (!relative) return json(res, 400, { error: 'Unsafe project path' });
      const full = path.join(workspace, relative);
      const bytes = await readFile(full);
      res.statusCode = 200;
      res.setHeader('Content-Type', 'application/octet-stream');
      res.setHeader('Content-Length', bytes.length);
      res.end(bytes);
      return;
    }

    if (pathname === '/__editor/blender-document' && req.method === 'POST') {
      const relative = safeRelative(url.searchParams.get('path'));
      if (!relative || !relative.endsWith('.blend')) return json(res, 400, { error: 'Expected a project-relative .blend path' });
      const manifest = JSON.parse((await bodyBytes(req, 2 * 1024 * 1024)).toString('utf8'));
      if (!Array.isArray(manifest.chunks) || manifest.chunks.some((entry) => !Array.isArray(entry) || typeof entry[0] !== 'string' || !Number.isInteger(entry[1]) || entry[1] < 0)) {
        return json(res, 400, { error: 'Invalid Blender document chunk manifest' });
      }
      pendingDocuments.set(relative, manifest.chunks);
      const missing = manifest.chunks.filter(([hash]) => !documentChunks.has(hash)).map(([hash]) => hash);
      if (missing.length) return json(res, 200, { ok: false, missing });
      const pieces = manifest.chunks.map(([hash, length]) => {
        const piece = documentChunks.get(hash);
        if (!piece || piece.length !== length) throw new Error(`Missing or malformed Blender document chunk ${hash}`);
        return piece;
      });
      const bytes = Buffer.concat(pieces);
      await mkdir(path.dirname(path.join(workspace, relative)), { recursive: true });
      await writeFile(path.join(workspace, relative), bytes);
      pendingDocuments.delete(relative);
      for (const [hash] of manifest.chunks) documentChunks.delete(hash);
      return json(res, 200, { ok: true, ms: { write: 0 } });
    }

    if (pathname === '/__editor/blender-document-chunk' && req.method === 'POST') {
      const relative = safeRelative(url.searchParams.get('path'));
      const hash = url.searchParams.get('hash');
      if (!relative || !relative.endsWith('.blend') || !hash || !/^[a-f0-9]{64}$/.test(hash)) {
        return json(res, 400, { error: 'Invalid Blender document chunk path/hash' });
      }
      const bytes = await bodyBytes(req);
      const actual = createHash('sha256').update(bytes).digest('hex');
      if (actual !== hash) return json(res, 400, { error: 'Blender document chunk hash mismatch' });
      documentChunks.set(hash, bytes);
      res.statusCode = 204;
      res.end();
      return;
    }

    if (pathname.startsWith('/api/artifacts/') && req.method === 'POST') {
      const name = pathname.slice('/api/artifacts/'.length);
      const destination = candidateArtifacts[name];
      if (!destination || !name.endsWith('.png')) return json(res, 410, { error: 'Only allowlisted head-study PNG evidence can be published' });
      const bytes = await bodyBytes(req, 32 * 1024 * 1024);
      await mkdir(path.dirname(destination), { recursive: true });
      await writeFile(destination, bytes);
      return json(res, 201, { path: path.relative(repoRoot, destination), bytes: bytes.length });
    }

    if (pathname === '/api/publish-document' && req.method === 'POST') {
      const name = url.searchParams.get('name');
      if (!['dad-head-study-v1.blend', 'dad-head-study-v2.blend'].includes(name)) return json(res, 410, { error: 'Only allowlisted unapproved head studies can be published' });
      const source = path.join(workspace, 'models', name);
      const destination = candidateArtifacts[name];
      const bytes = await readFile(source);
      await mkdir(path.dirname(destination), { recursive: true });
      await writeFile(destination, bytes);
      return json(res, 201, { path: path.relative(repoRoot, destination), bytes: bytes.length });
    }

    if (pathname.startsWith('/api/artifacts/') && req.method === 'GET') {
      const name = pathname.slice('/api/artifacts/'.length);
      const destination = archivedArtifacts[name] ?? candidateArtifacts[name];
      if (!destination) return json(res, 404, { error: 'Artifact name is not in the allowlist' });
      const bytes = await readFile(destination);
      res.statusCode = 200;
      res.setHeader('Content-Type', name.endsWith('.png') ? 'image/png' : 'application/octet-stream');
      res.setHeader('Content-Length', bytes.length);
      res.setHeader('Content-Disposition', `attachment; filename="${name}"`);
      res.end(bytes);
      return;
    }

    next();
  } catch (error) {
    if (res.headersSent) return res.end();
    json(res, 500, { error: error instanceof Error ? error.message : String(error) });
  }
}

function blenderRuntimePlugin() {
  return {
    name: 'family-studio-blender-wasm-runtime',
    configureServer(server) {
      server.middlewares.use((req, res, next) => { void handle(req, res, next); });
    },
    configurePreviewServer(server) {
      server.middlewares.use((req, res, next) => { void handle(req, res, next); });
    },
  };
}

const isolationHeaders = {
  'Cross-Origin-Opener-Policy': 'same-origin',
  'Cross-Origin-Embedder-Policy': 'credentialless',
  'Origin-Agent-Cluster': '?1',
};

export default defineConfig({
  root: toolRoot,
  plugins: [blenderRuntimePlugin()],
  server: { host: '0.0.0.0', port: 5173, strictPort: true, allowedHosts: true, headers: isolationHeaders },
  preview: { host: '0.0.0.0', port: 4173, strictPort: true, allowedHosts: true, headers: isolationHeaders },
});
