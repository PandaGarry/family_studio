import { BlenderRuntime } from '@volter/blender-engine/browser';
import buildDadScript from './dad_head_study_v1.py?raw';
import './style.css';

const statusNode = document.querySelector('#status');
const progressNode = document.querySelector('#progress');
const logNode = document.querySelector('#log');
const rendersNode = document.querySelector('#renders');
const buildButton = document.querySelector('#build');

let runtime = null;
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
    // Keep the in-page log usable if diagnostics are unavailable.
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
  const blobUrl = URL.createObjectURL(new Blob([bytes], { type: 'image/png' }));
  const figure = document.createElement('figure');
  const image = document.createElement('img');
  const caption = document.createElement('figcaption');
  const link = document.createElement('a');
  image.src = blobUrl;
  image.alt = `Blender Cycles review render — ${title}`;
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
  if (!response.ok) throw new Error(`Could not save ${name}: HTTP ${response.status} ${await response.text()}`);
  return response.json();
}

async function renderCamera(camera, width, height, samples) {
  const result = await runtime.nativePreview({ width, height, samples, camera });
  if (result.renderer !== 'CYCLES' || result.width !== width || result.height !== height || result.samples !== samples) {
    throw new Error(`Unexpected native preview result: ${JSON.stringify(result)}`);
  }
  return { png: await runtime.readFile(result.path), metadata: result };
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
      throw new Error('Эта вкладка не cross-origin isolated; Blender WebAssembly не может безопасно запуститься в данном preview-контексте.');
    }
    await report('info', 'Browser isolation confirmed; initializing BlenderRuntime.');
    setStatus('Подготовка проекта…', 3);
    const config = await getConfig();
    runtime = new BlenderRuntime({
      log: (level, message) => { void report(level, String(message)); },
      // Render evidence is produced by Blender's native Cycles API; no viewport frame is claimed.
      stage: async () => {},
      present: async () => ({ held: null }),
    });

    await report('info', `Starting ${config.blender}; project root: ${config.projectRoot}`);
    setStatus('Загрузка Blender WebAssembly…', 8);
    const started = await runtime.start(config.projectRoot, 'models/dad-head-study-v1.blend');
    await report('ready', 'BlenderRuntime.start() resolved.', { started });

    setStatus('Создаю custom head study в Blender…', 42);
    const python = buildDadScript.replace('__FAMILY_STUDIO_PROJECT_ROOT__', config.projectRoot.replaceAll('\\', '\\\\'));
    const execution = await runtime.execute(python, true, 'Build Dad head study v1 (unapproved)');
    await report('python', 'Blender Python head-study script executed.', { result: String(execution).slice(0, 1500) });
    if (typeof execution === 'string' && /Error executing code|Traceback \(most recent call last\)/i.test(execution)) {
      throw new Error(execution);
    }

    const views = [
      { camera: 'CAM_Front', title: 'Front · head study', file: 'dad-head-study-v1-front.png', width: 420, height: 560, samples: 36 },
      { camera: 'CAM_ThreeQuarter', title: 'Three-quarter · head study', file: 'dad-head-study-v1-three-quarter.png', width: 420, height: 560, samples: 36 },
      { camera: 'CAM_Profile', title: 'Profile · head study', file: 'dad-head-study-v1-profile.png', width: 420, height: 560, samples: 36 },
      { camera: 'CAM_FaceCloseup', title: 'Face close-up · head study', file: 'dad-head-study-v1-face-closeup.png', width: 512, height: 512, samples: 48 },
    ];

    for (let index = 0; index < views.length; index += 1) {
      const view = views[index];
      const progress = 48 + (index / views.length) * 36;
      setStatus(`Cycles render ${index + 1}/${views.length}: ${view.title}`, progress);
      await report('render', `Starting native Cycles preview: ${view.camera}`);
      const { png, metadata } = await renderCamera(view.camera, view.width, view.height, view.samples);
      const saved = await uploadPreview(view.file, png);
      addRender(view.title, view.file, png);
      await report('rendered', `${metadata.renderer} ${metadata.width}×${metadata.height}, ${metadata.samples} samples, ${metadata.seconds.toFixed(2)} s; saved ${saved.path} (${saved.bytes} bytes).`);
    }

    setStatus('Рендеры готовы · сохраняю Blender-файл…', 88);
    await runtime.stop();
    runtime = null;
    const published = await fetch('/api/publish-document?name=dad-head-study-v1.blend', { method: 'POST' });
    if (!published.ok) throw new Error(`Could not publish .blend: HTTP ${published.status} ${await published.text()}`);
    const artifact = await published.json();
    const modelLink = document.createElement('p');
    modelLink.className = 'model-link';
    modelLink.innerHTML = `Сцена Blender сохранена для технического осмотра: <a href="/api/artifacts/dad-head-study-v1.blend" download>dad-head-study-v1.blend</a> · ${artifact.bytes.toLocaleString()} bytes · <code>${artifact.path}</code>. Это не ручная скульптура и не одобренная модель.`;
    rendersNode.before(modelLink);
    setStatus('Технический запуск завершён · likeness review не пройден и не предполагается', 100);
    await report('complete', `Unapproved head study rendered with Blender WASM + native Cycles and saved as ${artifact.path}.`, artifact);
  } catch (error) {
    const message = safeError(error);
    setStatus(`Ошибка: ${message}`, 0);
    await report('error', message);
    if (runtime) {
      try {
        await runtime.stop();
      } catch (stopError) {
        await report('error', `Runtime cleanup/save failed: ${safeError(stopError)}`);
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
  setStatus('Среда готова · можно запускать Blender WASM', 0);
} else {
  setStatus('Preview не cross-origin isolated — запуск WASM остановлен', 0);
  buildButton.disabled = true;
  void report('warning', 'crossOriginIsolated is false at initial page load.');
}
