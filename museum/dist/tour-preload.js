// One speculative transfer at a time; failed requests remain retryable.
export function createTourPreloader({fetcher=fetch,connection=globalThis.navigator?.connection,timeout=20000}={}){
 const pending=[],known=new Set();let active=false;
 const constrained=()=>connection?.saveData||/^(slow-)?2g$/.test(connection?.effectiveType||'');
 async function pump(){
  if(active||!pending.length)return;active=true;
  const url=pending.shift(),controller=new AbortController(),timer=setTimeout(()=>controller.abort(),timeout);
  try{const response=await fetcher(url,{signal:controller.signal,priority:'low'});if(!response.ok)throw Error(response.status);await response.arrayBuffer();}
  catch{known.delete(url);}finally{clearTimeout(timer);active=false;pump();}
 }
 return {add(url){if(!url||known.has(url)||constrained())return;known.add(url);pending.push(url);pump();}};
}
