#!/usr/bin/env node
import process from 'node:process';

const CONTRACT = (process.env.CONTRACT || '0x019372bBee377109b8Eae66d7267f5C4EaAdBb79').toLowerCase();
const RPC_URL = process.env.RPC_URL || 'https://ethereum-rpc.publicnode.com';
const BLOCKSCOUT_API = process.env.BLOCKSCOUT_API || 'https://eth.blockscout.com/api/v2';

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

async function getJson(url, timeoutMs = 30_000) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetch(url, {
      headers: {accept: 'application/json', 'user-agent': 'trinity-accord-nft-index/1'},
      signal: controller.signal,
    });
    const text = await response.text();
    if (!response.ok) throw new Error(`GET ${url}: HTTP ${response.status}: ${text.slice(0, 300)}`);
    return JSON.parse(text);
  } finally {
    clearTimeout(timer);
  }
}

const fromHex = value => Number.parseInt(value, 16);
const call = data => rpc('eth_call', [{to: CONTRACT, data}, 'latest']);
const supportsData = id => `0x01ffc9a7${id.replace(/^0x/, '')}${'0'.repeat(56)}`;
const boolResult = value => typeof value === 'string' && BigInt(value) !== 0n;

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

function selectAddressSummary(address) {
  return {
    available_keys: Object.keys(address).sort(),
    hash: address.hash,
    name: address.name,
    is_contract: address.is_contract,
    proxy_type: address.proxy_type,
    implementations: address.implementations,
    creator_address_hash: address.creator_address_hash,
    creation_tx_hash: address.creation_tx_hash,
    creation_transaction_hash: address.creation_transaction_hash,
    token: address.token,
  };
}

async function inspectBlockscout() {
  const address = await getJson(`${BLOCKSCOUT_API}/addresses/${CONTRACT}`);
  const addressSummary = selectAddressSummary(address);
  console.log(`PROBE blockscout-address=${JSON.stringify(addressSummary)}`);

  const token = await getJson(`${BLOCKSCOUT_API}/tokens/${CONTRACT}`);
  console.log(`PROBE blockscout-token=${JSON.stringify(token)}`);

  const transfers = await getJson(`${BLOCKSCOUT_API}/tokens/${CONTRACT}/transfers`);
  const transferItems = Array.isArray(transfers.items) ? transfers.items : [];
  const transferSummary = {
    available_keys: Object.keys(transfers).sort(),
    item_count: transferItems.length,
    next_page_params: transfers.next_page_params || null,
    first_items: transferItems.slice(0, 3),
  };
  console.log(`PROBE blockscout-token-transfers=${JSON.stringify(transferSummary)}`);

  const instances = await getJson(`${BLOCKSCOUT_API}/tokens/${CONTRACT}/instances`);
  const instanceItems = Array.isArray(instances.items) ? instances.items : [];
  const instanceSummary = {
    available_keys: Object.keys(instances).sort(),
    item_count: instanceItems.length,
    next_page_params: instances.next_page_params || null,
    first_items: instanceItems.slice(0, 3),
  };
  console.log(`PROBE blockscout-instances=${JSON.stringify(instanceSummary)}`);

  return {address: addressSummary, token, transfers: transferSummary, instances: instanceSummary};
}

async function main() {
  console.log(`PROBE contract=${CONTRACT} rpc=${RPC_URL}`);
  const chainId = fromHex(await rpc('eth_chainId', []));
  const latest = fromHex(await rpc('eth_blockNumber', []));
  const latestCode = await rpc('eth_getCode', [CONTRACT, 'latest']);
  if (latestCode === '0x') throw new Error('contract has no current bytecode');
  console.log(`PROBE chain-id=${chainId} latest-block=${latest} code-bytes=${(latestCode.length - 2) / 2}`);

  const interfaces = await inspectInterfaces();
  const proxy = await inspectProxy();
  const blockscout = await inspectBlockscout();

  console.log('NFT_CONTRACT_SUMMARY=' + JSON.stringify({
    contract: CONTRACT,
    chain_id: chainId,
    latest_block: latest,
    interfaces,
    proxy,
    blockscout,
  }));
}

main().catch(error => {
  console.error(`PROBE_FATAL=${error?.stack || error}`);
  process.exit(1);
});
