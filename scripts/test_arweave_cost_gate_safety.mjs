#!/usr/bin/env node

import fs from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { spawn } from "node:child_process";

const CURRENT_OWNER = "r1EdzCQ9E7CaAOEywI5netR6EcSopNOa08oi2Coz68s";

async function mkTmpDir() {
  const root = process.env.RUNNER_TEMP || "/tmp";
  const dir = path.join(root, `trinity-arweave-cost-gate-test-${Date.now()}`);
  await fs.mkdir(dir, { recursive: true });
  return dir;
}

function runNode(args, env = {}) {
  return new Promise((resolve) => {
    const child = spawn(process.execPath, args, {
      stdio: ["ignore", "pipe", "pipe"],
      env: { ...process.env, ...env }
    });

    let stdout = "";
    let stderr = "";

    child.stdout.on("data", (d) => {
      stdout += String(d);
    });

    child.stderr.on("data", (d) => {
      stderr += String(d);
    });

    child.on("close", (code) => {
      resolve({ code, stdout, stderr });
    });
  });
}

async function main() {
  const dir = await mkTmpDir();
  const payloadFile = path.join(dir, "payload.json");
  const logDir = path.join(dir, "logs");

  await fs.mkdir(logDir, { recursive: true });

  await fs.writeFile(
    payloadFile,
    JSON.stringify(
      {
        test_run: true,
        canary_record: true,
        message: "arweave cost gate safety test"
      },
      null,
      2
    ),
    "utf8"
  );

  const result = await runNode(
    [
      "scripts/arweave_cost_gate.mjs",
      "--payload-file",
      payloadFile,
      "--record-type",
      "echo",
      "--run-id",
      "unit-arweave-cost-gate",
      "--log-dir",
      logDir,
      "--mode",
      "dry_run"
    ],
    {
      ARWEAVE_UPLOAD_MODE: "dry_run",
      ALLOW_PAID_ARWEAVE_CANARY: "false",
      ARWEAVE_MAX_UPLOAD_USD: "0.10",
      ARWEAVE_WALLET_ADDRESS: CURRENT_OWNER,
      ARWEAVE_UPLOAD_PRICE_WINSTON_OVERRIDE: "1000",
      AR_USD_PRICE_OVERRIDE: "10"
    }
  );

  if (result.code !== 0) {
    console.error(result.stdout);
    console.error(result.stderr);
    throw new Error(`dry-run cost gate failed with exit code ${result.code}`);
  }

  if (!result.stdout.includes("[ARWEAVE COST CHECK]")) {
    throw new Error("missing cost check log");
  }

  if (!result.stdout.includes("decision: DRY_RUN")) {
    throw new Error("dry-run did not report DRY_RUN decision");
  }

  const estimateFile = path.join(logDir, "10-arweave-cost-estimate.echo.json");
  const uploadFile = path.join(logDir, "11-arweave-upload-result.echo.json");

  const estimate = JSON.parse(await fs.readFile(estimateFile, "utf8"));
  const upload = JSON.parse(await fs.readFile(uploadFile, "utf8"));

  if (estimate.expected_owner !== CURRENT_OWNER) {
    throw new Error("expected owner address mismatch");
  }

  if (estimate.ar_usd_price_overridden !== true) {
    throw new Error("test did not use AR_USD_PRICE_OVERRIDE");
  }

  if (estimate.estimated_upload_cost_overridden !== true) {
    throw new Error("test did not use ARWEAVE_UPLOAD_PRICE_WINSTON_OVERRIDE");
  }

  if (upload.result !== "not_uploaded") {
    throw new Error("dry-run unexpectedly uploaded");
  }

  if (upload.tx_id !== null) {
    throw new Error("dry-run produced tx_id");
  }

  console.log("PASS: arweave cost gate dry-run safety");
}

main().catch((error) => {
  console.error("FAIL: arweave cost gate safety");
  console.error(error.message);
  process.exit(1);
});
