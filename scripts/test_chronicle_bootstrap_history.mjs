#!/usr/bin/env node
import assert from 'assert/strict';
import fs from 'fs';

const build = fs.readFileSync('scripts/build-chronicle-sidechain-evidence.mjs', 'utf8');
const workflow = fs.readFileSync('.github/workflows/chronicle-sidechain-mirror.yml', 'utf8');

assert.match(build, /CHRONICLE_EVIDENCE_REFRESH_HISTORY/);
assert.match(build, /verified_recovered_tokens_snapshot/);
assert.match(build, /snapshotHistory\(t\)/);
assert.match(workflow, /CHRONICLE_EVIDENCE_REFRESH_HISTORY: "false"/);

const baseline = workflow.indexOf('Restore complete CAR baseline cache');
const latest = workflow.indexOf('Restore latest CAR and block recovery cache');
assert.ok(baseline >= 0 && latest > baseline, 'complete baseline must be restored before the latest block cache overlay');
assert.match(workflow, /chronicle-sidechain-cars-v2-d0fe9d4c5f57d98f784ea9c9726d762a0980c08c19b909e6bdc60e97e29be7c8-32078752685-1/);
assert.match(workflow, /CHRONICLE_HISTORICAL_CHUNK_SIZES: "1048576,262144"/);
assert.match(workflow, /https:\/\/ipfs\.raribleuserdata\.com\/ipfs\/\{cid\}/);
assert.match(workflow, /https:\/\/rarible\.mypinata\.cloud\/ipfs\/\{cid\}/);
assert.match(build, /CAR HISTORICAL CHUNK VERIFIED/);
assert.match(build, /scope: 'all'/);
assert.match(build, /CAR LASSIE ROOT REUSE/);

console.log('[BOOTSTRAP HISTORY TEST PASS] verified snapshot history + layered CAR caches');
