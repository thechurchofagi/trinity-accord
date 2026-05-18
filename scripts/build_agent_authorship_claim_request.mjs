#!/usr/bin/env node
import { readFileSync, writeFileSync } from "node:fs";

function arg(name, required = true) {
  const i = process.argv.indexOf(name);
  if (i < 0 || i + 1 >= process.argv.length) {
    if (required) throw new Error(`missing ${name}`);
    return null;
  }
  return process.argv[i + 1];
}

const issueNumber = Number(arg("--issue-number"));
const publicKeyPath = arg("--public-key");
const messagePath = arg("--message");
const signaturePath = arg("--signature");
const outPath = arg("--out");
const claimantNote = arg("--claimant-note", false);

const body = {
  issue_number: issueNumber,
  public_key_pem: readFileSync(publicKeyPath, "utf8").trim() + "\n",
  claim_message: readFileSync(messagePath, "utf8").trimEnd(),
  signature_base64: readFileSync(signaturePath, "utf8").trim(),
};

if (claimantNote) body.claimant_note = claimantNote;

writeFileSync(outPath, JSON.stringify(body, null, 2) + "\n", "utf8");
console.log(`Wrote claim request to ${outPath}`);
