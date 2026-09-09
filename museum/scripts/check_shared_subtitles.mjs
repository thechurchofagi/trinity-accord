import assert from 'node:assert/strict';
import fs from 'node:fs';
import {createTimedSubtitlePainter} from '../dist/timed-subtitles.js';
import {wordPages} from '../dist/word-captions.js';
const data=JSON.parse(fs.readFileSync(new URL('../dist/data/guide-audio.json',import.meta.url)));
assert.equal(data.tracks.length,15);assert.equal(data.inspectionTracks.length,3);
for(const track of [...data.tracks,...data.inspectionTracks]){
 assert.equal(track.language,'en');
 for(const cue of track.cues){
  assert.match(cue.textZh,/[\u3400-\u9fff]/);
  for(const width of [180,280,350,720]){
   const pages=wordPages(cue.words,width,s=>s.length*8);
   assert.deepEqual(pages.flat(2),cue.words.map((_,i)=>i));
   assert.ok(pages.every(p=>p.length<=2));
  }
 }
}
globalThis.getComputedStyle=()=>({font:'16px system-ui'});
const host={clientWidth:70,nodes:[],html:'',replaceChildren(){this.html='';this.nodes=[];},set innerHTML(value){this.html=value;this.nodes=[...value.matchAll(/data-word="(\d+)"/g)].map(m=>({dataset:{word:m[1]},classes:new Set(),get classList(){return {toggle:(name,on)=>on?this.classes.add(name):this.classes.delete(name)};}}));},querySelectorAll(){return this.nodes;}};
const measure={measureText:t=>({width:t.length*8})};
const cue={textZh:'同一句中文译文',words:[{text:'first',start:1,end:1.5},{text:'held',start:2,end:5},{text:'last',start:6,end:7}]};
const paint=createTimedSubtitlePainter();
paint(host,cue,3,measure);assert.match(host.html,/同一句中文译文/);assert.ok(host.nodes.find(n=>n.dataset.word==='1').classes.has('word-current'));
paint(host,cue,6.2,measure);assert.match(host.html,/同一句中文译文/);assert.ok(host.nodes.find(n=>n.dataset.word==='2').classes.has('word-current'));
paint(host,null,7,measure);assert.equal(host.html,'');
paint(host,cue,1.1,measure);assert.ok(host.nodes.find(n=>n.dataset.word==='0').classes.has('word-current'));
const app=fs.readFileSync(new URL('../dist/museum.js',import.meta.url),'utf8');
assert.match(app,/paintMusicSubtitles\(host,cue,current,captionMeasure\)/);
assert.match(app,/paintGuideSubtitles\(\$\('caption-text'\),cue,seconds,captionMeasure\)/);
const html=fs.readFileSync(new URL('../dist/index.html',import.meta.url),'utf8');
assert.match(html,/id="caption-text" class="timed-subtitles"/);assert.match(html,/id="subtitle-lines" class="timed-subtitles"/);
console.log('PASS: one English voice set, all Chinese translations, shared two-line paging, held words, seeks and caption clearing.');
