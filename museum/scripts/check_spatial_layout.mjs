import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as T from '../dist/vendor/three.module.js';
import {floorAt,isWalkable,constrainStep,routeBetween,routePoint,routeLength,createSpatialShell} from '../dist/spatial-layout.js';
const layout=JSON.parse(fs.readFileSync(new URL('../dist/data/gallery-layout.json',import.meta.url)));
assert.equal(layout.rooms.length,5);assert.equal(layout.rooms[3].footprint.length,12);assert.equal(layout.rooms[3].height,8);
assert.deepEqual(layout.rooms.map(r=>r.width),[9,9,8,14,12]);
assert.deepEqual(layout.rooms[3].exhibits.map(e=>e.id),['canon-1','canon-2','canon-3','evidence-path','physical-alpha','eth-084','eth-170']);
assert.equal(layout.rooms[4].exhibits[0].id,'authority-boundary');
for(const d of layout.portals){assert.equal(d.visualOnly,true);assert.ok(isWalkable(layout,{x:d.x,z:-d.depth}));}
assert.equal(layout.ramp,null);
// Cross the old shoulders away from the former narrow doorway without obstruction.
for(const depth of [6,30])for(const x of [-3,3]){const a={x,z:-depth+.4},b=constrainStep(layout,a,{x,z:-depth-.4});assert.ok(Math.abs(b.z+depth+.4)<1e-6,'Light boundaries must be pass-through');}
for(let z=-.5;z>-63;z-=.5)assert.equal(floorAt(layout,{x:0,z}),0);
const crystal=layout.crystal;assert.ok(!isWalkable(layout,crystal));assert.ok(!isWalkable(layout,{x:0,z:2}));assert.ok(!isWalkable(layout,{x:0,z:-73}));
let prior={x:0,z:-2},routes=0;
for(const r of layout.rooms)for(const e of r.exhibits){
 if(e.kind==='pedestal')continue;
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
const floors=createSpatialShell(layout,{picking:true});assert.ok(floors.group.children.length===5);assert.ok(floors.group.children.every(m=>m.material.visible===false));
shell.group.updateMatrixWorld(true);
// The visible floor and collision plane are level throughout all five rooms.
assert.ok(!shell.group.children.some(m=>/step|ramp|Portal shoulder|Portal lintel/i.test(m.name)));
for(const r of layout.rooms){const z=-r.start-r.length/2,x=r.id==='originals'?2:0;const ray=new T.Raycaster(new T.Vector3(x,2,z),new T.Vector3(0,-1,0));const hit=ray.intersectObjects(shell.group.children,false).find(h=>h.object.userData.surface==='stone');assert.ok(hit);assert.ok(Math.abs(hit.point.y-floorAt(layout,{x,z}))<1e-6);}
for(const r of layout.rooms)for(const m of r.exhibits){
 if(m.kind==='pedestal')continue;
 const normal=new T.Vector3(Math.sin(m.angle),0,Math.cos(m.angle)),p=new T.Vector3(m.x,m.y,m.z);
 const ray=new T.Raycaster(p.clone().addScaledVector(normal,.05),normal.clone().negate(),0,.5);
 const hits=ray.intersectObjects(shell.group.children,false);assert.ok(hits.length,'Backing wall missing '+m.id);assert.ok(hits[0].distance>.05&&hits[0].distance<.22,'Wall mount must remain just ahead of wall '+m.id+' '+hits[0].distance);
 assert.ok(m.y+1.4<r.floor+r.height,'Plaque hits ceiling '+m.id);
}
shell.dispose();floors.dispose();console.log('PASS: five footprints, 12-sided core, '+routes+' safe observation routes, wide-room bounds, pass-through boundaries, level floors, crystal clearance, shared preview geometry and every wall mount.');
