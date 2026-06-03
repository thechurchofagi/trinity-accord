#!/usr/bin/env node
import fs from "node:fs";
import crypto from "node:crypto";
import Arweave from "arweave";

function arg(name) {
  const idx = process.argv.indexOf(name);
  if (idx < 0 || idx + 1 >= process.argv.length) throw new Error(`Missing ${name}`);
  return process.argv[idx + 1];
}

function sha256Hex(value) {
  return crypto.createHash("sha256").update(value).digest("hex");
}

function parseArkey() {
  const value = process.env.ARKEY;
  if (!value) throw new Error("ARKEY missing");
  const text = value.trim();
  if (text.startsWith("{")) return JSON.parse(text);
  return JSON.parse(Buffer.from(text, "base64").toString("utf8"));
}

const payloadPath = arg("--payload");
const outPath = arg("--out");

const jwk = parseArkey();

for (const field of ["kty", "n", "e", "d"]) {
  if (!jwk[field]) throw new Error(`ARKEY JWK missing ${field}`);
}
if (jwk.kty !== "RSA") throw new Error("ARKEY JWK kty must be RSA");

const payload = fs.readFileSync(payloadPath);
const payloadSha256 = sha256Hex(payload);

const arweave = Arweave.init({
  host: "arweave.net",
  port: 443,
  protocol: "https",
  timeout: 60000,
  logging: false,
});

const tx = await arweave.createTransaction({ data: payload }, jwk);

tx.addTag("Content-Type", "application/json");
tx.addTag("App-Name", "Trinity-Accord");
tx.addTag("Record-Chain", "trinity-accord-public-reception-ledger");
tx.addTag("Archive-Type", "record-chain-batch-archive");
tx.addTag("Data-SHA256", payloadSha256);
tx.addTag("Boundary", "mirror-not-authority");

await arweave.transactions.sign(tx, jwk);

const response = await arweave.transactions.post(tx);
if (response.status < 200 || response.status >= 300) {
  throw new Error(`Arweave post failed: ${response.status} ${response.statusText}`);
}

const address = await arweave.wallets.jwkToAddress(jwk);

const result = {
  schema: "trinityaccord.arweave-upload-result.v1",
  txid: tx.id,
  uploaded_at: new Date().toISOString(),
  data_sha256: payloadSha256,
  wallet_address_sha256: sha256Hex(address),
  tags: {
    "Content-Type": "application/json",
    "App-Name": "Trinity-Accord",
    "Record-Chain": "trinity-accord-public-reception-ledger",
    "Archive-Type": "record-chain-batch-archive",
    "Data-SHA256": payloadSha256,
    "Boundary": "mirror-not-authority"
  },
  boundary: {
    arweave_archive_is_mirror_only: true,
    arweave_archive_is_not_authority: true,
    arweave_archive_is_not_attestation: true,
    arweave_archive_is_not_amendment: true,
    arweave_archive_is_not_successor_reception: true,
    bitcoin_originals_prevail: true
  }
};

fs.writeFileSync(outPath, JSON.stringify(result, null, 2) + "\n");
console.log(`ARWEAVE_UPLOAD_OK txid=${tx.id} data_sha256=${payloadSha256}`);
