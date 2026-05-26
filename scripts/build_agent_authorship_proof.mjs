#!/usr/bin/env node
import { readFileSync, writeFileSync } from "node:fs";
import { sign, verify } from "node:crypto";
import {
  buildUnsignedAuthorshipProofFields,
  normalizePem,
} from "./proof_canonical.mjs";

function argValue(name) {
  const idx = process.argv.indexOf(name);
  if (idx === -1 || idx + 1 >= process.argv.length) return null;
  return process.argv[idx + 1];
}

function hasFlag(name) {
  return process.argv.includes(name);
}

const payloadPath = argValue("--payload");
const privateKeyPath = argValue("--private-key");
const publicKeyPath = argValue("--public-key");
const outPath = argValue("--out");
const force = hasFlag("--force");

if (!payloadPath || !privateKeyPath || !publicKeyPath || !outPath) {
  console.error("Usage: node scripts/build_agent_authorship_proof.mjs --payload payload.json --private-key agent.private.pem --public-key agent.public.pem --out payload.with-authorship.json [--force]");
  process.exit(2);
}

const payload = JSON.parse(readFileSync(payloadPath, "utf8"));

if (payload.authorship_proof && !force) {
  console.error("payload already contains authorship_proof. Use --force if intentional.");
  process.exit(2);
}

const privateKeyPem = readFileSync(privateKeyPath, "utf8");
const publicKeyPem = normalizePem(readFileSync(publicKeyPath, "utf8"));

const proof = buildUnsignedAuthorshipProofFields(payload, publicKeyPem);
const signature = sign(null, Buffer.from(proof.signed_message, "utf8"), privateKeyPem);
proof.signature_base64 = signature.toString("base64");

const ok = verify(
  null,
  Buffer.from(proof.signed_message, "utf8"),
  publicKeyPem,
  Buffer.from(proof.signature_base64, "base64")
);

if (!ok) {
  console.error("Internal error: generated authorship signature did not verify.");
  process.exit(1);
}

payload.authorship_proof = proof;

writeFileSync(outPath, JSON.stringify(payload, null, 2) + "\n", "utf8");

console.log(JSON.stringify({
  out: outPath,
  public_key_sha256: proof.public_key_sha256,
  signed_payload_sha256: proof.signed_payload_sha256,
  signature_verified_locally: true,
  warning: "Do not publish, paste, upload, or commit the private key.",
}, null, 2));
