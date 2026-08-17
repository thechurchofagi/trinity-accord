#!/usr/bin/env node
import fs from 'fs';import path from 'path';import crypto from 'crypto';
const OUT=process.env.CHRONICLE_OUT||'artifacts/chronicle-sidechain-scan';const E=path.join(OUT,'evidence-v2');
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
function writeJson(f,v){fs.mkdirSync(path.dirname(f),{recursive:true});fs.writeFileSync(f,JSON.stringify(v,null,2)+'\n');}
function read(f){return JSON.parse(fs.readFileSync(f,'utf8'));}
const offline=read(path.join(E,'OFFLINE-VERIFICATION.json'));const l2=read(path.join(E,'L2-CAPTURE-SUMMARY.json'));const l1=read(path.join(E,'SIDECHAIN-NFT-COLLECTION-COMMITMENT.json'));
if(!offline.pass||!l2.pass)throw new Error('refusing to finalize failed evidence');
const summary=read(path.join(OUT,'SUMMARY.json'));
summary.evidence_v2={l1_merkle_root_sha256:l1.merkle_root_sha256,l2_execution_inclusion_pass:true,offline_verification_pass:true,l3_settlement_status:'not_yet_captured',btc_signature:'pending_external_guardian_signature',ethereum_attestation:'pending_external_guardian_attestation',ots:'pending_new_timestamp_anchor',note:'Cryptographic anchor digests are in evidence-v2/ANCHOR-REQUEST.json; historical signatures/attestations are not retroactively extended.'};
writeJson(path.join(OUT,'SUMMARY.json'),summary);
const excluded=new Set(['MANIFEST.sha256','MANIFEST.sha256.json']);const manifest=[];
function walk(dir){for(const ent of fs.readdirSync(dir,{withFileTypes:true})){const f=path.join(dir,ent.name),rel=path.relative(OUT,f).replaceAll('\\','/');if(ent.isDirectory()){if(rel==='runtime')continue;walk(f);}else if(!excluded.has(ent.name)&&rel!=='evidence-v2/ANCHOR-REQUEST.json'){const b=fs.readFileSync(f);manifest.push({path:rel,bytes:b.length,sha256:sha(b)});}}}
walk(OUT);manifest.sort((a,b)=>a.path.localeCompare(b.path));writeJson(path.join(OUT,'MANIFEST.sha256.json'),manifest);fs.writeFileSync(path.join(OUT,'MANIFEST.sha256'),manifest.map(x=>`${x.sha256}  ${x.path}`).join('\n')+'\n');
const manifestJson=fs.readFileSync(path.join(OUT,'MANIFEST.sha256.json')),manifestTxt=fs.readFileSync(path.join(OUT,'MANIFEST.sha256'));
const anchorPayload={schema:'trinity-accord/chronicle-sidechain-anchor-payload/v2',record_count:l1.record_count,l1_merkle_root_sha256:l1.merkle_root_sha256,manifest_sha256_json:sha(manifestJson),manifest_sha256_txt:sha(manifestTxt),offline_verification_pass:true,l2_execution_inclusion_pass:true,l3_settlement_status:'not_yet_captured',canon_boundary:'non-amending; three Bitcoin inscriptions remain Canon'};
const canonical=JSON.stringify(anchorPayload,Object.keys(anchorPayload).sort());const messageSha=sha(Buffer.from(canonical));
const anchor={schema:'trinity-accord/chronicle-sidechain-anchor-request/v2',generated_at:new Date().toISOString(),payload:anchorPayload,canonical_payload_json:canonical,message_sha256:messageSha,bitcoin:{method:'bip340-taproot-xonly',address:'bc1ppmwvyxekh44m35x43k55z7r59nn33v8w2xmvu6s6ar4zyx57sxestxq0jf',status:'pending_external_guardian_signature',note:'The historical 2025 BIP340 signature is immutable and does not cover this 2026 sidechain evidence. Sign this new message_sha256 only with the corresponding guardian key.'},ethereum:{status:'pending_external_guardian_attestation',note:'A new Ethereum transaction/signature must bind message_sha256; historical ETH witnesses are not retroactively extended.'},ots:{status:'pending_new_timestamp_anchor'},boundary:'ANCHOR-REQUEST.json is intentionally excluded from MANIFEST.sha256 to avoid a circular self-commitment. The immutable release archive SHA-256 covers both the manifest and this request.'};
writeJson(path.join(E,'ANCHOR-REQUEST.json'),anchor);
console.log(`[FINALIZE COMPLETE] records=${l1.record_count} l1=${l1.merkle_root_sha256} manifest=${anchorPayload.manifest_sha256_json} anchor=${messageSha}`);
