#!/usr/bin/env node
import path from 'path';
import {
  auditWholeCarCache,
  installWholeDagFetchGuard,
} from './chronicle-sidechain-car-integrity.mjs';

const out = process.env.CHRONICLE_OUT || 'artifacts/chronicle-sidechain-scan';
const carDir = path.join(out, 'evidence-v2', 'cars');
const audit = auditWholeCarCache(carDir);
console.log(`[CAR CACHE AUDIT] checked=${audit.checked} valid=${audit.valid} removed=${audit.removed}`);
if (audit.removed) {
  console.log(`[CAR CACHE AUDIT] rejected cached CARs will be recovered through the existing verified gateway/blockwise/provider chain`);
}
installWholeDagFetchGuard();
await import('./build-chronicle-sidechain-evidence-core.mjs');
