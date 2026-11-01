import { BlenderRuntime } from '@volter/blender-engine/browser';
import buildDadScript from './dad_hero_v1.py?raw';
import './style.css';

const statusNode = document.querySelector('#status');
const progressNode = document.querySelector('#progress');
const logNode = document.querySelector('#log');
const rendersNode = document.querySelector('#renders');
const buildButton = document.querySelector('#build');

let runtime = null;
let projectRoot = null;
let running = false;

async function report(type, message, extra = {}) {
  const line = `[${new Date().toLocaleTimeString()}] ${message}`;
  logNode.textContent += `${line}\n`;
  logNode.scrollTop = logNode.scrollHeight;
  try {
    await fetch('/api/runtime-event', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ type, message, ...extra }),
    });
  } catch {
    // The on-page log remains useful if the diagnostic endpoint is unavailable.
  }
}

function setStatus(text, progress) {
  statusNode.textContent = text;
  if (progress !== undefined) progressNode.style.width = `${Math.max(0, Math.min(100, progress))}%`;
}

function safeError(error) {
  return error instanceof Error ? `${error.name}: ${error.message}` : String(error);
}

async function getConfig() {
  const response = await fetch('/api/config');
  if (!response.ok) throw new Error(`Runtime config returned HTTP ${response.status}`);
  return response.json();
}

function addRender(title, artifactName, bytes) {
  const blob = new Blob([bytes], { type: 'image/png' });
  const url = URL.createObjectURL(blob);
  const figure = document.createElement('figure');
  const image = document.createElement('img');
  const caption = document.createElement('figcaption');
  const link = document.createElement('a');
  image.src = url;
  image.alt = `Cycles render — ${title}`;
  caption.textContent = title;
  link.href = `/api/artifacts/${encodeURIComponent(artifactName)}`;
  link.textContent = 'PNG';
  link.download = artifactName;
  figure.append(image, caption, link);
  rendersNode.append(figure);
}

async function uploadPreview(name, bytes) {
  const response = await fetch(`/api/artifacts/${encodeURIComponent(name)}`, {
    method: 'POST',
    headers: { 'Content-Type': 'image/png' },
    body: bytes,
  });
  if (!response.ok) throw new Error(`Could not save ${name}: HTTP ${response.status}`);
  return response.json();
}

async function renderCamera(camera, width, height, samples) {
  const result = await runtime.nativePreview({ width, height, samples, camera });
  if (result.renderer !== 'CYCLES' || result.width !== width || result.height !== height || result.samples !== samples) {
    throw new Error(`Unexpected native preview result: ${JSON.stringify(result)}`);
  }
  const png = await runtime.readFile(result.path);
  return { png, metadata: result };
}

async function buildAndRender() {
  if (running) return;
  running = true;
  buildButton.disabled = true;
  rendersNode.replaceChildren();
  document.querySelector('.model-link')?.remove();
  progressNode.style.width = '0%';

  try {
    if (!window.crossOriginIsolated || typeof SharedArrayBuffer === 'undefined') {
      throw new Error('Страница не cross-origin isolated. COOP/COEP не дошли до браузера; WebAssembly runtime не запускается в этом preview-контексте.');
    }
    await report('info', 'Browser isolation confirmed; initializing BlenderRuntime.');
    setStatus('Подготовка проекта…', 3);
    const config = await getConfig();
    projectRoot = config.projectRoot;
    runtime = new BlenderRuntime({
      log: (level, message) => { void report(level, String(message)); },
      // This harness renders through Blender's native Cycles API and has no interactive
      // Three.js viewport; accept staged frame transport without pretending to display it.
      stage: async () => {},
      present: async (_frame, _description, _capture) => ({ held: null }),
    });

    await report('info', `Starting ${config.blender}; project root: ${projectRoot}`);
    setStatus('Загрузка Blender WebAssembly…', 8);
    const started = await runtime.start(projectRoot, 'models/dad-hero-v1.blend');
    await report('ready', 'BlenderRuntime.start() resolved.', { started });
    setStatus('Blender запущен · строю 3D-сцену…', 45);
    progressNode.style.width = '48%';

    const configPlaceholder = '__FAMILY_STUDIO_PROJECT_ROOT__';
    const python = buildDadScript.replace(configPlaceholder, projectRoot.replaceAll('\\', '\\\\'));
    const execution = await runtime.execute(python, true, 'Build the Dad R4 hero model v1');
    await report('python', 'Blender Python R4 hero-model script executed.', { result: String(execution).slice(0, 1200) });
    if (typeof execution === 'string' && /Error executing code|Traceback \(most recent call last\)/i.test(execution)) {
      throw new Error(execution);
    }

    const views = [
      { camera: 'CAM_Front', title: 'Full figure · Front · Cycles', file: 'dad-hero-v1-front.png', width: 512, height: 896, samples: 64 },
      { camera: 'CAM_ThreeQuarter', title: 'Full figure · ¾ · Cycles', file: 'dad-hero-v1-three-quarter.png', width: 512, height: 896, samples: 64 },
      { camera: 'CAM_Profile', title: 'Full figure · Profile · Cycles', file: 'dad-hero-v1-side.png', width: 512, height: 896, samples: 64 },
      { camera: 'CAM_Back', title: 'Full figure · Back · Cycles', file: 'dad-hero-v1-back.png', width: 512, height: 896, samples: 64 },
      { camera: 'CAM_FaceCloseup', title: 'Face close-up · Cycles', file: 'dad-hero-v1-face.png', width: 512, height: 512, samples: 80 },
    ];
    for (let index = 0; index < views.length; index += 1) {
      const view = views[index];
      setStatus(`Cycles render ${index + 1}/${views.length}: ${view.title}`, 52 + index * 8);
      await report('render', `Starting native Cycles preview: ${view.camera}`);
      const { png, metadata } = await renderCamera(view.camera, view.width, view.height, view.samples);
      const saved = await uploadPreview(view.file, png);
      addRender(view.title, view.file, png);
      await report('rendered', `${metadata.renderer} ${metadata.width}×${metadata.height}, ${metadata.samples} samples, ${metadata.seconds.toFixed(2)} s; saved ${saved.path} (${saved.bytes} bytes).`);
    }

    setStatus('Cycles готов · сохраняю .blend…', 92);
    await runtime.stop();
    runtime = null;
    const published = await fetch('/api/publish-document?name=dad-hero-v1.blend', { method: 'POST' });
    if (!published.ok) throw new Error(`Could not publish .blend: HTTP ${published.status} ${await published.text()}`);
    const artifact = await published.json();
    const modelLink = document.createElement('p');
    modelLink.className = 'model-link';
    modelLink.innerHTML = `Настоящий Blender hero-model файл сохранён: <a href="/api/artifacts/dad-hero-v1.blend" download>dad-hero-v1.blend</a> · ${artifact.bytes.toLocaleString()} bytes · <code>${artifact.path}</code>`;
    rendersNode.before(modelLink);
    setStatus('Готово · R4 hero model v1 · Blender Python + native Cycles подтверждены', 100);
    await report('complete', `Verified Blender WASM, Python execution, native Cycles and .blend save: ${artifact.path}.`, artifact);
  } catch (error) {
    const message = safeError(error);
    setStatus(`Ошибка: ${message}`, 0);
    await report('error', message);
    if (runtime) {
      try {
        await runtime.stop();
      } catch (stopError) {
        await report('error', `Runtime cleanup failed: ${safeError(stopError)}`);
      }
      runtime = null;
    }
  } finally {
    running = false;
    buildButton.disabled = false;
  }
}

buildButton.addEventListener('click', buildAndRender);

if (window.crossOriginIsolated && typeof SharedArrayBuffer !== 'undefined') {
  void buildAndRender();
} else {
  setStatus('Preview не cross-origin isolated — WASM запуск остановлен', 0);
  void report('warning', 'crossOriginIsolated is false at initial page load.');
}
