import assert from 'node:assert/strict';
import fs from 'node:fs';
import {advanceWalk} from '../dist/walk-progress.js';
import {routeBetween,routeLength,routePoint,isWalkable,floorAt} from '../dist/spatial-layout.js';
const layout=JSON.parse(fs.readFileSync(new URL('../dist/data/gallery-layout.json',import.meta.url)));
const source={x:0,z:-2},end={x:1,z:-59},route=routeBetween(layout,source,end),length=routeLength(route);
assert.ok(route&&length>55);source.z=-30;end.x=5;
assert.equal(route[0].z,-2,'Camera mutation must not move the route origin');assert.equal(route.at(-1).x,1);
let d=0,prior=routePoint(route,0),steps=0;
while(d<length){const dt=[1/60,1/30,.35,9,0,1/20][steps%6],next=advanceWalk(d,length,dt);assert.ok(next-d<=.1250001,'Slow frames never catch up');const point=routePoint(route,next/length);assert.ok(Math.hypot(point.x-prior.x,point.z-prior.z)<=.1250001);assert.ok(isWalkable(layout,point));assert.ok(Number.isFinite(floorAt(layout,point)+layout.eyeHeight));d=next;prior=point;steps++;}
assert.equal(advanceWalk(3,10,0),3);assert.equal(advanceWalk(3,10,NaN),3);assert.equal(advanceWalk(3,10,60),3.125);assert.equal(advanceWalk(9.99,10,1),10);
const c=layout.crystal;assert.equal(c.width,.246);assert.equal(c.height,.353);assert.equal(c.thickness,.04);assert.ok(!isWalkable(layout,c));assert.ok(!isWalkable(layout,{x:c.x+c.pedestalRadius-.01,z:c.z}));
console.log('PASS: immutable cross-room routes, bounded frame distance, no hidden-time catch-up, fixed eye height and physical pedestal clearance.');
