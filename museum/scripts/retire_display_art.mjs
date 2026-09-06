// Withdraw 2026 illustrations from the current export, retaining edition history.
import fs from 'node:fs';
process.chdir(new URL('../',import.meta.url).pathname);
const dir='history/withdrawn-art-2026';fs.mkdirSync(dir,{recursive:true});
const p='dist/data/curatorial-illustrations.json',manifest=JSON.parse(fs.readFileSync(p));
const files=[...manifest.items.map(e=>e.file),'assets/curatorial/star-ark-2026.webp'];
for(const file of files){const from='dist/'+file;if(fs.existsSync(from))fs.renameSync(from,dir+'/'+file.split('/').at(-1));}
if(manifest.items.length)fs.copyFileSync(p,dir+'/curatorial-illustrations.json');
const star='dist/data/star-ark-illustration.json';if(fs.existsSync(star))fs.renameSync(star,dir+'/star-ark-illustration.json');
fs.writeFileSync(p,JSON.stringify({schema:manifest.schema,edition:'museum-v1.20.0',scope:'All 2026 art illustrations withdrawn at the author’s request. Only original source images are exhibited.',items:[]},null,2)+'\n');
fs.writeFileSync(dir+'/README.md','# Withdrawn exhibition illustrations\n\nRemoved from the live exhibition in museum-v1.20.0 at the author’s request.\nThese are later 2026 illustrations, not original NFT or Bitcoin content.\nRetained here only as exhibition history; original manifests describe their prior distribution paths.\n');
console.log('Withdrawn',files.length,'illustrations from the export.');
