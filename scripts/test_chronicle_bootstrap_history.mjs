#!/usr/bin/env node
import assert from 'assert/strict';
import fs from 'fs';

const build = fs.readFileSync('scripts/build-chronicle-sidechain-evidence.mjs', 'utf8');
const workflowPath = '.github/workflows/chronicle-sidechain-mirror-v3.yml';
assert.ok(fs.existsSync(workflowPath), `active sidechain workflow missing: ${workflowPath}`);
assert.ok(!fs.existsSync('.github/workflows/chronicle-sidechain-mirror.yml'), 'retired serial sidechain workflow must remain absent');
const workflow = fs.readFileSync(workflowPath, 'utf8');

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
assert.match(workflow, /KUBO_VERSION: 0\.37\.0/);
assert.match(workflow, /KUBO_LINUX_AMD64_SHA512: [0-9a-f]{128}/);
assert.match(workflow, /sha512sum --check --strict/);
assert.match(workflow, /daemon --migrate=false/);
assert.match(build, /CAR HISTORICAL CHUNK VERIFIED/);
assert.match(build, /scope: 'all'/);
assert.match(build, /CAR LASSIE ROOT REUSE/);
assert.match(build, /CAR KUBO BLOCK VERIFIED/);
assert.match(build, /singleBlockCar\(cid, data\)/);

console.log('[BOOTSTRAP HISTORY TEST PASS] verified snapshot history + layered CAR caches + active v3 workflow');
