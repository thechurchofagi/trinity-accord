// Country lookup: https://country.is/ — caller IP only, no location permission.
const KEY='museum-language';
const valid=value=>value==='zh'||value==='en';
export function createLanguagePreference({search='',storage=()=>globalThis.localStorage,fetchCountry=globalThis.fetch,timeout=1800}={}){
 let saved=null;try{saved=storage()?.getItem(KEY);}catch{}
 const explicit=new URLSearchParams(search).get('lang');
 let language=valid(explicit)?explicit:valid(saved)?saved:'en';
 let chosen=valid(explicit)||valid(saved),pending=null;
 return {
  get language(){return language;},
  choose(value){if(!valid(value))return;chosen=true;language=value;try{storage()?.setItem(KEY,value);}catch{}},
  resolve(){
   if(chosen)return Promise.resolve(language);
   if(pending)return pending;
   pending=(async()=>{
    const controller=new AbortController();let timer;
    try{
     const country=await Promise.race([
      (async()=>{const response=await fetchCountry('https://api.country.is/',{signal:controller.signal,credentials:'omit',referrerPolicy:'no-referrer',cache:'no-store'});if(!response.ok)throw Error('Country unavailable');return (await response.json()).country;})(),
      new Promise(resolve=>{timer=setTimeout(()=>{controller.abort();resolve(null);},timeout);})
     ]);
     if(!chosen)language=country==='CN'?'zh':'en';
    }catch{if(!chosen)language='en';}
    finally{clearTimeout(timer);}
    return language;
   })();return pending;
  }
 };
}
