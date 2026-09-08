import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as T from '../dist/vendor/three.module.js';
import {floorAt,isWalkable,constrainStep,routeBetween,routePoint,routeLength,createSpatialShell} from '../dist/spatial-layout.js';
const layout=JSON.parse(fs.readFileSync(new URL('../dist/data/gallery-layout.json',import.meta.url)));
assert.equal(layout.rooms.length,6);assert.equal(layout.rooms[3].footprint.length,12);assert.equal(layout.rooms[3].height,8);
assert.deepEqual(layout.rooms.map(r=>r.width),[9,9,8,14,9,12]);
assert.deepEqual(layout.rooms[3].exhibits.map(e=>e.id),['canon-1','canon-2','canon-3']);
assert.equal(layout.rooms[5].exhibits[0].id,'authority-boundary');
for(const d of layout.portals){assert.ok(isWalkable(layout,{x:d.x,z:-d.depth}));assert.ok(!isWalkable(layout,{x:d.x+d.width/2+.3,z:-d.depth}));const a={x:d.x+d.width/2+.3,z:-d.depth+.4};if(isWalkable(layout,a)){const b=constrainStep(layout,a,{x:a.x,z:a.z-2});assert.ok(b.z>-d.depth+.2,'No tunnelling through portal shoulders');}}
for(let i=0;i<=100;i++){const z=-layout.ramp.start-i*(layout.ramp.end-layout.ramp.start)/100;assert.ok(Math.abs(floorAt(layout,{x:0,z})-.35*i/100)<1e-6);}
const crystal=layout.crystal;assert.ok(!isWalkable(layout,crystal));assert.ok(!isWalkable(layout,{x:0,z:2}));assert.ok(!isWalkable(layout,{x:0,z:-73}));
let prior={x:0,z:-2},routes=0;
for(const r of layout.rooms)for(const e of r.exhibits){
 for(const distance of [2.2,3,6.3]){
  const end={x:e.x+Math.sin(e.angle)*distance,z:e.z+Math.cos(e.angle)*distance};
  if(!isWalkable(layout,end))continue;
  const route=routeBetween(layout,prior,end);assert.ok(route,'Route to '+e.id);assert.ok(routeLength(route)<120);
  for(let i=0;i<=200;i++)assert.ok(isWalkable(layout,routePoint(route,i/200)),'Collision on '+e.id);
  prior=end;routes++;
 }
}
// Wide-room movement is no longer clamped to the old 2.5m corridor lane.
assert.ok(isWalkable(layout,{x:5.8,z:-47}));assert.ok(!isWalkable(layout,{x:6.8,z:-40.5}));
const shell=createSpatialShell(layout);assert.equal(shell.group.children.length,layout.architecture.length);
const floors=createSpatialShell(layout,{picking:true});assert.ok(floors.group.children.length>=6);assert.ok(floors.group.children.every(m=>m.material.visible===false));
shell.group.updateMatrixWorld(true);
// Compare walking height with the actual exported tread surfaces, on both sides.
const treads=shell.group.children.filter(m=>m.name==='Three shallow side steps');
assert.equal(treads.length,6);
for(const tread of treads){
 const ray=new T.Raycaster(new T.Vector3(tread.position.x,2,tread.position.z),new T.Vector3(0,-1,0));
 const hit=ray.intersectObject(tread,false)[0];assert.ok(hit);
 assert.ok(Math.abs(floorAt(layout,tread.position)-hit.point.y)<1e-6,'Walking height must match the visible tread');
}
assert.ok(Math.abs(floorAt(layout,{x:layout.ramp.width/2+.2,z:-layout.ramp.end})-layout.ramp.rise)<1e-6);
for(const r of layout.rooms)for(const m of r.exhibits){
 const normal=new T.Vector3(Math.sin(m.angle),0,Math.cos(m.angle)),p=new T.Vector3(m.x,m.y,m.z);
 const ray=new T.Raycaster(p.clone().addScaledVector(normal,.05),normal.clone().negate(),0,.5);
 const hits=ray.intersectObjects(shell.group.children,false);assert.ok(hits.length,'Backing wall missing '+m.id);assert.ok(hits[0].distance>.05&&hits[0].distance<.22,'Wall mount must remain just ahead of wall '+m.id+' '+hits[0].distance);
 assert.ok(m.y+1.4<r.floor+r.height,'Plaque hits ceiling '+m.id);
}
shell.dispose();floors.dispose();console.log('PASS: six footprints, 12-sided core, '+routes+' safe observation routes, wide-room bounds, portals, no tunnelling, ramp, crystal clearance, shared preview geometry and every wall mount.');
