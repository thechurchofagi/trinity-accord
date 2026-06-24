#!/usr/bin/env node
import fs from "node:fs";
import crypto from "node:crypto";

function arg(name) {
  const idx = process.argv.indexOf(name);
  if (idx < 0 || idx + 1 >= process.argv.length) throw new Error(`Missing ${name}`);
  return process.argv[idx + 1];
}

function sha256Hex(value) {
  return crypto.createHash("sha256").update(value).digest("hex");
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function txidFromResult(result) {
  return result.arweave_txid || result.arweave_tx_id || result.txid || result.tx_id;
}

function gatewaysFromEnv() {
  return (process.env.WAITING_HEARTBEAT_ARWEAVE_READBACK_GATEWAYS || "https://arweave.net")
    .split(",")
    .map((value) => value.trim())
    .filter(Boolean);
}

function txUrl(gateway, txid) {
  return `${gateway.replace(/\/$/, "")}/${txid}`;
}

function writeResult(path, result, patch) {
  fs.writeFileSync(path, JSON.stringify({ ...result, ...patch }, null, 2) + "\n");
}

async function fetchBytes(url) {
  const response = await fetch(url, {
    headers: {
      "User-Agent": "trinity-waiting-heartbeat-capsule-readback/1.0",
      Accept: "*/*",
    },
  });
  const bytes = Buffer.from(await response.arrayBuffer());
  return {
    status: response.status,
    ok: response.ok,
    bytes,
    contentType: response.headers.get("content-type"),
  };
}

const payloadPath = arg("--payload");
const heartbeatId = arg("--heartbeat-id");
const uploadResultPath = arg("--upload-result");
const timeoutMs = Number(process.env.WAITING_HEARTBEAT_ARWEAVE_REPAIR_TIMEOUT_SECONDS || "900") * 1000;
const retryMs = Number(process.env.WAITING_HEARTBEAT_ARWEAVE_REPAIR_RETRY_SECONDS || "15") * 1000;

const payload = fs.readFileSync(payloadPath);
const expectedSha256 = sha256Hex(payload);
const existing = JSON.parse(fs.readFileSync(uploadResultPath, "utf8"));
const txid = txidFromResult(existing);

if (!txid) {
  throw new Error(`No Arweave txid in ${uploadResultPath}`);
}

if (existing.heartbeat_id && existing.heartbeat_id !== heartbeatId) {
  throw new Error(`Heartbeat id mismatch: expected ${heartbeatId}, result has ${existing.heartbeat_id}`);
}

if (existing.payload_sha256 && existing.payload_sha256 !== expectedSha256) {
  writeResult(uploadResultPath, existing, {
    status: "local_payload_mismatch_for_existing_tx",
    hash_match: false,
    retryable: false,
    readback_attempted_at: new Date().toISOString(),
    last_readback_error: `local payload sha256 ${expectedSha256} does not match upload result ${existing.payload_sha256}`,
  });
  process.exit(2);
}

const gateways = gatewaysFromEnv();
const deadline = Date.now() + timeoutMs;
let attempts = 0;
let lastFailure = null;

while (Date.now() < deadline) {
  for (const gateway of gateways) {
    const url = txUrl(gateway, txid);
    attempts += 1;
    try {
      console.log(`ARWEAVE_CAPSULE_REPAIR_READBACK attempt=${attempts} url=${url}`);
      const fetched = await fetchBytes(url);
      const readbackSha256 = fetched.bytes.length > 0 ? sha256Hex(fetched.bytes) : null;
      console.log(`ARWEAVE_CAPSULE_REPAIR_STATUS status=${fetched.status} bytes=${fetched.bytes.length} sha256=${readbackSha256 || "null"}`);

      if (fetched.ok && fetched.bytes.length > 0) {
        if (readbackSha256 === expectedSha256) {
          writeResult(uploadResultPath, existing, {
            status: "uploaded",
            readback_sha256: readbackSha256,
            hash_match: true,
            retryable: false,
            verified_at: new Date().toISOString(),
            readback_attempts: attempts,
            last_readback_error: null,
            next_action: "no_op",
          });
          console.log(`ARWEAVE_CAPSULE_REPAIR_OK txid=${txid} sha256=${readbackSha256}`);
          process.exit(0);
        }

        writeResult(uploadResultPath, existing, {
          status: "readback_hash_mismatch",
          readback_sha256: readbackSha256,
          hash_match: false,
          retryable: false,
          readback_attempted_at: new Date().toISOString(),
          readback_attempts: attempts,
          last_readback_error: `hash mismatch: expected ${expectedSha256} got ${readbackSha256}`,
          next_action: "stop_and_investigate",
        });
        process.exit(2);
      }

      lastFailure = `status=${fetched.status} bytes=${fetched.bytes.length}`;
    } catch (error) {
      lastFailure = error.message;
      console.log(`ARWEAVE_CAPSULE_REPAIR_RETRY error=${error.message}`);
    }
  }

  if (Date.now() < deadline) {
    await sleep(retryMs);
  }
}

writeResult(uploadResultPath, existing, {
  status: "posted_pending_readback",
  hash_match: false,
  retryable: true,
  readback_attempted_at: new Date().toISOString(),
  readback_attempts: attempts,
  last_readback_error: lastFailure,
  next_action: "retry_readback_without_reupload",
});
console.warn(`ARWEAVE_CAPSULE_REPAIR_PENDING txid=${txid} attempts=${attempts} last=${lastFailure}`);
process.exit(0);
