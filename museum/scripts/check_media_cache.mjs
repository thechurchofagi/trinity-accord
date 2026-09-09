import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {createTourPreloader} from '../dist/tour-preload.js';
const source=fs.readFileSync(new URL('../dist/media-cache-worker.js',import.meta.url),'utf8');
const listeners={},stores=new Map();let network=0,offline=false,denyStorage=false;
const cacheAPI={
 async open(name){if(denyStorage)throw Error('storage denied');if(!stores.has(name))stores.set(name,new Map());const map=stores.get(name);return {
  async match(r){return map.get(r.url)?.clone();},async put(r,s){map.set(r.url,new Response(await s.arrayBuffer(),{status:s.status,headers:s.headers}));},
  async keys(){return [...map.keys()].map(url=>new Request(url));},async delete(r){return map.delete(r.url);}
 };},async keys(){return [...stores.keys()];},async delete(name){return stores.delete(name);}
};
vm.runInNewContext(source,{URL,Request,Response,Headers,Object,Promise,Map,decodeURIComponent,caches:cacheAPI,
 self:{location:{href:'https://museum.test/museum/media-cache-worker.js'},skipWaiting:async()=>{},clients:{claim:async()=>{}},addEventListener:(name,fn)=>listeners[name]=fn},
 fetch:async()=>{network++;if(offline)throw Error('offline');return new Response('0123456789',{headers:{'Content-Type':'audio/mpeg'}});}
});
async function request(path,headers){let response,work;listeners.fetch({request:new Request('https://museum.test/museum/'+path,{headers}),respondWith:r=>response=r,waitUntil:p=>work=p});if(!response)return null;const result=await response;await work;return result;}
assert.equal(await (await request('assets/eth-001.mp3')).text(),'0123456789');assert.equal(network,1);
offline=true;
assert.equal(await (await request('assets/eth-001.mp3')).text(),'0123456789');assert.equal(network,1,'Repeat visit avoids network');
const range=await request('assets/eth-001.mp3',{Range:'bytes=3-5'});assert.equal(range.status,206);assert.equal(range.headers.get('content-range'),'bytes 3-5/10');assert.equal(await range.text(),'345');
assert.equal(await (await request('assets/eth-001.mp3',{Range:'bytes=-2'})).text(),'89');
assert.equal((await request('assets/eth-001.mp3',{Range:'bytes=99-'})).status,416);
for(const path of ['index.html','museum.bundle.js','data/release-manifest.json','data/current-status.json'])assert.equal(await request(path),null);
assert.equal(await request('../assets/eth-001.mp3'),null,'Worker respects hosting path');
offline=false;denyStorage=true;
assert.equal(await (await request('assets/eth-001.mp3')).text(),'0123456789','Storage denial preserves network fallback');denyStorage=false;
let activation;stores.set('unrelated-cache',new Map());stores.set('trinity-museum-media:/museum/:old',new Map());listeners.activate({waitUntil:p=>activation=p});await activation;
assert.ok(stores.has('unrelated-cache'));assert.ok(!stores.has('trinity-museum-media:/museum/:old'));
const turns=()=>new Promise(r=>setTimeout(r,10));let active=0,max=0,calls=[];
const preload=createTourPreloader({fetcher:async url=>{calls.push(url);max=Math.max(max,++active);await turns();active--;return new Response('ok');}});
preload.add('a');preload.add('a');preload.add('b');await new Promise(r=>setTimeout(r,50));assert.deepEqual(calls,['a','b']);assert.equal(max,1);
const reduced=createTourPreloader({connection:{saveData:true},fetcher:()=>{throw Error('must not download');}});reduced.add('unused');
let failures=0;const retry=createTourPreloader({fetcher:async()=>{failures++;throw Error('temporary');}});retry.add('retry');await turns();retry.add('retry');await turns();assert.equal(failures,2);
console.log('PASS: persistent repeat/offline media reuse, audio ranges, scope, rotation, denied storage, sequential deduplicated prefetch and retry.');
