// verify.mjs — verify btc-signature.json (address match + Schnorr verify)
import { schnorr } from '@noble/curves/secp256k1';
import * as bitcoin from 'bitcoinjs-lib';
import fs from 'fs';

const hexToBytes = (h) => Uint8Array.from(Buffer.from(h, 'hex'));

// 读取签名对象
const sigObj = JSON.parse(fs.readFileSync('btc-signature.json', 'utf8')).bitcoin_signature;

// 地址 → witness program（x-only 32B）
const { data: wp, version } = bitcoin.address.fromBech32(sigObj.address);
if (version !== 1 || wp.length !== 32) throw new Error('Address is not Taproot (v1/32B)');

// pubkey_xonly 必须与地址一致
if (Buffer.from(wp).toString('hex') !== sigObj.pubkey_xonly.toLowerCase()) {
  throw new Error('pubkey_xonly != address witness program');
}

// Schnorr 验证
const ok = await schnorr.verify(
  hexToBytes(sigObj.signature),
  hexToBytes(sigObj.message_sha256),
  hexToBytes(sigObj.pubkey_xonly)
);

console.log('address_match:', true);
console.log('verify_ok    :', ok);