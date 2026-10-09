import {build} from 'esbuild';import {mkdir,writeFile,rm} from 'node:fs/promises';import {pathToFileURL,fileURLToPath} from 'node:url';import path from 'node:path';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');const out=path.join(root,'tests/fixtures');await mkdir(out,{recursive:true});
const temp=path.join(root,'frontend/.demo-fixture.mjs');await build({entryPoints:[path.join(root,'frontend/src/vision/demo.ts')],bundle:true,format:'esm',outfile:temp});
const {demoPose}=await import(pathToFileURL(temp));
for(const exercise of ['squat','lunge','reverse_lunge','pushup','bicep_curl','tricep_extension','shoulder_press','lateral_raise','plank','situp','crunch','leg_raise','jumping_jack','mountain_climber']){
 const frames=Array.from({length:115},(_,i)=>({timestamp:i*.08,aspect:16/9,landmarks:demoPose(exercise,i*.08)}));await writeFile(path.join(out,exercise+'.json'),JSON.stringify(frames));
}await rm(temp);console.log('Generated 14 deterministic pose sequences.');
