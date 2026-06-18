#!/usr/bin/env node
/**
 * Upload a Waiting Heartbeat capsule to Arweave with readback verification.
 *
 * Usage:
 *   node scripts/arweave_upload_waiting_heartbeat_capsule.mjs \
 *     --payload record-chain/heartbeat/capsules/hwb-YYYYMMDD.capsule.json \
 *     --heartbeat-id hwb-YYYYMMDD \
 *     --out record-chain/heartbeat/capsules/hwb-YYYYMMDD.upload-result.json
 *
 * Env:
 *   ARKEY  — Arweave wallet JWK (JSON or base64-encoded)
 *   WAITING_HEARTBEAT_ARWEAVE_MAX_COST_AR — max upload cost in AR (default 0.001)
 */

import fs from "node:fs";
import crypto from "node:crypto";
import Arweave from "arweave";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function arg(name) {
  const idx = process.argv.indexOf(name);
  if (idx < 0 || idx + 1 >= process.argv.length) throw new Error(`Missing ${name}`);
  return process.argv[idx + 1];
}

function sha256Hex(value) {
  return crypto.createHash("sha256").update(value).digest("hex");
}

function parseArkey() {
  const value = process.env.ARKEY;
  if (!value) throw new Error("ARKEY missing");
  const text = value.trim();
  if (text.startsWith("{")) return JSON.parse(text);
  return JSON.parse(Buffer.from(text, "base64").toString("utf8"));
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

const WINSTON_PER_AR = 1_000_000_000_000n;

function arToWinston(ar) {
  const [whole, frac = ""] = String(ar).split(".");
  const fracPadded = frac.padEnd(12, "0").slice(0, 12);
  return BigInt(whole) * WINSTON_PER_AR + BigInt(fracPadded);
}

function winstonToArDecimal(winstonValue) {
  if (winstonValue == null) return null;
  const value = BigInt(String(winstonValue));
  const negative = value < 0n;
  const abs = negative ? -value : value;
  const whole = abs / WINSTON_PER_AR;
  const frac = abs % WINSTON_PER_AR;
  const fracString = frac.toString().padStart(12, "0");
  return `${negative ? "-" : ""}${whole.toString()}.${fracString}`;
}

async function safeBalance(arweave, address) {
  try {
    const winston = await arweave.wallets.getBalance(address);
    return {
      available: true,
      winston: String(winston),
      ar: winstonToArDecimal(winston),
      reason: null,
    };
  } catch (err) {
    return { available: false, winston: null, ar: null, reason: err.message };
  }
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

const payloadPath = arg("--payload");
const heartbeatId = arg("--heartbeat-id");
const outPath = arg("--out");
const maxCostAr = parseFloat(process.env.WAITING_HEARTBEAT_ARWEAVE_MAX_COST_AR || "0.001");

const jwk = parseArkey();
for (const field of ["kty", "n", "e", "d"]) {
  if (!jwk[field]) throw new Error(`ARKEY JWK missing ${field}`);
}
if (jwk.kty !== "RSA") throw new Error("ARKEY JWK kty must be RSA");

const payload = fs.readFileSync(payloadPath);
const payloadSha256 = sha256Hex(payload);

const arweave = Arweave.init({
  host: "arweave.net",
  port: 443,
  protocol: "https",
  timeout: 60000,
  logging: false,
});

const address = await arweave.wallets.jwkToAddress(jwk);
const balanceBefore = await safeBalance(arweave, address);

console.log(`ARWEAVE_CAPSULE_UPLOAD heartbeat=${heartbeatId} size=${payload.length} sha256=${payloadSha256}`);
console.log(`ARWEAVE_WALLET address=${address} balance=${balanceBefore.ar ?? "unknown"} AR`);

// --- Cost gate ---
const price = await arweave.transactions.getPrice(payload.length);
const uploadCostWinston = String(price);
const uploadCostAr = winstonToArDecimal(price);
const maxCostWinston = arToWinston(maxCostAr);

if (BigInt(price) > maxCostWinston) {
  console.error(`ARWEAVE_COST_EXCEEDED cost=${uploadCostAr} AR max=${maxCostAr} AR`);
  const result = {
    schema: "trinityaccord.waiting-heartbeat-arweave-upload-result.v1",
    heartbeat_id: heartbeatId,
    status: "cost_exceeded",
    attempted_at: new Date().toISOString(),
    payload_sha256: payloadSha256,
    upload_cost_winston: uploadCostWinston,
    upload_cost_ar: uploadCostAr,
    max_cost_ar: String(maxCostAr),
    boundary: {
      arweave_archive_is_mirror_only: true,
      arweave_archive_is_not_authority: true,
    },
  };
  fs.writeFileSync(outPath, JSON.stringify(result, null, 2) + "\n");
  process.exit(0);
}

// --- Upload ---
const tx = await arweave.createTransaction({ data: payload }, jwk);
tx.addTag("Content-Type", "application/json");
tx.addTag("App-Name", "Trinity-Accord");
tx.addTag("Archive-Type", "waiting-heartbeat-capsule");
tx.addTag("Heartbeat-ID", heartbeatId);
tx.addTag("Data-SHA256", payloadSha256);
tx.addTag("Boundary", "mirror-not-authority");

await arweave.transactions.sign(tx, jwk);
const uploader = await arweave.transactions.getUploader(tx);

while (!uploader.isComplete) {
  await uploader.uploadChunk();
  console.log(`ARWEAVE_UPLOAD_CHUNK pct=${uploader.pctComplete}`);
}

console.log(`ARWEAVE_UPLOAD_POSTED txid=${tx.id}`);

function uploadResult(status, readbackSha256, hashMatch, retryable) {
  const balanceAfter = { available: false, winston: null, ar: null, reason: "pending" };
  return {
    schema: "trinityaccord.waiting-heartbeat-arweave-upload-result.v1",
    heartbeat_id: heartbeatId,
    status,
    attempted_at: new Date().toISOString(),
    arweave_txid: tx.id,
    payload_sha256: payloadSha256,
    data_sha256: payloadSha256,
    readback_sha256: readbackSha256,
    hash_match: hashMatch,
    retryable,
    wallet_address_sha256: sha256Hex(address),
    wallet_balance_before_available: balanceBefore.available,
    wallet_balance_before_winston: balanceBefore.winston,
    wallet_balance_before_ar: balanceBefore.ar,
    wallet_balance_after_available: balanceAfter.available,
    wallet_balance_after_reason: balanceAfter.reason,
    wallet_balance_after_winston: balanceAfter.winston,
    wallet_balance_after_ar: balanceAfter.ar,
    upload_cost_winston: uploadCostWinston,
    upload_cost_ar: uploadCostAr,
    tags: {
      "Content-Type": "application/json",
      "App-Name": "Trinity-Accord",
      "Archive-Type": "waiting-heartbeat-capsule",
      "Heartbeat-ID": heartbeatId,
      "Data-SHA256": payloadSha256,
      Boundary: "mirror-not-authority",
    },
    boundary: {
      arweave_archive_is_mirror_only: true,
      arweave_archive_is_not_authority: true,
      arweave_archive_is_not_attestation: true,
      arweave_archive_is_not_amendment: true,
      arweave_archive_is_not_successor_reception: true,
      bitcoin_originals_prevail: true,
    },
  };
}

fs.writeFileSync(outPath, JSON.stringify(uploadResult("posted_pending_readback", null, false, true), null, 2) + "\n");

// --- Readback verification ---
const READBACK_MAX_RETRIES = 30;
const READBACK_DELAY_MS = 15000;
let readbackSha256 = null;
let readbackVerified = false;

for (let attempt = 1; attempt <= READBACK_MAX_RETRIES; attempt++) {
  try {
    console.log(`ARWEAVE_READBACK attempt ${attempt}/${READBACK_MAX_RETRIES} txid=${tx.id}`);
    const readbackData = await arweave.transactions.getData(tx.id, { decode: true, string: false });
    const readbackBuf = Buffer.from(readbackData);
    readbackSha256 = sha256Hex(readbackBuf);
    readbackVerified = readbackSha256 === payloadSha256;
    if (readbackVerified) {
      console.log(`ARWEAVE_READBACK_OK readback_sha256=${readbackSha256}`);
      break;
    } else {
      console.error(`ARWEAVE_READBACK_MISMATCH attempt=${attempt} payload=${payloadSha256} readback=${readbackSha256}`);
    }
  } catch (err) {
    console.error(`ARWEAVE_READBACK_RETRY attempt=${attempt} error=${err.message}`);
  }
  if (attempt < READBACK_MAX_RETRIES) await sleep(READBACK_DELAY_MS);
}

if (!readbackVerified) {
  fs.writeFileSync(outPath, JSON.stringify(uploadResult("readback_failed", readbackSha256, false, true), null, 2) + "\n");
  throw new Error(`ARWEAVE_READBACK_FAILED after ${READBACK_MAX_RETRIES} attempts`);
}

// --- Update balance after ---
const balanceAfter = await safeBalance(arweave, address);
const actualDeltaWinston = balanceBefore.available && balanceAfter.available
  ? String(BigInt(balanceBefore.winston) - BigInt(balanceAfter.winston))
  : null;
const actualDeltaAr = actualDeltaWinston ? winstonToArDecimal(actualDeltaWinston) : null;

const result = uploadResult("uploaded", readbackSha256, true, false);
result.wallet_balance_after_available = balanceAfter.available;
result.wallet_balance_after_winston = balanceAfter.winston;
result.wallet_balance_after_ar = balanceAfter.ar;
result.wallet_balance_after_reason = balanceAfter.reason;
result.actual_delta_winston = actualDeltaWinston;
result.actual_delta_ar = actualDeltaAr;

fs.writeFileSync(outPath, JSON.stringify(result, null, 2) + "\n");
console.log(`ARWEAVE_UPLOAD_OK txid=${tx.id} sha256=${payloadSha256} readback_sha256=${readbackSha256} hash_match=true`);
