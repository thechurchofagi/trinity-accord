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
  try { return decodeURIComponent(match[1]); } catch { return match[1]; }
}

function report(onEvent, event) {
  if (typeof onEvent !== 'function') return;
  try { onEvent(event); } catch {}
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
  return { bytes: buf.length, blocks: blocks.size, reachable: seen.size };
}

export function auditWholeCarCache(dir, { onEvent } = {}) {
  const result = { checked: 0, valid: 0, removed: 0, errors: [] };
  report(onEvent, { event: 'cache_audit_start', phase: 'cache_audit', status: 'running', directory: dir });
  if (!fs.existsSync(dir)) {
    report(onEvent, { event: 'cache_audit_complete', phase: 'cache_audit', status: 'success', ...result });
    return result;
  }
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (!entry.isFile() || !entry.name.endsWith('.car')) continue;
    result.checked++;
    const rootCid = entry.name.slice(0, -4);
    const file = path.join(dir, entry.name);
    report(onEvent, { event: 'cache_check', phase: 'cache_audit', status: 'running', root_cid: rootCid });
    try {
      const verified = verifyCompleteCar(fs.readFileSync(file), rootCid);
      result.valid++;
      report(onEvent, { event: 'cache_valid', phase: 'cache_audit', status: 'success', root_cid: rootCid, ...verified });
    } catch (error) {
      fs.rmSync(file, { force: true });
      result.removed++;
      const message = error?.message || String(error);
      if (result.errors.length < 40) result.errors.push({ root_cid: rootCid, error: message });
      report(onEvent, { event: 'cache_rejected', phase: 'cache_audit', status: 'failure', root_cid: rootCid, error: message });
      console.warn(`[CAR CACHE REJECTED] cid=${rootCid} error=${message}`);
    }
  }
  report(onEvent, { event: 'cache_audit_complete', phase: 'cache_audit', status: 'success', ...result });
  return result;
}

export function installWholeDagFetchGuard({ onEvent } = {}) {
  const originalFetch = globalThis.fetch;
  if (typeof originalFetch !== 'function') throw Error('global fetch is unavailable');
  const threshold = Math.max(1, Math.min(20, Number(process.env.CHRONICLE_CAR_WHOLE_DAG_CIRCUIT_FAILURES || 2)));
  const failures = new Map();
  const hostOf = value => { try { return new URL(String(value)).host; } catch { return null; } };
  const markFailure = host => { if (host) failures.set(host, (failures.get(host) || 0) + 1); };
  const markSuccess = host => { if (host) failures.delete(host); };

  globalThis.fetch = async function guardedFetch(input, init) {
    const rawUrl = typeof input === 'string' || input instanceof URL ? input : input?.url;
    const rootCid = rootCidFromWholeDagUrl(rawUrl);
    const host = rootCid ? hostOf(rawUrl) : null;
    const started = Date.now();
    if (rootCid && host && (failures.get(host) || 0) >= threshold) {
      const count = failures.get(host) || 0;
      const error = Error(`whole-DAG endpoint circuit open host=${host} failures=${count}`);
      report(onEvent, { event: 'whole_dag_circuit_open', phase: 'whole_dag', status: 'failure', root_cid: rootCid, endpoint: rawUrl, host, failures: count, error: error.message });
      throw error;
    }
    if (rootCid) report(onEvent, { event: 'whole_dag_attempt', phase: 'whole_dag', status: 'running', root_cid: rootCid, endpoint: rawUrl, host });

    let response;
    try {
      response = await originalFetch(input, init);
    } catch (error) {
      if (rootCid) {
        markFailure(host);
        report(onEvent, { event: 'whole_dag_network_failure', phase: 'whole_dag', status: 'failure', root_cid: rootCid, endpoint: rawUrl, host, elapsed_ms: Date.now() - started, error: error?.message || String(error) });
      }
      throw error;
    }
    if (!rootCid) return response;
    if (!response.ok) {
      if (response.status === 429 || response.status >= 500) markFailure(host);
      report(onEvent, { event: 'whole_dag_http_failure', phase: 'whole_dag', status: 'failure', root_cid: rootCid, endpoint: rawUrl, host, http_status: response.status, elapsed_ms: Date.now() - started });
      return response;
    }

    let body;
    try {
      body = Buffer.from(await response.arrayBuffer());
    } catch (error) {
      markFailure(host);
      report(onEvent, { event: 'whole_dag_body_failure', phase: 'whole_dag', status: 'failure', root_cid: rootCid, endpoint: rawUrl, host, http_status: response.status, elapsed_ms: Date.now() - started, error: error?.message || String(error) });
      throw error;
    }

    try {
      const verified = verifyCompleteCar(body, rootCid);
      markSuccess(host);
      report(onEvent, { event: 'whole_dag_verified', phase: 'whole_dag', status: 'success', root_cid: rootCid, endpoint: rawUrl, host, http_status: response.status, elapsed_ms: Date.now() - started, bytes: verified.bytes, blocks: verified.blocks, reachable: verified.reachable });
      console.log(`[CAR WHOLE-DAG VERIFIED] cid=${rootCid} blocks=${verified.blocks} reachable=${verified.reachable} bytes=${verified.bytes}`);
    } catch (error) {
      markFailure(host);
      const message = error?.message || String(error);
      report(onEvent, { event: 'whole_dag_integrity_failure', phase: 'whole_dag', status: 'failure', root_cid: rootCid, endpoint: rawUrl, host, http_status: response.status, elapsed_ms: Date.now() - started, bytes: body.length, error: message });
      throw Error(`whole-DAG CAR integrity failure cid=${rootCid}: ${message}`);
    }
    return new Response(body, { status: response.status, statusText: response.statusText, headers: response.headers });
  };
  return () => { globalThis.fetch = originalFetch; };
}

export { rootCidFromWholeDagUrl };
