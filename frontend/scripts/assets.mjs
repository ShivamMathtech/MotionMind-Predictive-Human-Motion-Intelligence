import {mkdir,copyFile,readdir,stat,writeFile,readFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
for(const p of ['public/vendor','public/wasm','public/models'])await mkdir(path.join(root,p),{recursive:true});
const source=path.join(root,'node_modules/@mediapipe/tasks-vision');
await copyFile(path.join(source,'vision_bundle.cjs'),path.join(root,'public/vendor/vision_bundle.js'));
for(const name of await readdir(path.join(source,'wasm')))await copyFile(path.join(source,'wasm',name),path.join(root,'public/wasm',name));
const model=path.join(root,'public/models/pose_landmarker_lite.task');
try{if((await stat(model)).size<1000000)throw Error('Incomplete model');console.log('Bundled pose model found.');}
catch{
 const url='https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task';
 console.log('Downloading the official MediaPipe Pose Lite model…');
 const response=await fetch(url,{signal:AbortSignal.timeout(120000)});
 if(!response.ok)throw Error(`Model download failed (${response.status}). See docs/TROUBLESHOOTING.md.`);
 const bytes=Buffer.from(await response.arrayBuffer());if(bytes.length<1000000)throw Error('Model file is incomplete.');await writeFile(model,bytes);
}
console.log('Local model and WASM assets ready. No remote model calls are required at runtime.');
