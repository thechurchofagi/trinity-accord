#!/usr/bin/env node

import fs from "node:fs/promises";
import path from "node:path";
import crypto from "node:crypto";
import process from "node:process";
import { spawn } from "node:child_process";
import Arweave from "arweave";

const CURRENT_TRINITY_ARWEAVE_OWNER =
  "r1EdzCQ9E7CaAOEywI5netR6EcSopNOa08oi2Coz68s";

const OLD_TRINITY_ARWEAVE_OWNER =
  "8Y8GRimuESN_u8tJihCd5nywb-X-lJ_2vWqFAfHeQIE";

const DEFAULT_GATEWAY = "https://arweave.net";
const DEFAULT_MAX_UPLOAD_USD = 0.10;
const DEFAULT_SAFETY_MULTIPLIER = 1.20;
const WINSTON_PER_AR = 1_000_000_000_000n;

function nowIso() {
  return new Date().toISOString();
}

function sha256(bytes) {
  return crypto.createHash("sha256").update(bytes).digest("hex");
}

function fail(message, extra = {}) {
  const err = new Error(message);
  err.extra = extra;
  throw err;
}

function parseBoolean(value) {
  return String(value || "").toLowerCase() === "true";
}

function parseArgs(argv) {
  const args = {
    payloadFile: null,
    recordType: null,
    runId: process.env.E2E_RUN_ID || null,
    logDir: process.env.E2E_LOG_DIR || null,

    mode: process.env.ARWEAVE_UPLOAD_MODE || "dry_run",
    expectedOwner:
      process.env.EXPECTED_ARWEAVE_OWNER || CURRENT_TRINITY_ARWEAVE_OWNER,

    gatewayUrl: process.env.ARWEAVE_GATEWAY_URL || DEFAULT_GATEWAY,

    arUsdPriceSourceUrl:
      process.env.AR_USD_PRICE_SOURCE_URL ||
      "https://api.coingecko.com/api/v3/simple/price?ids=arweave&vs_currencies=usd",

    arUsdPriceOverride: process.env.AR_USD_PRICE_OVERRIDE || null,
    uploadPriceWinstonOverride:
      process.env.ARWEAVE_UPLOAD_PRICE_WINSTON_OVERRIDE || null,

    allowPriceOverrideInProduction: parseBoolean(
      process.env.ALLOW_ARWEAVE_PRICE_OVERRIDE_IN_PRODUCTION
    ),

    maxUploadUsd: Number(
      process.env.ARWEAVE_MAX_UPLOAD_USD || DEFAULT_MAX_UPLOAD_USD
    ),

    safetyMultiplier: Number(
      process.env.ARWEAVE_SAFETY_MULTIPLIER || DEFAULT_SAFETY_MULTIPLIER
    ),

    jwkPath: process.env.ARWEAVE_JWK_PATH || null,
    walletAddress: process.env.ARWEAVE_WALLET_ADDRESS || null,
    allowPaid: parseBoolean(process.env.ALLOW_PAID_ARWEAVE_CANARY),
    contentType: "application/json",
    appName: process.env.ARWEAVE_APP_NAME || "Trinity-Accord-E2E-Canary",
    extraTagsJson: process.env.ARWEAVE_EXTRA_TAGS_JSON || null,
    skipReadback: false
  };

  for (let i = 0; i < argv.length; i++) {
    const key = argv[i];
    const next = argv[i + 1];

    if (key === "--payload-file") {
      args.payloadFile = next;
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
    } else if (key === "--mode") {
      args.mode = next;
      i++;
    } else if (key === "--expected-owner") {
      args.expectedOwner = next;
      i++;
    } else if (key === "--gateway-url") {
      args.gatewayUrl = next;
      i++;
    } else if (key === "--max-upload-usd") {
      args.maxUploadUsd = Number(next);
      i++;
    } else if (key === "--safety-multiplier") {
      args.safetyMultiplier = Number(next);
      i++;
    } else if (key === "--jwk-path") {
      args.jwkPath = next;
      i++;
    } else if (key === "--wallet-address") {
      args.walletAddress = next;
      i++;
    } else if (key === "--content-type") {
      args.contentType = next;
      i++;
    } else if (key === "--skip-readback") {
      args.skipReadback = true;
    } else if (key === "--app-name") {
      args.appName = next;
      i++;
    } else if (key === "--extra-tags-json") {
      args.extraTagsJson = next;
      i++;
    } else if (key === "--help" || key === "-h") {
      printHelpAndExit();
    } else {
      fail(`Unknown argument: ${key}`);
    }
  }

  if (!args.payloadFile) fail("Missing --payload-file");
  if (!args.recordType) fail("Missing --record-type");
  if (!args.runId) fail("Missing --run-id or E2E_RUN_ID");
  if (!args.logDir) fail("Missing --log-dir or E2E_LOG_DIR");

  if (!["dry_run", "staging", "production"].includes(args.mode)) {
    fail("mode must be dry_run, staging, or production");
  }

  if (!Number.isFinite(args.maxUploadUsd) || args.maxUploadUsd <= 0) {
    fail("ARWEAVE_MAX_UPLOAD_USD must be a positive number");
  }

  if (!Number.isFinite(args.safetyMultiplier) || args.safetyMultiplier < 1) {
    fail("ARWEAVE_SAFETY_MULTIPLIER must be >= 1");
  }

  args.effectiveMaxUploadUsd = Math.min(
    args.maxUploadUsd,
    DEFAULT_MAX_UPLOAD_USD
  );

  if (
    args.mode === "production" &&
    (args.arUsdPriceOverride || args.uploadPriceWinstonOverride) &&
    !args.allowPriceOverrideInProduction
  ) {
    fail(
      "Price overrides are forbidden in production unless ALLOW_ARWEAVE_PRICE_OVERRIDE_IN_PRODUCTION=true"
    );
  }

  return args;
}

function parseExtraTags(extraTagsJson) {
  if (!extraTagsJson) return [];

  let parsed;
  try {
    parsed = JSON.parse(extraTagsJson);
  } catch {
    fail("ARWEAVE_EXTRA_TAGS_JSON / --extra-tags-json is not valid JSON");
  }

  if (!Array.isArray(parsed)) {
    fail("extra tags must be a JSON array");
  }

  const tags = [];
  for (const item of parsed) {
    if (!item || typeof item !== "object") {
      fail("each extra tag must be an object");
    }
    const name = item.name;
    const value = item.value;
    if (typeof name !== "string" || name.length < 1 || name.length > 128) {
      fail("extra tag name must be a non-empty string <= 128 chars", { item });
    }
    if (typeof value !== "string" || value.length > 512) {
      fail("extra tag value must be a string <= 512 chars", { item });
    }
    if (!/^[A-Za-z0-9._:-]+$/.test(name)) {
      fail("extra tag name contains unsupported characters", { name });
    }
    tags.push({ name, value });
  }
  return tags;
}

function printHelpAndExit() {
  console.log(`
Usage:
  node scripts/arweave_cost_gate.mjs \\
    --payload-file ./payload.json \\
    --record-type echo \\
    --run-id "$E2E_RUN_ID" \\
    --log-dir "$E2E_LOG_DIR"

Environment:
  ARWEAVE_UPLOAD_MODE=dry_run|staging|production
  ALLOW_PAID_ARWEAVE_CANARY=false
  ARWEAVE_MAX_UPLOAD_USD=0.10
  ARWEAVE_SAFETY_MULTIPLIER=1.20
  ARWEAVE_JWK_PATH=/secure/path/wallet.json
  EXPECTED_ARWEAVE_OWNER=${CURRENT_TRINITY_ARWEAVE_OWNER}
  ARWEAVE_GATEWAY_URL=https://arweave.net

Testing overrides, non-production only:
  ARWEAVE_UPLOAD_PRICE_WINSTON_OVERRIDE=1000
  AR_USD_PRICE_OVERRIDE=10
`);
  process.exit(0);
}

function makeArweave(gatewayUrl) {
  const url = new URL(gatewayUrl);
  return Arweave.init({
    host: url.hostname,
    protocol: url.protocol.replace(":", ""),
    port: url.port ? Number(url.port) : url.protocol === "http:" ? 80 : 443
  });
}

function winstonToArDecimal(winstonValue) {
  const value = BigInt(String(winstonValue));
  const negative = value < 0n;
  const abs = negative ? -value : value;
  const whole = abs / WINSTON_PER_AR;
  const frac = abs % WINSTON_PER_AR;
  const fracString = frac.toString().padStart(12, "0");
  return `${negative ? "-" : ""}${whole.toString()}.${fracString}`;
}

function decimalStringToNumber(s) {
  const n = Number(s);
  if (!Number.isFinite(n)) fail(`Invalid decimal number: ${s}`);
  return n;
}

async function fetchText(url, label) {
  const started = Date.now();
  const response = await fetch(url, {
    headers: {
      "User-Agent": "trinity-accord-e2e-arweave-cost-gate/1.0",
      Accept: "application/json,text/plain,*/*"
    }
  });

  const text = await response.text();

  return {
    label,
    url,
    status: response.status,
    ok: response.ok,
    duration_ms: Date.now() - started,
    content_type: response.headers.get("content-type"),
    cache_control: response.headers.get("cache-control"),
    text
  };
}

async function fetchArUsd(args) {
  if (args.arUsdPriceOverride) {
    const price = Number(args.arUsdPriceOverride);
    if (!Number.isFinite(price) || price <= 0) {
      fail("AR_USD_PRICE_OVERRIDE must be a positive number");
    }
    return {
      price,
      source: "AR_USD_PRICE_OVERRIDE",
      overridden: true,
      status: null,
      duration_ms: 0
    };
  }

  const result = await fetchText(args.arUsdPriceSourceUrl, "ar_usd_price");

  if (!result.ok) {
    fail("AR/USD price fetch failed", result);
  }

  let json;
  try {
    json = JSON.parse(result.text);
  } catch {
    fail("AR/USD price response is not JSON", {
      status: result.status,
      content_type: result.content_type,
      body_preview: result.text.slice(0, 200)
    });
  }

  const price = json?.arweave?.usd;

  if (!Number.isFinite(price) || price <= 0) {
    fail("AR/USD price missing or invalid", { json });
  }

  return {
    price,
    source: args.arUsdPriceSourceUrl,
    overridden: false,
    status: result.status,
    duration_ms: result.duration_ms
  };
}

async function getUploadPriceWinston(args, arweave, payloadBytes) {
  if (args.uploadPriceWinstonOverride) {
    if (!/^\d+$/.test(args.uploadPriceWinstonOverride)) {
      fail("ARWEAVE_UPLOAD_PRICE_WINSTON_OVERRIDE must be a positive integer string");
    }
    return {
      winston: args.uploadPriceWinstonOverride,
      source: "ARWEAVE_UPLOAD_PRICE_WINSTON_OVERRIDE",
      overridden: true
    };
  }

  const winston = await arweave.transactions.getPrice(payloadBytes);
  if (!/^\d+$/.test(String(winston))) {
    fail("arweave.transactions.getPrice did not return a Winston integer", {
      winston
    });
  }

  return {
    winston: String(winston),
    source: "arweave.transactions.getPrice",
    overridden: false
  };
}

async function readJwkIfNeeded(args, arweave) {
  if (!args.jwkPath) {
    return {
      jwk: null,
      derivedAddress: null
    };
  }

  const raw = await fs.readFile(args.jwkPath, "utf8");
  let jwk;

  try {
    jwk = JSON.parse(raw);
  } catch {
    fail("ARWEAVE_JWK_PATH does not contain valid JSON");
  }

  const derivedAddress = await arweave.wallets.jwkToAddress(jwk);

  return {
    jwk,
    derivedAddress
  };
}

async function getWalletBalance(arweave, address, required) {
  if (!address) {
    if (required) fail("Wallet address is required for production");
    return {
      winston: null,
      ar: null,
      available: false,
      reason: "no_wallet_address"
    };
  }

  try {
    const winston = await arweave.wallets.getBalance(address);
    return {
      winston: String(winston),
      ar: winstonToArDecimal(winston),
      available: true,
      reason: null
    };
  } catch (error) {
    if (required) {
      fail("Wallet balance fetch failed", {
        address,
        error: error.message
      });
    }

    return {
      winston: null,
      ar: null,
      available: false,
      reason: error.message
    };
  }
}

async function writeJson(file, data) {
  await fs.mkdir(path.dirname(file), { recursive: true });
  await fs.writeFile(file, JSON.stringify(data, null, 2) + "\n", "utf8");
}

function printCostCheck(data) {
  console.log("[ARWEAVE COST CHECK]");
  console.log(`run_id: ${data.run_id}`);
  console.log(`record_type: ${data.record_type}`);
  console.log(`payload_file: ${data.payload_file}`);
  console.log(`payload_bytes: ${data.payload_bytes}`);
  console.log(`payload_sha256: ${data.payload_sha256}`);
  console.log(`wallet_address: ${data.wallet_address || "null"}`);
  console.log(`expected_owner: ${data.expected_owner}`);
  console.log(`balance_before_winston: ${data.balance_before_winston}`);
  console.log(`balance_before_ar: ${data.balance_before_ar}`);
  console.log(`ar_usd_price: ${data.ar_usd_price}`);
  console.log(`estimated_upload_cost_winston: ${data.estimated_upload_cost_winston}`);
  console.log(`estimated_upload_cost_ar: ${data.estimated_upload_cost_ar}`);
  console.log(`estimated_upload_cost_usd: ${data.estimated_upload_cost_usd}`);
  console.log(`safety_multiplier: ${data.safety_multiplier}`);
  console.log(
    `estimated_upload_cost_usd_with_buffer: ${data.estimated_upload_cost_usd_with_buffer}`
  );
  console.log(`max_upload_usd: ${data.effective_max_upload_usd}`);
  console.log(`decision: ${data.decision}`);
  console.log(`reason: ${data.reason}`);
}

function printUploadResult(data) {
  if (data.result === "uploaded") {
    console.log("[ARWEAVE UPLOAD RESULT]");
    console.log(`run_id: ${data.run_id}`);
    console.log(`record_type: ${data.record_type}`);
    console.log(`tx_id: ${data.tx_id}`);
    console.log(`gateway_url: ${data.gateway_url}`);
    console.log(`balance_before_winston: ${data.balance_before_winston}`);
    console.log(`balance_after_winston: ${data.balance_after_winston}`);
    console.log(`actual_delta_winston: ${data.actual_delta_winston}`);
    console.log(`actual_delta_ar: ${data.actual_delta_ar}`);
    console.log(`estimated_cost_usd: ${data.estimated_cost_usd}`);
    console.log(
      `remaining_balance_estimated_usd: ${data.remaining_balance_estimated_usd}`
    );
  } else {
    console.log("[ARWEAVE UPLOAD BLOCKED]");
    console.log(`reason: ${data.reason}`);
    console.log("tx_id: null");
  }
}

async function runReadbackVerifier(args, txId, payloadSha256) {
  if (args.skipReadback) {
    return {
      skipped: true,
      reason: "skip_readback_argument"
    };
  }

  const verifierPath = path.resolve("scripts/verify_arweave_upload_readback.mjs");
  const childArgs = [
    verifierPath,
    "--tx-id",
    txId,
    "--expected-file",
    args.payloadFile,
    "--expected-sha256",
    payloadSha256,
    "--record-type",
    args.recordType,
    "--run-id",
    args.runId,
    "--log-dir",
    args.logDir
  ];

  console.log("[ARWEAVE READBACK VERIFY COMMAND]");
  console.log(`command: node ${childArgs.map((x) => JSON.stringify(x)).join(" ")}`);

  const result = await new Promise((resolve) => {
    const child = spawn(process.execPath, childArgs, {
      stdio: "inherit",
      env: process.env
    });

    child.on("close", (code) => {
      resolve({ exit_code: code });
    });
  });

  if (result.exit_code !== 0) {
    fail("Arweave readback verifier failed", result);
  }

  return result;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const extraTags = parseExtraTags(args.extraTagsJson);
  const arweave = makeArweave(args.gatewayUrl);

  const payloadBytes = await fs.readFile(args.payloadFile);
  const payloadSha256 = sha256(payloadBytes);
  const payloadBytesLength = payloadBytes.length;

  const { jwk, derivedAddress } = await readJwkIfNeeded(args, arweave);
  const walletAddress = derivedAddress || args.walletAddress || null;

  if (derivedAddress && derivedAddress !== args.expectedOwner) {
    fail("Arweave JWK owner does not match expected Trinity owner", {
      derivedAddress,
      expectedOwner: args.expectedOwner,
      oldOwner: OLD_TRINITY_ARWEAVE_OWNER
    });
  }

  if (args.mode === "production" && !args.allowPaid) {
    fail("Production upload requested but ALLOW_PAID_ARWEAVE_CANARY is not true");
  }

  if (args.mode === "production" && !jwk) {
    fail("Production upload requires ARWEAVE_JWK_PATH");
  }

  if (args.mode === "production" && walletAddress !== args.expectedOwner) {
    fail("Production wallet address does not match expected owner", {
      walletAddress,
      expectedOwner: args.expectedOwner
    });
  }

  const uploadPrice = await getUploadPriceWinston(
    args,
    arweave,
    payloadBytesLength
  );

  const arUsd = await fetchArUsd(args);
  const estimatedAr = winstonToArDecimal(uploadPrice.winston);
  const estimatedUsd =
    decimalStringToNumber(estimatedAr) * Number(arUsd.price);
  const estimatedUsdWithBuffer = estimatedUsd * args.safetyMultiplier;

  const balanceBefore = await getWalletBalance(
    arweave,
    walletAddress,
    args.mode === "production"
  );

  let decision = "DRY_RUN";
  let reason = "dry_run";

  if (args.mode === "production") {
    if (estimatedUsdWithBuffer > args.effectiveMaxUploadUsd) {
      decision = "BLOCK";
      reason = "over_cap";
    } else {
      decision = "ALLOW";
      reason = "under_cap";
    }
  } else if (args.mode === "staging") {
    decision = "DRY_RUN";
    reason = "staging_no_paid_upload_in_first_round";
  }

  const costEstimate = {
    generated_at: nowIso(),
    run_id: args.runId,
    record_type: args.recordType,
    payload_file: args.payloadFile,
    payload_bytes: payloadBytesLength,
    payload_sha256: payloadSha256,
    gateway_url: args.gatewayUrl,
    wallet_address: walletAddress,
    expected_owner: args.expectedOwner,
    old_owner_not_used: OLD_TRINITY_ARWEAVE_OWNER,
    balance_before_available: balanceBefore.available,
    balance_before_reason: balanceBefore.reason,
    balance_before_winston: balanceBefore.winston,
    balance_before_ar: balanceBefore.ar,
    ar_usd_price: arUsd.price,
    ar_usd_price_source: arUsd.source,
    ar_usd_price_overridden: arUsd.overridden,
    estimated_upload_cost_winston: uploadPrice.winston,
    estimated_upload_cost_source: uploadPrice.source,
    estimated_upload_cost_overridden: uploadPrice.overridden,
    estimated_upload_cost_ar: estimatedAr,
    estimated_upload_cost_usd: Number(estimatedUsd.toFixed(8)),
    safety_multiplier: args.safetyMultiplier,
    estimated_upload_cost_usd_with_buffer: Number(
      estimatedUsdWithBuffer.toFixed(8)
    ),
    configured_max_upload_usd: args.maxUploadUsd,
    effective_max_upload_usd: args.effectiveMaxUploadUsd,
    mode: args.mode,
    allow_paid: args.allowPaid,
    decision,
    reason,
    extra_tags: extraTags
  };

  printCostCheck(costEstimate);

  await writeJson(
    path.join(args.logDir, `10-arweave-cost-estimate.${args.recordType}.json`),
    costEstimate
  );

  if (decision !== "ALLOW") {
    const blocked = {
      generated_at: nowIso(),
      run_id: args.runId,
      record_type: args.recordType,
      result: "not_uploaded",
      reason,
      tx_id: null,
      gateway_url: null
    };

    printUploadResult(blocked);

    await writeJson(
      path.join(args.logDir, `11-arweave-upload-result.${args.recordType}.json`),
      blocked
    );

    process.exit(args.mode === "production" && reason === "over_cap" ? 2 : 0);
  }

  const tx = await arweave.createTransaction({ data: payloadBytes }, jwk);
  const txRewardWinston = tx.reward ? String(tx.reward) : null;
  const txRewardAr = txRewardWinston ? winstonToArDecimal(txRewardWinston) : null;
  tx.addTag("Content-Type", args.contentType);
  tx.addTag("App-Name", args.appName);
  tx.addTag("Record-Type", args.recordType);
  tx.addTag("E2E-Run-Id", args.runId);
  tx.addTag("Payload-SHA256", payloadSha256);
  tx.addTag("Trinity-Arweave-Owner", args.expectedOwner);
  tx.addTag("Canary-Record", "true");
  tx.addTag("Do-Not-Treat-As-First-Real-Agent", "true");
  for (const tag of extraTags) {
    tx.addTag(tag.name, tag.value);
  }

  await arweave.transactions.sign(tx, jwk);

  const postStarted = Date.now();
  const postResult = await arweave.transactions.post(tx);

  if (postResult.status < 200 || postResult.status >= 300) {
    fail("Arweave transaction post failed", {
      status: postResult.status,
      statusText: postResult.statusText,
      data_preview:
        typeof postResult.data === "string"
          ? postResult.data.slice(0, 300)
          : postResult.data
    });
  }

  const txId = tx.id;
  const gatewayReadUrl = `${args.gatewayUrl.replace(/\/$/, "")}/${txId}`;

  const balanceAfter = await getWalletBalance(arweave, walletAddress, false);

  let actualDeltaWinston = null;
  let actualDeltaAr = null;
  let remainingBalanceEstimatedUsd = null;

  if (
    balanceBefore.winston &&
    balanceAfter.winston &&
    /^\d+$/.test(balanceBefore.winston) &&
    /^\d+$/.test(balanceAfter.winston)
  ) {
    const beforeBig = BigInt(balanceBefore.winston);
    const afterBig = BigInt(balanceAfter.winston);
    actualDeltaWinston = (beforeBig - afterBig).toString();
    actualDeltaAr = winstonToArDecimal(actualDeltaWinston);
  }

  if (balanceAfter.ar) {
    remainingBalanceEstimatedUsd =
      decimalStringToNumber(balanceAfter.ar) * Number(arUsd.price);
  }

  const uploadResult = {
    generated_at: nowIso(),
    run_id: args.runId,
    record_type: args.recordType,
    result: "uploaded",
    tx_id: txId,
    gateway_url: gatewayReadUrl,
    post_status: postResult.status,
    post_duration_ms: Date.now() - postStarted,
    payload_file: args.payloadFile,
    payload_bytes: payloadBytesLength,
    payload_sha256: payloadSha256,
    wallet_address: walletAddress,
    balance_before_available: balanceBefore.available,
    balance_before_winston: balanceBefore.winston,
    balance_before_ar: balanceBefore.ar,
    balance_after_available: balanceAfter.available,
    balance_after_reason: balanceAfter.reason,
    balance_after_winston: balanceAfter.winston,
    balance_after_ar: balanceAfter.ar,
    actual_delta_winston: actualDeltaWinston,
    actual_delta_ar: actualDeltaAr,
    upload_cost_winston: txRewardWinston,
    upload_cost_ar: txRewardAr,
    estimated_upload_cost_winston: uploadPrice.winston,
    estimated_upload_cost_ar: estimatedAr,
    estimated_cost_usd: Number(estimatedUsd.toFixed(8)),
    remaining_balance_estimated_usd:
      remainingBalanceEstimatedUsd == null
        ? null
        : Number(remainingBalanceEstimatedUsd.toFixed(8)),
    readback_required: true,
    extra_tags: extraTags
  };

  printUploadResult(uploadResult);

  await writeJson(
    path.join(args.logDir, `11-arweave-upload-result.${args.recordType}.json`),
    uploadResult
  );

  await runReadbackVerifier(args, txId, payloadSha256);
}

main().catch((error) => {
  console.error("[ARWEAVE COST GATE ERROR]");
  console.error(error.message);
  if (error.extra) {
    console.error(JSON.stringify(error.extra, null, 2));
  }
  process.exit(1);
});
