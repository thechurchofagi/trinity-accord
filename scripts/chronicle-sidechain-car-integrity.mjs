import fs from 'fs';
import path from 'path';
import {
  cidStringToBytes,
  dagPbLinks,
  parseCarStrict,
} from './ipfs-car-blockwise.mjs';

const DAG_PB_CODEC = 0x70;
const RAW_CODEC = 0x55;

function rootCidFromWholeDagUrl(value) {
  let url;
  try {
    url = value instanceof URL ? value : new URL(String(value));
  } catch {
    return null;
  }
  if ((url.searchParams.get('format') || '').toLowerCase() !== 'car') return null;
  if ((url.searchParams.get('dag-scope') || '').toLowerCase() !== 'all') return null;
  const match = url.pathname.match(/\/ipfs\/([^/]+)/i);
  if (!match) return null;
  try {
    return decodeURIComponent(match[1]);
  } catch {
    return match[1];
  }
}

export function verifyCompleteCar(input, rootCid) {
  const buf = Buffer.from(input);
  const rootBytes = cidStringToBytes(rootCid);
  const parsed = parseCarStrict(buf);
  if (!parsed.header.includes(rootBytes)) throw Error('root absent header');

  const blocks = new Map(parsed.blocks.map(block => [block.key, block]));
  const rootKey = rootBytes.toString('hex');
  if (!blocks.has(rootKey)) throw Error('root block missing');

  const seen = new Set();
  const stack = [rootKey];
  while (stack.length) {
    const key = stack.pop();
    if (seen.has(key)) continue;
    const block = blocks.get(key);
    if (!block) throw Error('linked block missing');
    seen.add(key);
    if (block.codec === DAG_PB_CODEC) {
      for (const linkedCid of dagPbLinks(block.data)) {
        const linkedKey = linkedCid.toString('hex');
        if (!blocks.has(linkedKey)) throw Error('linked block missing');
        stack.push(linkedKey);
      }
    } else if (block.codec !== RAW_CODEC) {
      throw Error(`unsupported block codec ${block.codec}`);
    }
  }

  return {
    bytes: buf.length,
    blocks: blocks.size,
    reachable: seen.size,
  };
}

export function auditWholeCarCache(dir) {
  const result = { checked: 0, valid: 0, removed: 0, errors: [] };
  if (!fs.existsSync(dir)) return result;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (!entry.isFile() || !entry.name.endsWith('.car')) continue;
    result.checked++;
    const rootCid = entry.name.slice(0, -4);
    const file = path.join(dir, entry.name);
    try {
      verifyCompleteCar(fs.readFileSync(file), rootCid);
      result.valid++;
    } catch (error) {
      fs.rmSync(file, { force: true });
      result.removed++;
      if (result.errors.length < 40) result.errors.push({ root_cid: rootCid, error: error?.message || String(error) });
      console.warn(`[CAR CACHE REJECTED] cid=${rootCid} error=${error?.message || error}`);
    }
  }
  return result;
}

export function installWholeDagFetchGuard() {
  const originalFetch = globalThis.fetch;
  if (typeof originalFetch !== 'function') throw Error('global fetch is unavailable');
  globalThis.fetch = async function guardedFetch(input, init) {
    const response = await originalFetch(input, init);
    const rawUrl = typeof input === 'string' || input instanceof URL ? input : input?.url;
    const rootCid = rootCidFromWholeDagUrl(rawUrl);
    if (!rootCid || !response.ok) return response;

    const body = Buffer.from(await response.arrayBuffer());
    try {
      const verified = verifyCompleteCar(body, rootCid);
      console.log(`[CAR WHOLE-DAG VERIFIED] cid=${rootCid} blocks=${verified.blocks} reachable=${verified.reachable} bytes=${verified.bytes}`);
    } catch (error) {
      throw Error(`whole-DAG CAR integrity failure cid=${rootCid}: ${error?.message || error}`);
    }
    return new Response(body, {
      status: response.status,
      statusText: response.statusText,
      headers: response.headers,
    });
  };
  return () => { globalThis.fetch = originalFetch; };
}

export { rootCidFromWholeDagUrl };
