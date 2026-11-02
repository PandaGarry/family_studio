import { BlenderRuntime } from '@volter/blender-engine/browser';
const out = document.getElementById('out');
const log = (s) => { out.textContent += '\n' + s; console.log(s); };
const asBase64 = (value) => {
  const bytes = new Uint8Array(value);
  let binary = '';
  const chunk = 0x8000;
  for (let i = 0; i < bytes.length; i += chunk) {
    binary += String.fromCharCode(...bytes.subarray(i, i + chunk));
  }
  return btoa(binary);
};
let runtime;
try {
  if (!window.crossOriginIsolated || typeof SharedArrayBuffer === 'undefined') throw new Error('Blender WASM requires cross-origin isolation');
  const response = await fetch('/api/config');
  if (!response.ok) throw new Error('Runtime config HTTP ' + response.status);
  const config = await response.json();
  runtime = new BlenderRuntime({stage: async()=>{}, present: async()=>({held:null}), log:(level,text)=>log(level+': '+text)});
  log('Open disposable V8 copy; source V8 remains unchanged');
  await runtime.start(config.projectRoot, 'models/dad-beard-pair-agpl3-unapproved.blend');
  const probe = await fetch('/src/v9_beard_pair_probe.py').then(r => { if (!r.ok) throw new Error('Probe script HTTP ' + r.status); return r.text(); });
  const built = await runtime.execute(probe, true, 'Fit Full_beard + grinsegold_moustache under explicit AGPL3 diagnostic permission');
  log('BUILD: ' + String(built).slice(-8000));
  if (/Error executing code|Traceback \(most recent call last\)/i.test(String(built))) throw new Error(String(built));
  const views = [
    ['V8_MPF_FRONT','beard-pair-front.png',640,800],
    ['V8_MPF_THREE_QUARTER','beard-pair-three-quarter.png',640,800],
    ['V8_MPF_PROFILE','beard-pair-profile.png',640,800],
    ['V8_MPF_FACE_CLOSEUP','beard-pair-face-closeup.png',800,800],
  ];
  const images = {};
  for (const [camera,file,width,height] of views) {
    const result = await runtime.nativePreview({camera,width,height,samples:48});
    images[file] = asBase64(await runtime.readFile(result.path));
    log('RENDERED '+file+' '+width+'x'+height+' '+result.seconds.toFixed(1)+' s');
  }
  await runtime.stop(); runtime=null;
  window.__probeImages = images;
  window.__probeDone = true;
  log('BEARD PAIR PROBE DONE');
} catch (e) {
  log('ERROR: '+(e.stack||e));
  window.__probeError = String(e.stack||e);
  window.__probeDone = true;
  if(runtime){try{await runtime.stop()}catch(stopError){log('STOP ERROR: '+stopError)}}
}
