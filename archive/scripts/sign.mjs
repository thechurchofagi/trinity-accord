// sign.mjs — final: @noble/curves Schnorr + even-Y + TapTweak + direct witness match
import { secp256k1 as curve, schnorr } from '@noble/curves/secp256k1';
import * as bitcoin from 'bitcoinjs-lib';
import { randomBytes } from 'crypto';
import { sha256 as _sha256 } from '@noble/hashes/sha256';
import { utf8ToBytes } from '@noble/hashes/utils';
import fs from 'fs';

// 配置：签名对象与目标地址
const MANIFEST_SHA256_HEX = '41f95905e50cc699a7e6a3fcb0bd8633cf36170d3ef41170cd373467f8528b33';
const TARGET_ADDR = 'bc1ppmwvyxekh44m35x43k55z7r59nn33v8w2xmvu6s6ar4zyx57sxestxq0jf';

// 常量与工具
const CURVE_N = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141n;
const hexToBytes = (h) => Uint8Array.from(Buffer.from(h, 'hex'));
const bytesToHex = (b) => Buffer.from(b).toString('hex');
const bytesToNumberBE = (b) => BigInt('0x' + bytesToHex(b));
const numberToBytesBE = (num, len = 32) => {
  let hex = num.toString(16); if (hex.length % 2) hex = '0' + hex;
  if (hex.length > len * 2) throw new Error('number too large');
  return hexToBytes(hex.padStart(len * 2, '0'));
};
// BIP‑340 tagged hash
const taggedHash = (tag, ...msgs) => {
  const tagH = _sha256(utf8ToBytes(tag));
  const len = msgs.reduce((a, m) => a + m.length, 0);
  const buf = new Uint8Array(tagH.length * 2 + len);
  buf.set(tagH, 0); buf.set(tagH, tagH.length);
  let off = tagH.length * 2; for (const m of msgs) { buf.set(m, off); off += m.length; }
  return _sha256(buf);
};
// 偶数 Y 归一化（BIP‑340）
function evenYAdjustPriv(priv32) {
  const pub = curve.getPublicKey(priv32, true); // 33B: 0x02 偶, 0x03 奇
  const yOdd = pub[0] === 0x03;
  let p = bytesToNumberBE(priv32);
  if (yOdd) p = CURVE_N - p;
  return numberToBytesBE(p, 32);
}
// BIP‑86：无脚本路径 TapTweak 推导 tweaked 公私钥
function deriveTweaked(priv32) {
  const pEven = evenYAdjustPriv(priv32);
  const pubX = curve.getPublicKey(pEven, true).slice(1);       // x‑only 32B（偶数Y）
  const t = taggedHash('TapTweak', pubX);
  const tNum = bytesToNumberBE(t) % CURVE_N;
  const qNum = (bytesToNumberBE(pEven) + tNum) % CURVE_N;
  if (qNum === 0n) throw new Error('Invalid tweaked key');
  const tweakedPriv = numberToBytesBE(qNum, 32);
  const tweakedPubX = curve.getPublicKey(tweakedPriv, true).slice(1);
  return { tweakedPriv, tweakedPubX };
}

// 0) 载入 internal 私钥（64位 hex）
const PRIV_HEX = process.env.BTC_PRIV_HEX;
if (!PRIV_HEX || PRIV_HEX.length !== 64) throw new Error('Set BTC_PRIV_HEX as 32-byte hex');
const internalPriv = hexToBytes(PRIV_HEX);

// 1) 解析目标 Taproot 地址 → witness program（应为 32B x‑only tweaked pubkey）
const { data: wp, version } = bitcoin.address.fromBech32(TARGET_ADDR);
if (version !== 1 || wp.length !== 32) throw new Error('TARGET_ADDR is not Taproot (v1/32B)');

// 2) 推导 tweaked 公私钥，并与地址进行强一致性校验
const { tweakedPriv, tweakedPubX } = deriveTweaked(internalPriv);
console.log('target_wp_xonly   :', bytesToHex(wp));
console.log('derived_pubkey_x  :', bytesToHex(tweakedPubX));

if (bytesToHex(tweakedPubX) !== bytesToHex(wp)) {
  const derivedAddr = bitcoin.address.toBech32(Buffer.from(tweakedPubX), 1, bitcoin.networks.bitcoin.bech32);
  console.log('derived_addr       :', derivedAddr);
  console.log('target_addr        :', TARGET_ADDR);
  throw new Error('Tweaked pubkey mismatch: provided internal key does not correspond to TARGET_ADDR (BIP-86).');
}

// 3) Schnorr 签名（消息=manifest sha256 原始32B；可传入 auxRand）
const msg32 = hexToBytes(MANIFEST_SHA256_HEX);
const auxRand = randomBytes(32);
const sig = await schnorr.sign(msg32, tweakedPriv, auxRand);  // 64B
const ok = await schnorr.verify(sig, msg32, tweakedPubX);
if (!ok) throw new Error('Local verify failed');

const sigHex = bytesToHex(sig);
console.log('verify_ok         :', ok);
console.log('signature_hex     :', sigHex);
console.log('pubkey_xonly      :', bytesToHex(tweakedPubX));

// 4) 输出机读 JSON
const out = {
  bitcoin_signature: {
    method: 'bip340-taproot-xonly',
    address: TARGET_ADDR,
    message_sha256: MANIFEST_SHA256_HEX,
    pubkey_xonly: bytesToHex(tweakedPubX),
    signature: sigHex,
    boundary: 'non-amending; BTC originals prevail',
    created_at: new Date().toISOString(),
    tooling: { noble_curves: '>=1.0.0', noble_hashes: '>=1.0.0', bitcoinjs_lib: '>=6.0.0' }
  }
};
fs.writeFileSync('btc-signature.json', JSON.stringify(out, null, 2));
console.log('Wrote btc-signature.json');