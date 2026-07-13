#!/usr/bin/env node
import process from 'node:process';

const CONTRACT = (process.env.CONTRACT || '0x019372bBee377109b8Eae66d7267f5C4EaAdBb79').toLowerCase();
const RPC_URL = process.env.RPC_URL || 'https://ethereum-rpc.publicnode.com';

async function rpc(method, params, timeoutMs = 30_000) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetch(RPC_URL, {
      method: 'POST',
      headers: {'content-type': 'application/json'},
      body: JSON.stringify({jsonrpc: '2.0', id: 1, method, params}),
      signal: controller.signal,
    });
    const text = await response.text();
    if (!response.ok) throw new Error(`${method}: HTTP ${response.status}: ${text.slice(0, 300)}`);
    const payload = JSON.parse(text);
    if (payload.error) throw new Error(`${method}: ${JSON.stringify(payload.error)}`);
    return payload.result;
  } finally {
    clearTimeout(timer);
  }
}

const toHex = value => `0x${value.toString(16)}`;
const fromHex = value => Number.parseInt(value, 16);
const call = data => rpc('eth_call', [{to: CONTRACT, data}, 'latest']);
const supportsData = id => `0x01ffc9a7${id.replace(/^0x/, '')}${'0'.repeat(56)}`;
const boolResult = value => typeof value === 'string' && BigInt(value) !== 0n;

async function findCreationBlock(latest) {
  let lo = 0;
  let hi = latest;
  let calls = 0;
  while (lo < hi) {
    const mid = Math.floor((lo + hi) / 2);
    const code = await rpc('eth_getCode', [CONTRACT, toHex(mid)]);
    calls += 1;
    if (code !== '0x') hi = mid;
    else lo = mid + 1;
  }
  console.log(`PROBE creation-block=${lo} binary-search-calls=${calls}`);
  return lo;
}

async function inspectInterfaces() {
  const interfaces = {};
  for (const [name, id] of [
    ['erc165', '0x01ffc9a7'],
    ['erc721', '0x80ac58cd'],
    ['erc721_metadata', '0x5b5e139f'],
    ['erc1155', '0xd9b67a26'],
    ['erc1155_metadata_uri', '0x0e89341c'],
  ]) {
    try {
      interfaces[name] = boolResult(await call(supportsData(id)));
    } catch (error) {
      interfaces[name] = {error: String(error?.message || error)};
    }
  }
  console.log(`PROBE interfaces=${JSON.stringify(interfaces)}`);
  return interfaces;
}

async function inspectProxy() {
  const slots = {
    implementation: '0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc',
    beacon: '0xa3f0ad74e5423aebfd80d3ef4346578335a9a72aeaee59ff6cb3582b35133d50',
  };
  const proxy = {};
  for (const [name, slot] of Object.entries(slots)) {
    try {
      proxy[name] = await rpc('eth_getStorageAt', [CONTRACT, slot, 'latest']);
    } catch (error) {
      proxy[name] = {error: String(error?.message || error)};
    }
  }
  try {
    proxy.implementation_call = await call('0x5c60da1b');
  } catch (error) {
    proxy.implementation_call = {error: String(error?.message || error)};
  }
  console.log(`PROBE proxy=${JSON.stringify(proxy)}`);
  return proxy;
}

async function scanLogs(creationBlock, latest) {
  const topicCounts = new Map();
  const topicSamples = new Map();
  let totalLogs = 0;
  let start = creationBlock;
  let chunk = 25_000;
  let chunksDone = 0;

  while (start <= latest) {
    const end = Math.min(latest, start + chunk - 1);
    try {
      const logs = await rpc(
        'eth_getLogs',
        [{address: CONTRACT, fromBlock: toHex(start), toBlock: toHex(end)}],
        60_000,
      );
      totalLogs += logs.length;
      for (const log of logs) {
        const topic0 = (log.topics?.[0] || 'NO_TOPIC').toLowerCase();
        topicCounts.set(topic0, (topicCounts.get(topic0) || 0) + 1);
        if (!topicSamples.has(topic0)) {
          topicSamples.set(topic0, {
            transaction_hash: log.transactionHash,
            block_number: fromHex(log.blockNumber),
            log_index: fromHex(log.logIndex),
            topics: log.topics,
            data_prefix: String(log.data || '').slice(0, 194),
          });
        }
      }
      start = end + 1;
      chunksDone += 1;
      if (chunksDone % 100 === 0 || logs.length > 0) {
        console.log(`PROBE logs-progress through=${end} chunk=${chunk} found=${logs.length} total=${totalLogs}`);
      }
      if (logs.length < 500 && chunk < 100_000) chunk = Math.min(100_000, chunk * 2);
    } catch (error) {
      console.log(`PROBE logs-retry start=${start} end=${end} chunk=${chunk} error=${String(error?.message || error)}`);
      if (chunk <= 100) throw error;
      chunk = Math.max(100, Math.floor(chunk / 2));
    }
  }

  return {
    total_logs: totalLogs,
    topic_counts: Object.fromEntries([...topicCounts.entries()].sort()),
    topic_samples: Object.fromEntries([...topicSamples.entries()].sort()),
  };
}

async function main() {
  console.log(`PROBE contract=${CONTRACT} rpc=${RPC_URL}`);
  const chainId = fromHex(await rpc('eth_chainId', []));
  const latest = fromHex(await rpc('eth_blockNumber', []));
  const latestCode = await rpc('eth_getCode', [CONTRACT, 'latest']);
  if (latestCode === '0x') throw new Error('contract has no current bytecode');
  console.log(`PROBE chain-id=${chainId} latest-block=${latest} code-bytes=${(latestCode.length - 2) / 2}`);

  const creationBlock = await findCreationBlock(latest);
  const interfaces = await inspectInterfaces();
  const proxy = await inspectProxy();
  const logs = await scanLogs(creationBlock, latest);

  console.log('NFT_CONTRACT_SUMMARY=' + JSON.stringify({
    contract: CONTRACT,
    chain_id: chainId,
    latest_block: latest,
    first_block_with_code: creationBlock,
    interfaces,
    proxy,
    ...logs,
  }));
}

main().catch(error => {
  console.error(`PROBE_FATAL=${error?.stack || error}`);
  process.exit(1);
});
