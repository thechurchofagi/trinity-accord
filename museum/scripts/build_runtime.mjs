// npm ci (optional build tooling), then node scripts/build_runtime.mjs.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {build,version} from 'esbuild';
const root=fileURLToPath(new URL('../',import.meta.url)),dist=path.join(root,'dist');
const names={rooms:'rooms.json',sources:'sources.json',layout:'gallery-layout.json',illustrations:'curatorial-illustrations.json',curation:'curation.json',stars:'bright-stars.json',lyrics:'lyrics-index.json'};
const data=Object.fromEntries(Object.entries(names).map(([key,name])=>[key,JSON.parse(fs.readFileSync(path.join(dist,'data',name),'utf8'))]));
fs.writeFileSync(path.join(dist,'edition-data.js'),'// Generated from the frozen edition JSON; no startup manifest requests.\nexport default '+JSON.stringify(data)+';\n');
const result=await build({absWorkingDir:root,entryPoints:['dist/museum.js'],outfile:'dist/museum.bundle.js',bundle:true,minify:true,format:'iife',target:'es2022',legalComments:'eof',metafile:true});
const record=p=>{const b=fs.readFileSync(path.join(root,p));return {path:p,bytes:b.length,sha256:crypto.createHash('sha256').update(b).digest('hex')};};
const report={schema:'trinity-museum.runtime-build.v1',edition:data.rooms.edition,esbuild:version,inputs:[...new Set([...Object.keys(result.metafile.inputs),'scripts/build_runtime.mjs',...Object.values(names).map(n=>'dist/data/'+n)])].sort().map(record),output:record('dist/museum.bundle.js')};
// A rebuilt bundle and stylesheet must not reuse an earlier mobile cache entry.
const runtimeVersion=data.rooms.edition.replace('museum-v','')+'.'+report.output.sha256.slice(0,12);
const cssVersion=crypto.createHash('sha256').update(fs.readFileSync(path.join(dist,'museum.css'))).digest('hex').slice(0,12);
const loader=path.join(dist,'boot-loader.js'),html=path.join(dist,'index.html');
fs.writeFileSync(loader,fs.readFileSync(loader,'utf8').replace(/museum\.bundle\.js\?v=[^']+/,'museum.bundle.js?v='+runtimeVersion));
fs.writeFileSync(html,fs.readFileSync(html,'utf8').replace(/boot-loader\.js\?v=[^"]+/,'boot-loader.js?v='+runtimeVersion).replace(/href="\.\/museum\.css(?:\?v=[^"]+)?"/,'href="./museum.css?v='+cssVersion+'"'));
fs.writeFileSync(path.join(root,'scene/runtime-build.json'),JSON.stringify(report,null,2)+'\n');
console.log('Runtime bundle:',report.output.bytes,'bytes; edition data included; no external runtime imports');
