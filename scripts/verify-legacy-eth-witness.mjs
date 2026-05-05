#!/usr/bin/env node
/**
 * verify-legacy-eth-witness.mjs
 *
 * Verifies the legacy ETH witness record:
 *   archive/eth-witness/eth-witness.json
 *
 * This witness is separate from the authority.jcs.json ethereum.attestations[]
 * strict verifier. It specifically witnesses the BTC BIP-340 signature package.
 *
 * Output:
 *   LEGACY-ETH-WITNESS-AUDIT.json
 *
 * Required:
 *   Node 20+ or 22+
 *
 * Optional:
 *   ETH_RPC_URL. If unset, uses the rpc field in eth-witness.json.
 */

import fs from "fs";
import path from "path";
import crypto from "crypto";

const ROOT = process.cwd();
const WITNESS_PATH = path.join(ROOT, "archive/eth-witness/eth-witness.json");
const OUT_PATH = path.join(ROOT, "LEGACY-ETH-WITNESS-AUDIT.json");

function sha256hex(buf) {
  return crypto.createHash("sha256").update(buf).digest("hex");
}

function readJson(p) {
  return JSON.parse(fs.readFileSync(p, "utf8"));
}

function hexToBytes(hex) {
  const s = String(hex || "");
  if (!s.startsWith("0x")) throw new Error("input is not 0x-prefixed");
  const clean = s.slice(2);
  if (!/^[0-9a-fA-F]*$/.test(clean)) throw new Error("input has non-hex chars");
  if (clean.length % 2 !== 0) throw new Error("input has odd hex length");
  return Buffer.from(clean, "hex");
}

async function rpcCall(rpcUrl, method, params) {
  const res = await fetch(rpcUrl, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({jsonrpc: "2.0", id: 1, method, params})
  });
  if (!res.ok) throw new Error(`RPC HTTP ${res.status}`);
  const json = await res.json();
  if (json.error) throw new Error(`RPC ${method} error: ${json.error.message || JSON.stringify(json.error)}`);
  return json.result;
}

async function main() {
  const audit = {
    schema: "trinityaccord.legacy-eth-witness-audit.v1",
    generated_at: new Date().toISOString(),
    witness_path: "archive/eth-witness/eth-witness.json",
    legacy_eth_witness_pass: false,
    tx_hash: null,
    expected_from: null,
    expected_to: null,
    observed_from: null,
    observed_to: null,
    tx_exists: false,
    receipt_success: false,
    block_confirmed: false,
    input_len_expected: null,
    input_len_observed: null,
    input_len_match: false,
    input_sha256_expected: null,
    input_sha256_observed: null,
    input_sha256_match: false,
    chain_id_expected: null,
    chain_id_observed: null,
    chain_id_match: null,
    errors: []
  };

  try {
    if (!fs.existsSync(WITNESS_PATH)) throw new Error(`missing ${WITNESS_PATH}`);
    const witness = readJson(WITNESS_PATH);

    const rpcUrl = process.env.ETH_RPC_URL || witness.rpc;
    if (!rpcUrl) throw new Error("ETH_RPC_URL missing and witness.rpc unavailable");

    audit.tx_hash = witness.tx_hash;
    audit.expected_from = String(witness.from || "").toLowerCase();
    audit.expected_to = String(witness.to || "").toLowerCase();
    audit.input_len_expected = Number(witness.input_len);
    audit.input_sha256_expected = String(witness.input_sha256 || "").toLowerCase();
    audit.chain_id_expected = String(witness.chainId || "");

    if (!audit.tx_hash) throw new Error("witness tx_hash missing");
    if (!audit.expected_from) throw new Error("witness from missing");
    if (!audit.expected_to) throw new Error("witness to missing");
    if (!Number.isFinite(audit.input_len_expected)) throw new Error("witness input_len invalid");
    if (!/^[a-f0-9]{64}$/.test(audit.input_sha256_expected)) throw new Error("witness input_sha256 invalid");

    const tx = await rpcCall(rpcUrl, "eth_getTransactionByHash", [audit.tx_hash]);
    if (!tx) throw new Error("transaction not found");
    audit.tx_exists = true;

    audit.observed_from = String(tx.from || "").toLowerCase();
    audit.observed_to = String(tx.to || "").toLowerCase();
    audit.chain_id_observed = tx.chainId ? String(parseInt(tx.chainId, 16)) : null;

    if (audit.chain_id_expected && audit.chain_id_observed) {
      audit.chain_id_match = audit.chain_id_expected === audit.chain_id_observed;
    }

    if (audit.observed_from !== audit.expected_from) throw new Error(`from mismatch: expected ${audit.expected_from}, observed ${audit.observed_from}`);
    if (audit.observed_to !== audit.expected_to) throw new Error(`to mismatch: expected ${audit.expected_to}, observed ${audit.observed_to}`);

    const input = tx.input || tx.data || "0x";
    const inputBytes = hexToBytes(input);
    audit.input_len_observed = inputBytes.length;
    audit.input_sha256_observed = sha256hex(inputBytes);
    audit.input_len_match = audit.input_len_observed === audit.input_len_expected;
    audit.input_sha256_match = audit.input_sha256_observed === audit.input_sha256_expected;

    if (!audit.input_len_match) throw new Error(`input length mismatch: expected ${audit.input_len_expected}, observed ${audit.input_len_observed}`);
    if (!audit.input_sha256_match) throw new Error(`input sha256 mismatch: expected ${audit.input_sha256_expected}, observed ${audit.input_sha256_observed}`);

    const receipt = await rpcCall(rpcUrl, "eth_getTransactionReceipt", [audit.tx_hash]);
    if (!receipt) throw new Error("receipt not found");
    audit.receipt_success = receipt.status === "0x1";
    audit.block_confirmed = Boolean(receipt.blockNumber);

    if (!audit.receipt_success) throw new Error("receipt status is not success");
    if (!audit.block_confirmed) throw new Error("transaction not confirmed");

    audit.legacy_eth_witness_pass = true;
  } catch (e) {
    audit.errors.push(String(e.message || e));
  }

  fs.writeFileSync(OUT_PATH, JSON.stringify(audit, null, 2));
  console.log(`wrote ${OUT_PATH}`);
  if (!audit.legacy_eth_witness_pass) {
    console.error("LEGACY ETH WITNESS FAIL");
    console.error(audit.errors.join("\n"));
    process.exit(1);
  }
  console.log("LEGACY ETH WITNESS PASS");
}

main().catch(e => {
  console.error(e);
  process.exit(1);
});
