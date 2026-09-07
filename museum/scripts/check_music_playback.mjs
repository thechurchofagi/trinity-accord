import assert from 'node:assert/strict';
import {createMusicPlayback} from '../dist/music-playback.js';
class Audio extends EventTarget{
 currentTime=18.25;paused=true;ended=false;pending=null;block=false;
 pause(){this.paused=true;this.dispatchEvent(new Event('pause'));}
 play(){if(this.pending)return this.pending;if(this.block)return Promise.reject(Object.assign(new Error(),{name:'NotAllowedError'}));this.paused=false;this.dispatchEvent(new Event('playing'));return Promise.resolve();}
}
const audio=new Audio(),states=[],player=createMusicPlayback(audio,{onState:s=>states.push(s)});
audio.block=true;assert.equal(await player.play(),false);assert.equal(player.state,'blocked');assert.equal(player.waiting,true);assert.equal(player.recovering,true);
// A retry remains visible while loading and after another browser rejection.
let reject;audio.pending=new Promise((_,r)=>reject=r);const retry=player.play();assert.equal(player.state,'loading');assert.equal(player.recovering,true);assert.equal(player.waiting,true);
reject(Object.assign(new Error(),{name:'NotAllowedError'}));await retry;assert.equal(player.state,'blocked');
audio.pending=null;audio.block=false;assert.equal(await player.play(),true);assert.equal(player.recovering,false);assert.equal(player.waiting,false);assert.equal(audio.currentTime,18.25);
// A later interruption of already playing music must reopen the persistent prompt.
audio.pause();assert.equal(player.state,'blocked');assert.equal(player.recovering,true);await player.play();
audio.dispatchEvent(new Event('waiting'));assert.equal(player.waiting,true);assert.equal(player.recovering,true);audio.dispatchEvent(new Event('playing'));assert.equal(player.waiting,false);
// Deliberate pause holds the tour, but uses the normal resume control.
player.pause();assert.equal(player.state,'paused');assert.equal(player.recovering,false);assert.equal(player.waiting,true);await player.play();
// Neither cancelled nor superseded play promises may reopen the old prompt.
let deny;audio.pending=new Promise((_,r)=>deny=r);const old=player.play();audio.pending=null;await player.play();deny(new Error('stale'));await old;assert.equal(player.state,'playing');
let complete;audio.pending=new Promise(r=>complete=r);const cancelled=player.play();player.stop();complete();await cancelled;assert.equal(player.state,'idle');assert.equal(player.recovering,false);
console.log('PASS: repeated music blocking, persistent retry, original-time resume, interruption, buffering, deliberate pause and stale/cancelled playback.');
