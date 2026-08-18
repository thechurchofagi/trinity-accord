#!/usr/bin/env node
import fs from 'fs';
import path from 'path';
import {
  auditWholeCarCache,
  installWholeDagFetchGuard,
} from './chronicle-sidechain-car-integrity.mjs';
import { createCarProgress } from './chronicle-sidechain-car-progress.mjs';
import { createCarTrace } from './chronicle-sidechain-car-trace.mjs';

const out = process.env.CHRONICLE_OUT || 'artifacts/chronicle-sidechain-scan';
const configuredConcurrency = Number(process.env.CHRONICLE_EVIDENCE_CONCURRENCY || 0);
if (!Number.isFinite(configuredConcurrency) || configuredConcurrency < 4) {
  process.env.CHRONICLE_EVIDENCE_CONCURRENCY = '4';
}
const configuredWholeDagEndpoints = Number(process.env.CHRONICLE_CAR_WHOLE_DAG_ENDPOINT_LIMIT || 0);
if (!Number.isFinite(configuredWholeDagEndpoints) || configuredWholeDagEndpoints < 4) {
  process.env.CHRONICLE_CAR_WHOLE_DAG_ENDPOINT_LIMIT = '4';
}

const runtimeDir = path.join(out, 'runtime');
fs.mkdirSync(runtimeDir, { recursive: true });
const builderLog = path.join(runtimeDir, 'CAR-BUILDER.log');
fs.writeFileSync(builderLog, '');
const trace = createCarTrace({ out });
let progress = null;

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
});

const carDir = path.join(out, 'evidence-v2', 'cars');
trace.phase('cache_audit', 'running', { directory: carDir });
const audit = auditWholeCarCache(carDir, { onEvent: trace.emit });
trace.phase('cache_audit', 'success', { checked: audit.checked, valid: audit.valid, removed: audit.removed });
console.log(`[CAR CACHE AUDIT] checked=${audit.checked} valid=${audit.valid} removed=${audit.removed}`);
if (audit.removed) {
  console.log('[CAR CACHE AUDIT] rejected cached CARs will be recovered through the existing verified gateway/blockwise/provider chain');
}

progress = createCarProgress({ out, audit });
await progress.publish();
installWholeDagFetchGuard({ onEvent: trace.emit });
trace.phase('evidence_builder', 'running');
try {
  await import('./build-chronicle-sidechain-evidence-core.mjs');
  trace.phase('evidence_builder', 'success');
  await progress.finish('success');
  trace.phase('wrapper', 'success');
} catch (error) {
  trace.failure('evidence_builder_failure', error, { phase: 'evidence_builder' });
  try { await progress.finish('failure'); } catch (progressError) {
    trace.failure('progress_publish_failure', progressError, { phase: 'telemetry' });
  }
  trace.phase('wrapper', 'failure');
  throw error;
}
