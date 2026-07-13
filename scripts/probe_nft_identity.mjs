#!/usr/bin/env node
import process from 'node:process';

const RPC_URL = process.env.RPC_URL || 'https://ethereum-rpc.publicnode.com';
const BLOCKSCOUT_API = process.env.BLOCKSCOUT_API || 'https://eth.blockscout.com/api/v2';
const TOKEN_INDEX_URL = process.env.TOKEN_INDEX_URL;
const ZERO = '0x0000000000000000000000000000000000000000';

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

function withPage(baseUrl, params) {
  if (!params) return baseUrl;
  const url = new URL(baseUrl);
  for (const [key, value] of Object.entries(params)) {
    if (value !== null && value !== undefined) url.searchParams.set(key, String(value));
  }
  return url.toString();
}

async function fetchAllPages(baseUrl, maxPages = 100) {
  const items = [];
  let next = null;
  let pages = 0;
  do {
    const page = await getJson(withPage(baseUrl, next));
    if (!Array.isArray(page.items)) throw new Error(`missing items array: ${baseUrl}`);
    items.push(...page.items);
    next = page.next_page_params || null;
    pages += 1;
    if (pages > maxPages) throw new Error(`pagination exceeded ${maxPages} pages: ${baseUrl}`);
  } while (next);
  return {items, pages};
}

function conciseTransfer(item) {
  return {
    transaction_hash: item.transaction_hash || item.transaction?.hash || null,
    block_hash: item.block_hash || null,
    block_number: item.block_number,
    log_index: item.log_index,
    timestamp: item.timestamp,
    method: item.method,
    from: item.from?.hash || null,
    to: item.to?.hash || null,
    token_id: String(item.total?.token_id || item.token_id || item.token_instance?.id || ''),
    token_type: item.token_type || item.token?.type || null,
  };
}

async function inspectContract(contract, expectedTokenIds) {
  const normalized = contract.toLowerCase();
  const code = await rpc('eth_getCode', [normalized, 'latest']);
  if (code === '0x') throw new Error(`no Ethereum mainnet code for ${contract}`);

  const address = await getJson(`${BLOCKSCOUT_API}/addresses/${normalized}`);
  const token = await getJson(`${BLOCKSCOUT_API}/tokens/${normalized}`);
  const allTransfers = await fetchAllPages(`${BLOCKSCOUT_API}/tokens/${normalized}/transfers`);
  const transfers = allTransfers.items.map(conciseTransfer);
  const mints = transfers.filter(item => String(item.from).toLowerCase() === ZERO);
  const mintByTokenId = new Map();
  for (const mint of mints) {
    if (mintByTokenId.has(mint.token_id)) throw new Error(`duplicate mint event ${contract}/${mint.token_id}`);
    mintByTokenId.set(mint.token_id, mint);
  }

  const expected = new Set(expectedTokenIds.map(String));
  const missing = [...expected].filter(tokenId => !mintByTokenId.has(tokenId)).sort((a, b) => BigInt(a) < BigInt(b) ? -1 : 1);
  const unexpected = [...mintByTokenId.keys()].filter(tokenId => !expected.has(tokenId)).sort((a, b) => BigInt(a) < BigInt(b) ? -1 : 1);
  const matched = expectedTokenIds.map(String).filter(tokenId => mintByTokenId.has(tokenId));

  return {
    contract,
    name: token.name || address.name || null,
    symbol: token.symbol || null,
    standard: token.type || null,
    code_bytes: (code.length - 2) / 2,
    proxy_type: address.proxy_type || null,
    implementations: address.implementations || [],
    creator_address: address.creator_address_hash || null,
    creation_transaction_hash: address.creation_transaction_hash || null,
    expected_tokens: expected.size,
    transfer_pages: allTransfers.pages,
    all_transfers: transfers.length,
    mint_events: mints.length,
    unique_mint_token_ids: mintByTokenId.size,
    matched_tokens: matched.length,
    missing_tokens: missing,
    unexpected_tokens: unexpected,
    oldest_mint: mints.at(-1) || null,
    newest_mint: mints[0] || null,
  };
}

async function main() {
  if (!TOKEN_INDEX_URL) throw new Error('TOKEN_INDEX_URL is required');
  const chainId = Number.parseInt(await rpc('eth_chainId', []), 16);
  const latest = Number.parseInt(await rpc('eth_blockNumber', []), 16);
  if (chainId !== 1) throw new Error(`expected Ethereum mainnet chain id 1, got ${chainId}`);

  const tokenIndex = await getJson(TOKEN_INDEX_URL, 60_000);
  const contracts = Object.keys(tokenIndex);
  const totalTokens = contracts.reduce((sum, contract) => sum + Object.keys(tokenIndex[contract] || {}).length, 0);
  console.log(`PROBE token-index contracts=${contracts.length} tokens=${totalTokens}`);

  const contractResults = [];
  for (const contract of contracts) {
    const result = await inspectContract(contract, Object.keys(tokenIndex[contract] || {}));
    contractResults.push(result);
    console.log(`PROBE contract-summary=${JSON.stringify(result)}`);
  }

  const matched = contractResults.reduce((sum, item) => sum + item.matched_tokens, 0);
  const missing = contractResults.reduce((sum, item) => sum + item.missing_tokens.length, 0);
  const unexpected = contractResults.reduce((sum, item) => sum + item.unexpected_tokens.length, 0);
  const summary = {
    schema: 'trinityaccord.nft-identity-probe.v1',
    chain_id: chainId,
    latest_block: latest,
    token_index_url: TOKEN_INDEX_URL,
    contracts: contracts.length,
    expected_tokens: totalTokens,
    matched_tokens: matched,
    missing_tokens: missing,
    unexpected_tokens: unexpected,
    complete: matched === totalTokens && missing === 0 && unexpected === 0,
    contract_results: contractResults,
  };
  console.log('NFT_IDENTITY_PROBE=' + JSON.stringify(summary));
  if (!summary.complete) process.exitCode = 2;
}

main().catch(error => {
  console.error(`PROBE_FATAL=${error?.stack || error}`);
  process.exit(1);
});
