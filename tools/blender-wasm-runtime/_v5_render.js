import { BlenderRuntime } from '@volter/blender-engine/browser';
const out = document.getElementById('out');
const log = (s) => { out.textContent += '\n' + s; console.log(s); };
let runtime;
try {
  if (!window.crossOriginIsolated || typeof SharedArrayBuffer === 'undefined') throw new Error('Blender WASM requires cross-origin isolation');
  const response = await fetch('/api/config');
  if (!response.ok) throw new Error('Runtime config HTTP ' + response.status);
  const config = await response.json();
  runtime = new BlenderRuntime({stage: async()=>{}, present: async()=>({held:null}), log:(level,text)=>log(level+': '+text)});
  log('Open fresh copy of official Human Base Meshes v1.4.1');
  await runtime.start(config.projectRoot, 'models/dad-head-study-v5.blend');
  const code = await (await fetch('/src/dad_head_study_v5.py')).text();
  const built = await runtime.execute(code, true, 'Build unapproved Dad V5 with separate hair/beard meshes');
  log('BUILD: ' + String(built).slice(-4000));
  if (/Error executing code|Traceback \(most recent call last\)/i.test(String(built))) throw new Error(String(built));
  const views = [
    ['V5_FRONT','dad-head-study-v5-front.png',640,800],
    ['V5_THREE_QUARTER','dad-head-study-v5-three-quarter.png',640,800],
    ['V5_PROFILE','dad-head-study-v5-profile.png',640,800],
    ['V5_FACE_CLOSEUP','dad-head-study-v5-face-closeup.png',640,640],
  ];
  for (const [camera,file,width,height] of views) {
    const result = await runtime.nativePreview({camera,width,height,samples:40});
    const png = await runtime.readFile(result.path);
    const saved = await fetch('/api/artifacts/'+file,{method:'POST',headers:{'Content-Type':'image/png'},body:png});
    if (!saved.ok) throw new Error('Save failed: '+file+' '+await saved.text());
    log('RENDERED '+file+' '+width+'x'+height+' '+result.seconds.toFixed(1)+' s');
  }
  await runtime.stop(); runtime=null;
  log('V5 study saved in runtime workspace; original official bundle untouched. DONE');
} catch (e) {
  log('ERROR: '+(e.stack||e));
  if(runtime){try{await runtime.stop()}catch(stopError){log('STOP ERROR: '+stopError)}}
}
