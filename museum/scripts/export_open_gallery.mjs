// Export the exact shared procedural shell as a self-contained glTF, without stale baked walls.
import fs from 'node:fs';
import crypto from 'node:crypto';
import {createSpatialShell} from '../dist/spatial-layout.js';
const root=new URL('../',import.meta.url),layout=JSON.parse(fs.readFileSync(new URL('scene/gallery-layout.json',root)));
const shell=createSpatialShell(layout),chunks=[],views=[],accessors=[],meshes=[],nodes=[],materials=[],materialIds=new Map();let offset=0;
function buffer(array,target){const b=Buffer.from(array.buffer,array.byteOffset,array.byteLength),id=views.length;views.push({buffer:0,byteOffset:offset,byteLength:b.length,target});const pad=Buffer.alloc((4-b.length%4)%4);chunks.push(b,pad);offset+=b.length+pad.length;return id;}
function attribute(a,type,target){const id=accessors.length,componentType=a.array instanceof Float32Array?5126:a.array instanceof Uint32Array?5125:5123;const d={bufferView:buffer(a.array,target),componentType,count:a.count,type};if(type==='VEC3'){d.min=[0,1,2].map(i=>{let v=Infinity;for(let n=i;n<a.array.length;n+=3)v=Math.min(v,a.array[n]);return v;});d.max=[0,1,2].map(i=>{let v=-Infinity;for(let n=i;n<a.array.length;n+=3)v=Math.max(v,a.array[n]);return v;});}accessors.push(d);return id;}
for(const o of shell.group.children){
 const m=o.material;if(!materialIds.has(m)){materialIds.set(m,materials.length);materials.push({name:m.name||o.userData.surface,pbrMetallicRoughness:{baseColorFactor:[m.color.r,m.color.g,m.color.b,m.opacity],metallicFactor:m.metalness||0,roughnessFactor:m.roughness??1},...(m.transparent?{alphaMode:'BLEND'}:{}),doubleSided:m.side===2,extras:{surface:o.userData.surface}});}
 const g=o.geometry;const primitive={attributes:{POSITION:attribute(g.attributes.position,'VEC3',34962),NORMAL:attribute(g.attributes.normal,'VEC3',34962)},material:materialIds.get(m)};if(g.index)primitive.indices=attribute(g.index,'SCALAR',34963);
 meshes.push({name:o.name,primitives:[primitive]});nodes.push({name:o.name,mesh:meshes.length-1,translation:o.position.toArray(),rotation:o.quaternion.toArray(),extras:{...o.userData}});
}
const model={asset:{version:'2.0',generator:'Trinity shared procedural architecture / v1.34'},scene:0,scenes:[{nodes:nodes.map((_,i)=>i)}],nodes,meshes,materials,buffers:[{byteLength:offset}],bufferViews:views,accessors};
let json=Buffer.from(JSON.stringify(model));json=Buffer.concat([json,Buffer.alloc((4-json.length%4)%4,32)]);const bin=Buffer.concat(chunks),header=Buffer.alloc(20),bh=Buffer.alloc(8);header.writeUInt32LE(0x46546c67,0);header.writeUInt32LE(2,4);header.writeUInt32LE(28+json.length+bin.length,8);header.writeUInt32LE(json.length,12);header.writeUInt32LE(0x4e4f534a,16);bh.writeUInt32LE(bin.length,0);bh.writeUInt32LE(0x004e4942,4);
fs.writeFileSync(new URL('dist/assets/gallery/memory-gallery.glb',root),Buffer.concat([header,json,bh,bin]));
const files=['scripts/export_open_gallery.mjs','scripts/prepare_open_gallery.py','dist/spatial-layout.js','scene/gallery-layout.json','dist/assets/gallery/memory-gallery.glb'].map(path=>{const b=fs.readFileSync(new URL(path,root));return {path,bytes:b.length,sha256:crypto.createHash('sha256').update(b).digest('hex')};});
fs.writeFileSync(new URL('scene/build-provenance.json',root),JSON.stringify({schema:'trinity-museum.scene-build.v3',edition:layout.edition,application:'Shared Three.js procedural geometry',baked:false,source:'scripts/export_open_gallery.mjs',layout:'scene/gallery-layout.json',note:'Current open architecture is exported from the navigation layout. Earlier Blender source and baked images are retained as historical references, not current render evidence.',files},null,2)+'\n');
console.log('Exported',nodes.length,'architecture nodes,',28+json.length+bin.length,'bytes');shell.dispose();
