#!/usr/bin/env node

import fs from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import crypto from "node:crypto";
import http from "node:http";
import { spawn } from "node:child_process";

function sha256(bytes) {
  return crypto.createHash("sha256").update(bytes).digest("hex");
}

async function mkTmpDir() {
  const root = process.env.RUNNER_TEMP || "/tmp";
  const dir = path.join(root, `trinity-arweave-readback-test-${Date.now()}`);
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

function startFixtureServer(expectedTxId, bytesToServe) {
  const server = http.createServer((req, res) => {
    if (req.url === `/${expectedTxId}`) {
      res.writeHead(200, {
        "content-type": "application/json",
        "cache-control": "no-store"
      });
      res.end(bytesToServe);
      return;
    }

    res.writeHead(404, { "content-type": "text/plain" });
    res.end("not found");
  });

  return new Promise((resolve) => {
    server.listen(0, "127.0.0.1", () => {
      const { port } = server.address();
      resolve({
        server,
        gateway: `http://127.0.0.1:${port}`
      });
    });
  });
}

async function main() {
  const dir = await mkTmpDir();
  const logDir = path.join(dir, "logs");
  await fs.mkdir(logDir, { recursive: true });

  const expectedPayload = Buffer.from(
    JSON.stringify({ ok: true, payload: "expected" }, null, 2),
    "utf8"
  );

  const wrongPayload = Buffer.from(
    JSON.stringify({ ok: false, payload: "wrong" }, null, 2),
    "utf8"
  );

  const expectedFile = path.join(dir, "expected.json");
  await fs.writeFile(expectedFile, expectedPayload);

  const expectedSha = sha256(expectedPayload);
  const txId = "fixture_tx_1234567890abcdefghijklmnop";

  const { server, gateway } = await startFixtureServer(txId, wrongPayload);

  try {
    const result = await runNode(
      [
        "scripts/verify_arweave_upload_readback.mjs",
        "--tx-id",
        txId,
        "--expected-file",
        expectedFile,
        "--expected-sha256",
        expectedSha,
        "--record-type",
        "echo",
        "--run-id",
        "unit-readback-hash-fixture",
        "--log-dir",
        logDir
      ],
      {
        ARWEAVE_READBACK_GATEWAYS: gateway,
        ARWEAVE_READBACK_TIMEOUT_SECONDS: "2",
        ARWEAVE_READBACK_RETRY_SECONDS: "1"
      }
    );

    if (result.code === 0) {
      console.error(result.stdout);
      console.error(result.stderr);
      throw new Error("hash mismatch fixture unexpectedly passed");
    }

    if (!result.stdout.includes("reason: hash_mismatch")) {
      console.error(result.stdout);
      console.error(result.stderr);
      throw new Error("hash mismatch reason not printed");
    }

    const readbackLog = JSON.parse(
      await fs.readFile(
        path.join(logDir, "11b-arweave-readback-verify.echo.json"),
        "utf8"
      )
    );

    if (readbackLog.result !== "fail") {
      throw new Error("readback log did not record fail");
    }

    if (readbackLog.reason !== "hash_mismatch") {
      throw new Error("readback log did not record hash_mismatch");
    }

    console.log("PASS: arweave readback hash mismatch fixture");
  } finally {
    server.close();
  }
}

main().catch((error) => {
  console.error("FAIL: arweave readback hash fixture");
  console.error(error.message);
  process.exit(1);
});
