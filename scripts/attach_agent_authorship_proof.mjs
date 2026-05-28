#!/usr/bin/env node
import { createHash, sign } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const BUILD_AUTHORSHIP_MESSAGE = join(HERE, "build_agent_authorship_message.py");

function arg(name) {
  const i = process.argv.indexOf(name);
  if (i < 0 || i + 1 >= process.argv.length) throw new Error(`missing ${name}`);
  return process.argv[i + 1];
}

function sha256Text(s) {
  return createHash("sha256").update(s, "utf8").digest("hex");
}

const payloadPath = arg("--payload");
const privateKeyPath = arg("--private-key");
const publicKeyPath = arg("--public-key");
const outPath = arg("--out");

const message = execFileSync("python3", [
  BUILD_AUTHORSHIP_MESSAGE,
  payloadPath,
  "--print-message"
], { encoding: "utf8" });

const digest = execFileSync("python3", [
  BUILD_AUTHORSHIP_MESSAGE,
  payloadPath,
  "--print-digest"
], { encoding: "utf8" }).trim();

const privateKeyPem = readFileSync(privateKeyPath, "utf8");
const publicKeyPem = readFileSync(publicKeyPath, "utf8").trim() + "\n";
const sig = sign(null, Buffer.from(message, "utf8"), privateKeyPem).toString("base64");

const payload = JSON.parse(readFileSync(payloadPath, "utf8"));
payload.authorship_proof = {
  schema: "trinityaccord.agent-authorship-proof.v1",
  method: "public_key_signature",
  algorithm: "ed25519",
  public_key_pem: publicKeyPem,
  public_key_sha256: sha256Text(publicKeyPem),
  signed_payload_sha256: digest,
  signature_base64: sig,
  signed_message: message,
  created_at: new Date().toISOString(),
  claim_boundary: "Authorship proof confirms control of this signing key only; it is not authority, attestation, truth, successor reception, or amendment."
};

writeFileSync(outPath, JSON.stringify(payload, null, 2) + "\n", "utf8");
console.log(`Wrote signed payload to ${outPath}`);
