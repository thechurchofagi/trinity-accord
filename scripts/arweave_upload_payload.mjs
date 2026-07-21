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

function envInt(name, fallback, minimum) {
  const raw = process.env[name];
  const value = raw == null || raw === "" ? fallback : Number.parseInt(raw, 10);
  if (!Number.isInteger(value) || value < minimum) {
    throw new Error(`${name} must be an integer >= ${minimum}`);
  }
  return value;
}

function readExistingResult(path) {
  if (!fs.existsSync(path)) return null;
  try {
    const parsed = JSON.parse(fs.readFileSync(path, "utf8"));
    return parsed && typeof parsed === "object" && !Array.isArray(parsed) ? parsed : null;
  } catch (err) {
    throw new Error(`Existing upload result is not valid JSON: ${err.message}`);
  }
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
      reason: null,
    };
  } catch (err) {
    return {
      available: false,
      winston: null,
      ar: null,
      reason: err.message,
    };
  }
}

const payloadPath = arg("--payload");
const outPath = arg("--out");
const payload = fs.readFileSync(payloadPath);
const payloadSha256 = sha256Hex(payload);

const HTTP_TIMEOUT_MS = envInt("ARWEAVE_HTTP_TIMEOUT_MS", 30000, 5000);
const READBACK_MAX_RETRIES = envInt("ARWEAVE_READBACK_MAX_RETRIES", 30, 1);
const READBACK_DELAY_MS = envInt("ARWEAVE_READBACK_DELAY_MS", 10000, 0);
const READBACK_MAX_SECONDS = envInt("ARWEAVE_READBACK_MAX_SECONDS", 420, 30);

const jwk = parseArkey();
for (const field of ["kty", "n", "e", "d"]) {
  if (!jwk[field]) throw new Error(`ARKEY JWK missing ${field}`);
}
if (jwk.kty !== "RSA") throw new Error("ARKEY JWK kty must be RSA");

const arweave = Arweave.init({
  host: "arweave.net",
  port: 443,
  protocol: "https",
  timeout: HTTP_TIMEOUT_MS,
  logging: false,
});

const address = await arweave.wallets.jwkToAddress(jwk);
const walletAddressSha256 = sha256Hex(address);
const existing = readExistingResult(outPath);

let txId = null;
let uploadedAt = null;
let uploadCostWinston = null;
let uploadCostAr = null;
let balanceBefore = {
  available: false,
  winston: null,
  ar: null,
  reason: "not checked",
};
let balanceAfter = {
  available: false,
  winston: null,
  ar: null,
  reason: "not checked",
};
let actualDeltaWinston = null;
let actualDeltaAr = null;
let resumedFromCheckpoint = false;

function uploadResult(result, readbackSha256, hashMatch, retryable) {
  return {
    schema: "trinityaccord.arweave-upload-result.v1",
    result,
    txid: txId,
    tx_id: txId,
    uploaded_at: uploadedAt,
    data_sha256: payloadSha256,
    payload_sha256: payloadSha256,
    readback_sha256: readbackSha256,
    hash_match: hashMatch,
    retryable,
    resumed_from_checkpoint: resumedFromCheckpoint,
    wallet_address_sha256: walletAddressSha256,
    wallet_balance_before_available: balanceBefore.available,
    wallet_balance_before_reason: balanceBefore.reason,
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

function writeResult(result, readbackSha256, hashMatch, retryable) {
  fs.writeFileSync(
    outPath,
    JSON.stringify(uploadResult(result, readbackSha256, hashMatch, retryable), null, 2) + "\n"
  );
}

if (existing && (existing.txid || existing.tx_id)) {
  const existingTxId = existing.txid || existing.tx_id;
  const existingPayloadSha = existing.payload_sha256 || existing.data_sha256;
  if (existingPayloadSha !== payloadSha256) {
    throw new Error(
      `Refusing to resume transaction ${existingTxId}: checkpoint payload sha256 ` +
        `${existingPayloadSha} does not match local payload ${payloadSha256}`
    );
  }

  txId = existingTxId;
  uploadedAt = existing.uploaded_at || new Date().toISOString();
  uploadCostWinston = existing.upload_cost_winston ?? null;
  uploadCostAr = existing.upload_cost_ar ?? null;
  actualDeltaWinston = existing.actual_delta_winston ?? null;
  actualDeltaAr = existing.actual_delta_ar ?? null;
  balanceBefore = {
    available: existing.wallet_balance_before_available === true,
    winston: existing.wallet_balance_before_winston ?? null,
    ar: existing.wallet_balance_before_ar ?? null,
    reason: existing.wallet_balance_before_reason ?? null,
  };
  balanceAfter = {
    available: existing.wallet_balance_after_available === true,
    winston: existing.wallet_balance_after_winston ?? null,
    ar: existing.wallet_balance_after_ar ?? null,
    reason: existing.wallet_balance_after_reason ?? null,
  };
  resumedFromCheckpoint = true;
  console.log(`ARWEAVE_RESUME_READBACK txid=${txId} payload_sha256=${payloadSha256}`);
} else {
  balanceBefore = await safeBalance(arweave, address);

  const tx = await arweave.createTransaction({ data: payload }, jwk);
  tx.addTag("Content-Type", "application/json");
  tx.addTag("App-Name", "Trinity-Accord");
  tx.addTag("Record-Chain", "trinity-accord-public-reception-ledger");
  tx.addTag("Archive-Type", "record-chain-batch-archive");
  tx.addTag("Data-SHA256", payloadSha256);
  tx.addTag("Boundary", "mirror-not-authority");

  uploadCostWinston = String(tx.reward);
  uploadCostAr = winstonToArDecimal(uploadCostWinston);

  await arweave.transactions.sign(tx, jwk);
  const response = await arweave.transactions.post(tx);
  if (response.status < 200 || response.status >= 300) {
    throw new Error(`Arweave post failed: ${response.status} ${response.statusText}`);
  }

  txId = tx.id;
  uploadedAt = new Date().toISOString();

  // Persist the transaction id immediately after the paid post. A process kill,
  // runner timeout, or delayed gateway readback must never erase the tx identity.
  writeResult("posted_pending_readback", null, false, true);
  console.log(`ARWEAVE_POST_CHECKPOINT txid=${txId} payload_sha256=${payloadSha256}`);

  balanceAfter = await safeBalance(arweave, address);
  if (
    balanceBefore.winston &&
    balanceAfter.winston &&
    /^\d+$/.test(balanceBefore.winston) &&
    /^\d+$/.test(balanceAfter.winston)
  ) {
    actualDeltaWinston = (BigInt(balanceBefore.winston) - BigInt(balanceAfter.winston)).toString();
    actualDeltaAr = winstonToArDecimal(actualDeltaWinston);
  }

  // Refresh the durable checkpoint with cost and balance metadata before readback.
  writeResult("posted_pending_readback", null, false, true);
}

// --- Bounded readback verification ---
const readbackStartedAt = Date.now();
let readbackSha256 = null;
let readbackVerified = false;
let attempts = 0;

for (let attempt = 1; attempt <= READBACK_MAX_RETRIES; attempt++) {
  const elapsedSeconds = (Date.now() - readbackStartedAt) / 1000;
  if (elapsedSeconds >= READBACK_MAX_SECONDS) {
    console.error(
      `ARWEAVE_READBACK_BUDGET_EXHAUSTED elapsed_seconds=${elapsedSeconds.toFixed(1)} ` +
        `max_seconds=${READBACK_MAX_SECONDS}`
    );
    break;
  }

  attempts = attempt;
  try {
    console.log(`ARWEAVE_READBACK attempt ${attempt}/${READBACK_MAX_RETRIES} txid=${txId}`);
    const readbackData = await arweave.transactions.getData(txId, {
      decode: true,
      string: false,
    });
    const readbackBuf = Buffer.from(readbackData);
    readbackSha256 = sha256Hex(readbackBuf);
    readbackVerified = readbackSha256 === payloadSha256;
    if (readbackVerified) {
      console.log(`ARWEAVE_READBACK_OK readback_sha256=${readbackSha256}`);
      break;
    }
    console.error(
      `ARWEAVE_READBACK_MISMATCH attempt=${attempt} payload=${payloadSha256} ` +
        `readback=${readbackSha256}`
    );
  } catch (err) {
    console.error(`ARWEAVE_READBACK_RETRY attempt=${attempt} error=${err.message}`);
  }

  if (attempt < READBACK_MAX_RETRIES) {
    const remainingMs = READBACK_MAX_SECONDS * 1000 - (Date.now() - readbackStartedAt);
    if (remainingMs <= 0) break;
    await sleep(Math.min(READBACK_DELAY_MS, remainingMs));
  }
}

if (!readbackVerified) {
  writeResult("readback_failed", readbackSha256, false, true);
  throw new Error(
    `ARWEAVE_READBACK_FAILED attempts=${attempts} max_seconds=${READBACK_MAX_SECONDS} ` +
      `hash_match=false payload_sha256=${payloadSha256} readback_sha256=${readbackSha256}`
  );
}

writeResult("uploaded", readbackSha256, true, false);
console.log(
  `ARWEAVE_UPLOAD_OK txid=${txId} data_sha256=${payloadSha256} ` +
    `readback_sha256=${readbackSha256} hash_match=${readbackVerified} ` +
    `resumed=${resumedFromCheckpoint}`
);
