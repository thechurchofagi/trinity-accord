#!/usr/bin/env node

import fs from "node:fs/promises";
import path from "node:path";
import crypto from "node:crypto";
import process from "node:process";

function nowIso() {
  return new Date().toISOString();
}

function sha256(bytes) {
  return crypto.createHash("sha256").update(bytes).digest("hex");
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function fail(message, extra = {}) {
  const err = new Error(message);
  err.extra = extra;
  throw err;
}

function parseArgs(argv) {
  const args = {
    txId: null,
    expectedFile: null,
    expectedSha256: null,
    recordType: null,
    runId: process.env.E2E_RUN_ID || null,
    logDir: process.env.E2E_LOG_DIR || null,
    gateways: (
      process.env.ARWEAVE_READBACK_GATEWAYS || "https://arweave.net"
    )
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean),
    timeoutSeconds: Number(process.env.ARWEAVE_READBACK_TIMEOUT_SECONDS || 900),
    retrySeconds: Number(process.env.ARWEAVE_READBACK_RETRY_SECONDS || 15)
  };

  for (let i = 0; i < argv.length; i++) {
    const key = argv[i];
    const next = argv[i + 1];

    if (key === "--tx-id") {
      args.txId = next;
      i++;
    } else if (key === "--expected-file") {
      args.expectedFile = next;
      i++;
    } else if (key === "--expected-sha256") {
      args.expectedSha256 = next;
      i++;
    } else if (key === "--record-type") {
      args.recordType = next;
      i++;
    } else if (key === "--run-id") {
      args.runId = next;
      i++;
    } else if (key === "--log-dir") {
      args.logDir = next;
      i++;
    } else if (key === "--gateway") {
      args.gateways.push(next);
      i++;
    } else if (key === "--timeout-seconds") {
      args.timeoutSeconds = Number(next);
      i++;
    } else if (key === "--retry-seconds") {
      args.retrySeconds = Number(next);
      i++;
    } else if (key === "--help" || key === "-h") {
      printHelpAndExit();
    } else {
      fail(`Unknown argument: ${key}`);
    }
  }

  if (!args.txId) fail("Missing --tx-id");
  if (!args.expectedFile) fail("Missing --expected-file");
  if (!args.expectedSha256) fail("Missing --expected-sha256");
  if (!args.recordType) fail("Missing --record-type");
  if (!args.runId) fail("Missing --run-id or E2E_RUN_ID");
  if (!args.logDir) fail("Missing --log-dir or E2E_LOG_DIR");

  if (!/^[a-zA-Z0-9_-]{20,}$/.test(args.txId)) {
    fail("Invalid Arweave tx id format", { txId: args.txId });
  }

  if (!/^[a-f0-9]{64}$/i.test(args.expectedSha256)) {
    fail("Expected SHA256 must be 64 hex characters");
  }

  if (!Number.isFinite(args.timeoutSeconds) || args.timeoutSeconds <= 0) {
    fail("timeoutSeconds must be positive");
  }

  if (!Number.isFinite(args.retrySeconds) || args.retrySeconds <= 0) {
    fail("retrySeconds must be positive");
  }

  if (args.gateways.length === 0) {
    fail("At least one readback gateway is required");
  }

  return args;
}

function printHelpAndExit() {
  console.log(`
Usage:
  node scripts/verify_arweave_upload_readback.mjs \\
    --tx-id "<tx_id>" \\
    --expected-file "./payload.json" \\
    --expected-sha256 "<sha256>" \\
    --record-type echo \\
    --run-id "$E2E_RUN_ID" \\
    --log-dir "$E2E_LOG_DIR"
`);
  process.exit(0);
}

async function writeJson(file, data) {
  await fs.mkdir(path.dirname(file), { recursive: true });
  await fs.writeFile(file, JSON.stringify(data, null, 2) + "\n", "utf8");
}

function buildTxUrl(gateway, txId) {
  return `${gateway.replace(/\/$/, "")}/${txId}`;
}

async function fetchBytes(url) {
  const started = Date.now();

  const response = await fetch(url, {
    headers: {
      "User-Agent": "trinity-accord-e2e-arweave-readback/1.0",
      Accept: "*/*"
    }
  });

  const arrayBuffer = await response.arrayBuffer();
  const bytes = Buffer.from(arrayBuffer);

  return {
    url,
    status: response.status,
    ok: response.ok,
    duration_ms: Date.now() - started,
    content_type: response.headers.get("content-type"),
    cache_control: response.headers.get("cache-control"),
    etag: response.headers.get("etag"),
    last_modified: response.headers.get("last-modified"),
    bytes
  };
}

function printStart(args, expectedBytes, expectedSha256) {
  console.log("[ARWEAVE READBACK VERIFY]");
  console.log(`run_id: ${args.runId}`);
  console.log(`record_type: ${args.recordType}`);
  console.log(`tx_id: ${args.txId}`);
  console.log("gateway_urls:");
  for (const gateway of args.gateways) {
    console.log(`  - ${buildTxUrl(gateway, args.txId)}`);
  }
  console.log(`expected_file: ${args.expectedFile}`);
  console.log(`expected_bytes: ${expectedBytes}`);
  console.log(`expected_sha256: ${expectedSha256}`);
  console.log(`timeout_seconds: ${args.timeoutSeconds}`);
  console.log(`retry_seconds: ${args.retrySeconds}`);
}

function printAttempt(attempt) {
  console.log("[ARWEAVE READBACK REQUEST]");
  console.log(`tx_id: ${attempt.tx_id}`);
  console.log(`gateway_url: ${attempt.gateway_url}`);
  console.log(`attempt: ${attempt.attempt}`);
  console.log(`status: ${attempt.status}`);
  console.log(`duration_ms: ${attempt.duration_ms}`);
  console.log(`content_type: ${attempt.content_type || "null"}`);
  console.log(`downloaded_bytes: ${attempt.downloaded_bytes}`);
  console.log(`downloaded_sha256: ${attempt.downloaded_sha256 || "null"}`);
}

function printResult(result) {
  console.log("[ARWEAVE READBACK RESULT]");
  console.log(`tx_id: ${result.tx_id}`);
  console.log(`gateway_url: ${result.gateway_url || "null"}`);
  console.log(`result: ${result.result}`);
  console.log(`reason: ${result.reason || "null"}`);
  console.log(`expected_sha256: ${result.expected_sha256}`);
  console.log(`downloaded_sha256: ${result.downloaded_sha256 || "null"}`);
  console.log(`bytes_match: ${result.bytes_match}`);
  console.log(`hash_match: ${result.hash_match}`);

  if (result.result !== "pass") {
    console.log("action: mark_upload_unverified_and_stop_paid_uploads");
  }
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const expectedBytes = await fs.readFile(args.expectedFile);
  const fileSha256 = sha256(expectedBytes);

  if (fileSha256 !== args.expectedSha256) {
    fail("Expected file SHA256 does not match provided expected SHA256", {
      expectedFile: args.expectedFile,
      computed: fileSha256,
      provided: args.expectedSha256
    });
  }

  printStart(args, expectedBytes.length, args.expectedSha256);

  const started = Date.now();
  const deadline = started + args.timeoutSeconds * 1000;
  const attempts = [];
  let attemptNumber = 0;
  let lastFailure = null;

  while (Date.now() < deadline) {
    for (const gateway of args.gateways) {
      attemptNumber++;
      const gatewayUrl = buildTxUrl(gateway, args.txId);

      let fetched;

      try {
        fetched = await fetchBytes(gatewayUrl);
      } catch (error) {
        const attempt = {
          timestamp: nowIso(),
          tx_id: args.txId,
          gateway_url: gatewayUrl,
          attempt: attemptNumber,
          status: "fetch_error",
          duration_ms: null,
          content_type: null,
          downloaded_bytes: 0,
          downloaded_sha256: null,
          error: error.message
        };
        attempts.push(attempt);
        printAttempt(attempt);
        lastFailure = {
          reason: "gateway_error",
          error: error.message,
          gateway_url: gatewayUrl
        };
        continue;
      }

      const downloadedSha =
        fetched.bytes.length > 0 ? sha256(fetched.bytes) : null;

      const attempt = {
        timestamp: nowIso(),
        tx_id: args.txId,
        gateway_url: gatewayUrl,
        attempt: attemptNumber,
        status: fetched.status,
        duration_ms: fetched.duration_ms,
        content_type: fetched.content_type,
        cache_control: fetched.cache_control,
        etag: fetched.etag,
        last_modified: fetched.last_modified,
        downloaded_bytes: fetched.bytes.length,
        downloaded_sha256: downloadedSha
      };

      attempts.push(attempt);
      printAttempt(attempt);

      if (fetched.ok && fetched.bytes.length > 0) {
        const bytesMatch = fetched.bytes.length === expectedBytes.length;
        const hashMatch = downloadedSha === args.expectedSha256;

        if (bytesMatch && hashMatch) {
          const result = {
            run_id: args.runId,
            record_type: args.recordType,
            tx_id: args.txId,
            gateway_url: gatewayUrl,
            expected_file: args.expectedFile,
            expected_bytes: expectedBytes.length,
            downloaded_bytes: fetched.bytes.length,
            expected_sha256: args.expectedSha256,
            downloaded_sha256: downloadedSha,
            hash_match: true,
            byte_for_byte_match: true,
            bytes_match: true,
            attempts: attempts.length,
            duration_ms: Date.now() - started,
            verified_at: nowIso(),
            result: "pass",
            attempts_log: attempts
          };

          printResult(result);
          await writeJson(
            path.join(
              args.logDir,
              `11b-arweave-readback-verify.${args.recordType}.json`
            ),
            result
          );
          return;
        }

        const result = {
          run_id: args.runId,
          record_type: args.recordType,
          tx_id: args.txId,
          gateway_url: gatewayUrl,
          expected_file: args.expectedFile,
          expected_bytes: expectedBytes.length,
          downloaded_bytes: fetched.bytes.length,
          expected_sha256: args.expectedSha256,
          downloaded_sha256: downloadedSha,
          hash_match: hashMatch,
          byte_for_byte_match: false,
          bytes_match: bytesMatch,
          attempts: attempts.length,
          duration_ms: Date.now() - started,
          verified_at: nowIso(),
          result: "fail",
          severity: "P0",
          reason: hashMatch ? "byte_length_mismatch" : "hash_mismatch",
          action: "stop_paid_uploads_and_open_bug",
          attempts_log: attempts
        };

        printResult(result);
        await writeJson(
          path.join(
            args.logDir,
            `11b-arweave-readback-verify.${args.recordType}.json`
          ),
          result
        );
        process.exit(2);
      }

      if (![202, 404, 502, 503, 504].includes(fetched.status)) {
        lastFailure = {
          reason: "unexpected_status",
          status: fetched.status,
          gateway_url: gatewayUrl
        };
      }
    }

    if (Date.now() < deadline) {
      await sleep(args.retrySeconds * 1000);
    }
  }

  const result = {
    run_id: args.runId,
    record_type: args.recordType,
    tx_id: args.txId,
    gateway_url: null,
    expected_file: args.expectedFile,
    expected_bytes: expectedBytes.length,
    downloaded_bytes: null,
    expected_sha256: args.expectedSha256,
    downloaded_sha256: null,
    hash_match: false,
    byte_for_byte_match: false,
    bytes_match: false,
    attempts: attempts.length,
    duration_ms: Date.now() - started,
    verified_at: nowIso(),
    result: "fail",
    severity: "P0",
    reason: "timeout_or_unavailable",
    last_failure: lastFailure,
    action: "stop_paid_uploads_and_open_bug",
    attempts_log: attempts
  };

  printResult(result);

  await writeJson(
    path.join(
      args.logDir,
      `11b-arweave-readback-verify.${args.recordType}.json`
    ),
    result
  );

  process.exit(2);
}

main().catch((error) => {
  console.error("[ARWEAVE READBACK VERIFY ERROR]");
  console.error(error.message);
  if (error.extra) {
    console.error(JSON.stringify(error.extra, null, 2));
  }
  process.exit(1);
});
