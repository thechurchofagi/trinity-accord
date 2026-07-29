#!/usr/bin/env node
import assert from "node:assert/strict";
import crypto from "node:crypto";
import fs from "node:fs/promises";
import http from "node:http";
import os from "node:os";
import path from "node:path";
import { spawn } from "node:child_process";

function sha256(bytes) {
  return crypto.createHash("sha256").update(bytes).digest("hex");
}

function runNode(args, env = {}) {
  return new Promise((resolve) => {
    const child = spawn(process.execPath, args, {
      env: { ...process.env, ...env },
      stdio: ["ignore", "pipe", "pipe"]
    });
    let stdout = "";
    let stderr = "";
    child.stdout.on("data", (chunk) => { stdout += chunk; });
    child.stderr.on("data", (chunk) => { stderr += chunk; });
    child.on("close", (code) => resolve({ code, stdout, stderr }));
  });
}

const temp = await fs.mkdtemp(path.join(os.tmpdir(), "trinity-readback-test-"));
const expected = Buffer.from('{"ok":true,"payload":"canonical"}\n');
const expectedFile = path.join(temp, "payload.json");
const logDir = path.join(temp, "logs");
await fs.writeFile(expectedFile, expected);

let requestCount = 0;
const server = http.createServer((req, res) => {
  requestCount += 1;
  if (requestCount === 1) {
    res.statusCode = 404;
    res.setHeader("Content-Type", "text/plain");
    res.end("not propagated");
    return;
  }
  if (requestCount === 2) {
    res.statusCode = 200;
    res.setHeader("Content-Type", "application/json");
    res.end('{"status":"pending"}');
    return;
  }
  res.statusCode = 200;
  res.setHeader("Content-Type", "application/json");
  res.end(expected);
});
await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
const address = server.address();
const gateway = `http://127.0.0.1:${address.port}`;

try {
  const result = await runNode([
    path.resolve("scripts/verify_arweave_upload_readback.mjs"),
    "--tx-id=-validLeadingDashTransactionId_1234567890",
    "--expected-file", expectedFile,
    "--expected-sha256", sha256(expected),
    "--record-type", "native_ots_proof_bundle",
    "--run-id", "test-readback",
    "--log-dir", logDir,
    "--gateway", gateway,
    "--timeout-seconds", "3",
    "--retry-seconds", "0.05",
    "--request-timeout-seconds", "1"
  ], { ARWEAVE_READBACK_GATEWAYS: gateway });

  assert.equal(result.code, 0, result.stderr || result.stdout);
  const report = JSON.parse(await fs.readFile(
    path.join(logDir, "11b-arweave-readback-verify.native_ots_proof_bundle.json"),
    "utf8"
  ));
  assert.equal(report.result, "pass");
  assert.equal(report.hash_match, true);
  assert.equal(report.attempts, 3);
  assert.equal(report.attempts_log[1].provisional_mismatch, true);
  console.log("PASS: transient 2xx mismatch is retried and leading-dash tx id is accepted");
} finally {
  await new Promise((resolve) => server.close(resolve));
  await fs.rm(temp, { recursive: true, force: true });
}
