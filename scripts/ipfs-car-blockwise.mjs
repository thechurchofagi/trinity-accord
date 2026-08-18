import crypto from 'crypto';

const SHA256_CODE = 0x12;
const DAG_PB_CODEC = 0x70;
const RAW_CODEC = 0x55;
const B32 = 'abcdefghijklmnopqrstuvwxyz234567';
const B58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz';

export function readVarintStrict(buf, offset, label = 'varint') {
  let value = 0;
  let shift = 0;
  let pos = offset;
  for (let i = 0; i < 10; i++) {
    if (pos >= buf.length) throw Error(`truncated ${label}`);
    const byte = buf[pos++];
    value += (byte & 0x7f) * (2 ** shift);
    if (!Number.isSafeInteger(value)) throw Error(`unsafe ${label}`);
    if (byte < 0x80) return { value, next: pos };
    shift += 7;
  }
  throw Error(`overlong ${label}`);
}

export function encodeVarint(value) {
  if (!Number.isSafeInteger(value) || value < 0) throw Error(`invalid varint value ${value}`);
  const out = [];
  let n = value;
  do {
    let byte = n % 128;
    n = Math.floor(n / 128);
    if (n) byte |= 0x80;
    out.push(byte);
  } while (n);
  return Buffer.from(out);
}

function parseCidAt(buf, offset) {
  if (offset + 34 <= buf.length && buf[offset] === SHA256_CODE && buf[offset + 1] === 32) {
    return {
      bytes: buf.subarray(offset, offset + 34),
      next: offset + 34,
      version: 0,
      codec: DAG_PB_CODEC,
      multihashCode: SHA256_CODE,
      digest: buf.subarray(offset + 2, offset + 34),
    };
  }
  const version = readVarintStrict(buf, offset, 'CID version');
  if (version.value !== 1) throw Error(`unsupported CID version ${version.value}`);
  const codec = readVarintStrict(buf, version.next, 'CID codec');
  const multihashCode = readVarintStrict(buf, codec.next, 'CID multihash code');
  const digestLength = readVarintStrict(buf, multihashCode.next, 'CID digest length');
  const end = digestLength.next + digestLength.value;
  if (end > buf.length) throw Error('truncated CID digest');
  return {
    bytes: buf.subarray(offset, end),
    next: end,
    version: 1,
    codec: codec.value,
    multihashCode: multihashCode.value,
    digest: buf.subarray(digestLength.next, end),
  };
}

function base32Encode(buf) {
  let value = 0;
  let bits = 0;
  let out = '';
  for (const byte of buf) {
    value = (value << 8) | byte;
    bits += 8;
    while (bits >= 5) {
      out += B32[(value >>> (bits - 5)) & 31];
      bits -= 5;
      value &= (1 << bits) - 1;
    }
  }
  if (bits) out += B32[(value << (5 - bits)) & 31];
  return out;
}

function base32Decode(value) {
  let acc = 0;
  let bits = 0;
  const out = [];
  for (const char of value.toLowerCase()) {
    const n = B32.indexOf(char);
    if (n < 0) throw Error(`invalid base32 character ${char}`);
    acc = (acc << 5) | n;
    bits += 5;
    if (bits >= 8) {
      out.push((acc >>> (bits - 8)) & 255);
      bits -= 8;
      acc &= (1 << bits) - 1;
    }
  }
  return Buffer.from(out);
}

function base58Encode(buf) {
  const digits = [0];
  for (const byte of buf) {
    let carry = byte;
    for (let i = 0; i < digits.length; i++) {
      const n = digits[i] * 256 + carry;
      digits[i] = n % 58;
      carry = Math.floor(n / 58);
    }
    while (carry) {
      digits.push(carry % 58);
      carry = Math.floor(carry / 58);
    }
  }
  let out = '';
  for (let i = 0; i < buf.length - 1 && buf[i] === 0; i++) out += '1';
  return out + digits.reverse().map(x => B58[x]).join('');
}

function base58Decode(value) {
  const bytes = [0];
  for (const char of value) {
    const n = B58.indexOf(char);
    if (n < 0) throw Error(`invalid base58 character ${char}`);
    let carry = n;
    for (let i = 0; i < bytes.length; i++) {
      const v = bytes[i] * 58 + carry;
      bytes[i] = v & 255;
      carry = v >>> 8;
    }
    while (carry) {
      bytes.push(carry & 255);
      carry >>>= 8;
    }
  }
  for (let i = 0; i < value.length - 1 && value[i] === '1'; i++) bytes.push(0);
  return Buffer.from(bytes.reverse());
}

export function cidBytesToString(bytes) {
  const cid = Buffer.from(bytes);
  if (cid.length === 34 && cid[0] === SHA256_CODE && cid[1] === 32) return base58Encode(cid);
  const parsed = parseCidAt(cid, 0);
  if (parsed.next !== cid.length) throw Error('trailing CID bytes');
  return `b${base32Encode(cid)}`;
}

export function cidStringToBytes(value) {
  if (typeof value !== 'string' || !value) throw Error('CID string is required');
  if (value.startsWith('Qm')) return base58Decode(value);
  if (value[0]?.toLowerCase() === 'b') return base32Decode(value.slice(1));
  throw Error(`unsupported CID multibase ${value[0] || '(empty)'}`);
}

function verifyBlock(block) {
  if (block.multihashCode !== SHA256_CODE || block.digest.length !== 32) {
    throw Error(`unsupported block multihash code=${block.multihashCode} bytes=${block.digest.length}`);
  }
  const actual = crypto.createHash('sha256').update(block.data).digest();
  if (!actual.equals(block.digest)) throw Error(`block CID hash mismatch ${block.key}`);
  if (block.codec !== DAG_PB_CODEC && block.codec !== RAW_CODEC) {
    throw Error(`unsupported block codec ${block.codec}`);
  }
}

export function parseCarStrict(input) {
  const buf = Buffer.from(input);
  const headerLength = readVarintStrict(buf, 0, 'CAR header length');
  if (headerLength.value <= 0) throw Error(`invalid CAR header length ${headerLength.value}`);
  const headerEnd = headerLength.next + headerLength.value;
  if (headerEnd > buf.length) throw Error('CAR header exceeds input');
  const blocks = [];
  let pos = headerEnd;
  while (pos < buf.length) {
    const sectionStart = pos;
    const sectionLength = readVarintStrict(buf, pos, `CAR block ${blocks.length} length`);
    if (sectionLength.value <= 0) throw Error(`invalid CAR block length ${sectionLength.value}`);
    const payloadStart = sectionLength.next;
    const sectionEnd = payloadStart + sectionLength.value;
    if (sectionEnd > buf.length) throw Error(`CAR block ${blocks.length} exceeds input`);
    const cid = parseCidAt(buf, payloadStart);
    if (cid.next > sectionEnd) throw Error(`CAR block ${blocks.length} CID exceeds section`);
    const block = {
      ...cid,
      key: cid.bytes.toString('hex'),
      data: buf.subarray(cid.next, sectionEnd),
      section: buf.subarray(sectionStart, sectionEnd),
    };
    verifyBlock(block);
    blocks.push(block);
    pos = sectionEnd;
  }
  return { header: buf.subarray(0, headerEnd), blocks };
}

export function dagPbLinks(data) {
  const out = [];
  let pos = 0;
  while (pos < data.length) {
    const key = readVarintStrict(data, pos, 'DAG-PB field key');
    pos = key.next;
    const field = key.value >>> 3;
    const wire = key.value & 7;
    if (wire === 2) {
      const length = readVarintStrict(data, pos, 'DAG-PB field length');
      pos = length.next;
      const end = pos + length.value;
      if (end > data.length) throw Error('truncated DAG-PB field');
      if (field === 2) {
        const link = data.subarray(pos, end);
        let linkPos = 0;
        while (linkPos < link.length) {
          const linkKey = readVarintStrict(link, linkPos, 'DAG-PB link key');
          linkPos = linkKey.next;
          const linkField = linkKey.value >>> 3;
          const linkWire = linkKey.value & 7;
          if (linkWire === 2) {
            const linkLength = readVarintStrict(link, linkPos, 'DAG-PB link field length');
            linkPos = linkLength.next;
            const linkEnd = linkPos + linkLength.value;
            if (linkEnd > link.length) throw Error('truncated DAG-PB link field');
            if (linkField === 1) out.push(Buffer.from(link.subarray(linkPos, linkEnd)));
            linkPos = linkEnd;
          } else if (linkWire === 0) {
            linkPos = readVarintStrict(link, linkPos, 'DAG-PB link integer').next;
          } else if (linkWire === 1) {
            linkPos += 8;
          } else if (linkWire === 5) {
            linkPos += 4;
          } else {
            throw Error(`unsupported DAG-PB link wire type ${linkWire}`);
          }
          if (linkPos > link.length) throw Error('truncated DAG-PB link value');
        }
      }
      pos = end;
    } else if (wire === 0) {
      pos = readVarintStrict(data, pos, 'DAG-PB integer').next;
    } else if (wire === 1) {
      pos += 8;
    } else if (wire === 5) {
      pos += 4;
    } else {
      throw Error(`unsupported DAG-PB wire type ${wire}`);
    }
    if (pos > data.length) throw Error('truncated DAG-PB value');
  }
  return out;
}

export function carScopeUrl(template, cid, scope) {
  const replaced = template.includes('{cid}')
    ? template.replaceAll('{cid}', encodeURIComponent(cid))
    : `${template.replace(/\/$/, '')}/ipfs/${encodeURIComponent(cid)}`;
  const url = new URL(replaced);
  url.searchParams.set('format', 'car');
  url.searchParams.set('dag-scope', scope);
  url.searchParams.delete('entity-bytes');
  return url.toString();
}

function semaphore(limit) {
  let active = 0;
  const waiting = [];
  const release = () => {
    active--;
    waiting.shift()?.();
  };
  return async fn => {
    if (active >= limit) await new Promise(resolve => waiting.push(resolve));
    active++;
    try {
      return await fn();
    } finally {
      release();
    }
  };
}

export async function fetchBlockwiseCar({
  rootCid,
  gateways,
  fetchCar,
  maxBytes,
  concurrency = 2,
  maxBlocks = 4096,
  gatewayRace = 1,
  loadBlock = null,
  saveBlock = null,
}) {
  if (!Array.isArray(gateways) || gateways.length === 0) throw Error('at least one CAR gateway is required');
  if (typeof fetchCar !== 'function') throw Error('fetchCar callback is required');
  if (!Number.isSafeInteger(maxBytes) || maxBytes <= 0) throw Error(`invalid maxBytes ${maxBytes}`);
  if (!Number.isInteger(concurrency) || concurrency < 1 || concurrency > 16) throw Error(`invalid concurrency ${concurrency}`);
  if (!Number.isInteger(maxBlocks) || maxBlocks < 1) throw Error(`invalid maxBlocks ${maxBlocks}`);
  if (!Number.isInteger(gatewayRace) || gatewayRace < 1 || gatewayRace > gateways.length) {
    throw Error(`invalid gatewayRace ${gatewayRace}`);
  }
  if (loadBlock !== null && typeof loadBlock !== 'function') throw Error('loadBlock must be a function');
  if (saveBlock !== null && typeof saveBlock !== 'function') throw Error('saveBlock must be a function');

  const rootBytes = cidStringToBytes(rootCid);
  const rootKey = rootBytes.toString('hex');
  const blocks = new Map();
  const tasks = new Map();
  const limit = semaphore(concurrency);
  let header = null;
  let totalBytes = 0;
  let requestCount = 0;
  let cacheHitCount = 0;
  let cacheWriteCount = 0;
  let preferredGateway = 0;

  function addBlock(block) {
    const prior = blocks.get(block.key);
    if (prior) {
      if (!prior.data.equals(block.data)) throw Error(`conflicting duplicate block ${block.key}`);
      return;
    }
    if (blocks.size >= maxBlocks) throw Error(`CAR block count exceeds cap ${maxBlocks}`);
    totalBytes += block.section.length;
    if (totalBytes > maxBytes) throw Error(`CAR block bytes exceed cap ${maxBytes}`);
    blocks.set(block.key, block);
  }

  function parseRequestedBlock(response, cidBytes, cid, source) {
    const parsed = parseCarStrict(response);
    const target = parsed.blocks.find(block => block.key === cidBytes.toString('hex'));
    if (!target) throw Error(`requested block absent for ${cid} from ${source}`);
    return parsed;
  }

  async function fetchOne(cidBytes) {
    const cid = cidBytesToString(cidBytes);
    const key = cidBytes.toString('hex');
    if (loadBlock) {
      try {
        const cached = await loadBlock({ cid, key });
        if (cached) {
          const parsed = parseRequestedBlock(cached, cidBytes, cid, 'cache');
          cacheHitCount++;
          return { ...parsed, gatewayIndex: null, url: null, cached: true };
        }
      } catch (error) {
        console.warn(`[CAR BLOCK CACHE REJECTED] cid=${cid} ${error.message}`);
      }
    }

    const errors = [];
    const order = [preferredGateway, ...gateways.map((_, i) => i).filter(i => i !== preferredGateway)];
    const attempt = async i => {
      const url = carScopeUrl(gateways[i], cid, 'block');
      try {
        requestCount++;
        const response = await fetchCar(url, { cid, scope: 'block', gatewayIndex: i + 1 });
        const parsed = parseRequestedBlock(response, cidBytes, cid, `gateway ${i + 1}`);
        return { parsed, response: Buffer.from(response), gatewayIndex: i + 1, gatewayOffset: i, url };
      } catch (error) {
        throw Error(`gateway ${i + 1}: ${error.message}`);
      }
    };

    for (let start = 0; start < order.length; start += gatewayRace) {
      const batch = order.slice(start, start + gatewayRace);
      let winner;
      try {
        winner = await Promise.any(batch.map(attempt));
      } catch (error) {
        const batchErrors = error instanceof AggregateError ? error.errors : [error];
        errors.push(...batchErrors.map(item => item.message));
        continue;
      }
      if (saveBlock) {
        await saveBlock({ cid, key, buffer: winner.response });
        cacheWriteCount++;
      }
      preferredGateway = winner.gatewayOffset;
      return { ...winner.parsed, gatewayIndex: winner.gatewayIndex, url: winner.url };
    }
    throw Error(`block ${cid} unavailable from ${gateways.length} gateways: ${errors.join('; ')}`);
  }

  function visit(cidBytes, isRoot = false) {
    const key = cidBytes.toString('hex');
    if (tasks.has(key)) return tasks.get(key);
    const task = (async () => {
      const parsed = await limit(() => fetchOne(cidBytes));
      if (isRoot) {
        if (!parsed.header.includes(rootBytes)) throw Error('root CID absent from block CAR header');
        header = Buffer.from(parsed.header);
      }
      for (const block of parsed.blocks) addBlock(block);
      const target = blocks.get(key);
      if (!target) throw Error(`requested block not retained ${cidBytesToString(cidBytes)}`);
      const links = target.codec === DAG_PB_CODEC ? dagPbLinks(target.data) : [];
      await Promise.all(links.map(link => visit(link)));
    })();
    tasks.set(key, task);
    return task;
  }

  await visit(rootBytes, true);
  if (!header) throw Error('root CAR header was not captured');
  if (!blocks.has(rootKey)) throw Error('root block is missing after blockwise retrieval');

  const ordered = [blocks.get(rootKey), ...[...blocks.values()]
    .filter(block => block.key !== rootKey)
    .sort((a, b) => a.key.localeCompare(b.key))];
  const car = Buffer.concat([header, ...ordered.map(block => block.section)]);
  if (car.length > maxBytes) throw Error(`assembled CAR exceeds cap ${maxBytes}`);

  const verified = parseCarStrict(car);
  const verifiedBlocks = new Map(verified.blocks.map(block => [block.key, block]));
  const reachable = new Set();
  const stack = [rootKey];
  while (stack.length) {
    const key = stack.pop();
    if (reachable.has(key)) continue;
    const block = verifiedBlocks.get(key);
    if (!block) throw Error(`assembled CAR linked block missing ${key}`);
    reachable.add(key);
    if (block.codec === DAG_PB_CODEC) {
      for (const link of dagPbLinks(block.data)) stack.push(link.toString('hex'));
    }
  }
  if (reachable.size !== verifiedBlocks.size) throw Error('assembled CAR contains unreachable blocks');

  return {
    buffer: car,
    blocks: verifiedBlocks.size,
    reachable: reachable.size,
    requests: requestCount,
    cacheHits: cacheHitCount,
    cacheWrites: cacheWriteCount,
  };
}
