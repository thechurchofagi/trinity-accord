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
function numberEnv(name, fallback) {
  const value = Number(process.env[name] || fallback);
  if (!Number.isFinite(value) || value < 0) throw new Error(`Invalid ${name}`);
  return value;
}
function sleep(ms) { return new Promise(resolve => setTimeout(resolve, ms)); }
function write(path, value) { fs.writeFileSync(path, JSON.stringify(value, null, 2) + '\n'); }

const payloadPath = arg('--payload');
const priorReceiptPath = arg('--prior-receipt');
const outPath = arg('--out');
const txid = arg('--txid');
const sourceSha = arg('--source-sha');
const versionDoi = arg('--doi');
const expectedSha = arg('--sha256');
if (!/^[A-Za-z0-9_-]{43}$/.test(txid)) throw new Error('Invalid Arweave transaction id');
if (!/^[0-9a-f]{40}$/.test(sourceSha)) throw new Error('Invalid source SHA');
if (!/^10\.5281\/zenodo\.\d+$/.test(versionDoi)) throw new Error('Invalid repository DOI');
if (!/^[0-9a-f]{64}$/.test(expectedSha)) throw new Error('Invalid payload SHA-256');

const payload = fs.readFileSync(payloadPath);
const payloadSha = sha256(payload);
if (payloadSha !== expectedSha) throw new Error('Local payload digest mismatch');
const prior = JSON.parse(fs.readFileSync(priorReceiptPath, 'utf8'));
if ((prior.txid || prior.tx_id) !== txid) throw new Error('Prior receipt transaction mismatch');
if (prior.source_git_commit_sha !== sourceSha) throw new Error('Prior receipt source mismatch');
if (prior.repository_version_doi !== versionDoi) throw new Error('Prior receipt DOI mismatch');
if ((prior.payload_sha256 || prior.data_sha256) !== payloadSha) throw new Error('Prior receipt payload mismatch');

const arweave = Arweave.init({host:'arweave.net', port:443, protocol:'https', timeout:30000, logging:false});
const transaction = await arweave.transactions.get(txid);
const tags = Object.fromEntries(transaction.tags.map(tag => [
  tag.get('name', {decode:true, string:true}),
  tag.get('value', {decode:true, string:true}),
]));
const expectedTags = {
  'Content-Type': 'application/gzip',
  'App-Name': 'Trinity-Accord',
  'Archive-Type': 'homepage-machine-entrypoint-snapshot',
  'Source-Git-Commit': sourceSha,
  'Repository-Version-DOI': versionDoi,
  'Data-SHA256': payloadSha,
  'Boundary': 'mirror-not-authority-non-amending',
};
for (const [name, value] of Object.entries(expectedTags)) {
  if (tags[name] !== value) throw new Error(`Arweave tag mismatch: ${name}`);
}

const retries = numberEnv('ARWEAVE_READBACK_MAX_RETRIES', 30);
const delayMs = numberEnv('ARWEAVE_READBACK_DELAY_MS', 10000);
const maxSeconds = numberEnv('ARWEAVE_READBACK_MAX_SECONDS', 420);
const started = Date.now();
let readbackSha = null;
for (let attempt = 1; attempt <= retries; attempt++) {
  if ((Date.now() - started) / 1000 >= maxSeconds) break;
  try {
    const raw = await arweave.transactions.getData(txid, {decode:true, string:false});
    readbackSha = sha256(Buffer.from(raw));
    if (readbackSha === payloadSha) {
      const result = {
        ...prior,
        schema: 'trinityaccord.homepage-arweave-upload-result.v1',
        result: 'uploaded',
        txid,
        tx_id: txid,
        source_git_commit_sha: sourceSha,
        repository_version_doi: versionDoi,
        payload_sha256: payloadSha,
        data_sha256: payloadSha,
        readback_sha256: readbackSha,
        hash_match: true,
        bytes: payload.length,
        resumed_from_checkpoint: true,
        tags: expectedTags,
        boundary: {
          arweave_snapshot_is_mirror_only: true,
          arweave_snapshot_is_not_authority: true,
          arweave_snapshot_is_not_amendment: true,
          bitcoin_originals_prevail: true,
        },
      };
      write(outPath, result);
      console.log(`ARWEAVE_EXISTING_PAYLOAD_VERIFIED txid=${txid} sha256=${payloadSha}`);
      process.exit(0);
    }
    console.error(`ARWEAVE_EXISTING_PAYLOAD_RETRY attempt=${attempt} digest=${readbackSha}`);
  } catch (error) {
    console.error(`ARWEAVE_EXISTING_PAYLOAD_RETRY attempt=${attempt} error=${error.message}`);
  }
  if (attempt < retries) await sleep(delayMs);
}
throw new Error(`Existing Arweave payload verification failed for ${txid}; last_digest=${readbackSha}`);
