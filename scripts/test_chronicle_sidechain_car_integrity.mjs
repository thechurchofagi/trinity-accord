#!/usr/bin/env node
import assert from 'assert/strict';
import crypto from 'crypto';
import fs from 'fs';
import os from 'os';
import path from 'path';
import {
  cidBytesToString,
  encodeVarint,
  singleBlockCar,
} from './ipfs-car-blockwise.mjs';
import {
  auditWholeCarCache,
  rootCidFromWholeDagUrl,
  verifyCompleteCar,
} from './chronicle-sidechain-car-integrity.mjs';
import { updateCarProgressFromLine } from './chronicle-sidechain-car-progress.mjs';

function cidV1(codec, data) {
  const digest = crypto.createHash('sha256').update(data).digest();
  return Buffer.concat([
    encodeVarint(1),
    encodeVarint(codec),
    encodeVarint(0x12),
    encodeVarint(digest.length),
    digest,
  ]);
}

const raw = Buffer.from('trinity-sidechain-car-integrity-regression');
const rawCidBytes = cidV1(0x55, raw);
const rawCid = cidBytesToString(rawCidBytes);
const validCar = singleBlockCar(rawCid, raw);
const valid = verifyCompleteCar(validCar, rawCid);
assert.equal(valid.blocks, 1);
assert.equal(valid.reachable, 1);
assert.throws(() => verifyCompleteCar(validCar.subarray(0, validCar.length - 1), rawCid), /exceeds input|truncated/i);

const child = Buffer.from('missing-linked-child');
const childCidBytes = cidV1(0x55, child);
const pbLink = Buffer.concat([Buffer.from([0x0a]), encodeVarint(childCidBytes.length), childCidBytes]);
const rootData = Buffer.concat([Buffer.from([0x12]), encodeVarint(pbLink.length), pbLink]);
const rootCidBytes = cidV1(0x70, rootData);
const rootCid = cidBytesToString(rootCidBytes);
const incompleteDagCar = singleBlockCar(rootCid, rootData);
assert.throws(() => verifyCompleteCar(incompleteDagCar, rootCid), /linked block missing/);

assert.equal(rootCidFromWholeDagUrl(`https://example.invalid/ipfs/${rawCid}?format=car&dag-scope=all`), rawCid);
assert.equal(rootCidFromWholeDagUrl(`https://example.invalid/ipfs/${rawCid}?format=car&dag-scope=block`), null);
assert.equal(rootCidFromWholeDagUrl(`https://example.invalid/ipfs/${rawCid}`), null);

const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'trinity-car-audit-'));
try {
  fs.writeFileSync(path.join(temp, `${rawCid}.car`), validCar);
  fs.writeFileSync(path.join(temp, `${rootCid}.car`), incompleteDagCar);
  const audit = auditWholeCarCache(temp);
  assert.equal(audit.checked, 2);
  assert.equal(audit.valid, 1);
  assert.equal(audit.removed, 1);
  assert.equal(fs.existsSync(path.join(temp, `${rawCid}.car`)), true);
  assert.equal(fs.existsSync(path.join(temp, `${rootCid}.car`)), false);
} finally {
  fs.rmSync(temp, { recursive: true, force: true });
}

const progress = {};
assert.equal(updateCarProgressFromLine(progress, '[EVIDENCE START] 38/217 worker=3 base 0xabc #42'), true);
assert.equal(progress.workers['3'].record_index, 38);
assert.equal(progress.workers['3'].chain, 'base');
assert.equal(progress.workers['3'].contract, '0xabc');
assert.equal(progress.workers['3'].token_id, '42');
assert.equal(updateCarProgressFromLine(progress, '[EVIDENCE PROGRESS] 37/217 origin=mint car=ok'), true);
assert.equal(progress.records_completed, 37);
assert.equal(progress.records_expected, 217);
assert.equal(progress.last_metadata_car_status, 'ok');
assert.equal(updateCarProgressFromLine(progress, '[CAR BLOCKWISE COMPLETE] cid=test blocks=2'), true);
assert.equal(progress.blockwise_completed, 1);
assert.equal(progress.last_cid, 'test');
assert.equal(updateCarProgressFromLine(progress, '[CAR FAILED] cid=bafyfailed endpoints=11 blockwise=no-provider'), true);
assert.equal(progress.car_failed_events, 1);
assert.deepEqual(progress.failed_cids, ['bafyfailed']);
assert.equal(progress.last_cid, 'bafyfailed');
assert.match(progress.last_event_detail, /bafyfailed/);
assert.equal(updateCarProgressFromLine(progress, '[CAR LASSIE START] cid=bafyroot scope=all needed=bafychild delegated_multiaddrs=2'), true);
assert.equal(progress.lassie_starts, 1);
assert.equal(progress.last_cid, 'bafyroot');

const wrapper = fs.readFileSync('scripts/build-chronicle-sidechain-evidence.mjs', 'utf8');
assert.match(wrapper, /CHRONICLE_CAR_WHOLE_DAG_ENDPOINT_LIMIT/);
assert.match(wrapper, /configuredWholeDagEndpoints < 4/);

console.log('[CAR INTEGRITY TEST PASS] valid cache retained; incomplete DAG rejected; multi-gateway retry and white-box CAR telemetry verified');
