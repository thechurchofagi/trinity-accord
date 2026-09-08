import {createSpatialShell} from './spatial-layout.js';
import * as THREE from './vendor/three.module.js';

// A stalled response must never hold the museum entrance indefinitely.
export async function fetchBytes(url,{timeout=15000,attempts=2,fetcher=fetch}={}){
 let last;
 for(let attempt=0;attempt<attempts;attempt++){
  const controller=new AbortController();let timer;
  try{
   return await Promise.race([
    (async()=>{const response=await fetcher(url,{signal:controller.signal});if(!response.ok)throw Error(`Resource ${response.status}: ${url}`);return response.arrayBuffer();})(),
    new Promise((_,reject)=>{timer=setTimeout(()=>{controller.abort();reject(Error(`Resource timed out: ${url}`));},timeout);})
   ]);
  }catch(error){last=error;}finally{clearTimeout(timer);}
 }
 throw last;
}

export function createResourceQueue(limit=3){
 let active=0;const pending=[];
 function pump(){pending.sort((a,b)=>a.priority()-b.priority());while(active<limit&&pending.length){const task=pending.shift();active++;Promise.resolve().then(task.work).then(task.resolve,task.reject).finally(()=>{active--;pump();});}}
 return {add(work,priority=()=>0){return new Promise((resolve,reject)=>{pending.push({work,priority,resolve,reject});pump();});}};
}

// The same corridor footprint is available before any model/image downloads.
export function createPreviewHall(layout){return createSpatialShell(layout);}

// Refuse a stale model even if an intermediary ignores its version query.
export async function fetchModel(url,sha256,{fetcher=fetch,...options}={}){
 const versioned=url+(url.includes('?')?'&':'?')+'v='+sha256.slice(0,16);
 const bytes=await fetchBytes(versioned,{...options,fetcher});
 const actual=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),b=>b.toString(16).padStart(2,'0')).join('');
 if(actual!==sha256)throw Error('Model edition mismatch: '+url);
 return bytes;
}
