import assert from 'node:assert/strict';
import {createLanguagePreference} from '../dist/language-preference.js';
const storage=()=>({getItem:()=>null,setItem:()=>{}});
const locate=country=>async()=>({ok:true,json:async()=>({country})});
for(const [country,expected] of [['CN','zh'],['US','en'],['HK','en'],['MO','en'],['TW','en'],[null,'en']]){
 const p=createLanguagePreference({storage,fetchCountry:locate(country)});assert.equal(await p.resolve(),expected);assert.equal(p.language,expected);
}
let calls=0;
const fetchCountry=()=>{calls++;throw Error('Should not query');};
assert.equal(await createLanguagePreference({search:'?lang=zh',storage,fetchCountry}).resolve(),'zh');
assert.equal(await createLanguagePreference({search:'?lang=en',storage:()=>({getItem:()=> 'zh'}),fetchCountry}).resolve(),'en');
assert.equal(await createLanguagePreference({storage:()=>({getItem:()=> 'zh'}),fetchCountry}).resolve(),'zh');assert.equal(calls,0);
assert.equal(await createLanguagePreference({search:'?lang=invalid',storage,fetchCountry:locate('CN')}).resolve(),'zh');
assert.equal(await createLanguagePreference({storage:()=>{throw Error('Storage blocked');},fetchCountry:async()=>{throw Error('Offline');}}).resolve(),'en');
assert.equal(await createLanguagePreference({storage,fetchCountry:async()=>({ok:false})}).resolve(),'en');
assert.equal(await createLanguagePreference({storage,fetchCountry:()=>new Promise(()=>{}),timeout:5}).resolve(),'en');
let complete,saved;
const p=createLanguagePreference({storage:()=>({getItem:()=>null,setItem:(key,value)=>saved=[key,value]}),fetchCountry:()=>new Promise(r=>complete=r)});
const pending=p.resolve();p.choose('en');complete({ok:true,json:async()=>({country:'CN'})});assert.equal(await pending,'en');assert.equal(p.language,'en');assert.deepEqual(saved,['museum-language','en']);
const reload=createLanguagePreference({storage:()=>({getItem:()=>saved[1]}),fetchCountry});assert.equal(await reload.resolve(),'en');
console.log('PASS: mainland IP default, other regions, URL and saved-language priority, no unnecessary query, timeout/offline fallback and manual-choice race.');
