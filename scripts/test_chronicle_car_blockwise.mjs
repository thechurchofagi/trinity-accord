#!/usr/bin/env node
import assert from 'assert/strict';
import crypto from 'crypto';
import {
  cidBytesToString,
  cidSha256Digest,
  cidStringToBytes,
  delegatedProviderMultiaddrs,
  encodeVarint,
  fetchBlockwiseCar,
  parseCarStrict,
  singleBlockCar,
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
assert.deepEqual(cidSha256Digest(cidBytesToString(imageCid)), sha(image));

const delegatedProviders = delegatedProviderMultiaddrs({
  Providers: [
    {
      ID: '12D3KooWCL2pXbQVaVnJntNZFNvz58PdY9gXo2R6NJajnDyhzxc4',
      Addrs: [
        '/ip6/2607:5300:60:7e71::/tcp/4001',
        '/ip4/158.69.25.113/udp/4001/quic-v1/webtransport/certhash/not-used',
        '/ip4/158.69.25.113/tcp/4001',
        '/ip4/158.69.25.113/udp/4001/quic-v1',
        '/dns4/provider.libp2p.direct/tcp/4001/tls/ws',
      ],
    },
    { ID: 'invalid peer id', Addrs: ['/ip4/127.0.0.1/tcp/4001'] },
  ],
});
assert.deepEqual(delegatedProviders, [
  '/ip4/158.69.25.113/tcp/4001/p2p/12D3KooWCL2pXbQVaVnJntNZFNvz58PdY9gXo2R6NJajnDyhzxc4',
  '/dns4/provider.libp2p.direct/tcp/4001/tls/ws/p2p/12D3KooWCL2pXbQVaVnJntNZFNvz58PdY9gXo2R6NJajnDyhzxc4',
  '/ip4/158.69.25.113/udp/4001/quic-v1/p2p/12D3KooWCL2pXbQVaVnJntNZFNvz58PdY9gXo2R6NJajnDyhzxc4',
  '/ip6/2607:5300:60:7e71::/tcp/4001/p2p/12D3KooWCL2pXbQVaVnJntNZFNvz58PdY9gXo2R6NJajnDyhzxc4',
]);
assert.deepEqual(delegatedProviderMultiaddrs({ Providers: 'not-an-array' }), []);
assert.throws(() => delegatedProviderMultiaddrs({}, { maxProviders: 0 }), /invalid maxProviders/);

const source = new Map([
  [rootCid.toString('hex'), car(rootCid, [{ cid: rootCid, data: rootData }])],
  [imageCid.toString('hex'), car(imageCid, [{ cid: imageCid, data: image }])],
  [animationCid.toString('hex'), car(animationCid, [{ cid: animationCid, data: animation }])],
]);

const rawWrapped = singleBlockCar(cidBytesToString(imageCid), image);
const rawParsed = parseCarStrict(rawWrapped);
assert.equal(rawParsed.blocks.length, 1);
assert.equal(rawParsed.blocks[0].key, imageCid.toString('hex'));
assert.deepEqual(rawParsed.blocks[0].data, image);
await assert.rejects(
  async () => singleBlockCar(cidBytesToString(imageCid), Buffer.from('wrong historical bytes')),
  /block CID hash mismatch/,
);

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

const raceCalls = [];
const raced = await fetchBlockwiseCar({
  rootCid: cidBytesToString(rootCid),
  gateways: [
    'https://slow.invalid/ipfs/{cid}',
    'https://fast.invalid/ipfs/{cid}',
  ],
  gatewayRace: 2,
  maxBytes: 1024 * 1024,
  concurrency: 2,
  fetchCar: async (_url, context) => {
    raceCalls.push(context);
    if (context.gatewayIndex === 1) {
      await new Promise(resolve => setTimeout(resolve, 40));
      throw Error('fixture slow gateway unavailable');
    }
    return source.get(context.cid === cidBytesToString(rootCid)
      ? rootCid.toString('hex')
      : context.cid === cidBytesToString(imageCid)
        ? imageCid.toString('hex')
        : animationCid.toString('hex'));
  },
});
assert.equal(raced.blocks, 3);
assert.equal(raced.requests, 6);
assert.equal(raceCalls.filter(call => call.gatewayIndex === 1).length, 3);
assert.equal(raceCalls.filter(call => call.gatewayIndex === 2).length, 3);

const blockCache = new Map();
await assert.rejects(
  fetchBlockwiseCar({
    rootCid: cidBytesToString(rootCid),
    gateways: ['https://example.invalid/ipfs/{cid}'],
    maxBytes: 1024 * 1024,
    concurrency: 2,
    loadBlock: async ({ key }) => blockCache.get(key) || null,
    saveBlock: async ({ key, buffer }) => blockCache.set(key, Buffer.from(buffer)),
    fetchCar: async (_url, context) => {
      if (context.cid === cidBytesToString(animationCid)) {
        await new Promise(resolve => setTimeout(resolve, 10));
        throw Error('fixture interrupted after partial progress');
      }
      return source.get(context.cid === cidBytesToString(rootCid)
        ? rootCid.toString('hex')
        : imageCid.toString('hex'));
    },
  }),
  /fixture interrupted after partial progress/,
);
assert.equal(blockCache.size, 2);

const resumedCalls = [];
const resumed = await fetchBlockwiseCar({
  rootCid: cidBytesToString(rootCid),
  gateways: ['https://example.invalid/ipfs/{cid}'],
  maxBytes: 1024 * 1024,
  concurrency: 2,
  loadBlock: async ({ key }) => blockCache.get(key) || null,
  saveBlock: async ({ key, buffer }) => blockCache.set(key, Buffer.from(buffer)),
  fetchCar: async (_url, context) => {
    resumedCalls.push(context.cid);
    if (context.cid !== cidBytesToString(animationCid)) throw Error(`unexpected resumed request ${context.cid}`);
    return source.get(animationCid.toString('hex'));
  },
});
assert.equal(resumed.blocks, 3);
assert.equal(resumed.cacheHits, 2);
assert.equal(resumed.requests, 1);
assert.deepEqual(resumedCalls, [cidBytesToString(animationCid)]);
assert.equal(blockCache.size, 3);

const fallbackCalls = [];
const fallbackCache = new Map();
const fallbackResult = await fetchBlockwiseCar({
  rootCid: cidBytesToString(rootCid),
  gateways: ['https://unavailable.invalid/ipfs/{cid}'],
  maxBytes: 1024 * 1024,
  concurrency: 2,
  saveBlock: async ({ key, buffer }) => fallbackCache.set(key, Buffer.from(buffer)),
  fetchCar: async () => {
    throw Error('fixture gateway unavailable');
  },
  fetchFallback: async context => {
    fallbackCalls.push(context);
    return source.get(context.cid === cidBytesToString(rootCid)
      ? rootCid.toString('hex')
      : context.cid === cidBytesToString(imageCid)
        ? imageCid.toString('hex')
        : animationCid.toString('hex'));
  },
});
assert.equal(fallbackResult.blocks, 3);
assert.equal(fallbackResult.requests, 6);
assert.equal(fallbackResult.fallbackRequests, 3);
assert.equal(fallbackResult.fallbackHits, 3);
assert.equal(fallbackCalls.length, 3);
assert.ok(fallbackCalls.every(call => call.scope === 'block'));
assert.equal(fallbackCache.size, 3);

const rootAwareCache = new Map([
  [rootCid.toString('hex'), source.get(rootCid.toString('hex'))],
  [imageCid.toString('hex'), source.get(imageCid.toString('hex'))],
]);
const fullDagCar = car(rootCid, [
  { cid: rootCid, data: rootData },
  { cid: imageCid, data: image },
  { cid: animationCid, data: animation },
]);
const rootAware = await fetchBlockwiseCar({
  rootCid: cidBytesToString(rootCid),
  gateways: ['https://unavailable.invalid/ipfs/{cid}'],
  maxBytes: 1024 * 1024,
  loadBlock: async ({ key }) => rootAwareCache.get(key) || null,
  saveBlock: async ({ key, buffer }) => rootAwareCache.set(key, Buffer.from(buffer)),
  fetchCar: async () => {
    throw Error('fixture gateway unavailable');
  },
  fetchFallback: async () => fullDagCar,
});
assert.equal(rootAware.blocks, 3);
assert.equal(rootAware.cacheHits, 2);
assert.equal(rootAware.requests, 2);
assert.equal(rootAware.fallbackRequests, 1);
assert.equal(rootAware.fallbackHits, 1);
assert.deepEqual(parseCarStrict(rootAwareCache.get(animationCid.toString('hex'))).blocks.map(block => block.key), [
  rootCid.toString('hex'),
  imageCid.toString('hex'),
  animationCid.toString('hex'),
]);

let invalidFallbackCacheWrites = 0;
await assert.rejects(
  fetchBlockwiseCar({
    rootCid: cidBytesToString(rootCid),
    gateways: ['https://unavailable.invalid/ipfs/{cid}'],
    maxBytes: 1024 * 1024,
    fetchCar: async () => {
      throw Error('fixture gateway unavailable');
    },
    fetchFallback: async () => source.get(imageCid.toString('hex')),
    saveBlock: async () => {
      invalidFallbackCacheWrites++;
    },
  }),
  /fallback: requested block absent/,
);
assert.equal(invalidFallbackCacheWrites, 0);

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
