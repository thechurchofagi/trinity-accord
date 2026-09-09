import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
import {guideCueAt,createRecordedGuide} from '../dist/recorded-guide.js';
import {createMicroscopeMotion,microscopePose,createMicroscopeModel} from '../dist/microscope-motion.js';
import {stopsForLanguage} from '../dist/tour-language.js';
import * as THREE from '../dist/vendor/three.module.js';
const data=JSON.parse(fs.readFileSync(new URL('../dist/data/guide-audio.json',import.meta.url)));
assert.equal(data.tracks.length,stopsForLanguage('en').length);assert.deepEqual(stopsForLanguage('zh'),stopsForLanguage('en'));
const norm=s=>s.normalize('NFKC').replace(/[^\p{L}\p{N}]/gu,'').toLowerCase();
for(const language of ['en'])for(const [index,stop] of stopsForLanguage(language).entries()){
 const tracks=data.tracks.filter(t=>t.stop===index&&t.language===language);assert.equal(tracks.length,1);const t=tracks[0];
 assert.equal(t.text,stop[language]);assert.equal(crypto.createHash('sha256').update(t.text).digest('hex'),t.textSha256);
 const audio=fs.readFileSync(new URL('../dist/'+t.file,import.meta.url));assert.equal(crypto.createHash('sha256').update(audio).digest('hex'),t.sha256);
 assert.ok(audio.length>1000&&t.duration>5);assert.ok(t.duration>0,'Narration has a measured duration');
 if(stop.musicAt!==undefined)assert.ok(Number.isFinite(stop.musicDuration)&&stop.musicDuration>0&&stop.musicDuration<=45,'Main-tour excerpts have bounded audio-clock durations');
 assert.equal(norm(t.cues.map(c=>c.text).join('')),norm(t.text),'Caption text coverage '+index+language);
 let last=0;for(const cue of t.cues){assert.ok(cue.start>=last&&cue.end>cue.start&&cue.end<t.duration+.05);last=cue.end;assert.ok(cue.textZh&&cue.words.length);assert.equal(norm(cue.words.map(w=>w.text).join(' ')),norm(cue.text));let wordEnd=cue.start;for(const w of cue.words){assert.ok(w.start>=wordEnd&&w.end>w.start);wordEnd=w.end;}assert.equal(guideCueAt(t.cues,(cue.start+cue.end)/2),cue);}
 assert.equal(guideCueAt(t.cues,t.duration+1),null);
}
class Audio extends EventTarget{
 currentTime=0;readyState=1;duration=100;paused=true;muted=false;calls=[];block=false;pending=null;
 set src(value){this.file=value;this.currentTime=0;}get src(){return this.file;}
 pause(){this.paused=true;}
 play(){this.calls.push([this.src,this.muted]);if(this.pending)return this.pending;if(this.block&&!this.muted)return Promise.reject(Object.assign(new Error('gesture'),{name:'NotAllowedError'}));this.paused=false;return Promise.resolve();}
}
const a=new Audio(),captions=[],states=[],guide=createRecordedGuide(a,{onCaption:(text,lang)=>captions.push([text,lang]),onState:s=>states.push(s)});
const first=data.tracks.find(t=>t.stop===0&&t.language==='en'),en=data.tracks.find(t=>t.stop===1&&t.language==='en');
await guide.play(first);assert.equal(a.src,first.file);assert.equal(a.playbackRate,1);a.currentTime=first.cues[1].start+.01;a.dispatchEvent(new Event('timeupdate'));assert.equal(captions.at(-1)[0],first.cues[1].text);
await guide.play(en);assert.equal(a.src,en.file);assert.equal(a.muted,false);a.currentTime=en.cues[0].start+.1;guide.paint();assert.equal(captions.at(-1)[1],'en');assert.equal(captions.at(-1)[0],en.cues[0].text);
await guide.play(first);assert.equal(a.src,first.file); // Switch back without speech synthesis or installed voices.
a.block=true;await guide.play(en);assert.equal(guide.state,'blocked');assert.equal(a.muted,false);assert.equal(a.paused,true);assert.equal(a.currentTime,0);assert.equal(a.calls.at(-1)[1],false);a.block=false;await guide.setMuted(false);assert.equal(guide.state,'playing');assert.equal(a.muted,false);
guide.setRate(1.25);assert.equal(a.playbackRate,1.25);await guide.play(first,{offset:7.5});assert.equal(a.currentTime,7.5);assert.equal(a.playbackRate,1.25);
let reject;a.pending=new Promise((_,r)=>reject=r);const old=guide.play(first);a.pending=null;await guide.play(en);reject(new Error('stale'));await old;assert.equal(guide.state,'playing');assert.equal(guide.track.language,'en');guide.stop();assert.equal(a.paused,true);assert.equal(guide.track,null);assert.equal(captions.at(-1)[0],'');
// A late autoplay rejection must not undo the user's successful enable click.
let deny;a.pending=new Promise((_,r)=>deny=r);const autoplay=guide.play(first);a.pending=null;await guide.setMuted(false);deny(Object.assign(new Error('late autoplay denial'),{name:'NotAllowedError'}));await autoplay;assert.equal(guide.state,'playing');assert.equal(a.muted,false);assert.equal(a.paused,false);guide.stop();
const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(60,1,.01,100),crystal=new THREE.Group();crystal.position.set(0,1,-3);scene.add(crystal);let frame=null,photos=0;
const scope=createMicroscopeMotion(scene,camera,{requestFrame:fn=>{frame=fn;return 1;},cancelFrame:()=>{frame=null;}});
await scope.start(crystal,0,{onComplete:()=>photos++});assert.equal(photos,0);frame(0);frame(2200);assert.equal(photos,0,'A slow frame cannot skip the demonstration');for(let t=2300;t<=5100;t+=100)frame(t);assert.equal(photos,1,'Only reveal photo after 3D movement');assert.equal(scene.getObjectByName('virtual-hand-microscope').visible,false);
await scope.start(crystal,1,{onComplete:()=>photos++});const stale=frame;scope.stop();stale(5000);assert.equal(photos,1,'Leaving must cancel pending photo');assert.equal(scene.getObjectByName('virtual-hand-microscope').visible,false);
await scope.start(crystal,2,{reduced:true,onComplete:()=>photos++});assert.equal(photos,1,'Reduced motion must not skip the requested inspection');frame(0);assert.equal(scene.getObjectByName('virtual-hand-microscope').visible,true);for(let t=100;t<=3000;t+=100)frame(t);assert.equal(photos,2);scope.dispose();assert.equal(scene.children.some(c=>c.name==='virtual-hand-microscope'),false);
const start=new THREE.Vector3(1,2,3),end=new THREE.Vector3(1,5,3);assert.deepEqual(microscopePose(0,start,end),start);assert.deepEqual(microscopePose(1,start,end),end);
const app=fs.readFileSync(new URL('../dist/museum.js',import.meta.url),'utf8');assert.ok(!/speechSynthesis|SpeechSynthesisUtterance/.test(app));
const photoFunction=app.slice(app.indexOf('function showFlawPhoto('),app.indexOf('async function showFlaw('));assert.equal((photoFunction.match(/<img /g)||[]).length,1);assert.ok(!/microscope-prop|flaw-focus|filter:|<canvas/.test(photoFunction),'No prop, marker or filter in photo rendering');
console.log('PASS: one English route plus three English manual-inspection recordings, full timed caption coverage, bilingual word cues, recording-clock seeks, language switches, faster rates, autoplay recovery, stale requests, 3D movement-before-photo and leave cancellation.');

const model=createMicroscopeModel();let meshes=0;model.traverse(m=>{assert.ok(!m.isSprite);if(m.isMesh){meshes++;assert.equal(m.material.map,null);assert.ok(m.geometry.attributes.position.count>0);}});assert.ok(meshes>30);assert.ok(model.getObjectByName('modelled-gloved-hand'));assert.ok(model.getObjectByName('microscope'));
for(let t=0;t<=1;t+=.1){const p=microscopePose(t,start,end);assert.equal(p.x,end.x);assert.equal(p.z,end.z);assert.ok(p.y>=start.y&&p.y<=end.y);}

assert.equal(data.inspectionTracks.length,3);
for(const t of data.inspectionTracks){assert.equal(crypto.createHash("sha256").update(fs.readFileSync(new URL("../dist/"+t.file,import.meta.url))).digest("hex"),t.sha256);assert.equal(norm(t.cues.map(c=>c.text).join("")),norm(t.text));}
