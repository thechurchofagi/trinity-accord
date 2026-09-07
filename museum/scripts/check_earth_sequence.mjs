import assert from 'node:assert/strict';
import {createEarthSequence,EARTH_FRAMES} from '../dist/earth-sequence.js';
let live=0,peak=0,shown=[],failNext=false,loads=[];
const settle=()=>new Promise(resolve=>setImmediate(resolve));
const sequence=createEarthSequence(async file=>{
 loads.push(file);
 if(failNext){failNext=false;throw Error('temporary offline');}
 live++;peak=Math.max(peak,live);
 return {file,dispose(){live--;}};
},(current,next,mix)=>shown.push([current.file,next?.file,mix]));
await sequence.load();await settle();sequence.update(0);sequence.update(9999);
assert.equal(shown.length,1);assert.equal(shown[0][0],EARTH_FRAMES[0]);
sequence.update(10000);assert.equal(shown.at(-1)[1],EARTH_FRAMES[1]);assert.equal(shown.at(-1)[2],0);
sequence.update(10750);assert.equal(shown.at(-1)[2],.5);
sequence.update(11500);assert.equal(shown.at(-1)[0],EARTH_FRAMES[1]);await settle();
for(let i=2;i<=6;i++){
 sequence.update(i*10000);sequence.update(i*10000+1500);await settle();
 assert.equal(shown.at(-1)[0],EARTH_FRAMES[i%6]);
}
assert.equal(peak,2,'Must not retain all six decoded textures');
// Hidden-tab time must not advance the sequence when its clock is reset.
sequence.resetClock();const before=shown.length;sequence.update(900000);assert.equal(shown.length,before);
// A failed preload holds the previous image, retries later, then resumes.
failNext=true;sequence.update(908500);sequence.update(910000);await settle();
const held=shown.at(-1)[0];sequence.update(918500);assert.equal(shown.at(-1)[0],held);
sequence.update(920000);await settle();sequence.update(920001);sequence.update(921501);await settle();
assert.notEqual(shown.at(-1)[0],held);assert.equal(peak,2);
let firstFails=true;
const retry=createEarthSequence(async()=>{if(firstFails){firstFails=false;throw Error('offline');}return {dispose(){}};},()=>{});
assert.equal(await retry.load(),false);assert.equal(await retry.load(),true);
console.log('PASS: six frames, 10-second cadence, smooth crossfade, loop wrap, two-texture limit, visibility pause and failed-load recovery.');
