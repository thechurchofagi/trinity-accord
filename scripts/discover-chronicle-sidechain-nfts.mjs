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
 for(let n=0;n<5;n++){
  const c=new AbortController(),t=setTimeout(()=>c.abort(),60000);
  try{const r=await fetch(url,{...opt,signal:c.signal,headers:{'user-agent':'trinity-accord-sidechain-mirror/1.1',...(opt.headers||{})}});clearTimeout(t);if(r.ok)return r;err=new Error(`${r.status} ${await r.text()}`)}catch(e){clearTimeout(t);err=e}
  await sleep(900*2**n);
 }
 throw err;
}
const json=async(url,opt)=>await (await get(url,opt)).json();

function normalizeV2Transfer(chain,standard,r){
 const c=CHAINS[chain],contract=String(r?.token?.address_hash||r?.token?.address||r?.contract_address||'').toLowerCase();
 const rawTokenId=r?.total?.token_id??r?.token_id??r?.tokenID??r?.token?.token_id??r?.token?.tokenId;
 if(!/^0x[a-f0-9]{40}$/.test(contract)||rawTokenId===undefined||rawTokenId===null)return null;
 const token=String(rawTokenId);if(!/^\d+$/.test(token))return null;
 const ts=typeof r.timestamp==='string'?r.timestamp:null,ms=ts?Date.parse(ts):NaN;
 return {chain,chain_id:c.id,standard,discovery_source:'blockscout_v2',block_number:Number(r.block_number||0),block_hash:r.block_hash||null,log_index:Number.isFinite(Number(r.log_index))?Number(r.log_index):null,timestamp:ts,timestamp_unix:Number.isFinite(ms)?Math.floor(ms/1000):0,transaction_hash:r.transaction_hash||r.hash||null,contract,token_id:token,from:String(r?.from?.hash||r.from||'').toLowerCase(),to:String(r?.to?.hash||r.to||'').toLowerCase(),quantity:String(r?.total?.value??r?.value??'1')};
}

async function historyV2(chain,standard){
 const c=CHAINS[chain],rows=[];let cursor=null;
 for(let page=1;page<=10000;page++){
  const u=new URL(`/api/v2/addresses/${ADDRESS}/token-transfers`,c.explorer);u.searchParams.set('type',standard);
  if(cursor)for(const [k,v] of Object.entries(cursor))if(v!==null&&v!==undefined)u.searchParams.set(k,String(v));
  const p=await json(u);write(path.join(OUT,'discovery',`${chain}-${standard.toLowerCase()}-v2-page-${String(page).padStart(4,'0')}.json`),{url:u.toString(),response:p});
  if(!Array.isArray(p.items))throw new Error(`${chain}/${standard} v2 returned no items array`);
  for(const r of p.items){const x=normalizeV2Transfer(chain,standard,r);if(x)rows.push(x)}
  if(!p.next_page_params)break;cursor=p.next_page_params;
  if(page===10000)throw new Error(`${chain}/${standard} v2 pagination safety stop`);
 }
 return rows;
}

async function historyLegacy(chain,action,standard){
 const c=CHAINS[chain],rows=[];
 for(let page=1;;page++){
  const u=new URL('/api',c.explorer);for(const [k,v] of Object.entries({module:'account',action,address:ADDRESS,page,offset:1000,sort:'asc'}))u.searchParams.set(k,v);
  if(process.env.BLOCKSCOUT_API_KEY)u.searchParams.set('apikey',process.env.BLOCKSCOUT_API_KEY);
  const p=await json(u),a=Array.isArray(p.result)?p.result:[];write(path.join(OUT,'discovery',`${chain}-${standard.toLowerCase()}-legacy-page-${String(page).padStart(4,'0')}.json`),{url:u.toString().replace(/apikey=[^&]+/,'apikey=REDACTED'),response:p});
  if(p.status==='0'&&/no transactions/i.test(`${p.message||''} ${p.result||''}`))break;
  if(!Array.isArray(p.result))throw new Error(`${chain}/${action}: ${JSON.stringify(p).slice(0,400)}`);
  for(const r of a){const contract=String(r.contractAddress||'').toLowerCase(),token=String(r.tokenID??r.tokenId??'');if(/^0x[a-f0-9]{40}$/.test(contract)&&/^\d+$/.test(token))rows.push({chain,chain_id:c.id,standard,discovery_source:'blockscout_legacy',block_number:+r.blockNumber||0,block_hash:r.blockHash||null,log_index:Number.isFinite(Number(r.logIndex))?Number(r.logIndex):null,timestamp:r.timeStamp?new Date(+r.timeStamp*1000).toISOString():null,timestamp_unix:+r.timeStamp||0,transaction_hash:r.hash||null,contract,token_id:token,from:String(r.from||'').toLowerCase(),to:String(r.to||'').toLowerCase(),quantity:String(r.tokenValue??'1')})}
  if(a.length<1000)break;if(page>1000)throw new Error('legacy pagination safety stop');
 }
 return rows;
}

async function history(chain,standard){
 try{return await historyV2(chain,standard)}catch(v2Error){
  console.warn(`${chain}/${standard} Blockscout v2 failed: ${v2Error.message}; trying legacy fallback`);
  const action=standard==='ERC-1155'?'token1155tx':'tokennfttx';
  try{return await historyLegacy(chain,action,standard)}catch(legacyError){throw new Error(`${chain}/${standard} discovery failed: v2=${v2Error.message}; legacy=${legacyError.message}`)}
 }
}

async function rpc(chain,method,params){const p=await json(CHAINS[chain].rpc,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({jsonrpc:'2.0',id:1,method,params})});if(p.error)throw new Error(JSON.stringify(p.error));return p.result}
const idhex=id=>BigInt(id).toString(16).padStart(64,'0');
function abiString(h){try{h=h.slice(2);const o=Number(BigInt('0x'+h.slice(0,64)))*2,l=Number(BigInt('0x'+h.slice(o,o+64)));return Buffer.from(h.slice(o+64,o+64+l*2),'hex').toString()}catch{return null}}
async function tokenURI(t){try{const sel=t.standard==='ERC-1155'?'0x0e89341c':'0xc87b56dd',h=await rpc(t.chain,'eth_call',[{to:t.contract,data:sel+idhex(t.token_id)},'latest']);let u=abiString(h);if(u&&t.standard==='ERC-1155')u=u.replaceAll('{id}',idhex(t.token_id));return {uri:u,rpc:CHAINS[t.chain].rpc,error:null}}catch(e){return {uri:null,rpc:CHAINS[t.chain].rpc,error:e.message}}}

function candidates(u){if(!u)return[];if(u.startsWith('ipfs://')){const x=u.slice(7).replace(/^ipfs\//,'');return['https://ipfs.io/ipfs/','https://dweb.link/ipfs/'].map(g=>g+x)}if(u.startsWith('ar://'))return['https://arweave.net/'+u.slice(5)];if(/^https?:\/\//i.test(u))return[u];return[]}
async function mirror(u,base){
 if(!u)return {status:'missing'};
 if(u.startsWith('data:')){const i=u.indexOf(','),head=u.slice(5,i),payload=u.slice(i+1),b=Buffer.from(head.includes(';base64')?payload:decodeURIComponent(payload),head.includes(';base64')?'base64':'utf8');const f=base+'.bin';fs.mkdirSync(path.dirname(f),{recursive:true});fs.writeFileSync(f,b);return {status:'ok',original_uri:u.slice(0,200),file:f,bytes:b.length,sha256:sha(b)}}
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
const occurrences=[];for(const chain of Object.keys(CHAINS)){console.log(`Scanning ${chain} ${ADDRESS}`);for(const standard of ['ERC-721','ERC-1155']){const rows=await history(chain,standard);console.log(`${chain}/${standard}: ${rows.length} historical transfer occurrences`);occurrences.push(...rows)}}
const uniq=new Map;for(const r of occurrences){const k=[r.chain,r.transaction_hash||'',r.log_index??'',r.contract,r.token_id,r.from,r.to,r.quantity].join('|');if(!uniq.has(k))uniq.set(k,r)}const deduped=[...uniq.values()];deduped.sort((a,b)=>a.timestamp_unix-b.timestamp_unix||a.chain.localeCompare(b.chain));write(path.join(OUT,'transfer-occurrences.json'),deduped);
const map=new Map;for(const r of deduped){const k=`${r.chain}|${r.contract}|${r.token_id}`;if(!map.has(k))map.set(k,{chain:r.chain,chain_id:r.chain_id,standard:r.standard,contract:r.contract,token_id:r.token_id,first_seen:r.timestamp,first_seen_unix:r.timestamp_unix,first_seen_block:r.block_number,transfers:[]});const t=map.get(k);t.transfers.push(r);if(r.timestamp_unix&&(!t.first_seen_unix||r.timestamp_unix<t.first_seen_unix)){t.first_seen=r.timestamp;t.first_seen_unix=r.timestamp_unix;t.first_seen_block=r.block_number}}
const tokens=[...map.values()].sort((a,b)=>a.first_seen_unix-b.first_seen_unix),recovered=[];for(let i=0;i<tokens.length;i++){console.log(`[${i+1}/${tokens.length}] ${tokens[i].chain} ${tokens[i].contract} #${tokens[i].token_id}`);try{recovered.push(await recover(tokens[i]))}catch(e){recovered.push({...tokens[i],recovery_error:e.message})}}write(path.join(OUT,'recovered-tokens.json'),recovered);
const old=existing(),comparison=recovered.map(t=>({chain:t.chain,contract:t.contract,token_id:t.token_id,first_seen:t.first_seen,same_contract_token_coordinate_in_existing_index:old.set.has(`${t.contract}|${t.token_id}`),name:t.metadata?.name||null,recovery_error:t.recovery_error||null}));write(path.join(OUT,'comparison-with-token-index.json'),comparison);
const byChain={};for(const chain of Object.keys(CHAINS)){const os=deduped.filter(x=>x.chain===chain),rs=recovered.filter(x=>x.chain===chain),cs=comparison.filter(x=>x.chain===chain);byChain[chain]={transfer_occurrences:os.length,unique_coordinates:rs.length,metadata_recovered:rs.filter(x=>x.metadata).length,same_contract_token_coordinate_in_existing_index:cs.filter(x=>x.same_contract_token_coordinate_in_existing_index).length,not_same_contract_token_coordinate_in_existing_index:cs.filter(x=>!x.same_contract_token_coordinate_in_existing_index).length,earliest_observed_transfer:os[0]?{timestamp:os[0].timestamp,block_number:os[0].block_number,transaction_hash:os[0].transaction_hash,contract:os[0].contract,token_id:os[0].token_id,standard:os[0].standard}:null}}
const dated=deduped.filter(x=>x.timestamp_unix>0),e=dated[0]||deduped[0]||null,summary={schema:'trinity-accord/chronicle-sidechain-scan/v2',generated_at:new Date().toISOString(),target_address:ADDRESS,chains:Object.entries(CHAINS).map(([name,c])=>({name,chain_id:c.id,explorer:c.explorer,rpc:c.rpc})),per_chain:byChain,existing_token_index:{contracts:old.contracts,tokens:old.tokens,error:old.error||null},transfer_occurrences:deduped.length,unique_sidechain_coordinates:recovered.length,same_contract_token_coordinate_in_existing_index:comparison.filter(x=>x.same_contract_token_coordinate_in_existing_index).length,not_same_contract_token_coordinate_in_existing_index:comparison.filter(x=>!x.same_contract_token_coordinate_in_existing_index).length,metadata_recovered:recovered.filter(x=>x.metadata).length,recovery_errors:recovered.filter(x=>x.recovery_error).length,earliest_observed_sidechain_nft_transfer:e?{chain:e.chain,timestamp:e.timestamp,block_number:e.block_number,transaction_hash:e.transaction_hash,contract:e.contract,token_id:e.token_id,standard:e.standard}:null,comparison_note:'The existing token_index.json does not encode chain identity in this comparison. Matching contract+token coordinates across chains is a heuristic overlap signal, not proof that two NFT occurrences are the same logical Chronicle record.',evidence_boundary:'An observed sidechain occurrence is evidence input only. Cross-chain remints require semantic deduplication; this workflow does not amend Canon or automatically redefine Chronicle membership, record count, or formation time.'};write(path.join(OUT,'SUMMARY.json'),summary);
const manifest=[];function walk(d){for(const x of fs.readdirSync(d,{withFileTypes:true})){const f=path.join(d,x.name);if(x.isDirectory())walk(f);else if(!f.endsWith('MANIFEST.sha256')&&!f.endsWith('MANIFEST.sha256.json')){const b=fs.readFileSync(f);manifest.push({path:path.relative(OUT,f).replaceAll('\\','/'),bytes:b.length,sha256:sha(b)})}}}walk(OUT);manifest.sort((a,b)=>a.path.localeCompare(b.path));write(path.join(OUT,'MANIFEST.sha256.json'),manifest);fs.writeFileSync(path.join(OUT,'MANIFEST.sha256'),manifest.map(x=>`${x.sha256}  ${x.path}`).join('\n')+'\n');console.log(JSON.stringify(summary,null,2));
