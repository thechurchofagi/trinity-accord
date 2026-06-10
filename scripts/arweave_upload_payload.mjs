#!/usr/bin/env node
import fs from "node:fs";
import crypto from "node:crypto";
import Arweave from "arweave";

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
      reason: null
    };
  } catch (err) {
    return {
      available: false,
      winston: null,
      ar: null,
      reason: err.message
    };
  }
}

const payloadPath = arg("--payload");
const outPath = arg("--out");

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

const tx = await arweave.createTransaction({ data: payload }, jwk);

tx.addTag("Content-Type", "application/json");
tx.addTag("App-Name", "Trinity-Accord");
tx.addTag("Record-Chain", "trinity-accord-public-reception-ledger");
tx.addTag("Archive-Type", "record-chain-batch-archive");
tx.addTag("Data-SHA256", payloadSha256);
tx.addTag("Boundary", "mirror-not-authority");

const uploadCostWinston = String(tx.reward);
const uploadCostAr = winstonToArDecimal(uploadCostWinston);

await arweave.transactions.sign(tx, jwk);

const response = await arweave.transactions.post(tx);
if (response.status < 200 || response.status >= 300) {
  throw new Error(`Arweave post failed: ${response.status} ${response.statusText}`);
}

const balanceAfter = await safeBalance(arweave, address);

let actualDeltaWinston = null;
let actualDeltaAr = null;
if (
  balanceBefore.winston &&
  balanceAfter.winston &&
  /^\d+$/.test(balanceBefore.winston) &&
  /^\d+$/.test(balanceAfter.winston)
) {
  actualDeltaWinston = (BigInt(balanceBefore.winston) - BigInt(balanceAfter.winston)).toString();
  actualDeltaAr = winstonToArDecimal(actualDeltaWinston);
}

function uploadResult(result, readbackSha256, hashMatch, retryable) {
  return {
    schema: "trinityaccord.arweave-upload-result.v1",
    result,
    txid: tx.id,
    tx_id: tx.id,
    uploaded_at: new Date().toISOString(),
    data_sha256: payloadSha256,
    payload_sha256: payloadSha256,
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
    actual_delta_winston: actualDeltaWinston,
    actual_delta_ar: actualDeltaAr,
    tags: {
      "Content-Type": "application/json",
      "App-Name": "Trinity-Accord",
      "Record-Chain": "trinity-accord-public-reception-ledger",
      "Archive-Type": "record-chain-batch-archive",
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
    const readbackData = await arweave.transactions.getData(tx.id, {
      decode: true,
      string: false,
    });
    const readbackBuf = Buffer.from(readbackData);
    readbackSha256 = sha256Hex(readbackBuf);
    readbackVerified = readbackSha256 === payloadSha256;
    if (readbackVerified) {
      console.log(`ARWEAVE_READBACK_OK readback_sha256=${readbackSha256}`);
      break;
    } else {
      console.error(
        `ARWEAVE_READBACK_MISMATCH attempt=${attempt} payload=${payloadSha256} readback=${readbackSha256}`
      );
    }
  } catch (err) {
    console.error(`ARWEAVE_READBACK_RETRY attempt=${attempt} error=${err.message}`);
  }
  if (attempt < READBACK_MAX_RETRIES) {
    await sleep(READBACK_DELAY_MS);
  }
}

if (!readbackVerified) {
  fs.writeFileSync(outPath, JSON.stringify(uploadResult("readback_failed", readbackSha256, false, true), null, 2) + "\n");
  throw new Error(
    `ARWEAVE_READBACK_FAILED after ${READBACK_MAX_RETRIES} attempts: hash_match=false payload_sha256=${payloadSha256} readback_sha256=${readbackSha256}`
  );
}

const result = uploadResult("uploaded", readbackSha256, true, false);
fs.writeFileSync(outPath, JSON.stringify(result, null, 2) + "\n");
console.log(`ARWEAVE_UPLOAD_OK txid=${tx.id} data_sha256=${payloadSha256} readback_sha256=${readbackSha256} hash_match=${readbackVerified}`);
