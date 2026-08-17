#!/usr/bin/env node

import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import process from 'node:process';
import { Contract, Interface, JsonRpcProvider, id, zeroPadValue } from 'ethers';

const DEFAULT_ADDRESS = '0xbc63566A41cBfDB9C266a5941CBe47894DaA54A8';
const FORMATION_BASELINE = '2024-03-16T08:02:59Z';
const CLOSURE_TIME = '2025-06-29T10:49:16Z';
const OUT_DIR = path.resolve(process.env.CROSSCHAIN_OUT_DIR || 'out/chronicle-crosschain');
const WALLET = (process.env.CHRONICLE_ADDRESS || DEFAULT_ADDRESS).toLowerCase();
const ETHERSCAN_API_KEY = (process.env.ETHERSCAN_API_KEY || '').trim();
const MIRROR_MEDIA = !/^(0|false|no)$/i.test(process.env.MIRROR_MEDIA || 'true');
const MAX_MEDIA_BYTES = Number(process.env.MAX_MEDIA_BYTES || 100 * 1024 * 1024);
const FETCH_TIMEOUT_MS = Number(process.env.FETCH_TIMEOUT_MS || 45_000);
const PAGE_SIZE = 1000;

const CHAINS = [
  {
    key: 'polygon',
    name: 'Polygon Mainnet',
    chainId: 137,
    rpcUrl: process.env.POLYGON_RPC_URL || 'https://polygon.drpc.org',
    explorer: 'https://polygonscan.com',
    blockscout: 'https://polygon.blockscout.com',
  },
  {
    key: 'base',
    name: 'Base Mainnet',
    chainId: 8453,
    rpcUrl: process.env.BASE_RPC_URL || 'https://mainnet.base.org',
    explorer: 'https://base.blockscout.com',
    blockscout: 'https://base.blockscout.com',
  },
];

const erc721Abi = ['function tokenURI(uint256 tokenId) view returns (string)'];
const erc1155Abi = ['function uri(uint256 tokenId) view returns (string)'];
const transferIface = new Interface([
  'event Transfer(address indexed from,address indexed to,uint256 indexed tokenId)',
  'event TransferSingle(address indexed operator,address indexed from,address indexed to,uint256 id,uint256 value)',
  'event TransferBatch(address indexed operator,address indexed from,address indexed to,uint256[] ids,uint256[] values)',
]);
const TOPICS = {
  erc721: id('Transfer(address,address,uint256)'),
  erc1155Single: id('TransferSingle(address,address,address,uint256,uint256)'),
  erc1155Batch: id('TransferBatch(address,address,address,uint256[],uint256[])'),
};

function sha256(data) {
  return crypto.createHash('sha256').update(data).digest('hex');
}

function safeSegment(value) {
  return String(value).replace(/[^a-zA-Z0-9._-]/g, '_').slice(0, 160) || '_';
}

function sortObject(value) {
  if (Array.isArray(value)) return value.map(sortObject);
  if (value && typeof value === 'object') {
    return Object.fromEntries(Object.keys(value).sort().map((key) => [key, sortObject(value[key])]));
  }
  return value;
}

function stableJson(value) {
  return JSON.stringify(sortObject(value));
}

function direction(from, to) {
  const f = String(from || '').toLowerCase();
  const t = String(to || '').toLowerCase();
  if (f === WALLET && t === WALLET) return 'self';
  if (t === WALLET) return 'in';
  if (f === WALLET) return 'out';
  return 'related';
}

function occurrenceKey(o) {
  return [o.chainId, o.txHash, o.logIndex ?? o.transactionIndex ?? '', o.contract, o.tokenId, o.standard, o.from, o.to].join(':').toLowerCase();
}

async function mkdirp(p) {
  await fs.mkdir(p, { recursive: true });
}

async function writeJson(filename, value) {
  await mkdirp(path.dirname(filename));
  await fs.writeFile(filename, `${JSON.stringify(value, null, 2)}\n`);
}

async function fetchWithTimeout(url, options = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), FETCH_TIMEOUT_MS);
  try {
    return await fetch(url, {
      ...options,
      signal: controller.signal,
      headers: { 'user-agent': 'trinity-accord-crosschain-mirror/1.0', ...(options.headers || {}) },
    });
  } finally {
    clearTimeout(timer);
  }
}

function resolveContentUri(uri) {
  if (!uri) return null;
  if (uri.startsWith('ipfs://')) {
    const gateway = (process.env.IPFS_GATEWAY || 'https://ipfs.io/ipfs/').replace(/\/*$/, '/');
    return gateway + uri.slice('ipfs://'.length).replace(/^ipfs\//, '');
  }
  if (uri.startsWith('ar://')) {
    const gateway = (process.env.ARWEAVE_GATEWAY || 'https://arweave.net/').replace(/\/*$/, '/');
    return gateway + uri.slice('ar://'.length);
  }
  if (/^https?:\/\//i.test(uri)) return uri;
  return null;
}

function decodeDataUri(uri) {
  if (!uri?.startsWith('data:')) return null;
  const comma = uri.indexOf(',');
  if (comma < 0) return null;
  const header = uri.slice(5, comma);
  const payload = uri.slice(comma + 1);
  const isBase64 = /;base64(?:;|$)/i.test(header);
  const buffer = isBase64 ? Buffer.from(payload, 'base64') : Buffer.from(decodeURIComponent(payload), 'utf8');
  return { buffer, contentType: header.split(';')[0] || 'application/octet-stream' };
}

function replaceErc1155Id(uri, tokenId) {
  if (!uri?.includes('{id}')) return uri;
  let hex;
  try {
    hex = BigInt(tokenId).toString(16).padStart(64, '0');
  } catch {
    return uri;
  }
  return uri.replaceAll('{id}', hex);
}

async function fetchBytesFromUri(uri, maxBytes = MAX_MEDIA_BYTES) {
  const data = decodeDataUri(uri);
  if (data) {
    if (data.buffer.length > maxBytes) throw new Error(`data URI exceeds ${maxBytes} bytes`);
    return { ...data, resolvedUrl: 'data:' };
  }
  const resolvedUrl = resolveContentUri(uri);
  if (!resolvedUrl) throw new Error(`unsupported URI scheme: ${String(uri).slice(0, 80)}`);
  const response = await fetchWithTimeout(resolvedUrl);
  if (!response.ok) throw new Error(`HTTP ${response.status} for ${resolvedUrl}`);
  const announced = Number(response.headers.get('content-length') || 0);
  if (announced && announced > maxBytes) throw new Error(`content-length ${announced} exceeds ${maxBytes}`);
  const arrayBuffer = await response.arrayBuffer();
  const buffer = Buffer.from(arrayBuffer);
  if (buffer.length > maxBytes) throw new Error(`downloaded ${buffer.length} bytes exceeds ${maxBytes}`);
  return {
    buffer,
    contentType: response.headers.get('content-type') || 'application/octet-stream',
    resolvedUrl,
  };
}

function guessExtension(uri, contentType) {
  const byType = {
    'application/json': '.json', 'image/png': '.png', 'image/jpeg': '.jpg', 'image/gif': '.gif',
    'image/webp': '.webp', 'image/svg+xml': '.svg', 'video/mp4': '.mp4', 'video/webm': '.webm',
    'audio/mpeg': '.mp3', 'audio/mp4': '.m4a', 'audio/ogg': '.ogg', 'application/pdf': '.pdf', 'text/plain': '.txt', 'text/html': '.html',
  };
  const cleanType = String(contentType || '').split(';')[0].toLowerCase();
  if (byType[cleanType]) return byType[cleanType];
  try {
    const u = new URL(resolveContentUri(uri) || 'https://invalid/' + safeSegment(uri));
    const ext = path.extname(u.pathname).toLowerCase();
    if (/^\.[a-z0-9]{1,8}$/.test(ext)) return ext;
  } catch {}
  return '.bin';
}

async function etherscanPage(chainId, action, page) {
  const params = new URLSearchParams({
    chainid: String(chainId), module: 'account', action, address: WALLET,
    startblock: '0', endblock: '999999999', page: String(page), offset: String(PAGE_SIZE), sort: 'asc', apikey: ETHERSCAN_API_KEY,
  });
  const response = await fetchWithTimeout(`https://api.etherscan.io/v2/api?${params}`);
  if (!response.ok) throw new Error(`Etherscan HTTP ${response.status}`);
  const payload = await response.json();
  if (payload.status === '0') {
    const text = String(payload.result || payload.message || '');
    if (/no transactions found/i.test(text)) return [];
    throw new Error(`Etherscan ${action} failed: ${text}`);
  }
  if (!Array.isArray(payload.result)) throw new Error(`Etherscan ${action}: unexpected result`);
  return payload.result;
}

async function discoverWithEtherscan(chain) {
  const out = [];
  for (const spec of [
    { action: 'tokennfttx', standard: 'erc721' },
    { action: 'token1155tx', standard: 'erc1155' },
  ]) {
    for (let page = 1; ; page += 1) {
      const rows = await etherscanPage(chain.chainId, spec.action, page);
      for (const row of rows) {
        out.push({
          chain: chain.key, chainName: chain.name, chainId: chain.chainId, discovery: 'etherscan-v2', standard: spec.standard,
          blockNumber: Number(row.blockNumber), blockTimestamp: row.timeStamp ? new Date(Number(row.timeStamp) * 1000).toISOString() : null,
          txHash: row.hash, transactionIndex: row.transactionIndex != null ? Number(row.transactionIndex) : null,
          logIndex: row.logIndex != null ? Number(row.logIndex) : null, contract: String(row.contractAddress || '').toLowerCase(),
          tokenId: String(row.tokenID ?? row.tokenId ?? ''), value: String(row.tokenValue ?? '1'),
          from: String(row.from || '').toLowerCase(), to: String(row.to || '').toLowerCase(),
          tokenName: row.tokenName || null, tokenSymbol: row.tokenSymbol || null,
          direction: direction(row.from, row.to), explorerTx: `${chain.explorer}/tx/${row.hash}`,
        });
      }
      if (rows.length < PAGE_SIZE) break;
      await new Promise((r) => setTimeout(r, 250));
    }
  }
  return out;
}

function addressHash(value) {
  if (value && typeof value === 'object') return String(value.hash || value.address_hash || '').toLowerCase();
  return String(value || '').toLowerCase();
}

function blockscoutTokenIds(row) {
  const candidates = [
    row.token_id,
    row.tokenId,
    row.id,
    row.total?.token_id,
    row.total?.tokenId,
  ];
  if (Array.isArray(row.token_ids)) candidates.push(...row.token_ids);
  if (Array.isArray(row.tokenIds)) candidates.push(...row.tokenIds);
  const ids = candidates
    .flatMap((v) => Array.isArray(v) ? v : [v])
    .filter((v) => v !== null && v !== undefined && String(v) !== '')
    .map(String);
  return [...new Set(ids)];
}

async function discoverWithBlockscout(chain) {
  const out = [];
  let next = {};
  let page = 0;
  const seenPages = new Set();
  for (;;) {
    page += 1;
    const url = new URL(`${chain.blockscout}/api/v2/addresses/${WALLET}/token-transfers`);
    url.searchParams.set('type', 'ERC-721,ERC-1155');
    for (const [key, value] of Object.entries(next || {})) {
      if (value !== null && value !== undefined) url.searchParams.set(key, String(value));
    }
    const pageKey = url.searchParams.toString();
    if (seenPages.has(pageKey)) throw new Error(`Blockscout pagination loop on ${chain.key}`);
    seenPages.add(pageKey);
    const response = await fetchWithTimeout(url);
    if (!response.ok) throw new Error(`Blockscout HTTP ${response.status} for ${chain.key}`);
    const payload = await response.json();
    if (!Array.isArray(payload.items)) throw new Error(`Blockscout ${chain.key}: unexpected items payload`);
    for (const row of payload.items) {
      const tokenType = String(row.token?.type || '').toUpperCase();
      if (!/(ERC-721|ERC-1155)/.test(tokenType)) continue;
      const standard = tokenType.includes('1155') ? 'erc1155' : 'erc721';
      const contract = String(row.token?.address_hash || row.contract_address_hash || row.contractAddress || '').toLowerCase();
      const from = addressHash(row.from);
      const to = addressHash(row.to);
      const ids = blockscoutTokenIds(row);
      if (!contract || ids.length === 0) {
        process.stderr.write(`Blockscout ${chain.key}: skipped NFT transfer without contract/token id in ${row.transaction_hash || 'unknown tx'}\n`);
        continue;
      }
      for (let i = 0; i < ids.length; i += 1) {
        out.push({
          chain: chain.key,
          chainName: chain.name,
          chainId: chain.chainId,
          discovery: 'blockscout-v2',
          standard,
          blockNumber: row.block_number != null ? Number(row.block_number) : null,
          blockTimestamp: row.timestamp ? new Date(row.timestamp).toISOString() : null,
          txHash: row.transaction_hash || row.transactionHash || '',
          transactionIndex: row.transaction_index != null ? Number(row.transaction_index) : null,
          logIndex: row.log_index != null ? Number(row.log_index) : null,
          batchIndex: ids.length > 1 ? i : undefined,
          contract,
          tokenId: ids[i],
          value: String(row.total?.value ?? row.value ?? '1'),
          from,
          to,
          tokenName: row.token?.name || null,
          tokenSymbol: row.token?.symbol || null,
          direction: direction(from, to),
          explorerTx: `${chain.explorer}/tx/${row.transaction_hash || row.transactionHash}`,
        });
      }
    }
    next = payload.next_page_params;
    process.stdout.write(`Blockscout ${chain.key}: page ${page}, ${payload.items.length} rows, ${out.length} NFT occurrences normalized\n`);
    if (!next || Object.keys(next).length === 0) break;
    await new Promise((r) => setTimeout(r, 120));
  }
  return out;
}

async function getBlockTimestamp(provider, cache, blockNumber) {
  if (cache.has(blockNumber)) return cache.get(blockNumber);
  const block = await provider.getBlock(blockNumber);
  const ts = block ? new Date(Number(block.timestamp) * 1000).toISOString() : null;
  cache.set(blockNumber, ts);
  return ts;
}

async function scanLogsAdaptive(provider, filterBase, onLogs) {
  const latest = await provider.getBlockNumber();
  let from = 0;
  let span = Number(process.env.RPC_LOG_INITIAL_SPAN || 100_000);
  const minSpan = 250;
  while (from <= latest) {
    const to = Math.min(latest, from + span - 1);
    try {
      const logs = await provider.getLogs({ ...filterBase, fromBlock: from, toBlock: to });
      await onLogs(logs);
      from = to + 1;
      if (logs.length === 0) span = Math.min(span * 2, 500_000);
      else span = Math.min(Math.max(span, 5_000), 200_000);
    } catch (error) {
      if (span <= minSpan) throw error;
      span = Math.max(minSpan, Math.floor(span / 2));
      process.stderr.write(`RPC log range failed; reducing span to ${span}: ${error.message}\n`);
    }
  }
}

async function discoverWithRpc(chain) {
  const provider = new JsonRpcProvider(chain.rpcUrl, chain.chainId, { staticNetwork: true });
  const padded = zeroPadValue(WALLET, 32);
  const rawLogs = new Map();
  const filters = [
    { topics: [TOPICS.erc721, null, padded] },
    { topics: [TOPICS.erc721, padded] },
    { topics: [TOPICS.erc1155Single, null, null, padded] },
    { topics: [TOPICS.erc1155Single, null, padded] },
    { topics: [TOPICS.erc1155Batch, null, null, padded] },
    { topics: [TOPICS.erc1155Batch, null, padded] },
  ];
  for (const filter of filters) {
    await scanLogsAdaptive(provider, filter, async (logs) => {
      for (const log of logs) rawLogs.set(`${log.transactionHash}:${log.index}`, log);
    });
  }
  const cache = new Map();
  const out = [];
  const sorted = [...rawLogs.values()].sort((a, b) => a.blockNumber - b.blockNumber || a.index - b.index);
  for (const log of sorted) {
    let parsed;
    try { parsed = transferIface.parseLog(log); } catch { continue; }
    const ts = await getBlockTimestamp(provider, cache, log.blockNumber);
    if (parsed.name === 'Transfer') {
      // Exclude ERC-20 Transfer logs: ERC-721 has indexed tokenId => four topics total.
      if (log.topics.length !== 4) continue;
      const [from, to, tokenId] = parsed.args;
      out.push({ chain: chain.key, chainName: chain.name, chainId: chain.chainId, discovery: 'rpc-log-scan', standard: 'erc721',
        blockNumber: log.blockNumber, blockTimestamp: ts, txHash: log.transactionHash, transactionIndex: log.transactionIndex ?? null,
        logIndex: log.index, contract: log.address.toLowerCase(), tokenId: tokenId.toString(), value: '1',
        from: String(from).toLowerCase(), to: String(to).toLowerCase(), tokenName: null, tokenSymbol: null,
        direction: direction(from, to), explorerTx: `${chain.explorer}/tx/${log.transactionHash}` });
    } else if (parsed.name === 'TransferSingle') {
      const [, from, to, tokenId, value] = parsed.args;
      out.push({ chain: chain.key, chainName: chain.name, chainId: chain.chainId, discovery: 'rpc-log-scan', standard: 'erc1155',
        blockNumber: log.blockNumber, blockTimestamp: ts, txHash: log.transactionHash, transactionIndex: log.transactionIndex ?? null,
        logIndex: log.index, contract: log.address.toLowerCase(), tokenId: tokenId.toString(), value: value.toString(),
        from: String(from).toLowerCase(), to: String(to).toLowerCase(), tokenName: null, tokenSymbol: null,
        direction: direction(from, to), explorerTx: `${chain.explorer}/tx/${log.transactionHash}` });
    } else if (parsed.name === 'TransferBatch') {
      const [, from, to, ids, values] = parsed.args;
      for (let i = 0; i < ids.length; i += 1) {
        out.push({ chain: chain.key, chainName: chain.name, chainId: chain.chainId, discovery: 'rpc-log-scan', standard: 'erc1155',
          blockNumber: log.blockNumber, blockTimestamp: ts, txHash: log.transactionHash, transactionIndex: log.transactionIndex ?? null,
          logIndex: log.index, batchIndex: i, contract: log.address.toLowerCase(), tokenId: ids[i].toString(), value: values[i].toString(),
          from: String(from).toLowerCase(), to: String(to).toLowerCase(), tokenName: null, tokenSymbol: null,
          direction: direction(from, to), explorerTx: `${chain.explorer}/tx/${log.transactionHash}` });
      }
    }
  }
  await provider.destroy();
  return out;
}

async function discoverChain(chain) {
  if (ETHERSCAN_API_KEY) {
    try {
      return await discoverWithEtherscan(chain);
    } catch (error) {
      process.stderr.write(`Etherscan discovery failed on ${chain.key}; trying Blockscout: ${error.message}\n`);
    }
  }
  try {
    return await discoverWithBlockscout(chain);
  } catch (error) {
    process.stderr.write(`Blockscout discovery failed on ${chain.key}; falling back to RPC log scan: ${error.message}\n`);
  }
  return discoverWithRpc(chain);
}

async function readTokenUri(provider, contractAddress, tokenId, standard) {
  const errors = [];
  const order = standard === 'erc1155' ? ['erc1155', 'erc721'] : ['erc721', 'erc1155'];
  for (const kind of order) {
    try {
      if (kind === 'erc721') {
        const c = new Contract(contractAddress, erc721Abi, provider);
        const value = await c.tokenURI(tokenId);
        if (value) return { uri: String(value), resolvedStandard: 'erc721' };
      } else {
        const c = new Contract(contractAddress, erc1155Abi, provider);
        const value = await c.uri(tokenId);
        if (value) return { uri: replaceErc1155Id(String(value), tokenId), resolvedStandard: 'erc1155' };
      }
    } catch (error) {
      errors.push(`${kind}: ${error.shortMessage || error.message}`);
    }
  }
  return { uri: null, resolvedStandard: standard, error: errors.join(' | ') };
}

function extractMediaUris(metadata) {
  const values = [];
  const add = (role, uri) => {
    if (typeof uri === 'string' && uri.trim()) values.push({ role, uri: uri.trim() });
  };
  add('image', metadata?.image);
  add('image_data', metadata?.image_data);
  add('animation_url', metadata?.animation_url);
  if (Array.isArray(metadata?.properties?.files)) {
    for (let i = 0; i < metadata.properties.files.length; i += 1) {
      const f = metadata.properties.files[i];
      if (typeof f === 'string') add(`properties.files.${i}`, f);
      else add(`properties.files.${i}`, f?.uri || f?.url);
    }
  }
  const seen = new Set();
  return values.filter(({ uri }) => !seen.has(uri) && seen.add(uri));
}

async function loadExistingIndex() {
  try {
    const raw = await fs.readFile('token_index.json', 'utf8');
    const parsed = JSON.parse(raw);
    const set = new Set();
    const contracts = [];
    for (const [contract, tokens] of Object.entries(parsed)) {
      if (!/^0x[0-9a-f]{40}$/i.test(contract)) continue;
      contracts.push(contract.toLowerCase());
      if (!tokens || typeof tokens !== 'object' || Array.isArray(tokens)) continue;
      for (const tokenId of Object.keys(tokens)) set.add(`${contract.toLowerCase()}:${tokenId}`);
    }
    return { set, contracts };
  } catch (error) {
    return { set: new Set(), contracts: [], error: error.message };
  }
}

async function mirrorTokens(occurrences, existingIndex) {
  const providers = new Map(CHAINS.map((c) => [c.chainId, new JsonRpcProvider(c.rpcUrl, c.chainId, { staticNetwork: true })]));
  const unique = new Map();
  for (const o of occurrences) {
    const key = `${o.chainId}:${o.contract}:${o.tokenId}`;
    if (!unique.has(key)) unique.set(key, o);
  }
  const tokenResults = new Map();
  for (const [key, seed] of unique) {
    const provider = providers.get(seed.chainId);
    const tokenDir = path.join(OUT_DIR, 'mirror', seed.chain, safeSegment(seed.contract), safeSegment(seed.tokenId));
    await mkdirp(tokenDir);
    const result = {
      chain: seed.chain,
      chainId: seed.chainId,
      contract: seed.contract,
      tokenId: seed.tokenId,
      standard: seed.standard,
      existingIndexMatch: existingIndex.set.has(`${seed.contract}:${seed.tokenId}`),
      tokenUri: null,
      tokenUriError: null,
      metadata: null,
      media: [],
    };
    const uriResult = await readTokenUri(provider, seed.contract, seed.tokenId, seed.standard);
    result.tokenUri = uriResult.uri;
    result.resolvedStandard = uriResult.resolvedStandard;
    result.tokenUriError = uriResult.error || null;
    if (result.tokenUri) {
      try {
        const metadataFetch = await fetchBytesFromUri(result.tokenUri, 10 * 1024 * 1024);
        const metadataSha = sha256(metadataFetch.buffer);
        const rawPath = path.join(tokenDir, 'metadata.source.json');
        await fs.writeFile(rawPath, metadataFetch.buffer);
        let parsed = null;
        try { parsed = JSON.parse(metadataFetch.buffer.toString('utf8')); } catch {}
        result.metadata = {
          sourceUri: result.tokenUri,
          resolvedUrl: metadataFetch.resolvedUrl,
          contentType: metadataFetch.contentType,
          bytes: metadataFetch.buffer.length,
          sha256: metadataSha,
          localPath: path.relative(OUT_DIR, rawPath),
          name: parsed?.name ?? null,
          description: parsed?.description ?? null,
        };
        if (parsed) {
          await writeJson(path.join(tokenDir, 'metadata.normalized.json'), parsed);
          const mediaUris = extractMediaUris(parsed);
          for (let i = 0; i < mediaUris.length; i += 1) {
            const media = mediaUris[i];
            const item = { role: media.role, sourceUri: media.uri, mirrored: false, error: null };
            if (MIRROR_MEDIA) {
              try {
                const fetched = await fetchBytesFromUri(media.uri, MAX_MEDIA_BYTES);
                const ext = guessExtension(media.uri, fetched.contentType);
                const mediaPath = path.join(tokenDir, 'media', `${String(i + 1).padStart(2, '0')}-${safeSegment(media.role)}${ext}`);
                await mkdirp(path.dirname(mediaPath));
                await fs.writeFile(mediaPath, fetched.buffer);
                Object.assign(item, {
                  mirrored: true,
                  resolvedUrl: fetched.resolvedUrl,
                  contentType: fetched.contentType,
                  bytes: fetched.buffer.length,
                  sha256: sha256(fetched.buffer),
                  localPath: path.relative(OUT_DIR, mediaPath),
                });
              } catch (error) {
                item.error = error.message;
              }
            }
            result.media.push(item);
          }
        }
      } catch (error) {
        result.metadata = { sourceUri: result.tokenUri, error: error.message };
      }
    }
    tokenResults.set(key, result);
    await writeJson(path.join(tokenDir, 'token.json'), result);
    process.stdout.write(`mirrored ${seed.chain} ${seed.contract} #${seed.tokenId}\n`);
  }
  for (const provider of providers.values()) await provider.destroy();
  return tokenResults;
}

function buildLogicalRecords(occurrences, tokenResults) {
  const groups = new Map();
  for (const o of occurrences) {
    const token = tokenResults.get(`${o.chainId}:${o.contract}:${o.tokenId}`);
    const mediaHashes = (token?.media || []).filter((m) => m.sha256).map((m) => m.sha256).sort();
    const core = token?.metadata?.sha256
      ? { metadataSha256: token.metadata.sha256, mediaSha256: mediaHashes }
      : { name: token?.metadata?.name || o.tokenName || null, contract: o.contract, tokenId: o.tokenId };
    const fingerprint = sha256(Buffer.from(stableJson(core)));
    if (!groups.has(fingerprint)) {
      groups.set(fingerprint, {
        logicalId: `sha256:${fingerprint}`,
        evidenceBasis: token?.metadata?.sha256 ? 'content-hash' : 'fallback-identity',
        occurrences: [],
      });
    }
    groups.get(fingerprint).occurrences.push(occurrenceKey(o));
  }
  return [...groups.values()].map((g) => ({ ...g, occurrenceCount: g.occurrences.length }));
}

function buildFormationCandidate(occurrences) {
  const dated = occurrences
    .filter((o) => o.blockTimestamp)
    .sort((a, b) => Date.parse(a.blockTimestamp) - Date.parse(b.blockTimestamp));
  const earliest = dated[0] || null;
  const baselineMs = Date.parse(FORMATION_BASELINE);
  const earliestMs = earliest ? Date.parse(earliest.blockTimestamp) : null;
  return {
    currentFormationBaseline: FORMATION_BASELINE,
    closureTime: CLOSURE_TIME,
    earliestRecoveredSidechainOccurrence: earliest ? {
      chain: earliest.chain,
      chainId: earliest.chainId,
      blockNumber: earliest.blockNumber,
      blockTimestamp: earliest.blockTimestamp,
      txHash: earliest.txHash,
      contract: earliest.contract,
      tokenId: earliest.tokenId,
      explorerTx: earliest.explorerTx,
    } : null,
    wouldMoveFormationStartEarlier: earliestMs != null ? earliestMs < baselineMs : false,
    note: 'Audit candidate only. Do not rewrite the Bitcoin canonical ontology or historical claims automatically.',
  };
}

function summaryMarkdown({ occurrences, tokenResults, logicalRecords, formation, chainStats, existingIndex }) {
  const missing = [...tokenResults.values()].filter((t) => !t.existingIndexMatch).length;
  const metadataOk = [...tokenResults.values()].filter((t) => t.metadata?.sha256).length;
  const mediaOk = [...tokenResults.values()].reduce((n, t) => n + (t.media || []).filter((m) => m.mirrored).length, 0);
  const lines = [
    '# Polygon + Base Chronicle NFT discovery', '',
    `- Address: \`${WALLET}\``, `- Generated: ${new Date().toISOString()}`,
    `- Historical NFT transfer occurrences: **${occurrences.length}**`,
    `- Unique chain/contract/token tuples: **${tokenResults.size}**`,
    `- Logical content groups: **${logicalRecords.length}**`,
    `- Tuples not found in legacy token_index.json: **${missing}**`,
    `- Metadata recovered: **${metadataOk}/${tokenResults.size}**`,
    `- Media objects mirrored: **${mediaOk}**`,
    `- Existing index contracts detected: **${existingIndex.contracts.length}**`, '',
    '## Chain counts', '', '| Chain | Occurrences | Unique tokens | Discovery |', '|---|---:|---:|---|',
    ...chainStats.map((s) => `| ${s.chain} | ${s.occurrences} | ${s.uniqueTokens} | ${s.discovery.join(', ')} |`), '',
    '## Formation-time audit', '',
    `Current formation baseline: **${FORMATION_BASELINE}**`, `Closure: **${CLOSURE_TIME}**`,
    formation.earliestRecoveredSidechainOccurrence
      ? `Earliest recovered Polygon/Base occurrence: **${formation.earliestRecoveredSidechainOccurrence.blockTimestamp}** on ${formation.earliestRecoveredSidechainOccurrence.chain}.`
      : 'No dated Polygon/Base occurrence was recovered.',
    `Would move the formation start earlier: **${formation.wouldMoveFormationStartEarlier ? 'YES' : 'NO'}**`, '',
    '> Cross-chain occurrences are evidence records, not automatically new Chronicle logical records. This workflow never modifies the Bitcoin Canon.', '',
  ];
  return lines.join('\n');
}

async function main() {
  if (!/^0x[0-9a-f]{40}$/.test(WALLET)) throw new Error(`Invalid CHRONICLE_ADDRESS: ${WALLET}`);
  await fs.rm(OUT_DIR, { recursive: true, force: true });
  await mkdirp(OUT_DIR);
  const existingIndex = await loadExistingIndex();
  const raw = [];
  for (const chain of CHAINS) {
    process.stdout.write(`discovering ${chain.name} for ${WALLET}...\n`);
    const found = await discoverChain(chain);
    raw.push(...found);
    process.stdout.write(`found ${found.length} historical transfer occurrences on ${chain.key}\n`);
  }
  const dedupedMap = new Map();
  for (const o of raw) dedupedMap.set(`${occurrenceKey(o)}:${o.batchIndex ?? ''}`, o);
  const occurrences = [...dedupedMap.values()].sort((a, b) =>
    (Date.parse(a.blockTimestamp || 0) - Date.parse(b.blockTimestamp || 0)) ||
    a.chainId - b.chainId || (a.blockNumber ?? 0) - (b.blockNumber ?? 0),
  );
  for (const o of occurrences) {
    o.preClosure = o.blockTimestamp ? Date.parse(o.blockTimestamp) <= Date.parse(CLOSURE_TIME) : null;
    o.existingIndexMatch = existingIndex.set.has(`${o.contract}:${o.tokenId}`);
  }
  const tokenResults = await mirrorTokens(occurrences, existingIndex);
  const logicalRecords = buildLogicalRecords(occurrences, tokenResults);
  const formation = buildFormationCandidate(occurrences);
  const chainStats = CHAINS.map((c) => {
    const subset = occurrences.filter((o) => o.chainId === c.chainId);
    return {
      chain: c.key, chainId: c.chainId, occurrences: subset.length,
      uniqueTokens: new Set(subset.map((o) => `${o.contract}:${o.tokenId}`)).size,
      discovery: [...new Set(subset.map((o) => o.discovery))],
    };
  });
  const mirrorManifest = [...tokenResults.values()];
  const report = {
    schema: 'trinity-accord/chronicle-crosschain-audit-v1', generatedAt: new Date().toISOString(), address: WALLET,
    chains: CHAINS.map(({ key, name, chainId, explorer }) => ({ key, name, chainId, explorer })),
    legacyIndex: { contracts: existingIndex.contracts, loadError: existingIndex.error || null },
    counts: { occurrences: occurrences.length, uniqueTokens: tokenResults.size, logicalRecords: logicalRecords.length }, formation,
  };
  await writeJson(path.join(OUT_DIR, 'audit.json'), report);
  await writeJson(path.join(OUT_DIR, 'occurrences.json'), occurrences);
  await writeJson(path.join(OUT_DIR, 'logical-records.json'), logicalRecords);
  await writeJson(path.join(OUT_DIR, 'formation-candidate.json'), formation);
  await writeJson(path.join(OUT_DIR, 'mirror-manifest.json'), mirrorManifest);
  await fs.writeFile(path.join(OUT_DIR, 'summary.md'), summaryMarkdown({ occurrences, tokenResults, logicalRecords, formation, chainStats, existingIndex }));
  const files = [];
  async function walk(dir) {
    for (const entry of await fs.readdir(dir, { withFileTypes: true })) {
      const full = path.join(dir, entry.name);
      if (entry.isDirectory()) await walk(full);
      else {
        const bytes = await fs.readFile(full);
        files.push({ path: path.relative(OUT_DIR, full).replaceAll(path.sep, '/'), bytes: bytes.length, sha256: sha256(bytes) });
      }
    }
  }
  await walk(OUT_DIR);
  await writeJson(path.join(OUT_DIR, 'sha256-manifest.json'), { generatedAt: new Date().toISOString(), files });
  process.stdout.write(`done: ${occurrences.length} occurrences; ${tokenResults.size} unique tokens; ${logicalRecords.length} logical groups\n`);
}

main().catch((error) => {
  console.error(error.stack || error);
  process.exitCode = 1;
});
