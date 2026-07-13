#!/usr/bin/env node
/**
 * Generate a durable NFT identity index by linking the repository's canonical
 * contract+token_id records to their earliest on-chain mint events.
 *
 * The generated JSON is intentionally small and repository-friendly. NFT CAR
 * payloads remain on Arweave/GitHub Releases; this file only stores identifiers,
 * hashes, links, and immutable mint-event coordinates.
 */
import fs from 'fs';
import crypto from 'crypto';
import path from 'path';
import { fileURLToPath } from 'url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const ZERO_ADDRESS = '0x0000000000000000000000000000000000000000';
const ZERO_TOPIC = `0x${'0'.repeat(64)}`;
const ERC165 = {
  erc721: '0x80ac58cd',
  erc1155: '0xd9b67a26',
};
const SUPPORTS_INTERFACE_SELECTOR = '0x01ffc9a7';
const EVENT_SIGNATURES = {
  erc721_transfer: 'Transfer(address,address,uint256)',
  erc1155_transfer_single: 'TransferSingle(address,address,address,uint256,uint256)',
  erc1155_transfer_batch: 'TransferBatch(address,address,address,uint256[],uint256[])',
};
const EXPLORERS = new Map([
  [1n, 'https://etherscan.io'],
  [10n, 'https://optimistic.etherscan.io'],
  [56n, 'https://bscscan.com'],
  [137n, 'https://polygonscan.com'],
  [42161n, 'https://arbiscan.io'],
  [8453n, 'https://basescan.org'],
  [7777777n, 'https://explorer.zora.energy'],
]);

function fail(message) {
  throw new Error(message);
}

function parseArgs(argv) {
  const args = {
    input: 'token_index.json',
    output: 'nft-identity-index.json',
    rpcUrl: process.env.ETH_RPC_URL || process.env.EVM_RPC_URL || '',
    initialChunk: Number(process.env.NFT_MINT_SCAN_INITIAL_CHUNK || 250000),
    minChunk: Number(process.env.NFT_MINT_SCAN_MIN_CHUNK || 1000),
    maxChunk: Number(process.env.NFT_MINT_SCAN_MAX_CHUNK || 1000000),
    startBlock: process.env.NFT_MINT_SCAN_FROM_BLOCK || null,
    maxRequests: Number(process.env.NFT_MINT_SCAN_MAX_REQUESTS || 20000),
    selfTest: false,
  };
  for (let i = 0; i < argv.length; i++) {
    const value = argv[i];
    if (value === '--self-test') args.selfTest = true;
    else if (value === '--input') args.input = argv[++i];
    else if (value === '--output') args.output = argv[++i];
    else if (value === '--rpc-url') args.rpcUrl = argv[++i];
    else if (value === '--from-block') args.startBlock = argv[++i];
    else if (value === '--initial-chunk') args.initialChunk = Number(argv[++i]);
    else if (value === '--min-chunk') args.minChunk = Number(argv[++i]);
    else if (value === '--max-chunk') args.maxChunk = Number(argv[++i]);
    else if (value === '--max-requests') args.maxRequests = Number(argv[++i]);
    else fail(`Unknown argument: ${value}`);
  }
  if (!args.selfTest && !args.rpcUrl) fail('ETH_RPC_URL or EVM_RPC_URL is required');
  for (const name of ['initialChunk', 'minChunk', 'maxChunk', 'maxRequests']) {
    if (!Number.isSafeInteger(args[name]) || args[name] <= 0) fail(`Invalid ${name}: ${args[name]}`);
  }
  if (args.minChunk > args.initialChunk || args.initialChunk > args.maxChunk) {
    fail('Expected minChunk <= initialChunk <= maxChunk');
  }
  return args;
}

function readJson(filePath) {
  const raw = fs.readFileSync(filePath);
  return { raw, value: JSON.parse(raw.toString('utf8')) };
}

function sha256(data) {
  return crypto.createHash('sha256').update(data).digest('hex');
}

function hexQuantity(value) {
  return `0x${BigInt(value).toString(16)}`;
}

function parseQuantity(value, label) {
  if (typeof value !== 'string' || !/^0x[0-9a-f]+$/i.test(value)) fail(`Invalid ${label}: ${value}`);
  return BigInt(value);
}

function normalizeAddress(value, label = 'address') {
  if (typeof value !== 'string' || !/^0x[0-9a-f]{40}$/i.test(value)) fail(`Invalid ${label}: ${value}`);
  return value.toLowerCase();
}

function normalizeHash(value, label = 'hash') {
  if (typeof value !== 'string' || !/^0x[0-9a-f]{64}$/i.test(value)) fail(`Invalid ${label}: ${value}`);
  return value.toLowerCase();
}

function topicAddress(address) {
  return `0x${normalizeAddress(address).slice(2).padStart(64, '0')}`;
}

function decodeTopicAddress(topic, label) {
  normalizeHash(topic, label);
  return normalizeAddress(`0x${topic.slice(-40)}`, label);
}

function decodeWord(data, wordIndex, label) {
  if (typeof data !== 'string' || !/^0x[0-9a-f]*$/i.test(data)) fail(`Invalid ABI data for ${label}`);
  const start = 2 + wordIndex * 64;
  const word = data.slice(start, start + 64);
  if (word.length !== 64) fail(`Truncated ABI word for ${label}`);
  return BigInt(`0x${word}`);
}

function decodeUintArray(data, offsetBytes, label) {
  if (offsetBytes > BigInt(Number.MAX_SAFE_INTEGER)) fail(`${label} offset is unsafe`);
  const offsetWords = Number(offsetBytes / 32n);
  const length = decodeWord(data, offsetWords, `${label}.length`);
  if (length > 100000n) fail(`${label} array is unreasonably large: ${length}`);
  const values = [];
  for (let i = 0; i < Number(length); i++) values.push(decodeWord(data, offsetWords + 1 + i, `${label}[${i}]`));
  return values;
}

function compareLogCoordinates(a, b) {
  const keys = ['block_number', 'transaction_index', 'log_index'];
  for (const key of keys) {
    const av = BigInt(a[key]);
    const bv = BigInt(b[key]);
    if (av < bv) return -1;
    if (av > bv) return 1;
  }
  return 0;
}

function stableSortObject(value) {
  if (Array.isArray(value)) return value.map(stableSortObject);
  if (!value || typeof value !== 'object') return value;
  return Object.fromEntries(Object.keys(value).sort().map(key => [key, stableSortObject(value[key])]));
}

class RpcClient {
  constructor(url, maxRequests) {
    this.url = url;
    this.maxRequests = maxRequests;
    this.requests = 0;
    this.id = 0;
  }

  async call(method, params = [], retries = 4) {
    this.requests++;
    if (this.requests > this.maxRequests) fail(`RPC request ceiling exceeded (${this.maxRequests})`);
    let lastError;
    for (let attempt = 0; attempt <= retries; attempt++) {
      try {
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), 120000);
        const response = await fetch(this.url, {
          method: 'POST',
          headers: { 'content-type': 'application/json' },
          body: JSON.stringify({ jsonrpc: '2.0', id: ++this.id, method, params }),
          signal: controller.signal,
        });
        clearTimeout(timeout);
        if (!response.ok) throw new Error(`HTTP ${response.status}: ${(await response.text()).slice(0, 500)}`);
        const payload = await response.json();
        if (payload.error) {
          const error = new Error(`${method}: ${payload.error.message || JSON.stringify(payload.error)}`);
          error.rpcCode = payload.error.code;
          throw error;
        }
        return payload.result;
      } catch (error) {
        lastError = error;
        const message = String(error?.message || error);
        const retryable = /timeout|abort|429|rate|limit|busy|temporar|gateway|502|503|504/i.test(message);
        if (!retryable || attempt === retries) throw error;
        await new Promise(resolve => setTimeout(resolve, 1500 * (attempt + 1)));
      }
    }
    throw lastError;
  }
}

async function eventTopic(rpc, signature) {
  const hex = `0x${Buffer.from(signature, 'utf8').toString('hex')}`;
  return normalizeHash(await rpc.call('web3_sha3', [hex]), `topic(${signature})`);
}

async function supportsInterface(rpc, contract, interfaceId) {
  const data = `${SUPPORTS_INTERFACE_SELECTOR}${interfaceId.slice(2).padEnd(64, '0')}`;
  try {
    const result = await rpc.call('eth_call', [{ to: contract, data }, 'latest'], 2);
    return typeof result === 'string' && result !== '0x' && BigInt(result) === 1n;
  } catch {
    return null;
  }
}

async function historicalCodeAvailable(rpc, contract, block) {
  try {
    const code = await rpc.call('eth_getCode', [contract, hexQuantity(block)], 1);
    return { supported: true, hasCode: typeof code === 'string' && code !== '0x' };
  } catch (error) {
    return { supported: false, hasCode: false, error: String(error?.message || error) };
  }
}

async function findDeploymentBlock(rpc, contract, latestBlock) {
  const latest = await historicalCodeAvailable(rpc, contract, latestBlock);
  if (!latest.supported) return { block: 0n, method: 'fallback_zero', warning: latest.error };
  if (!latest.hasCode) fail(`No contract code at latest block for ${contract}`);

  const genesis = await historicalCodeAvailable(rpc, contract, 0n);
  if (!genesis.supported) return { block: 0n, method: 'fallback_zero', warning: genesis.error };
  if (genesis.hasCode) return { block: 0n, method: 'historical_code_binary_search' };

  let low = 0n;
  let high = latestBlock;
  while (low + 1n < high) {
    const mid = (low + high) / 2n;
    const probe = await historicalCodeAvailable(rpc, contract, mid);
    if (!probe.supported) return { block: 0n, method: 'fallback_zero', warning: probe.error };
    if (probe.hasCode) high = mid;
    else low = mid;
  }
  return { block: high, method: 'historical_code_binary_search' };
}

function loadTargets(index) {
  if (!index || typeof index !== 'object' || Array.isArray(index)) fail('token_index.json must be an object');
  const contracts = new Map();
  for (const [contractRaw, tokens] of Object.entries(index)) {
    const contract = normalizeAddress(contractRaw, 'contract address');
    if (!tokens || typeof tokens !== 'object' || Array.isArray(tokens)) fail(`${contract} token map is invalid`);
    const tokenMap = new Map();
    for (const [tokenIdRaw, record] of Object.entries(tokens)) {
      if (!/^[0-9]+$/.test(tokenIdRaw)) fail(`Invalid token ID ${contract}/${tokenIdRaw}`);
      const tokenId = BigInt(tokenIdRaw).toString(10);
      if (!record?.metadata?.txid || !record?.metadata?.root_cid) fail(`Missing metadata reference for ${contract}/${tokenId}`);
      const media = Array.isArray(record.media) ? record.media : [];
      tokenMap.set(tokenId, {
        token_id: tokenId,
        metadata: {
          arweave_txid: String(record.metadata.txid),
          root_cid: String(record.metadata.root_cid),
          car_sha256: record.metadata.car_sha256 || null,
          car_size: record.metadata.car_size ?? null,
        },
        media: media.map(item => ({
          arweave_txid: String(item.txid),
          root_cid: String(item.root_cid),
          leaf_path: item.leaf_path || null,
          car_sha256: item.car_sha256 || null,
          car_size: item.car_size ?? null,
        })),
      });
    }
    contracts.set(contract, tokenMap);
  }
  return contracts;
}

function parseMintLog(log, topics) {
  const topic0 = normalizeHash(log.topics?.[0] || '', 'log topic0');
  const base = {
    block_number: parseQuantity(log.blockNumber, 'blockNumber').toString(10),
    transaction_index: parseQuantity(log.transactionIndex, 'transactionIndex').toString(10),
    log_index: parseQuantity(log.logIndex, 'logIndex').toString(10),
    transaction_hash: normalizeHash(log.transactionHash, 'transactionHash'),
    block_hash: normalizeHash(log.blockHash, 'blockHash'),
    contract_address: normalizeAddress(log.address, 'log address'),
    removed: Boolean(log.removed),
  };
  if (base.removed) return [];

  if (topic0 === topics.erc721_transfer) {
    if (log.topics.length !== 4 || normalizeHash(log.topics[1], 'from topic') !== ZERO_TOPIC) return [];
    return [{
      ...base,
      standard: 'erc721',
      event: 'Transfer',
      from: ZERO_ADDRESS,
      to: decodeTopicAddress(log.topics[2], 'to topic'),
      token_id: BigInt(log.topics[3]).toString(10),
      quantity: '1',
      operator: null,
    }];
  }

  if (topic0 === topics.erc1155_transfer_single) {
    if (log.topics.length !== 4 || normalizeHash(log.topics[2], 'from topic') !== ZERO_TOPIC) return [];
    return [{
      ...base,
      standard: 'erc1155',
      event: 'TransferSingle',
      operator: decodeTopicAddress(log.topics[1], 'operator topic'),
      from: ZERO_ADDRESS,
      to: decodeTopicAddress(log.topics[3], 'to topic'),
      token_id: decodeWord(log.data, 0, 'TransferSingle.id').toString(10),
      quantity: decodeWord(log.data, 1, 'TransferSingle.value').toString(10),
    }];
  }

  if (topic0 === topics.erc1155_transfer_batch) {
    if (log.topics.length !== 4 || normalizeHash(log.topics[2], 'from topic') !== ZERO_TOPIC) return [];
    const idsOffset = decodeWord(log.data, 0, 'TransferBatch.idsOffset');
    const valuesOffset = decodeWord(log.data, 1, 'TransferBatch.valuesOffset');
    const ids = decodeUintArray(log.data, idsOffset, 'TransferBatch.ids');
    const values = decodeUintArray(log.data, valuesOffset, 'TransferBatch.values');
    if (ids.length !== values.length) fail(`TransferBatch ids/values length mismatch in ${base.transaction_hash}`);
    return ids.map((id, index) => ({
      ...base,
      standard: 'erc1155',
      event: 'TransferBatch',
      operator: decodeTopicAddress(log.topics[1], 'operator topic'),
      from: ZERO_ADDRESS,
      to: decodeTopicAddress(log.topics[3], 'to topic'),
      token_id: id.toString(10),
      quantity: values[index].toString(10),
      batch_index: index,
    }));
  }

  return [];
}

function isRangeError(error) {
  return /block range|range is too wide|more than|too many results|response size|query returned more|exceed|limit|timeout|timed out|413|504/i.test(String(error?.message || error));
}

async function scanMintLogs({ rpc, contract, targetIds, fromBlock, latestBlock, topics, initialChunk, minChunk, maxChunk, interfaces }) {
  const found = new Map();
  let cursor = fromBlock;
  let chunk = BigInt(initialChunk);
  const min = BigInt(minChunk);
  const max = BigInt(maxChunk);
  let successfulRanges = 0;

  const include721 = interfaces.erc721 !== false;
  const include1155 = interfaces.erc1155 !== false;
  if (!include721 && !include1155) fail(`${contract} supports neither ERC-721 nor ERC-1155`);

  while (cursor <= latestBlock && found.size < targetIds.size) {
    let end = cursor + chunk - 1n;
    if (end > latestBlock) end = latestBlock;
    const baseFilter = {
      address: contract,
      fromBlock: hexQuantity(cursor),
      toBlock: hexQuantity(end),
    };
    try {
      const logGroups = [];
      if (include721) {
        logGroups.push(await rpc.call('eth_getLogs', [{
          ...baseFilter,
          topics: [topics.erc721_transfer, ZERO_TOPIC],
        }], 2));
      }
      if (include1155) {
        logGroups.push(await rpc.call('eth_getLogs', [{
          ...baseFilter,
          topics: [[topics.erc1155_transfer_single, topics.erc1155_transfer_batch], null, ZERO_TOPIC],
        }], 2));
      }
      const logs = logGroups.flat();
      if (!logs.every(log => log && typeof log === 'object')) fail(`eth_getLogs returned invalid entries for ${contract}`);
      for (const log of logs) {
        for (const mint of parseMintLog(log, topics)) {
          if (!targetIds.has(mint.token_id)) continue;
          const previous = found.get(mint.token_id);
          if (!previous || compareLogCoordinates(mint, previous) < 0) found.set(mint.token_id, mint);
        }
      }
      successfulRanges++;
      process.stdout.write(`\r${contract}: blocks ${cursor}-${end}, found ${found.size}/${targetIds.size}, rpc ${rpc.requests}`);
      cursor = end + 1n;
      if (logs.length === 0 && chunk < max) chunk = chunk * 2n > max ? max : chunk * 2n;
      else if (logs.length > 5000 && chunk > min) chunk = chunk / 2n < min ? min : chunk / 2n;
    } catch (error) {
      if (!isRangeError(error) || chunk <= min) throw error;
      chunk = chunk / 2n;
      if (chunk < min) chunk = min;
      process.stdout.write(`\r${contract}: reducing scan chunk to ${chunk} after RPC range error`);
    }
  }
  process.stdout.write('\n');
  return { found, scanned_to: cursor > latestBlock ? latestBlock : cursor - 1n, successful_ranges: successfulRanges };
}

async function verifyReceipts(rpc, mints, topics) {
  const byTx = new Map();
  for (const mint of mints.values()) {
    if (!byTx.has(mint.transaction_hash)) byTx.set(mint.transaction_hash, []);
    byTx.get(mint.transaction_hash).push(mint);
  }
  const receiptSummaries = new Map();
  for (const [txHash, expected] of byTx) {
    const receipt = await rpc.call('eth_getTransactionReceipt', [txHash]);
    if (!receipt) fail(`Missing transaction receipt for ${txHash}`);
    if (normalizeHash(receipt.transactionHash, 'receipt transactionHash') !== txHash) fail(`Receipt hash mismatch for ${txHash}`);
    if (receipt.status !== undefined && BigInt(receipt.status) !== 1n) fail(`Mint transaction failed: ${txHash}`);
    const receiptLogs = new Map((receipt.logs || []).map(log => [parseQuantity(log.logIndex, 'receipt logIndex').toString(10), log]));
    for (const mint of expected) {
      const rawLog = receiptLogs.get(mint.log_index);
      if (!rawLog) fail(`Receipt ${txHash} is missing logIndex ${mint.log_index}`);
      const parsed = parseMintLog(rawLog, topics).find(item => item.token_id === mint.token_id);
      if (!parsed) fail(`Receipt ${txHash} log ${mint.log_index} does not mint token ${mint.token_id}`);
    }
    receiptSummaries.set(txHash, {
      block_number: parseQuantity(receipt.blockNumber, 'receipt blockNumber').toString(10),
      block_hash: normalizeHash(receipt.blockHash, 'receipt blockHash'),
      status: receipt.status === undefined ? null : parseQuantity(receipt.status, 'receipt status').toString(10),
      verified_token_count: expected.length,
    });
  }
  return receiptSummaries;
}

function explorerLinks(chainId, contract, tokenId, txHash) {
  const explorer = EXPLORERS.get(chainId);
  if (!explorer) return { transaction: null, token: null };
  return {
    transaction: `${explorer}/tx/${txHash}`,
    token: `${explorer}/token/${contract}?a=${tokenId}`,
  };
}

function inferPackedTokenId(tokenId) {
  const value = BigInt(tokenId);
  const low96Mask = (1n << 96n) - 1n;
  const prefix = value >> 96n;
  if (prefix > 0n && prefix < (1n << 160n)) {
    return {
      high_160_bits_address: `0x${prefix.toString(16).padStart(40, '0')}`,
      low_96_bits_serial: (value & low96Mask).toString(10),
      interpretation: 'informational_only_not_part_of_identity',
    };
  }
  return null;
}

function encodeWord(value) {
  return BigInt(value).toString(16).padStart(64, '0');
}

function assertSelfTest(condition, message) {
  if (!condition) fail(`self-test: ${message}`);
}

function runSelfTest() {
  const topics = {
    erc721_transfer: `0x${'11'.repeat(32)}`,
    erc1155_transfer_single: `0x${'22'.repeat(32)}`,
    erc1155_transfer_batch: `0x${'33'.repeat(32)}`,
  };
  const base = {
    address: '0x1111111111111111111111111111111111111111',
    blockNumber: '0xa',
    transactionIndex: '0x1',
    logIndex: '0x2',
    transactionHash: `0x${'44'.repeat(32)}`,
    blockHash: `0x${'55'.repeat(32)}`,
    removed: false,
  };
  const to = '0x2222222222222222222222222222222222222222';
  const operator = '0x3333333333333333333333333333333333333333';

  const erc721 = parseMintLog({
    ...base,
    topics: [topics.erc721_transfer, ZERO_TOPIC, topicAddress(to), `0x${encodeWord(7)}`],
    data: '0x',
  }, topics);
  assertSelfTest(erc721.length === 1 && erc721[0].token_id === '7' && erc721[0].standard === 'erc721', 'ERC-721 decode');

  const single = parseMintLog({
    ...base,
    topics: [topics.erc1155_transfer_single, topicAddress(operator), ZERO_TOPIC, topicAddress(to)],
    data: `0x${encodeWord(8)}${encodeWord(3)}`,
  }, topics);
  assertSelfTest(single.length === 1 && single[0].token_id === '8' && single[0].quantity === '3', 'ERC-1155 TransferSingle decode');

  const batchData = `0x${[
    encodeWord(64), encodeWord(160),
    encodeWord(2), encodeWord(9), encodeWord(10),
    encodeWord(2), encodeWord(4), encodeWord(5),
  ].join('')}`;
  const batch = parseMintLog({
    ...base,
    topics: [topics.erc1155_transfer_batch, topicAddress(operator), ZERO_TOPIC, topicAddress(to)],
    data: batchData,
  }, topics);
  assertSelfTest(batch.length === 2, 'ERC-1155 TransferBatch length');
  assertSelfTest(batch[0].token_id === '9' && batch[0].quantity === '4', 'ERC-1155 TransferBatch item 0');
  assertSelfTest(batch[1].token_id === '10' && batch[1].quantity === '5', 'ERC-1155 TransferBatch item 1');

  const packed = (BigInt('0xbc63566a41cbfdb9c266a5941cbe47894daa54a8') << 96n) | 1n;
  const hint = inferPackedTokenId(packed.toString());
  assertSelfTest(hint?.high_160_bits_address === '0xbc63566a41cbfdb9c266a5941cbe47894daa54a8', 'packed-token creator hint');
  assertSelfTest(hint?.low_96_bits_serial === '1', 'packed-token serial hint');
  console.log('PASS: NFT mint identity generator self-test');
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.selfTest) { runSelfTest(); return; }
  const inputPath = path.resolve(ROOT, args.input);
  const outputPath = path.resolve(ROOT, args.output);
  const { raw, value: index } = readJson(inputPath);
  const targetsByContract = loadTargets(index);
  const totalTargets = [...targetsByContract.values()].reduce((sum, map) => sum + map.size, 0);
  if (totalTargets === 0) fail('No NFT targets found');

  const rpc = new RpcClient(args.rpcUrl, args.maxRequests);
  const chainId = parseQuantity(await rpc.call('eth_chainId'), 'chainId');
  const latestBlock = parseQuantity(await rpc.call('eth_blockNumber'), 'latestBlock');
  const latestBlockData = await rpc.call('eth_getBlockByNumber', [hexQuantity(latestBlock), false]);
  if (!latestBlockData) fail(`Latest block ${latestBlock} not found`);

  const topics = {
    erc721_transfer: await eventTopic(rpc, EVENT_SIGNATURES.erc721_transfer),
    erc1155_transfer_single: await eventTopic(rpc, EVENT_SIGNATURES.erc1155_transfer_single),
    erc1155_transfer_batch: await eventTopic(rpc, EVENT_SIGNATURES.erc1155_transfer_batch),
  };

  const allMints = new Map();
  const contractSummaries = [];
  for (const [contract, tokenMap] of [...targetsByContract.entries()].sort(([a], [b]) => a.localeCompare(b))) {
    const interfaces = {
      erc721: await supportsInterface(rpc, contract, ERC165.erc721),
      erc1155: await supportsInterface(rpc, contract, ERC165.erc1155),
    };
    let start;
    if (args.startBlock !== null) start = { block: BigInt(args.startBlock), method: 'operator_override' };
    else start = await findDeploymentBlock(rpc, contract, latestBlock);
    const targetIds = new Set(tokenMap.keys());
    const scan = await scanMintLogs({
      rpc,
      contract,
      targetIds,
      fromBlock: start.block,
      latestBlock,
      topics,
      initialChunk: args.initialChunk,
      minChunk: args.minChunk,
      maxChunk: args.maxChunk,
      interfaces,
    });
    const missing = [...targetIds].filter(id => !scan.found.has(id));
    if (missing.length) {
      fail(`Unresolved mint events for ${contract}: ${missing.length}/${targetIds.size}; first missing: ${missing.slice(0, 10).join(', ')}`);
    }
    for (const [tokenId, mint] of scan.found) allMints.set(`${contract}/${tokenId}`, mint);
    contractSummaries.push({
      contract_address: contract,
      interface_support: interfaces,
      target_tokens: tokenMap.size,
      resolved_tokens: scan.found.size,
      scan_start_block: start.block.toString(10),
      scan_start_method: start.method,
      scan_start_warning: start.warning || null,
      scan_end_block: scan.scanned_to.toString(10),
      successful_log_ranges: scan.successful_ranges,
    });
  }

  const receiptMints = new Map([...allMints.values()].map(mint => [`${mint.contract_address}/${mint.token_id}`, mint]));
  const receipts = await verifyReceipts(rpc, receiptMints, topics);

  const assets = [];
  for (const [contract, tokenMap] of [...targetsByContract.entries()].sort(([a], [b]) => a.localeCompare(b))) {
    const standardByContract = contractSummaries.find(x => x.contract_address === contract)?.interface_support || {};
    for (const [tokenId, content] of [...tokenMap.entries()].sort((a, b) => (BigInt(a[0]) < BigInt(b[0]) ? -1 : 1))) {
      const mint = allMints.get(`${contract}/${tokenId}`);
      const standard = mint.standard;
      if (standard === 'erc721' && standardByContract.erc721 === false) fail(`${contract}/${tokenId} emitted ERC-721 mint but interface reports false`);
      if (standard === 'erc1155' && standardByContract.erc1155 === false) fail(`${contract}/${tokenId} emitted ERC-1155 mint but interface reports false`);
      const links = explorerLinks(chainId, contract, tokenId, mint.transaction_hash);
      assets.push({
        asset_id: `eip155:${chainId}/${standard}:${contract}/${tokenId}`,
        chain: { namespace: 'eip155', chain_id: chainId.toString(10) },
        standard,
        contract_address: contract,
        token_id: tokenId,
        token_id_encoding_hint: inferPackedTokenId(tokenId),
        mint: {
          transaction_hash: mint.transaction_hash,
          block_number: mint.block_number,
          block_hash: mint.block_hash,
          transaction_index: mint.transaction_index,
          log_index: mint.log_index,
          event: mint.event,
          batch_index: mint.batch_index ?? null,
          operator: mint.operator,
          from: mint.from,
          to: mint.to,
          quantity: mint.quantity,
          receipt_verified: true,
          receipt_status: receipts.get(mint.transaction_hash)?.status ?? null,
          transaction_url: links.transaction,
        },
        lookup: {
          token_url: links.token,
          canonical_key: `${chainId}:${contract}:${tokenId}`,
        },
        content,
      });
    }
  }

  const output = {
    schema: 'trinityaccord.nft-identity-index.v1',
    purpose: 'Link canonical NFT identities and immutable mint-event coordinates to Arweave/GitHub Release content backups.',
    storage_policy: {
      repository_contains: ['identity index', 'mint transaction/log coordinates', 'content hashes and Arweave transaction IDs'],
      large_binary_payloads_remain_in: ['Arweave', 'GitHub Releases'],
      repository_does_not_embed_car_payloads: true,
    },
    source: {
      token_index_path: path.relative(ROOT, inputPath).replaceAll(path.sep, '/'),
      token_index_sha256: sha256(raw),
      chain_id: chainId.toString(10),
      snapshot_block_number: latestBlock.toString(10),
      snapshot_block_hash: normalizeHash(latestBlockData.hash, 'snapshot block hash'),
      rpc_requests: rpc.requests,
      event_topics: topics,
    },
    summary: {
      contracts: targetsByContract.size,
      nfts: assets.length,
      mint_transactions: new Set(assets.map(asset => asset.mint.transaction_hash)).size,
      unresolved: 0,
      receipt_verified: assets.filter(asset => asset.mint.receipt_verified).length,
    },
    contracts: contractSummaries,
    assets,
  };

  const normalized = stableSortObject(output);
  fs.writeFileSync(outputPath, `${JSON.stringify(normalized, null, 2)}\n`, 'utf8');
  console.log(`Wrote ${path.relative(ROOT, outputPath)}: ${assets.length} NFTs, ${output.summary.mint_transactions} mint transactions, ${rpc.requests} RPC requests`);
}

main().catch(error => {
  console.error(`FAIL: ${error.stack || error.message || error}`);
  process.exit(1);
});
