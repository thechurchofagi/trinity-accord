#!/usr/bin/env node

import fs from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import Arweave from "arweave";

const DEFAULT_GATEWAY = "https://arweave.net";
const CURRENT_OWNER = "r1EdzCQ9E7CaAOEywI5netR6EcSopNOa08oi2Coz68s";
const WINSTON_PER_AR = 1_000_000_000_000n;

function nowIso() {
  return new Date().toISOString();
}

function fail(message, extra = {}) {
  const err = new Error(message);
  err.extra = extra;
  throw err;
}

function winstonToArDecimal(winstonValue) {
  const value = BigInt(String(winstonValue));
  const negative = value < 0n;
  const abs = negative ? -value : value;
  const whole = abs / WINSTON_PER_AR;
  const frac = abs % WINSTON_PER_AR;
  return `${negative ? "-" : ""}${whole.toString()}.${frac.toString().padStart(12, "0")}`;
}

function signedDelta(before, after) {
  if (!/^\d+$/.test(String(before)) || !/^\d+$/.test(String(after))) {
    return null;
  }
  return (BigInt(before) - BigInt(after)).toString();
}

function parseArgs(argv) {
  const args = {
    uploadResult: null,
    costEstimate: null,
    recordType: "echo",
    runId: process.env.E2E_RUN_ID || null,
    logDir: process.env.E2E_LOG_DIR || null,
    gatewayUrl: process.env.ARWEAVE_GATEWAY_URL || DEFAULT_GATEWAY,
    expectedOwner: process.env.EXPECTED_ARWEAVE_OWNER || CURRENT_OWNER,
    delaySeconds: (process.env.ARWEAVE_BALANCE_RECHECK_DELAYS || "600,1800")
      .split(",")
      .map((s) => Number(s.trim()))
      .filter((n) => Number.isFinite(n) && n >= 0),
    noWait: false
  };

  for (let i = 0; i < argv.length; i++) {
    const key = argv[i];
    const next = argv[i + 1];

    if (key === "--upload-result") {
      args.uploadResult = next;
      i++;
    } else if (key === "--cost-estimate") {
      args.costEstimate = next;
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
    } else if (key === "--gateway-url") {
      args.gatewayUrl = next;
      i++;
    } else if (key === "--expected-owner") {
      args.expectedOwner = next;
      i++;
    } else if (key === "--delay-seconds") {
      args.delaySeconds = next
        .split(",")
        .map((s) => Number(s.trim()))
        .filter((n) => Number.isFinite(n) && n >= 0);
      i++;
    } else if (key === "--no-wait") {
      args.noWait = true;
    } else if (key === "--help" || key === "-h") {
      console.log(`
Usage:
  node scripts/arweave_delayed_balance_recheck.mjs \\
    --upload-result record-chain/audit/e2e/<run>/11-arweave-upload-result.echo.json \\
    --cost-estimate record-chain/audit/e2e/<run>/10-arweave-cost-estimate.echo.json \\
    --record-type echo \\
    --run-id "$E2E_RUN_ID" \\
    --log-dir "$E2E_LOG_DIR"

Environment:
  ARWEAVE_BALANCE_RECHECK_DELAYS=600,1800
  ARWEAVE_GATEWAY_URL=https://arweave.net
`);
      process.exit(0);
    } else {
      fail(`Unknown argument: ${key}`);
    }
  }

  if (!args.uploadResult) fail("Missing --upload-result");
  if (!args.costEstimate) fail("Missing --cost-estimate");
  if (!args.runId) fail("Missing --run-id or E2E_RUN_ID");
  if (!args.logDir) fail("Missing --log-dir or E2E_LOG_DIR");
  if (args.delaySeconds.length === 0) fail("At least one delay is required");

  return args;
}

function makeArweave(gatewayUrl) {
  const url = new URL(gatewayUrl);
  return Arweave.init({
    host: url.hostname,
    protocol: url.protocol.replace(":", ""),
    port: url.port ? Number(url.port) : url.protocol === "http:" ? 80 : 443
  });
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function readJson(file) {
  return JSON.parse(await fs.readFile(file, "utf8"));
}

async function writeJson(file, data) {
  await fs.mkdir(path.dirname(file), { recursive: true });
  await fs.writeFile(file, JSON.stringify(data, null, 2) + "\n", "utf8");
}

async function getBalance(arweave, address) {
  const winston = await arweave.wallets.getBalance(address);
  return {
    winston: String(winston),
    ar: winstonToArDecimal(winston),
    checked_at: nowIso()
  };
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const arweave = makeArweave(args.gatewayUrl);

  const upload = await readJson(args.uploadResult);
  const estimate = await readJson(args.costEstimate);

  const walletAddress = upload.wallet_address || estimate.wallet_address;

  if (!walletAddress) fail("wallet_address missing from audit logs");
  if (walletAddress !== args.expectedOwner) {
    fail("wallet address does not match expected owner", {
      walletAddress,
      expectedOwner: args.expectedOwner
    });
  }

  if (!upload.tx_id) fail("tx_id missing from upload result");
  if (upload.result !== "uploaded") fail("upload result is not uploaded");

  const initialBefore = upload.balance_before_winston || estimate.balance_before_winston;
  const immediateAfter = upload.balance_after_winston;

  const checks = [];

  console.log("[ARWEAVE DELAYED BALANCE RECHECK]");
  console.log(`run_id: ${args.runId}`);
  console.log(`record_type: ${args.recordType}`);
  console.log(`tx_id: ${upload.tx_id}`);
  console.log(`wallet_address: ${walletAddress}`);
  console.log(`initial_before_winston: ${initialBefore}`);
  console.log(`immediate_after_winston: ${immediateAfter}`);
  console.log(`delay_seconds: ${args.delaySeconds.join(",")}`);

  for (const delay of args.delaySeconds) {
    if (!args.noWait && delay > 0) {
      console.log(`[BALANCE RECHECK WAIT] seconds=${delay}`);
      await sleep(delay * 1000);
    }

    const balance = await getBalance(arweave, walletAddress);
    const deltaFromBefore =
      initialBefore && balance.winston ? signedDelta(initialBefore, balance.winston) : null;

    const item = {
      delay_seconds: delay,
      checked_at: balance.checked_at,
      wallet_address: walletAddress,
      balance_winston: balance.winston,
      balance_ar: balance.ar,
      delta_from_initial_before_winston: deltaFromBefore,
      delta_from_initial_before_ar:
        deltaFromBefore == null ? null : winstonToArDecimal(deltaFromBefore)
    };

    checks.push(item);

    console.log("[ARWEAVE BALANCE RECHECK RESULT]");
    console.log(`delay_seconds: ${item.delay_seconds}`);
    console.log(`balance_winston: ${item.balance_winston}`);
    console.log(`balance_ar: ${item.balance_ar}`);
    console.log(`delta_from_initial_before_winston: ${item.delta_from_initial_before_winston}`);
    console.log(`delta_from_initial_before_ar: ${item.delta_from_initial_before_ar}`);
  }

  const result = {
    generated_at: nowIso(),
    run_id: args.runId,
    record_type: args.recordType,
    tx_id: upload.tx_id,
    gateway_url: upload.gateway_url,
    wallet_address: walletAddress,
    expected_owner: args.expectedOwner,
    estimated_upload_cost_usd: estimate.estimated_upload_cost_usd,
    estimated_upload_cost_usd_with_buffer: estimate.estimated_upload_cost_usd_with_buffer,
    initial_balance_before_winston: initialBefore,
    immediate_balance_after_winston: immediateAfter,
    checks,
    result: "recorded",
    note: "A zero or delayed wallet delta is not a paid-canary failure if tx upload and readback hash verification passed."
  };

  await writeJson(
    path.join(args.logDir, `11c-arweave-delayed-balance-recheck.${args.recordType}.json`),
    result
  );
}

main().catch((error) => {
  console.error("[ARWEAVE DELAYED BALANCE RECHECK ERROR]");
  console.error(error.message);
  if (error.extra) console.error(JSON.stringify(error.extra, null, 2));
  process.exit(1);
});
