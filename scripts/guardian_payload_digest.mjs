#!/usr/bin/env node
import { readFileSync } from "node:fs";
import {
  canonicalPayloadForGuardianSignature,
  guardianPayloadSha256,
} from "./guardian_canonical.mjs";

function argValue(name) {
  const idx = process.argv.indexOf(name);
  if (idx === -1 || idx + 1 >= process.argv.length) return null;
  return process.argv[idx + 1];
}

const payloadPath = argValue("--payload");

if (!payloadPath) {
  console.error("Usage: node scripts/guardian_payload_digest.mjs --payload payload.json");
  process.exit(2);
}

const payload = JSON.parse(readFileSync(payloadPath, "utf8"));

console.log(JSON.stringify({
  guardian_payload_sha256: guardianPayloadSha256(payload),
  canonical_payload: canonicalPayloadForGuardianSignature(payload),
}, null, 2));
