#!/usr/bin/env node
import fs from 'node:fs';
import crypto from 'node:crypto';
import Arweave from 'arweave';

function arg(name) {
  const i = process.argv.indexOf(name);
  if (i < 0 || i + 1 >= process.argv.length) throw new Error(`Missing ${name}`);
  return process.argv[i + 1];
}
function sha256(data) { return crypto.createHash('sha256').update(data).digest('hex'); }
function parseKey() {
  const raw = (process.env.ARKEY || '').trim();
  if (!raw) throw new Error('ARKEY missing');
  return JSON.parse(raw.startsWith('{') ? raw : Buffer.from(raw, 'base64').toString('utf8'));
}
function numberEnv(name, fallback) {
  const value = Number(process.env[name] || fallback);
  if (!Number.isFinite(value) || value < 0) throw new Error(`Invalid ${name}`);
  return value;
}
function sleep(ms) { return new Promise(resolve => setTimeout(resolve, ms)); }
function write(path, value) { fs.writeFileSync(path, JSON.stringify(value, null, 2) + '\n'); }

const payloadPath = arg('--payload');
const outPath = arg('--out');
const sourceSha = arg('--source-sha');
const versionDoi = arg('--doi');
if (!/^[0-9a-f]{40}$/.test(sourceSha)) throw new Error('Invalid source SHA');
if (!/^10\.5281\/zenodo\.\d+$/.test(versionDoi)) throw new Error('Invalid repository DOI');
const payload = fs.readFileSync(payloadPath);
const payloadSha = sha256(payload);
const maxBytes = numberEnv('ARWEAVE_MAX_PAYLOAD_BYTES', 8 * 1024 * 1024);
if (payload.length > maxBytes) throw new Error(`Payload exceeds ${maxBytes} bytes`);

const arweave = Arweave.init({host:'arweave.net', port:443, protocol:'https', timeout:30000, logging:false});
const jwk = parseKey();
const address = await arweave.wallets.jwkToAddress(jwk);
const addressHash = sha256(address);
const retries = numberEnv('ARWEAVE_READBACK_MAX_RETRIES', 30);
const delayMs = numberEnv('ARWEAVE_READBACK_DELAY_MS', 10000);
const maxSeconds = numberEnv('ARWEAVE_READBACK_MAX_SECONDS', 420);
let existing = null;
if (fs.existsSync(outPath)) existing = JSON.parse(fs.readFileSync(outPath, 'utf8'));
let txid = existing?.txid || existing?.tx_id || null;
let uploadedAt = existing?.uploaded_at || null;
let reward = existing?.upload_cost_winston || null;
let resumed = Boolean(txid);

function receipt(result, readbackSha, match) {
  return {
    schema: 'trinityaccord.homepage-arweave-upload-result.v1',
    result,
    txid,
    tx_id: txid,
    uploaded_at: uploadedAt,
    source_git_commit_sha: sourceSha,
    repository_version_doi: versionDoi,
    payload_sha256: payloadSha,
    data_sha256: payloadSha,
    readback_sha256: readbackSha,
    hash_match: match,
    bytes: payload.length,
    upload_cost_winston: reward,
    wallet_address_sha256: addressHash,
    resumed_from_checkpoint: resumed,
    tags: {
      'Content-Type': 'application/gzip',
      'App-Name': 'Trinity-Accord',
      'Archive-Type': 'homepage-machine-entrypoint-snapshot',
      'Source-Git-Commit': sourceSha,
      'Repository-Version-DOI': versionDoi,
      'Data-SHA256': payloadSha,
      'Boundary': 'mirror-not-authority-non-amending'
    },
    boundary: {
      arweave_snapshot_is_mirror_only: true,
      arweave_snapshot_is_not_authority: true,
      arweave_snapshot_is_not_amendment: true,
      bitcoin_originals_prevail: true
    }
  };
}

if (existing && txid) {
  if ((existing.payload_sha256 || existing.data_sha256) !== payloadSha) throw new Error('Checkpoint payload mismatch');
  if (existing.source_git_commit_sha !== sourceSha) throw new Error('Checkpoint source mismatch');
  if (existing.repository_version_doi !== versionDoi) throw new Error('Checkpoint DOI mismatch');
  console.log(`ARWEAVE_HOMEPAGE_RESUME txid=${txid}`);
} else {
  const tx = await arweave.createTransaction({data: payload}, jwk);
  const tags = receipt('pending', null, false).tags;
  for (const [key, value] of Object.entries(tags)) tx.addTag(key, value);
  reward = String(tx.reward);
  const maxRewardAr = numberEnv('ARWEAVE_MAX_TRANSACTION_REWARD_AR', 0.05);
  if (Number(reward) / 1e12 > maxRewardAr) throw new Error('Arweave reward exceeds transaction limit');
  const balance = Number(await arweave.wallets.getBalance(address)) / 1e12;
  const minimum = numberEnv('ARWEAVE_MINIMUM_REMAINING_AR', 0.25);
  if (balance - Number(reward) / 1e12 < minimum) throw new Error('Arweave balance would fall below reserve');
  await arweave.transactions.sign(tx, jwk);
  const response = await arweave.transactions.post(tx);
  if (response.status < 200 || response.status >= 300) throw new Error(`Arweave post failed: ${response.status}`);
  txid = tx.id;
  uploadedAt = new Date().toISOString();
  write(outPath, receipt('posted_pending_readback', null, false));
  console.log(`ARWEAVE_HOMEPAGE_POST_CHECKPOINT txid=${txid} sha256=${payloadSha}`);
}

const started = Date.now();
let readbackSha = null;
for (let attempt = 1; attempt <= retries; attempt++) {
  if ((Date.now() - started) / 1000 >= maxSeconds) break;
  try {
    const raw = await arweave.transactions.getData(txid, {decode:true, string:false});
    readbackSha = sha256(Buffer.from(raw));
    if (readbackSha === payloadSha) {
      write(outPath, receipt('uploaded', readbackSha, true));
      console.log(`ARWEAVE_HOMEPAGE_UPLOAD_OK txid=${txid} sha256=${payloadSha}`);
      process.exit(0);
    }
  } catch (error) {
    console.error(`ARWEAVE_HOMEPAGE_READBACK_RETRY attempt=${attempt} error=${error.message}`);
  }
  if (attempt < retries) await sleep(delayMs);
}
write(outPath, receipt('readback_failed', readbackSha, false));
throw new Error(`Arweave homepage snapshot readback failed for ${txid}`);
