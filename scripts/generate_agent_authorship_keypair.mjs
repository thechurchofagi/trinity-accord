#!/usr/bin/env node
import { generateKeyPairSync } from "node:crypto";
import { writeFileSync, mkdirSync } from "node:fs";
import { dirname } from "node:path";

const outPrefix = process.argv[2] || "agent-authorship-key";
const { publicKey, privateKey } = generateKeyPairSync("ed25519", {
  publicKeyEncoding: { type: "spki", format: "pem" },
  privateKeyEncoding: { type: "pkcs8", format: "pem" }
});

mkdirSync(dirname(outPrefix), { recursive: true });
writeFileSync(`${outPrefix}.public.pem`, publicKey, "utf8");
writeFileSync(`${outPrefix}.private.pem`, privateKey, { encoding: "utf8", mode: 0o600 });

console.log(`Wrote ${outPrefix}.public.pem`);
console.log(`Wrote ${outPrefix}.private.pem`);
console.log("WARNING: never submit, commit, paste, or upload the private key.");
