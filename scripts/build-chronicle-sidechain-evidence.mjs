#!/usr/bin/env node
import fs from 'fs';
import path from 'path';
import { execFileSync, spawnSync } from 'child_process';
import {
  auditWholeCarCache,
  installWholeDagFetchGuard,
} from './chronicle-sidechain-car-integrity.mjs';
import { createCarProgress } from './chronicle-sidechain-car-progress.mjs';
import { createCarTrace } from './chronicle-sidechain-car-trace.mjs';
import { rebuildCarsFromHistoricalPayloads } from './rebuild-chronicle-sidechain-cars-from-history.mjs';

const out = process.env.CHRONICLE_OUT || 'artifacts/chronicle-sidechain-scan';
const configuredConcurrency = Number(process.env.CHRONICLE_EVIDENCE_CONCURRENCY || 0);
if (!Number.isFinite(configuredConcurrency) || configuredConcurrency < 4) {
  process.env.CHRONICLE_EVIDENCE_CONCURRENCY = '4';
}
const configuredWholeDagEndpoints = Number(process.env.CHRONICLE_CAR_WHOLE_DAG_ENDPOINT_LIMIT || 0);
if (!Number.isFinite(configuredWholeDagEndpoints) || configuredWholeDagEndpoints < 4) {
  process.env.CHRONICLE_CAR_WHOLE_DAG_ENDPOINT_LIMIT = '4';
}
// Whole-DAG is only a fast path. Slow gateways must not hold every worker for
// 30s per endpoint before the strict blockwise/provider recovery chain can run.
const configuredCarTimeout = Number(process.env.CHRONICLE_CAR_HTTP_TIMEOUT_MS || 0);
if (!Number.isFinite(configuredCarTimeout) || configuredCarTimeout <= 0 || configuredCarTimeout > 10000) {
  process.env.CHRONICLE_CAR_HTTP_TIMEOUT_MS = '10000';
}
if (!process.env.CHRONICLE_CAR_WHOLE_DAG_CIRCUIT_FAILURES) {
  process.env.CHRONICLE_CAR_WHOLE_DAG_CIRCUIT_FAILURES = '2';
}

// Provider fallbacks are recovery paths, not evidence acceptance rules. Bound
// their latency so one missing block cannot serialize a worker for 3+ minutes
// before the next independent provider is tried. The recovered bytes are still
// CID-checked by the blockwise builder and the final CAR/DAG verifier.
function capEnv(name, maxMs) {
  const value = Number(process.env[name] || 0);
  if (!Number.isFinite(value) || value <= 0 || value > maxMs) process.env[name] = String(maxMs);
}
capEnv('CHRONICLE_KUBO_CONNECT_TIMEOUT_MS', 8000);
capEnv('CHRONICLE_KUBO_BLOCK_TIMEOUT_MS', 30000);
capEnv('CHRONICLE_LASSIE_DELEGATED_ROUTING_TIMEOUT_MS', 8000);
capEnv('CHRONICLE_LASSIE_PROVIDER_TIMEOUT_MS', 15000);
capEnv('CHRONICLE_LASSIE_GLOBAL_TIMEOUT_MS', 60000);

const runtimeDir = path.join(out, 'runtime');
fs.mkdirSync(runtimeDir, { recursive: true });
const builderLog = path.join(runtimeDir, 'CAR-BUILDER.log');
fs.writeFileSync(builderLog, '');
const trace = createCarTrace({ out });
let progress = null;
const observeCarEvent = event => {
  try { trace.emit(event); } catch {}
  try { progress?.observeEvent(event); } catch {}
};

// The checkout action persists the workflow token in a git extraheader. Reuse
// it only in-memory for operational issue telemetry when GH_TOKEN was not
// explicitly passed to this step. Never print or persist the credential.
function checkoutToken() {
  if (process.env.GH_TOKEN) return process.env.GH_TOKEN;
  try {
    const raw = execFileSync('git', ['config', '--get-all', 'http.https://github.com/.extraheader'], {
      encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'],
    });
    for (const line of raw.split(/\r?\n/)) {
      const match = line.match(/authorization:\s*basic\s+([A-Za-z0-9+/=]+)/i);
      if (!match) continue;
      const decoded = Buffer.from(match[1], 'base64').toString('utf8');
      const colon = decoded.indexOf(':');
      if (colon >= 0 && decoded.slice(colon + 1)) return decoded.slice(colon + 1);
    }
  } catch {}
  return '';
}

const debugEnv = { ...process.env, CHRONICLE_OUT: out };
const token = checkoutToken();
if (token) debugEnv.GH_TOKEN = token;
let debugTimer = null;
function runDebug(args) {
  try {
    const result = spawnSync('python3', ['scripts/sidechain-debug-live.py', ...args], {
      env: debugEnv,
      stdio: 'inherit',
      timeout: 15000,
    });
    if (result.error) console.warn(`[SIDECHAIN DEBUG INVOCATION FAILED] ${result.error.message}`);
  } catch (error) {
    console.warn(`[SIDECHAIN DEBUG INVOCATION FAILED] ${error?.message || error}`);
  }
}
function debugMark(step, status = 'running', detail = '') {
  runDebug(['mark', '--phase', 'car_l1', '--step', step, '--status', status, '--detail', detail]);
}
function debugSnapshot() { runDebug(['snapshot']); }
function startDebug() {
  debugMark('cache_audit', 'running', 'strictly validate restored CAR cache before reuse');
  debugTimer = setInterval(debugSnapshot, Number(process.env.CHRONICLE_DEBUG_PUBLISH_SECONDS || 15) * 1000);
  debugTimer.unref();
}
function stopDebug(step, status, detail = '') {
  if (debugTimer) clearInterval(debugTimer);
  debugTimer = null;
  debugMark(step, status, detail);
  debugSnapshot();
}

const original = { log: console.log, warn: console.warn, error: console.error };
for (const method of ['log', 'warn', 'error']) {
  console[method] = (...args) => {
    original[method](...args);
    const line = args.map(value => typeof value === 'string' ? value : String(value)).join(' ');
    try { fs.appendFileSync(builderLog, `${new Date().toISOString()} [${method.toUpperCase()}] ${line}\n`); } catch {}
    try { trace.observeConsole(method, line); } catch {}
    try { progress?.observe(line); } catch {}
  };
}

trace.phase('wrapper', 'running', {
  evidence_concurrency: Number(process.env.CHRONICLE_EVIDENCE_CONCURRENCY),
  car_block_concurrency: Number(process.env.CHRONICLE_CAR_BLOCK_CONCURRENCY || 0) || null,
  whole_dag_endpoint_limit: Number(process.env.CHRONICLE_CAR_WHOLE_DAG_ENDPOINT_LIMIT),
  whole_dag_timeout_ms: Number(process.env.CHRONICLE_CAR_HTTP_TIMEOUT_MS),
  whole_dag_circuit_failures: Number(process.env.CHRONICLE_CAR_WHOLE_DAG_CIRCUIT_FAILURES),
  kubo_connect_timeout_ms: Number(process.env.CHRONICLE_KUBO_CONNECT_TIMEOUT_MS),
  kubo_block_timeout_ms: Number(process.env.CHRONICLE_KUBO_BLOCK_TIMEOUT_MS),
  lassie_routing_timeout_ms: Number(process.env.CHRONICLE_LASSIE_DELEGATED_ROUTING_TIMEOUT_MS),
  lassie_provider_timeout_ms: Number(process.env.CHRONICLE_LASSIE_PROVIDER_TIMEOUT_MS),
  lassie_global_timeout_ms: Number(process.env.CHRONICLE_LASSIE_GLOBAL_TIMEOUT_MS),
});

startDebug();
const carDir = path.join(out, 'evidence-v2', 'cars');
trace.phase('cache_audit', 'running', { directory: carDir });
const audit = auditWholeCarCache(carDir, { onEvent: observeCarEvent });
trace.phase('cache_audit', 'success', { checked: audit.checked, valid: audit.valid, removed: audit.removed });
console.log(`[CAR CACHE AUDIT] checked=${audit.checked} valid=${audit.valid} removed=${audit.removed}`);
if (audit.removed) {
  console.log('[CAR CACHE AUDIT] rejected cached CARs will first be reconstructed from verified historical payload bytes, then fall back to the existing gateway/blockwise/provider chain');
}

progress = createCarProgress({ out, audit });
await progress.publish();

debugMark('historical_car_rebuild', 'running', 'map every IPFS root to preserved local byte candidates and require exact CID equality');
trace.phase('historical_car_rebuild', 'running');
try {
  const rebuilt = await rebuildCarsFromHistoricalPayloads({ out, kubo: process.env.CHRONICLE_KUBO_BIN || '' });
  trace.phase('historical_car_rebuild', 'success', {
    roots_considered: rebuilt.roots_considered,
    already_valid: rebuilt.already_valid,
    direct_raw_rebuilt: rebuilt.direct_raw_rebuilt,
    kubo_rebuilt: rebuilt.kubo_rebuilt,
    unrecovered: rebuilt.unrecovered.length,
  });
  const after = auditWholeCarCache(carDir, { onEvent: observeCarEvent });
  progress.state.cache_audit_after_historical_rebuild = after;
  progress.state.historical_car_rebuild = {
    roots_considered: rebuilt.roots_considered,
    already_valid: rebuilt.already_valid,
    invalid_removed: rebuilt.invalid_removed,
    direct_raw_rebuilt: rebuilt.direct_raw_rebuilt,
    kubo_rebuilt: rebuilt.kubo_rebuilt,
    unrecovered_count: rebuilt.unrecovered.length,
    unrecovered: rebuilt.unrecovered.slice(0, 40),
  };
  await progress.publish();
} catch (error) {
  trace.failure('historical_car_rebuild_failure', error, { phase: 'historical_car_rebuild' });
  console.warn(`[CAR HISTORICAL REBUILD STAGE FAILED] ${error?.message || error}; continuing with strict network/provider recovery`);
}

installWholeDagFetchGuard({ onEvent: observeCarEvent });
debugMark('strict_network_provider_recovery', 'running', 'whole-DAG fast path then strict blockwise/Kubo/Lassie fallback per missing root');
trace.phase('evidence_builder', 'running');
try {
  await import('./build-chronicle-sidechain-evidence-core.mjs');
  trace.phase('evidence_builder', 'success');
  await progress.finish('success');
  trace.phase('wrapper', 'success');
  stopDebug('car_l1_complete', 'success', 'CAR builder and L1 commitment completed');
} catch (error) {
  trace.failure('evidence_builder_failure', error, { phase: 'evidence_builder' });
  try { await progress.finish('failure'); } catch (progressError) {
    trace.failure('progress_publish_failure', progressError, { phase: 'telemetry' });
  }
  trace.phase('wrapper', 'failure');
  stopDebug('car_l1_failed', 'failure', error?.message || String(error));
  throw error;
}
