#!/usr/bin/env node
import { sign } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";

function arg(name) {
  const i = process.argv.indexOf(name);
  if (i < 0 || i + 1 >= process.argv.length) throw new Error(`missing ${name}`);
  return process.argv[i + 1];
}

const messagePath = arg("--message");
const privateKeyPath = arg("--private-key");
const outPath = arg("--out");

const message = readFileSync(messagePath, "utf8");
const privateKeyPem = readFileSync(privateKeyPath, "utf8");
const sig = sign(null, Buffer.from(message, "utf8"), privateKeyPem).toString("base64");

writeFileSync(outPath, sig + "\n", "utf8");
console.log(`Wrote claim signature to ${outPath}`);
