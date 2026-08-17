#!/usr/bin/env node
import fs from 'fs';
import path from 'path';
import crypto from 'crypto';

const ADDRESS=(process.env.CHRONICLE_ADDRESS||'0xbc63566A41cBfDB9C266a5941CBe47894DaA54A8').toLowerCase();
const OUT=process.env.CHRONICLE_OUT||'artifacts/chronicle-sidechain-scan';
const CHAINS={
 polygon:{id:137,explorer:'https://polygon.blockscout.com',rpc:process.env.POLYGON_RPC_URL||'https://polygon.drpc.org'},
 base:{id:8453,explorer:'https://base.blockscout.com',rpc:process.env.BASE_RPC_URL||'https://mainnet.base.org'}
};
const MAX=Number(process.env.CHRONICLE_MIRROR_MAX_BYTES||104857600);
if(!/^0x[a-f0-9]{40}$/.test(ADDRESS)) throw new Error(`invalid address ${ADDRESS}`);

const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const safe=s=>String(s).replace(/[^A-Za-z0-9._-]/g,'_').slice(0,180);
const write=(f,v)=>{fs.mkdirSync(path.dirname(f),{recursive:true});fs.writeFileSync(f,JSON.stringify(v,null,2)+'\n')};

async function get(url,opt={}){
 let err;
 for(let n=0;n<4;n++){
  const c=new AbortController(),t=setTimeout(()=>c.abort(),60000);
  try{const r=await fetch(url,{...opt,signal:c.signal,headers:{'user-agent':'trinity-accord-sidechain-mirror/1.0',...(opt.headers||{})}});clearTimeout(t);if(r.ok)return r;err=new Error(`${r.status} ${await r.text()}`)}catch(e){clearTimeout(t);err=e}
  await sleep(750*2**n);
 }
 throw err;
}
const json=async(url,opt)=>await (await get(url,opt)).json();

async function history(chain,action,standard){
 const c=CHAINS[chain],rows=[];
 for(let page=1;;page++){
  const u=new URL('/api',c.explorer);for(const [k,v] of Object.entries({module:'account',action,address:ADDRESS,page,offset:1000,sort:'asc'}))u.searchParams.set(k,v);
  if(process.env.BLOCKSCOUT_API_KEY)u.searchParams.set('apikey',process.env.BLOCKSCOUT_API_KEY);
  const p=await json(u),a=Array.isArray(p.result)?p.result:[];
  if(p.status==='0'&&/no transactions/i.test(`${p.message||''} ${p.result||''}`))break;
  if(!Array.isArray(p.result))throw new Error(`${chain}/${action}: ${JSON.stringify(p).slice(0,400)}`);
  for(const r of a){const contract=String(r.contractAddress||'').toLowerCase(),token=String(r.tokenID??r.tokenId??'');if(/^0x[a-f0-9]{40}$/.test(contract)&&/^\d+$/.test(token))rows.push({chain,chain_id:c.id,standard,block_number:+r.blockNumber||0,timestamp:r.timeStamp?new Date(+r.timeStamp*1000).toISOString():null,timestamp_unix:+r.timeStamp||0,transaction_hash:r.hash||null,contract,token_id:token,from:String(r.from||'').toLowerCase(),to:String(r.to||'').toLowerCase(),quantity:String(r.tokenValue??'1')})}
  if(a.length<1000)break;if(page>1000)throw new Error('pagination safety stop');
 }
 return rows;
}

async function rpc(chain,method,params){const p=await json(CHAINS[chain].rpc,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({jsonrpc:'2.0',id:1,method,params})});if(p.error)throw new Error(JSON.stringify(p.error));return p.result}
const idhex=id=>BigInt(id).toString(16).padStart(64,'0');
function abiString(h){try{h=h.slice(2);const o=Number(BigInt('0x'+h.slice(0,64)))*2,l=Number(BigInt('0x'+h.slice(o,o+64)));return Buffer.from(h.slice(o+64,o+64+l*2),'hex').toString()}catch{return null}}
async function tokenURI(t){try{const sel=t.standard==='ERC-1155'?'0x0e89341c':'0xc87b56dd',h=await rpc(t.chain,'eth_call',[{to:t.contract,data:sel+idhex(t.token_id)},'latest']);let u=abiString(h);if(u&&t.standard==='ERC-1155')u=u.replaceAll('{id}',idhex(t.token_id));return {uri:u,rpc:CHAINS[t.chain].rpc,error:null}}catch(e){return {uri:null,rpc:CHAINS[t.chain].rpc,error:e.message}}}

function candidates(u){if(!u)return[];if(u.startsWith('ipfs://')){const x=u.slice(7).replace(/^ipfs\//,'');return['https://ipfs.io/ipfs/','https://dweb.link/ipfs/'].map(g=>g+x)}if(u.startsWith('ar://'))return['https://arweave.net/'+u.slice(5)];if(/^https?:\/\//i.test(u))return[u];return[]}
async function mirror(u,base){
 if(!u)return {status:'missing'};
 if(u.startsWith('data:')){const i=u.indexOf(','),head=u.slice(5,i),b=Buffer.from(u.slice(i+1),head.includes(';base64')?'base64':'utf8');const f=base+'.bin';fs.mkdirSync(path.dirname(f),{recursive:true});fs.writeFileSync(f,b);return {status:'ok',original_uri:u.slice(0,200),file:f,bytes:b.length,sha256:sha(b)}}
 const errors=[];for(const x of candidates(u))try{const r=await get(x),n=+(r.headers.get('content-length')||0);if(n>MAX)throw new Error(`too large ${n}`);const b=Buffer.from(await r.arrayBuffer());if(b.length>MAX)throw new Error(`too large ${b.length}`);const ct=r.headers.get('content-type')||'',ext=ct.includes('json')?'.json':(path.extname(new URL(r.url).pathname).slice(0,12)||'.bin'),f=base+ext;fs.mkdirSync(path.dirname(f),{recursive:true});fs.writeFileSync(f,b);return {status:'ok',original_uri:u,resolved_url:r.url,file:f,bytes:b.length,sha256:sha(b),content_type:ct}}catch(e){errors.push(`${x}: ${e.message}`)}
 return {status:'failed',original_uri:u,errors};
}

async function recover(t){
 const dir=path.join(OUT,t.chain,t.contract,t.token_id);fs.mkdirSync(dir,{recursive:true});
 const uri=await tokenURI(t),instUrl=`${CHAINS[t.chain].explorer}/api/v2/tokens/${t.contract}/instances/${encodeURIComponent(t.token_id)}`;let inst=null,instErr=null;try{inst=await json(instUrl)}catch(e){instErr=e.message}write(path.join(dir,'blockscout-instance.json'),{url:instUrl,data:inst,error:instErr});
 let meta=null,mm=null;if(uri.uri){mm=await mirror(uri.uri,path.join(dir,'metadata'));if(mm.status==='ok')try{meta=JSON.parse(fs.readFileSync(mm.file,'utf8'))}catch{}}
 if(!meta&&inst?.metadata)meta=inst.metadata;if(meta)write(path.join(dir,'metadata.normalized.json'),meta);
 const media=[];for(const k of ['image','image_url','animation_url','animation','video','audio'])if(typeof meta?.[k]==='string')media.push({role:k,...await mirror(meta[k],path.join(dir,`media-${safe(k)}`))});
 const r={...t,token_uri:uri,metadata_mirror:mm,metadata:meta,media};write(path.join(dir,'record.json'),r);return r;
}

function existing(){try{const x=JSON.parse(fs.readFileSync('token_index.json','utf8')),s=new Set;for(const[c,ts]of Object.entries(x))for(const id of Object.keys(ts||{}))s.add(`${c.toLowerCase()}|${id}`);return{contracts:Object.keys(x).length,tokens:s.size,set:s}}catch(e){return{contracts:0,tokens:0,set:new Set,error:e.message}}}

fs.rmSync(OUT,{recursive:true,force:true});fs.mkdirSync(OUT,{recursive:true});
const occurrences=[];for(const chain of Object.keys(CHAINS)){console.log(`Scanning ${chain} ${ADDRESS}`);occurrences.push(...await history(chain,'tokennfttx','ERC-721'),...await history(chain,'token1155tx','ERC-1155'))}
occurrences.sort((a,b)=>a.timestamp_unix-b.timestamp_unix||a.chain.localeCompare(b.chain));write(path.join(OUT,'transfer-occurrences.json'),occurrences);
const map=new Map;for(const r of occurrences){const k=`${r.chain}|${r.contract}|${r.token_id}`;if(!map.has(k))map.set(k,{chain:r.chain,chain_id:r.chain_id,standard:r.standard,contract:r.contract,token_id:r.token_id,first_seen:r.timestamp,first_seen_unix:r.timestamp_unix,first_seen_block:r.block_number,transfers:[]});const t=map.get(k);t.transfers.push(r);if(r.timestamp_unix<t.first_seen_unix){t.first_seen=r.timestamp;t.first_seen_unix=r.timestamp_unix;t.first_seen_block=r.block_number}}
const tokens=[...map.values()].sort((a,b)=>a.first_seen_unix-b.first_seen_unix),recovered=[];for(let i=0;i<tokens.length;i++){console.log(`[${i+1}/${tokens.length}] ${tokens[i].chain} ${tokens[i].contract} #${tokens[i].token_id}`);try{recovered.push(await recover(tokens[i]))}catch(e){recovered.push({...tokens[i],recovery_error:e.message})}}write(path.join(OUT,'recovered-tokens.json'),recovered);
const old=existing(),comparison=recovered.map(t=>({chain:t.chain,contract:t.contract,token_id:t.token_id,first_seen:t.first_seen,present_in_existing_token_index_by_contract_token:old.set.has(`${t.contract}|${t.token_id}`),name:t.metadata?.name||null,recovery_error:t.recovery_error||null}));write(path.join(OUT,'comparison-with-token-index.json'),comparison);
const e=occurrences[0]||null,summary={schema:'trinity-accord/chronicle-sidechain-scan/v1',generated_at:new Date().toISOString(),target_address:ADDRESS,chains:Object.entries(CHAINS).map(([name,c])=>({name,chain_id:c.id,explorer:c.explorer,rpc:c.rpc})),existing_token_index:{contracts:old.contracts,tokens:old.tokens,error:old.error||null},transfer_occurrences:occurrences.length,unique_sidechain_coordinates:recovered.length,already_in_existing_index_by_contract_token:comparison.filter(x=>x.present_in_existing_token_index_by_contract_token).length,not_in_existing_index_by_contract_token:comparison.filter(x=>!x.present_in_existing_token_index_by_contract_token).length,metadata_recovered:recovered.filter(x=>x.metadata).length,recovery_errors:recovered.filter(x=>x.recovery_error).length,earliest_observed_sidechain_nft_transfer:e?{chain:e.chain,timestamp:e.timestamp,block_number:e.block_number,transaction_hash:e.transaction_hash,contract:e.contract,token_id:e.token_id}:null,note:'An observed sidechain occurrence is evidence input only. Cross-chain remints require semantic deduplication; this workflow does not amend Canon or automatically redefine Chronicle membership or formation time.'};write(path.join(OUT,'SUMMARY.json'),summary);
const manifest=[];function walk(d){for(const x of fs.readdirSync(d,{withFileTypes:true})){const f=path.join(d,x.name);if(x.isDirectory())walk(f);else{const b=fs.readFileSync(f);manifest.push({path:path.relative(OUT,f).replaceAll('\\','/'),bytes:b.length,sha256:sha(b)})}}}walk(OUT);manifest.sort((a,b)=>a.path.localeCompare(b.path));write(path.join(OUT,'MANIFEST.sha256.json'),manifest);fs.writeFileSync(path.join(OUT,'MANIFEST.sha256'),manifest.map(x=>`${x.sha256}  ${x.path}`).join('\n')+'\n');console.log(JSON.stringify(summary,null,2));
