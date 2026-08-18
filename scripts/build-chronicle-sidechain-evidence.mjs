#!/usr/bin/env node
import path from 'path';
import {
  auditWholeCarCache,
  installWholeDagFetchGuard,
} from './chronicle-sidechain-car-integrity.mjs';
import { createCarProgress } from './chronicle-sidechain-car-progress.mjs';

const out = process.env.CHRONICLE_OUT || 'artifacts/chronicle-sidechain-scan';
const configuredConcurrency = Number(process.env.CHRONICLE_EVIDENCE_CONCURRENCY || 0);
if (!Number.isFinite(configuredConcurrency) || configuredConcurrency < 4) {
  process.env.CHRONICLE_EVIDENCE_CONCURRENCY = '4';
}
const configuredWholeDagEndpoints = Number(process.env.CHRONICLE_CAR_WHOLE_DAG_ENDPOINT_LIMIT || 0);
if (!Number.isFinite(configuredWholeDagEndpoints) || configuredWholeDagEndpoints < 4) {
  process.env.CHRONICLE_CAR_WHOLE_DAG_ENDPOINT_LIMIT = '4';
}
const carDir = path.join(out, 'evidence-v2', 'cars');
const audit = auditWholeCarCache(carDir);
console.log(`[CAR CACHE AUDIT] checked=${audit.checked} valid=${audit.valid} removed=${audit.removed}`);
if (audit.removed) {
  console.log('[CAR CACHE AUDIT] rejected cached CARs will be recovered through the existing verified gateway/blockwise/provider chain');
}

const progress = createCarProgress({ out, audit });
const original = { log: console.log, warn: console.warn, error: console.error };
for (const method of ['log', 'warn', 'error']) {
  console[method] = (...args) => {
    original[method](...args);
    try { progress.observe(args.map(value => typeof value === 'string' ? value : String(value)).join(' ')); } catch {}
  };
}
await progress.publish();
installWholeDagFetchGuard();
try {
  await import('./build-chronicle-sidechain-evidence-core.mjs');
  await progress.finish('success');
} catch (error) {
  await progress.finish('failure');
  throw error;
}
