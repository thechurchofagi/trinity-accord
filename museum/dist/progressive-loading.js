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
