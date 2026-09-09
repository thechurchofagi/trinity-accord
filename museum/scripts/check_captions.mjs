import {fallbackLyricsFor} from '../dist/lyrics-fallback.js';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {cleanLyrics,extractRecordLyrics,captionPages,frameSeconds} from '../dist/caption-utils.js';
const sources=JSON.parse(fs.readFileSync(new URL('../dist/data/sources.json',import.meta.url)));
const byId=new Map(sources.items.map(e=>[e.id,e]));
const runtime=fs.readFileSync(new URL('../dist/museum.js',import.meta.url),'utf8');
const fallback=fallbackLyricsFor('eth-071');
let total=0;
for(const e of sources.items.filter(e=>e.media?.some(m=>m.kind==='audio'))){
 let raw=e.lyrics||fallbackLyricsFor(e.id)||'';
 if(e.id==='eth-089')continue; // Complete suite has a source track list instead of fabricated global captions.
 if(!raw&&e.id==='eth-042')raw=byId.get('eth-001').lyrics;
 if(!raw&&e.id==='eth-010')raw=byId.get('eth-049').lyrics;
 if(!raw&&e.id==='eth-071')raw=fallback;
 if(!raw&&e.localRecord)raw=extractRecordLyrics(fs.readFileSync(new URL('../dist/'+e.localRecord,import.meta.url),'utf8'),e.songTitle);
 const rows=cleanLyrics(raw,e.songTitle);assert(rows.length>10,e.id+' missing lyrics');
 assert(!rows.some(r=>/^(?:Song Lyrics|Disclaimer|Significance of this NFT|The song vividly portrays|Looking Ahead)/i.test(r)),e.id+' metadata');
 assert.notEqual(rows[0],e.songTitle,e.id+' title');
 if(e.id==='eth-031')assert(rows[0].startsWith('As a child,'));
 if(e.id==='eth-049')assert(rows.at(-1).includes('I sever'));
 for(const width of [180,280,350,720])for(const row of rows){
  const measure=text=>[...text].length*9;
  const pages=captionPages(row,width,measure);
  assert.equal(pages.join('').replace(/\s/g,''),row.replace(/\s/g,''),e.id+' lost words');
  for(const page of pages){assert(page.split('\n').length<=2);assert(page.split('\n').every(l=>measure(l)<=width));}
 }
 total+=rows.length;console.log(e.id,rows.length,'reference lines; text paging passes');
}
for(const fps of [10,20,30,60,120]){let distance=0,previous=1000;for(let i=1;i<=fps*10;i++){const now=1000+i*1000/fps;distance+=frameSeconds(now,previous)*1.38;previous=now;}assert(Math.abs(distance-13.8)<1e-8);}
assert.equal(frameSeconds(60000,1000),0);
assert.equal(frameSeconds(1600,1000),.25,'Slow rendering retains bounded movement instead of freezing input');
console.log(total+' reference lines checked; 10–120 fps walking speed agrees; background gap ignored.');
