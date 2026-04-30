#!/usr/bin/env node
/**
 * backup-nft-individual.mjs
 * 
 * Downloads each NFT's CAR files individually from Arweave,
 * packages per-NFT tar.gz with manifest, uploads to GitHub Release.
 * 
 * Usage:
 *   GITHUB_TOKEN=xxx node scripts/backup-nft-individual.mjs [--contract 0x019372bB...] [--dry-run]
 * 
 * Resumable: skips already-downloaded files.
 */

import fs from 'fs';
import path from 'path';
import crypto from 'crypto';
import { execSync } from 'child_process';

const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const REPO = 'thechurchofagi/trinity-accord';
const RELEASE_TAG = 'nft-individual-v1';
const CAR_FILE = 'archive/evidence/nft-recovery-package/recovery-package.bin';
const TMP_DIR = '/tmp/nft-individual';
const GATEWAYS = ['https://arweave.net', 'https://ar-io.net'];
const MAX_RETRIES = 3;

function sha256(buf) {
  return crypto.createHash('sha256').update(buf).digest('hex');
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

// Parse recovery-package.bin to extract token_index.json
function extractTokenIndex() {
  const raw = fs.readFileSync(CAR_FILE);
  let pos = 0;
  
  // Parse CAR header (unsigned varint)
  let shift = 0, headerLen = 0;
  while (true) {
    const b = raw[pos]; headerLen |= (b & 0x7f) << shift; pos++; shift += 7;
    if (b < 0x80) break;
  }
  pos += headerLen;

  // Iterate blocks
  while (pos < raw.length) {
    shift = 0; let blockLen = 0;
    while (pos < raw.length) {
      const b = raw[pos]; blockLen |= (b & 0x7f) << shift; pos++; shift += 7;
      if (b < 0x80) break;
    }
    if (blockLen === 0 || pos + blockLen > raw.length) break;
    
    const block = raw.slice(pos, pos + blockLen);
    pos += blockLen;

    // Search for JSON with token_index structure
    let search = 0;
    while (search < block.length) {
      const start = block.indexOf(0x7b, search); // '{'
      if (start < 0) break;
      let depth = 0, end = -1;
      for (let i = start; i < block.length; i++) {
        if (block[i] === 0x7b) depth++;
        else if (block[i] === 0x7d) depth--;
        if (depth === 0) { end = i; break; }
      }
      if (end > start) {
        try {
          const obj = JSON.parse(block.slice(start, end + 1).toString());
          if (typeof obj === 'object' && !Array.isArray(obj)) {
            const keys = Object.keys(obj);
            const isTokenIndex = keys.some(k => {
              const v = obj[k];
              if (typeof v !== 'object' || v === null || Array.isArray(v)) return false;
              return Object.values(v).some(t => t && typeof t === 'object' && (t.metadata || t.media));
            });
            if (isTokenIndex) return obj;
          }
        } catch {}
        search = end + 1;
      } else {
        search = start + 1;
      }
    }
  }
  throw new Error('token_index.json not found in CAR');
}

// Download from Arweave with retries
async function downloadTxid(txid, retries = MAX_RETRIES) {
  for (let attempt = 0; attempt <= retries; attempt++) {
    const gw = GATEWAYS[attempt % GATEWAYS.length];
    try {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 120_000);
      const res = await fetch(`${gw}/${txid}`, { signal: controller.signal });
      clearTimeout(timeout);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return Buffer.from(await res.arrayBuffer());
    } catch (err) {
      if (attempt === retries) throw err;
      await sleep(2000 * (attempt + 1));
    }
  }
}

// GitHub Release helpers
async function ensureRelease() {
  const res = await fetch(`https://api.github.com/repos/${REPO}/releases/tags/${RELEASE_TAG}`, {
    headers: { Authorization: `Bearer ${GITHUB_TOKEN}`, Accept: 'application/vnd.github+json' },
  });
  if (res.ok) return await res.json();

  console.log(`Creating release ${RELEASE_TAG}...`);
  const create = await fetch(`https://api.github.com/repos/${REPO}/releases`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${GITHUB_TOKEN}`,
      Accept: 'application/vnd.github+json',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      tag_name: RELEASE_TAG,
      name: `NFT Individual Backup - 175 NFTs`,
      body: `## Individual NFT CAR Files\n\nEach NFT's metadata and media CAR files from Arweave.\n\nSee NFT-BACKUP-PROVENANCE.md for the chain of trust from Bitcoin signature to each NFT.\n\nGenerated: ${new Date().toISOString()}`,
    }),
  });
  if (!create.ok) throw new Error(`Create release failed: ${create.status}`);
  return await create.json();
}

async function uploadAsset(releaseId, filePath, filename) {
  const buf = fs.readFileSync(filePath);
  const url = `https://uploads.github.com/repos/${REPO}/releases/${releaseId}/assets?name=${encodeURIComponent(filename)}`;
  const res = await fetch(url, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${GITHUB_TOKEN}`,
      'Content-Type': 'application/gzip',
      'Content-Length': buf.length.toString(),
    },
    body: buf,
  });
  if (!res.ok) throw new Error(`Upload failed: ${res.status}`);
  console.log(`  ✅ ${filename} (${(buf.length / 1024).toFixed(1)}KB)`);
}

// Main
async function main() {
  const args = process.argv.slice(2);
  const dryRun = args.includes('--dry-run');
  const contractFilter = args.includes('--contract') ? args[args.indexOf('--contract') + 1] : null;

  console.log('📦 NFT Individual Backup → GitHub Release');
  console.log(`   Source: ${CAR_FILE}`);
  console.log(`   Release: ${RELEASE_TAG}`);
  if (contractFilter) console.log(`   Contract filter: ${contractFilter}`);
  console.log();

  // 1. Extract token index
  console.log('📖 Extracting token_index.json...');
  const index = extractTokenIndex();
  const contracts = contractFilter ? [contractFilter] : Object.keys(index);
  
  let totalNfts = 0, totalTxids = 0;
  for (const c of contracts) {
    if (!index[c]) { console.log(`  ⚠️ Contract ${c} not found`); continue; }
    totalNfts += Object.keys(index[c]).length;
    for (const entry of Object.values(index[c])) {
      if (entry.metadata?.txid) totalTxids++;
      for (const m of entry.media || []) {
        if (m.txid) totalTxids++;
      }
    }
  }
  console.log(`   ${totalNfts} NFTs, ${totalTxids} CAR files to download`);
  console.log();

  if (dryRun) {
    console.log('🔍 DRY RUN — listing NFTs:');
    for (const c of contracts) {
      for (const [tid, entry] of Object.entries(index[c] || {})) {
        const metaTx = entry.metadata?.txid || 'N/A';
        const mediaCount = (entry.media || []).filter(m => m.txid).length;
        console.log(`  ${c.slice(0,10)}.../${tid.slice(0,20)}...  meta=${metaTx.slice(0,12)}...  media=${mediaCount}`);
      }
    }
    return;
  }

  // 2. Download and package
  fs.mkdirSync(TMP_DIR, { recursive: true });
  fs.mkdirSync(path.join(TMP_DIR, 'cars'), { recursive: true });

  let done = 0, pass = 0, fail = 0;
  const release = await ensureRelease();
  console.log(`Release: ${RELEASE_TAG} (id: ${release.id})`);
  console.log();

  for (const contract of contracts) {
    if (!index[contract]) continue;
    
    for (const [tokenId, entry] of Object.entries(index[contract])) {
      const nftDir = path.join(TMP_DIR, 'cars', `${contract}_${tokenId}`);
      fs.mkdirSync(nftDir, { recursive: true });

      const manifest = { contract, tokenId, files: [] };
      const files = [];

      // Collect all CARs for this NFT
      if (entry.metadata?.txid) {
        files.push({ role: 'metadata', ...entry.metadata });
      }
      for (const m of entry.media || []) {
        if (m.txid) {
          files.push({ role: `media:${m.leaf_path || 'unknown'}`, ...m });
        }
      }

      // Download each CAR
      for (const f of files) {
        const dest = path.join(nftDir, `${f.role.replace(/[^a-z0-9]/g, '_')}.car`);
        
        if (fs.existsSync(dest) && fs.statSync(dest).size > 0) {
          const hash = sha256(fs.readFileSync(dest));
          manifest.files.push({ ...f, local_sha256: hash, cached: true });
          pass++;
        } else {
          try {
            const buf = await downloadTxid(f.txid);
            fs.writeFileSync(dest, buf);
            const hash = sha256(buf);
            manifest.files.push({ ...f, local_sha256: hash, downloaded: true });
            pass++;
          } catch (err) {
            manifest.files.push({ ...f, error: err.message });
            fail++;
          }
        }
        done++;
        if (done % 10 === 0) process.stdout.write(`\r   ${done}/${totalTxids} CARs`);
      }

      // Write per-NFT manifest
      fs.writeFileSync(path.join(nftDir, 'manifest.json'), JSON.stringify(manifest, null, 2));

      // Package as tar.gz
      const shortContract = contract.slice(2, 10);
      const shortToken = tokenId.slice(0, 20);
      const tarName = `nft-${shortContract}-${shortToken}.tar.gz`;
      const tarPath = path.join(TMP_DIR, tarName);
      
      try {
        execSync(`tar czf "${tarPath}" -C "${TMP_DIR}/cars" "${contract}_${tokenId}"`, { stdio: 'pipe' });
        
        // Upload to release
        await uploadAsset(release.id, tarPath, tarName);
        
        // Clean up tar to save disk
        fs.unlinkSync(tarPath);
      } catch (err) {
        console.error(`  ❌ ${tarName}: ${err.message}`);
      }
    }
  }

  console.log(`\n=========================================`);
  console.log(`  ✅ Done! ${pass} CARs downloaded, ❌ ${fail} failed`);
  console.log(`  📦 ${totalNfts} NFT packages uploaded`);
  console.log(`=========================================`);
}

main().catch(err => {
  console.error('Fatal:', err);
  process.exit(1);
});
