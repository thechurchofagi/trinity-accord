import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as T from '../dist/vendor/three.module.js';
import {makeWallFrame,makeWallPlaque,resizeWallPlaque,WALL_PLAQUE} from '../dist/wall-presentation.js';
const layout=JSON.parse(fs.readFileSync(new URL('../dist/data/gallery-layout.json',import.meta.url)));
for(const height of [.4,.9,1.3,1.7]){
 const group=new T.Group();const f=makeWallFrame(group,1.2,height);const face=makeWallPlaque(group,new T.Texture(),1.2,height);
 assert.equal(face.position.x,0);assert.ok(face.position.y-WALL_PLAQUE.height/2>height/2+.018);assert.equal(f.frame.children.length,4);
 const body=group.children.find(o=>o.name==='Satin titanium plaque');assert.equal(body.geometry.parameters.width,1.236);assert.equal(body.geometry.parameters.height,.72);assert.ok(body.material.metalness>=.8);resizeWallPlaque(face,.8,height);assert.ok(Math.abs(body.geometry.parameters.width-.836)<1e-9);assert.equal(face.position.y,body.position.y);
}
for(const r of layout.rooms){
 for(const m of r.exhibits){if(m.kind==='pedestal')continue;const group=new T.Group();group.position.set(m.x,m.y,m.z);group.rotation.y=m.angle;const f=makeWallFrame(group,1.9,1.7);assert.equal(group.children.length,1);assert.equal(f.frame.children.length,4);assert.ok(-m.z>r.start&&-m.z<r.start+r.length);assert.ok(m.y+1.4<r.floor+r.height);}
 if(r.id==='originals')continue;
 for(const side of [-1,1]){const mounts=r.exhibits.filter(e=>Math.sign(e.x)===side);for(let i=1;i<mounts.length;i++)assert.ok(Math.abs(mounts[i].z-mounts[i-1].z)>=1.94,'Frames overlap '+r.id);}
}
const buffer=fs.readFileSync(new URL('../dist/assets/gallery/memory-gallery.glb',import.meta.url));assert.equal(buffer.readUInt32LE(0),0x46546c67);const len=buffer.readUInt32LE(12),model=JSON.parse(buffer.subarray(20,20+len));assert.ok(model.nodes.length>0);assert.ok(!model.nodes.some(n=>/^(Mount |Mat |Frame edge |Caption plate |Chapter upright)/.test(n.name||'')),'No baked legacy backs or posts');
console.log('PASS: original-ratio four-edge frames, uniform plaques, valid positions throughout the selected route, ceiling/spacing clearance, and no obsolete baked backboards.');
