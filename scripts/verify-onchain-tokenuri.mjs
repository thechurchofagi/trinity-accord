#!/usr/bin/env node
/**
 * verify-onchain-tokenuri.mjs  (ETH onchain tokenURI read audit)
 *
 * Reads token metadata from ETH chain. No Arweave download, no CAR download.
 * Data source: token_index.json or RELEASE-MANIFEST.json (for contract/token_id/expected_root_cid).
 *
 * Per-token checks:
 *   - supportsInterface: ERC-721, ERC-721 Metadata, ERC-1155, ERC-1155 Metadata URI
 *   - tokenURI(uint256)  — ERC-721
 *   - uri(uint256)       — ERC-1155
 *   - ownerOf(uint256)   — ERC-721
 *
 * Classification:
 *   pass                       — URI returned, CID matches expected_root_cid
 *   fail                       — URI returned but CID mismatch, or hard_warning promoted
 *   hard_warning               — URI returned but CID not extractable
 *   skip_metadata_unavailable  — contract doesn't support metadata, both URI calls empty/reverted
 *   unknown                    — RPC error, decode error, needs manual review
 *
 * Output: ONCHAIN-READ-AUDIT.json
 *
 * Usage:
 *   ETH_RPC_URL=xxx node scripts/verify-onchain-tokenuri.mjs \
 *     [--release-tag nft-arweave-mirror-175-v1] \
 *     [--source token_index|manifest] \
 *     [--concurrency 10]
 */

import fs from 'fs';
import path from 'path';
import crypto from 'crypto';

// ─── Config ────────────────────────────────────────────────────────────────

const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const ETH_RPC_URL = process.env.ETH_RPC_URL || '';
const REPO = process.env.REPO || 'thechurchofagi/trinity-accord';
const TOKEN_INDEX_FILE = 'token_index.json';
const MAX_RETRIES = 3;
const ETH_CONCURRENCY = Number(process.env.ETH_CONCURRENCY || 5);

// ERC-721 tokenURI(uint256) selector
const ERC721_TOKENURI_SELECTOR = '0xc87b56dd';
// ERC-1155 uri(uint256) selector
const ERC1155_URI_SELECTOR = '0x0e89341c';
// supportsInterface(bytes4) selector
const SUPPORTS_INTERFACE_SELECTOR = '0x01ffc9a7';
// Interface IDs
const IFACE_ERC721            = '0x80ac58cd';
const IFACE_ERC721_METADATA   = '0x5b5e139f';
const IFACE_ERC1155           = '0xd9b67a26';
const IFACE_ERC1155_METADATA  = '0x0e89341c';
// ownerOf(uint256) selector
const ERC721_OWNEROF_SELECTOR = '0x6352211e';

// ─── Helpers ───────────────────────────────────────────────────────────────

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }
function log(msg) { console.log(msg); }
function err(msg) { console.error(msg); }

// ─── Concurrency pool ──────────────────────────────────────────────────────

async function runConcurrent(tasks, limit) {
  const results = new Array(tasks.length);
  let nextIdx = 0;
  async function worker() {
    while (nextIdx < tasks.length) {
      const idx = nextIdx++;
      try { results[idx] = await tasks[idx](); }
      catch (e) { results[idx] = e; }
    }
  }
  const workers = Array.from({ length: Math.min(limit, tasks.length) }, () => worker());
  await Promise.all(workers);
  return results;
}

// ─── ETH helpers ───────────────────────────────────────────────────────────

async function tryEthCallRaw(rpcUrl, contractAddr, callData) {
  for (let attempt = 0; attempt < 3; attempt++) {
    try {
      const res = await fetch(rpcUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          jsonrpc: '2.0', id: 1,
          method: 'eth_call',
          params: [{ to: contractAddr, data: callData }, 'latest'],
        }),
      });
      const json = await res.json();
      if (json.error) {
        const msg = json.error.message || JSON.stringify(json.error);
        if (msg.includes('CUP') || msg.includes('rate') || msg.includes('limit')) {
          await sleep(2000 * (attempt + 1));
          continue;
        }
        return { raw_hex: null, error: msg };
      }
      return { raw_hex: json.result || '0x', error: null };
    } catch (e) {
      if (attempt < 2) { await sleep(1000 * (attempt + 1)); continue; }
      return { raw_hex: null, error: e.message };
    }
  }
  return { raw_hex: null, error: 'max retries exceeded' };
}

function decodeAbiString(hex) {
  if (!hex || hex === '0x' || hex.length < 130) return null;
  try {
    const offset = parseInt(hex.slice(2, 66), 16) * 2 + 2;
    const len = parseInt(hex.slice(66, 130), 16) * 2;
    const strHex = hex.slice(130, 130 + len);
    let s = '';
    for (let i = 0; i < strHex.length; i += 2) {
      s += String.fromCharCode(parseInt(strHex.slice(i, i + 2), 16));
    }
    return s || null;
  } catch {
    return null;
  }
}

async function checkSupportsInterface(rpcUrl, contractAddr, interfaceId) {
  const callData = SUPPORTS_INTERFACE_SELECTOR + interfaceId.slice(2).padEnd(64, '0');
  const { raw_hex, error } = await tryEthCallRaw(rpcUrl, contractAddr, callData);
  if (error) return { supported: null, raw_hex, error };
  if (!raw_hex || raw_hex === '0x') return { supported: false, raw_hex, error: null };
  const val = parseInt(raw_hex, 16);
  return { supported: val === 1, raw_hex, error: null };
}

async function callOwnerOf(rpcUrl, contractAddr, tokenId) {
  const paddedId = BigInt(tokenId).toString(16).padStart(64, '0');
  const callData = ERC721_OWNEROF_SELECTOR + paddedId;
  const { raw_hex, error } = await tryEthCallRaw(rpcUrl, contractAddr, callData);
  if (error) return { address: null, raw_hex, error };
  if (!raw_hex || raw_hex === '0x' || raw_hex.length < 66) return { address: null, raw_hex, error: 'empty result' };
  const addr = '0x' + raw_hex.slice(26, 66);
  return { address: addr, raw_hex, error: null };
}

function extractCidFromUri(uri) {
  if (!uri) return null;
  const ipfsMatch = uri.match(/ipfs:\/\/(?:ipfs\/)?([a-zA-Z0-9]+)/);
  if (ipfsMatch) return ipfsMatch[1];
  const httpsIpfsMatch = uri.match(/\/ipfs\/([a-zA-Z0-9]+)/);
  if (httpsIpfsMatch) return httpsIpfsMatch[1];
  const arMatch = uri.match(/ar:\/\/([a-zA-Z0-9_-]+)/);
  if (arMatch) return arMatch[1];
  const arHttpMatch = uri.match(/arweave\.net\/([a-zA-Z0-9_-]+)/);
  if (arHttpMatch) return arHttpMatch[1];
  return null;
}

function expandErc1155Id(uri, tokenId) {
  if (!uri || !uri.includes('{id}')) return uri;
  const hexId = BigInt(tokenId).toString(16).padStart(64, '0');
  return uri.replace('{id}', hexId);
}

// ─── Classification ────────────────────────────────────────────────────────

function classifyOnchainAudit(rec) {
  const { interface_support, token_uri, uri, owner_of } = rec;

  const erc721  = interface_support?.erc721?.supported;
  const erc1155 = interface_support?.erc1155?.supported;
  const has721Meta = interface_support?.erc721_metadata?.supported;
  const has1155Meta = interface_support?.erc1155_metadata_uri?.supported;

  const tuErr = token_uri?.error;
  const tuUri = token_uri?.decoded_uri;
  const urErr = uri?.error;
  const urUri = uri?.decoded_uri;
  const tuRaw = token_uri?.raw_hex;
  const urRaw = uri?.raw_hex;

  // Check for RPC / unknown errors first
  const hasRpcError = [token_uri, uri, owner_of].some(f => f?.error && !f.error.includes('revert') && !f.error.includes('execution reverted'));
  if (hasRpcError) {
    return { status: 'unknown', reason: 'rpc_error — needs manual review of raw result' };
  }

  const effectiveUri = tuUri || urUri;
  const effectiveCid = token_uri?.extracted_cid || uri?.extracted_cid;

  if (effectiveUri) {
    if (effectiveCid) {
      if (rec.metadata_root_cid && effectiveCid === rec.metadata_root_cid) {
        return { status: 'pass', reason: 'uri_cid_matches_token_index' };
      } else if (rec.metadata_root_cid) {
        return { status: 'fail', reason: `cid_mismatch: onchain=${effectiveCid} vs token_index=${rec.metadata_root_cid}` };
      } else {
        return { status: 'pass', reason: 'uri_cid_extracted_but_no_token_index_to_compare' };
      }
    } else {
      return { status: 'hard_warning', reason: `uri_returned_but_cid_not_extractable: ${effectiveUri.slice(0, 120)}` };
    }
  }

  // No URI from either tokenURI or uri
  const tuReverted = tuErr && (tuErr.includes('revert') || tuErr.includes('execution reverted'));
  const urReverted = urErr && (urErr.includes('revert') || urErr.includes('execution reverted'));
  const tuEmpty = tuRaw === '0x' || tuRaw === null;
  const urEmpty = urRaw === '0x' || urRaw === null;

  if ((tuReverted || tuEmpty) && (urReverted || urEmpty)) {
    if (!has721Meta && !has1155Meta) {
      return { status: 'skip_metadata_unavailable', reason: 'contract_does_not_support_metadata_interface_and_both_uri_calls_empty' };
    }
    if (tuReverted || urReverted) {
      return { status: 'unknown', reason: 'metadata_interface_supported_but_uri_calls_reverted — needs manual review' };
    }
    return { status: 'skip_metadata_unavailable', reason: 'uri_calls_returned_empty' };
  }

  return { status: 'unknown', reason: 'mixed_uri_results — needs manual review' };
}

// ─── GitHub helpers ────────────────────────────────────────────────────────

function ghHeaders(extra = {}) {
  return { Authorization: `Bearer ${GITHUB_TOKEN}`, Accept: 'application/vnd.github+json', ...extra };
}

async function getReleaseByTag(tag) {
  const res = await fetch(
    `https://api.github.com/repos/${REPO}/releases/tags/${tag}`,
    { headers: ghHeaders() }
  );
  if (!res.ok) throw new Error(`Release ${tag} not found: ${res.status}`);
  return res.json();
}

async function downloadAsset(assetId, retries = MAX_RETRIES) {
  for (let attempt = 0; attempt <= retries; attempt++) {
    const res = await fetch(
      `https://api.github.com/repos/${REPO}/releases/assets/${assetId}`,
      { headers: ghHeaders({ Accept: 'application/octet-stream' }) }
    );
    if (res.ok) return Buffer.from(await res.arrayBuffer());
    if ((res.status >= 500 || res.status === 403 || res.status === 429) && attempt < retries) {
      await sleep(5000 * (attempt + 1));
      continue;
    }
    throw new Error(`Download failed: ${res.status}`);
  }
}

// ─── Main ──────────────────────────────────────────────────────────────────

async function main() {
  const args = process.argv.slice(2);
  const releaseTag = args.includes('--release-tag') ? args[args.indexOf('--release-tag') + 1] : 'nft-arweave-mirror-175-v1';
  const source = args.includes('--source') ? args[args.indexOf('--source') + 1] : 'manifest';
  const concurrencyArg = args.includes('--concurrency') ? Number(args[args.indexOf('--concurrency') + 1]) : null;
  const concurrency = concurrencyArg || ETH_CONCURRENCY;

  if (!ETH_RPC_URL) { err('❌ ETH_RPC_URL required'); process.exit(1); }

  let sourceCommit = 'unknown';
  try { sourceCommit = require('child_process').execFileSync('git', ['rev-parse', 'HEAD'], { encoding: 'utf-8' }).trim(); } catch {}

  log('═══════════════════════════════════════════════════════════');
  log('  ETH Onchain tokenURI Read Audit');
  log('═══════════════════════════════════════════════════════════');
  log(`  Source     : ${source}`);
  log(`  Concurrency: ${concurrency}`);
  log(`  Commit     : ${sourceCommit}`);
  log('');

  // ── Load token list ─────────────────────────────────────────────────

  let nftList = [];

  if (source === 'manifest') {
    log('📦 Loading from RELEASE-MANIFEST.json (via GitHub Release)...');
    const release = await getReleaseByTag(releaseTag);
    const allAssets = [];
    let page = 1;
    while (true) {
      const res = await fetch(
        `https://api.github.com/repos/${REPO}/releases/${release.id}/assets?per_page=100&page=${page}`,
        { headers: ghHeaders() }
      );
      if (!res.ok) break;
      const batch = await res.json();
      if (!batch.length) break;
      allAssets.push(...batch);
      page++;
    }
    const manifestAsset = allAssets.find(a => a.name === 'RELEASE-MANIFEST.json');
    if (!manifestAsset) { err('❌ RELEASE-MANIFEST.json not found'); process.exit(1); }
    const manifestBuf = await downloadAsset(manifestAsset.id);
    const manifest = JSON.parse(manifestBuf.toString('utf-8'));

    for (const entry of manifest.per_nft_assets || []) {
      const metaFile = entry.files?.find(f => f.role === 'metadata');
      nftList.push({
        contract: entry.contract,
        token_id: entry.token_id,
        metadata_root_cid: metaFile?.expected_root_cid || null,
      });
    }
    log(`  ${nftList.length} NFTs from manifest`);
  } else {
    log('📖 Loading from token_index.json...');
    const index = JSON.parse(fs.readFileSync(TOKEN_INDEX_FILE, 'utf-8'));
    for (const [contract, tokens] of Object.entries(index)) {
      for (const [tokenId, entry] of Object.entries(tokens)) {
        nftList.push({
          contract,
          token_id: tokenId,
          metadata_root_cid: entry.metadata?.root_cid || null,
        });
      }
    }
    log(`  ${nftList.length} NFTs from token_index`);
  }
  log('');

  // ── Onchain audit ───────────────────────────────────────────────────

  log('🔗 Auditing onchain tokenURI (per-token)...');
  const auditRecords = [];

  const tasks = nftList.map(nft => async () => {
    const rec = {
      contract: nft.contract,
      token_id: nft.token_id,
      metadata_root_cid: nft.metadata_root_cid,
      interface_support: {},
      token_uri: null,
      uri: null,
      owner_of: null,
      decoded_uri: null,
      extracted_cid: null,
      status: null,
      status_reason: null,
    };

    // 1. supportsInterface checks
    const ifaceChecks = [
      { key: 'erc721',                 id: IFACE_ERC721,           label: 'ERC721 (0x80ac58cd)' },
      { key: 'erc721_metadata',        id: IFACE_ERC721_METADATA,  label: 'ERC721Metadata (0x5b5e139f)' },
      { key: 'erc1155',                id: IFACE_ERC1155,          label: 'ERC1155 (0xd9b67a26)' },
      { key: 'erc1155_metadata_uri',   id: IFACE_ERC1155_METADATA, label: 'ERC1155MetadataURI (0x0e89341c)' },
    ];

    for (const iface of ifaceChecks) {
      const result = await checkSupportsInterface(ETH_RPC_URL, nft.contract, iface.id);
      rec.interface_support[iface.key] = {
        interface_id: iface.id,
        label: iface.label,
        supported: result.supported,
        raw_hex: result.raw_hex,
        error: result.error,
      };
      await sleep(100); // rate limit protection
    }

    // 2. tokenURI(uint256)
    {
      const paddedId = BigInt(nft.token_id).toString(16).padStart(64, '0');
      const callData = ERC721_TOKENURI_SELECTOR + paddedId;
      const { raw_hex, error } = await tryEthCallRaw(ETH_RPC_URL, nft.contract, callData);
      const decoded = decodeAbiString(raw_hex);
      rec.token_uri = {
        selector: ERC721_TOKENURI_SELECTOR,
        raw_hex,
        error,
        decoded_uri: decoded,
        extracted_cid: decoded ? extractCidFromUri(expandErc1155Id(decoded, nft.token_id)) : null,
      };
      await sleep(100);
    }

    // 3. uri(uint256)
    {
      const paddedId = BigInt(nft.token_id).toString(16).padStart(64, '0');
      const callData = ERC1155_URI_SELECTOR + paddedId;
      const { raw_hex, error } = await tryEthCallRaw(ETH_RPC_URL, nft.contract, callData);
      const decoded = decodeAbiString(raw_hex);
      rec.uri = {
        selector: ERC1155_URI_SELECTOR,
        raw_hex,
        error,
        decoded_uri: decoded,
        extracted_cid: decoded ? extractCidFromUri(expandErc1155Id(decoded, nft.token_id)) : null,
      };
      await sleep(100);
    }

    // 4. ownerOf(uint256)
    {
      const result = await callOwnerOf(ETH_RPC_URL, nft.contract, nft.token_id);
      rec.owner_of = {
        selector: ERC721_OWNEROF_SELECTOR,
        raw_hex: result.raw_hex,
        address: result.address,
        error: result.error,
      };
      await sleep(100);
    }

    // 5. Effective decoded_uri / extracted_cid
    rec.decoded_uri = rec.token_uri?.decoded_uri || rec.uri?.decoded_uri || null;
    rec.extracted_cid = rec.token_uri?.extracted_cid || rec.uri?.extracted_cid || null;

    // 6. Classify
    const classification = classifyOnchainAudit(rec);
    rec.status = classification.status;
    rec.status_reason = classification.reason;

    auditRecords.push(rec);

    if (auditRecords.length % 20 === 0) {
      process.stdout.write(`\r   ${auditRecords.length}/${nftList.length} tokens`);
    }
  });

  await runConcurrent(tasks, concurrency);
  log(`\r   ${auditRecords.length}/${nftList.length} tokens audited`);

  // ── Summary ─────────────────────────────────────────────────────────

  const statusCounts = {};
  for (const rec of auditRecords) {
    statusCounts[rec.status] = (statusCounts[rec.status] || 0) + 1;
  }
  log('');
  log('  On-chain audit summary:');
  for (const [status, count] of Object.entries(statusCounts).sort((a, b) => b[1] - a[1])) {
    log(`    ${status}: ${count}`);
  }

  // ── Write ONCHAIN-READ-AUDIT.json ───────────────────────────────────

  const readablePass = statusCounts['pass'] || 0;
  const failCount = statusCounts['fail'] || 0;
  const hardWarning = statusCounts['hard_warning'] || 0;
  const skipCount = statusCounts['skip_metadata_unavailable'] || 0;
  const unknownCount = statusCounts['unknown'] || 0;

  const auditReport = {
    schema: 'onchain-read-audit-v2',
    generated_at: new Date().toISOString(),
    source_commit: sourceCommit,
    source: source,
    eth_rpc_url: ETH_RPC_URL.replace(/\/\/[^@]+@/, '//***@'),
    total_tokens: auditRecords.length,
    onchain_scope: 'readable_token_uris_only',
    readable_pass: readablePass,
    fail: failCount,
    hard_warning: hardWarning,
    skip_metadata_unavailable: skipCount,
    unknown: unknownCount,
    status_summary: statusCounts,
    tokens: auditRecords,
  };

  const auditPath = path.join(process.cwd(), 'ONCHAIN-READ-AUDIT.json');
  fs.writeFileSync(auditPath, JSON.stringify(auditReport, null, 2));
  log(`\n  📝 ONCHAIN-READ-AUDIT.json written`);

  // ── Final ───────────────────────────────────────────────────────────

  log('');
  log('═══════════════════════════════════════════════════════════');
  log(`  Tokens audited   : ${auditRecords.length}`);
  log(`  readable_pass    : ${readablePass}`);
  log(`  fail             : ${failCount}`);
  log(`  hard_warning     : ${hardWarning}`);
  log(`  skip_meta_unavail: ${skipCount}`);
  log(`  unknown          : ${unknownCount}`);
  log('═══════════════════════════════════════════════════════════');

  if (failCount > 0 || unknownCount > 0) {
    err(`\n  ❌ ${failCount} fail + ${unknownCount} unknown — see ONCHAIN-READ-AUDIT.json`);
    process.exit(1);
  }

  log('\n  ✅ All tokens classified.');
}

main().catch(e => { err('Fatal:', e); process.exit(1); });
