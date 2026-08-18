#!/usr/bin/env node
import assert from 'assert/strict';
import crypto from 'crypto';
import {
  cidBytesToString,
  cidStringToBytes,
  encodeVarint,
  fetchBlockwiseCar,
  parseCarStrict,
} from './ipfs-car-blockwise.mjs';

const sha = value => crypto.createHash('sha256').update(value).digest();
const cid = (codec, data) => Buffer.concat([Buffer.from([1, codec, 0x12, 0x20]), sha(data)]);
const field = (number, value) => Buffer.concat([Buffer.from([(number << 3) | 2]), encodeVarint(value.length), value]);
const link = (child, name) => field(2, Buffer.concat([field(1, child), field(2, Buffer.from(name))]));
const car = (root, entries) => {
  // The production parser deliberately treats the header as opaque and later requires
  // the expected root CID bytes to be present, matching the offline verifier boundary.
  const headerBody = Buffer.concat([Buffer.from([0xa1, 0x65]), Buffer.from('roots'), root]);
  const header = Buffer.concat([encodeVarint(headerBody.length), headerBody]);
  const sections = entries.map(({ cid: blockCid, data }) => {
    const body = Buffer.concat([blockCid, data]);
    return Buffer.concat([encodeVarint(body.length), body]);
  });
  return Buffer.concat([header, ...sections]);
};

const image = Buffer.from('historical image bytes');
const animation = Buffer.from('historical animation bytes');
const imageCid = cid(0x55, image);
const animationCid = cid(0x55, animation);
const rootData = Buffer.concat([link(imageCid, 'image.png'), link(animationCid, 'animation.mpga')]);
const rootCid = cid(0x70, rootData);
const cidV0 = Buffer.concat([Buffer.from([0x12, 0x20]), sha(Buffer.from('cid-v0 fixture'))]);
assert.ok(cidBytesToString(cidV0).startsWith('Qm'));
assert.deepEqual(cidStringToBytes(cidBytesToString(cidV0)), cidV0);

const source = new Map([
  [rootCid.toString('hex'), car(rootCid, [{ cid: rootCid, data: rootData }])],
  [imageCid.toString('hex'), car(imageCid, [{ cid: imageCid, data: image }])],
  [animationCid.toString('hex'), car(animationCid, [{ cid: animationCid, data: animation }])],
]);

const calls = [];
const result = await fetchBlockwiseCar({
  rootCid: cidBytesToString(rootCid),
  gateways: [
    'https://slow.invalid/ipfs/{cid}?format=car&dag-scope=all',
    'https://example.invalid/ipfs/{cid}?format=car&dag-scope=all',
  ],
  maxBytes: 1024 * 1024,
  concurrency: 2,
  fetchCar: async (url, context) => {
    calls.push({ url, context });
    if (context.gatewayIndex === 1) throw Error('fixture gateway unavailable');
    const bytes = source.get(context.cid === cidBytesToString(rootCid)
      ? rootCid.toString('hex')
      : context.cid === cidBytesToString(imageCid)
        ? imageCid.toString('hex')
        : animationCid.toString('hex'));
    if (!bytes) throw Error('fixture block absent');
    return bytes;
  },
});

assert.equal(result.blocks, 3);
assert.equal(result.reachable, 3);
assert.equal(result.requests, 4);
assert.equal(calls.length, 4);
assert.equal(calls.filter(call => call.context.gatewayIndex === 1).length, 1);
assert.ok(calls.every(call => call.url.includes('dag-scope=block')));
assert.ok(calls.every(call => call.context.scope === 'block'));
const parsed = parseCarStrict(result.buffer);
assert.deepEqual(new Set(parsed.blocks.map(block => block.key)), new Set(source.keys()));

const corrupt = Buffer.from(source.get(imageCid.toString('hex')));
corrupt[corrupt.length - 1] ^= 1;
await assert.rejects(
  fetchBlockwiseCar({
    rootCid: cidBytesToString(rootCid),
    gateways: ['https://example.invalid/ipfs/{cid}'],
    maxBytes: 1024 * 1024,
    fetchCar: async (_url, context) => context.cid === cidBytesToString(imageCid)
      ? corrupt
      : source.get(context.cid === cidBytesToString(rootCid)
        ? rootCid.toString('hex')
        : animationCid.toString('hex')),
  }),
  /block .* unavailable|block CID hash mismatch/,
);

console.log('[BLOCKWISE CAR TEST PASS] root + linked blocks merged and corruption rejected');
