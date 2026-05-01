/**
 * blake3-pure.mjs — Pure JavaScript BLAKE3 implementation
 *
 * Reference: https://github.com/BLAKE3-specs/BLAKE3
 */

const IV = new Uint32Array([
  0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
  0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19,
]);

const MSG_SCHEDULE = [
  [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
  [2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8],
  [3, 4, 10, 12, 13, 2, 7, 14, 6, 5, 9, 0, 11, 15, 8, 1],
  [10, 7, 12, 9, 14, 3, 13, 15, 4, 0, 11, 2, 5, 8, 1, 6],
  [12, 13, 9, 11, 15, 10, 14, 8, 7, 2, 5, 3, 0, 1, 6, 4],
  [9, 14, 11, 5, 8, 12, 15, 1, 13, 3, 0, 10, 2, 6, 4, 7],
  [11, 15, 5, 0, 1, 9, 8, 6, 14, 10, 2, 12, 3, 4, 7, 13],
];

function rotr32(x, n) { return ((x >>> n) | (x << (32 - n))) >>> 0; }

function g(s, a, b, c, d, mx, my) {
  s[a] = (s[a] + s[b] + mx) >>> 0;
  s[d] = rotr32(s[d] ^ s[a], 16);
  s[c] = (s[c] + s[d]) >>> 0;
  s[b] = rotr32(s[b] ^ s[c], 12);
  s[a] = (s[a] + s[b] + my) >>> 0;
  s[d] = rotr32(s[d] ^ s[a], 8);
  s[c] = (s[c] + s[d]) >>> 0;
  s[b] = rotr32(s[b] ^ s[c], 7);
}

function compress(cv, block, counter, blockLen, flags) {
  const s = new Uint32Array(16);
  s[0]  = cv[0]; s[1]  = cv[1]; s[2]  = cv[2]; s[3]  = cv[3];
  s[4]  = cv[4]; s[5]  = cv[5]; s[6]  = cv[6]; s[7]  = cv[7];
  s[8]  = IV[0]; s[9]  = IV[1]; s[10] = IV[2]; s[11] = IV[3];
  s[12] = counter >>> 0;
  s[13] = (counter / 0x100000000) >>> 0;
  s[14] = blockLen;
  s[15] = flags;

  for (let r = 0; r < 7; r++) {
    const m = MSG_SCHEDULE[r];
    g(s, 0, 4,  8, 12, block[m[ 0]], block[m[ 1]]);
    g(s, 1, 5,  9, 13, block[m[ 2]], block[m[ 3]]);
    g(s, 2, 6, 10, 14, block[m[ 4]], block[m[ 5]]);
    g(s, 3, 7, 11, 15, block[m[ 6]], block[m[ 7]]);
    g(s, 0, 5, 10, 15, block[m[ 8]], block[m[ 9]]);
    g(s, 1, 6, 11, 12, block[m[10]], block[m[11]]);
    g(s, 2, 7,  8, 13, block[m[12]], block[m[13]]);
    g(s, 3, 4,  9, 14, block[m[14]], block[m[15]]);
  }

  const out = new Uint32Array(16);
  for (let i = 0; i < 8; i++) {
    out[i]     = (cv[i] ^ s[i] ^ s[i + 8]) >>> 0;
    out[i + 8] = (IV[i] ^ s[i + 8]) >>> 0;
  }
  return out;
}

function outputChainingValue(out) {
  return new Uint32Array([out[0], out[1], out[2], out[3], out[4], out[5], out[6], out[7]]);
}

function wordsFromBytesLE(bytes, offset, count) {
  const w = new Uint32Array(count);
  for (let i = 0; i < count; i++) {
    const o = offset + i * 4;
    w[i] = (bytes[o] | (bytes[o+1] << 8) | (bytes[o+2] << 16) | (bytes[o+3] << 24)) >>> 0;
  }
  return w;
}

function parentCV(left, right, key, flags) {
  const block = new Uint32Array(16);
  block.set(left, 0);
  block.set(right, 8);
  const out = compress(key, block, 0, 64, flags | 4); // PARENT = 4
  return outputChainingValue(out);
}

const CHUNK_LEN = 1024;
const BLOCK_LEN = 64;

function chunkState(cv, chunkCounter, flags) {
  return { cv, buf: new Uint8Array(BLOCK_LEN), bufLen: 0, counter: chunkCounter, flags, blocksCompressed: 0 };
}

function chunkStateUpdate(cs, input) {
  let pos = 0;
  while (pos < input.length) {
    if (cs.bufLen === BLOCK_LEN) {
      const blockWords = wordsFromBytesLE(cs.buf, 0, 16);
      let blockFlags = cs.flags;
      if (cs.blocksCompressed === 0) blockFlags |= 1; // CHUNK_START
      const out = compress(cs.cv, blockWords, cs.counter, BLOCK_LEN, blockFlags);
      cs.cv = outputChainingValue(out);
      cs.blocksCompressed++;
      cs.bufLen = 0;
      cs.buf.fill(0);
    }
    const want = BLOCK_LEN - cs.bufLen;
    const take = Math.min(want, input.length - pos);
    cs.buf.set(input.subarray(pos, pos + take), cs.bufLen);
    cs.bufLen += take;
    pos += take;
  }
}

function chunkStateFinalize(cs) {
  const blockWords = wordsFromBytesLE(cs.buf, 0, 16);
  let blockFlags = cs.flags | 2; // CHUNK_END
  if (cs.blocksCompressed === 0) blockFlags |= 1; // CHUNK_START (single-block chunk)
  const out = compress(cs.cv, blockWords, cs.counter, cs.bufLen, blockFlags);
  return outputChainingValue(out);
}

function hashChunk(input, key, chunkCounter, flags) {
  const cs = chunkState(new Uint32Array(key), chunkCounter, flags);
  chunkStateUpdate(cs, input);
  return chunkStateFinalize(cs);
}

function hashRepeated(input, key, flags) {
  // Special case: repeated input pattern (not used in general case)
  return null;
}

/**
 * Compute BLAKE3 hash.
 * @param {Uint8Array|Buffer} data
 * @returns {Uint8Array} 32-byte hash
 */
export function blake3(data) {
  const input = data instanceof Uint8Array ? data : new Uint8Array(data);
  const key = new Uint32Array(IV);

  if (input.length <= CHUNK_LEN) {
    const out = hashChunk(input, key, 0, 8); // ROOT = 8
    const result = new Uint32Array(8);
    for (let i = 0; i < 8; i++) result[i] = out[i];
    return new Uint8Array(result.buffer);
  }

  // Build Merkle tree
  let cvs = [];
  let pos = 0;
  let chunkCounter = 0;
  while (pos < input.length) {
    const end = Math.min(pos + CHUNK_LEN, input.length);
    cvs.push(hashChunk(input.subarray(pos, end), key, chunkCounter, 0));
    pos = end;
    chunkCounter++;
  }

  // Reduce
  while (cvs.length > 1) {
    const parents = [];
    for (let i = 0; i < cvs.length; i += 2) {
      if (i + 1 < cvs.length) {
        parents.push(parentCV(cvs[i], cvs[i + 1], key, 0));
      } else {
        parents.push(cvs[i]);
      }
    }
    cvs = parents;
  }

  // Final root
  const block = new Uint32Array(16);
  block.set(cvs[0], 0);
  const rootOut = compress(key, block, 0, 32, 8); // ROOT
  const result = new Uint32Array(8);
  for (let i = 0; i < 8; i++) result[i] = rootOut[i];
  return new Uint8Array(result.buffer);
}

/**
 * Compute BLAKE3 hash and return hex string.
 * @param {Uint8Array|Buffer} data
 * @returns {string} 64-char hex string
 */
export function blake3hex(data) {
  return Buffer.from(blake3(data)).toString('hex');
}
