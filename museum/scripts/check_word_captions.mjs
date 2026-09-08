import {exhibitLabel} from '../dist/exhibit-label.js';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
import {validTimeline,lineAt,wordAt,wordPages,pageAt} from '../dist/word-captions.js';
const dist=new URL('../dist/',import.meta.url),read=p=>JSON.parse(fs.readFileSync(new URL(p,dist))),sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const index=read('data/lyrics-index.json'),sources=read('data/sources.json');
const zhRaw=fs.readFileSync(new URL(index.translation.file,dist)),zh=JSON.parse(zhRaw);
assert.equal(sha(zhRaw),index.translation.sha256);
const audioTracks=sources.items.filter(e=>e.media?.some(m=>m.kind==='audio'));
assert.equal(index.items.length,audioTracks.length);assert.equal(new Set(index.items.map(e=>e.exhibitId)).size,index.items.length);
let count=0;
for(const entry of index.items){
 const raw=fs.readFileSync(new URL(entry.timelineFile,dist)),timeline=JSON.parse(raw),audio=audioTracks.find(e=>e.id===entry.exhibitId)?.media.find(m=>m.kind==='audio');
 assert.equal(entry.audioSha256,audio?.sha256);assert.equal(timeline.audioFile,audio.file);assert.equal(sha(raw),entry.timelineSha256);
 assert(validTimeline(timeline,entry),entry.exhibitId+' invalid/overlapping word times');
 assert.equal(lineAt(timeline.lines,entry.duration),-1);
 for(const [i,line] of timeline.lines.entries()){
  assert.equal(typeof zh.lines[line.text],'string');assert(/[\u3400-\u9fff]/u.test(zh.lines[line.text]),entry.exhibitId+' missing Chinese line');
  assert.equal(line.text,line.words.map(w=>w.text).join(' '));assert.equal(lineAt(timeline.lines,line.start),i);
  for(const [j,w] of line.words.entries()){
   assert.equal(wordAt(line.words,w.start),j);assert.equal(wordAt(line.words,(w.start+w.end)/2),j);assert.notEqual(wordAt(line.words,w.end),j);
   assert(w.acousticScore>=0&&w.acousticScore<=1);count++;
  }
  if(i && line.start>timeline.lines[i-1].end)assert.equal(lineAt(timeline.lines,(line.start+timeline.lines[i-1].end)/2),-1);
  for(const width of [180,280,350,720]){
   const pages=wordPages(line.words,width,t=>t.length*9);
   assert.deepEqual(pages.flat(2),line.words.map((_,i)=>i),'Words lost during wrapping');
   for(const [pi,page] of pages.entries()){
    assert(page.length<=2);const first=page[0][0];assert.equal(pageAt(pages,line.words,line.words[first].start),pi);
   }
  }
 }
 const wrong=structuredClone(timeline);wrong.audioSha256='different';assert.equal(validTimeline(wrong,entry),false);
 const zero=structuredClone(timeline);zero.lines[0].words[0].end=zero.lines[0].words[0].start;assert.equal(validTimeline(zero,entry),false);
}
// Seeking may move either direction; playback rate never changes these positions.
const irregular=[{text:'short',start:2,end:2.15},{text:'held',start:2.2,end:8},{text:'last',start:8.1,end:8.4}];
const pages=wordPages(irregular,50,t=>t.length*10);
assert.equal(pageAt(pages,irregular,7.9),0);assert.equal(pageAt(pages,irregular,8.1),1);assert.equal(pageAt(pages,irregular,2),0);
assert.equal(wordAt(irregular,2.17),-1);assert.equal(wordAt(irregular,5),1);
const runtime=fs.readFileSync(new URL('museum.js',dist),'utf8');
assert(!runtime.includes('estimateCues('),'Estimated timing must not drive lyrics');
assert(runtime.includes('request!==lyricRequest'),'Stale caption fetch guard missing');
console.log(`${index.items.length} audio bindings; ${count} word intervals; gaps, seeks, paging, rejection and hashes pass.`);

assert.ok(exhibitLabel({ordinal:103,date:'2025-01-01',title:'AI therapy',songTitle:'Unspoken'},false,true).includes('Song: Unspoken'));
assert(!exhibitLabel({ordinal:103,date:'2025-01-01'},false,false).includes('♪'));
console.log(Object.keys(zh.lines).length+' complete Chinese translations; music plaque symbol passes.');
