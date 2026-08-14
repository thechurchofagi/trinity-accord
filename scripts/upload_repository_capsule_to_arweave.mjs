#!/usr/bin/env node
import fs from "node:fs";
import crypto from "node:crypto";
import Arweave from "arweave";

function arg(name) {
  const i = process.argv.indexOf(name);
  if (i < 0 || i + 1 >= process.argv.length) throw new Error(`Missing ${name}`);
  return process.argv[i + 1];
}
function sha256(v) { return crypto.createHash("sha256").update(v).digest("hex"); }
function parseArkey() {
  const value = (process.env.ARKEY || "").trim();
  if (!value) throw new Error("ARKEY missing");
  return JSON.parse(value.startsWith("{") ? value : Buffer.from(value, "base64").toString("utf8"));
}
const W = 1_000_000_000_000n;
function arToWinston(v) {
  const [a,b=""] = String(v).split(".");
  return BigInt(a) * W + BigInt(b.padEnd(12,"0").slice(0,12));
}
function winstonToAr(v) {
  const n = BigInt(String(v));
  return `${n / W}.${(n % W).toString().padStart(12,"0")}`;
}
function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

const payloadPath = arg("--payload");
const outPath = arg("--out");
const capsuleId = arg("--capsule-id");
const sourceSha = arg("--source-sha");
const packageSha = arg("--package-sha256");
const maxCost = process.env.REPOSITORY_ARWEAVE_MAX_COST_AR || "0.75";
const minRemaining = process.env.REPOSITORY_ARWEAVE_MIN_REMAINING_AR || "0.25";
const payload = fs.readFileSync(payloadPath);
const payloadSha = sha256(payload);
const jwk = parseArkey();
for (const f of ["kty","n","e","d"]) if (!jwk[f]) throw new Error(`ARKEY JWK missing ${f}`);
if (jwk.kty !== "RSA") throw new Error("ARKEY must be RSA JWK");

const arweave = Arweave.init({host:"arweave.net",port:443,protocol:"https",timeout:60000,logging:false});
const address = await arweave.wallets.jwkToAddress(jwk);
const balanceBefore = BigInt(await arweave.wallets.getBalance(address));
const price = BigInt(await arweave.transactions.getPrice(payload.length));
if (price > arToWinston(maxCost)) throw new Error(`Arweave cost gate exceeded: ${winstonToAr(price)} > ${maxCost} AR`);
if (balanceBefore - price < arToWinston(minRemaining)) throw new Error(`Arweave reserve gate failed: post-cost balance would fall below ${minRemaining} AR`);

const tx = await arweave.createTransaction({data: payload}, jwk);
for (const [k,v] of Object.entries({
  "Content-Type":"application/x-tar",
  "App-Name":"Trinity-Accord",
  "Archive-Type":"repository-preservation-capsule",
  "Capsule-ID":capsuleId,
  "Source-Git-Commit":sourceSha,
  "Package-Identity-SHA256":packageSha,
  "Data-SHA256":payloadSha,
  "Boundary":"mirror-not-authority-non-amending"
})) tx.addTag(k,v);
await arweave.transactions.sign(tx,jwk);
const uploader = await arweave.transactions.getUploader(tx);
while (!uploader.isComplete) await uploader.uploadChunk();

const posted = {
  schema:"trinityaccord.repository-capsule-arweave-upload-result.v1",
  status:"posted_pending_readback",
  txid:tx.id,
  capsule_id:capsuleId,
  source_git_commit_sha:sourceSha,
  package_identity_sha256:packageSha,
  payload_bytes:payload.length,
  payload_sha256:payloadSha,
  upload_cost_winston:String(price),
  upload_cost_ar:winstonToAr(price),
  balance_before_winston:String(balanceBefore),
  minimum_remaining_winston:String(arToWinston(minRemaining)),
  owner_address_sha256:sha256(address),
  boundary:{capsule_is_non_authoritative_mirror:true,bitcoin_originals_prevail:true}
};
fs.writeFileSync(outPath, JSON.stringify(posted,null,2)+"\n");

let readback = null;
let readbackSha = null;
let error = null;
for (let attempt=1; attempt<=40; attempt++) {
  try {
    const data = await arweave.transactions.getData(tx.id,{decode:true,string:false});
    const buf = Buffer.from(data);
    if (buf.length) {
      readback = buf;
      readbackSha = sha256(buf);
      if (readbackSha !== payloadSha) throw new Error(`non-empty readback SHA mismatch ${readbackSha}`);
      break;
    }
  } catch (e) { error = e.message; if (String(error).startsWith("non-empty readback SHA mismatch")) throw e; }
  if (attempt < 40) await sleep(15000);
}
if (!readback) {
  posted.status = "posted_pending_readback";
  posted.last_readback_error = error || "empty_readback";
  fs.writeFileSync(outPath, JSON.stringify(posted,null,2)+"\n");
  process.exit(2);
}
const balanceAfter = BigInt(await arweave.wallets.getBalance(address));
const result = {
  ...posted,
  status:"uploaded_and_publicly_verified",
  public_readback:"passed",
  readback_bytes:readback.length,
  readback_sha256:readbackSha,
  balance_after_winston:String(balanceAfter),
  reserve_gate_passed:balanceAfter >= arToWinston(minRemaining),
  verified_at:new Date().toISOString()
};
if (!result.reserve_gate_passed) throw new Error("post-upload reserve gate unexpectedly failed");
fs.writeFileSync(outPath, JSON.stringify(result,null,2)+"\n");
console.log(JSON.stringify({txid:tx.id,payload_sha256:payloadSha,readback_sha256:readbackSha,status:result.status}));
