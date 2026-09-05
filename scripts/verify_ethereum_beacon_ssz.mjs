#!/usr/bin/env node
/** Offline SSZ/root/execution-payload verification for captured Beacon blocks. */
import fs from "node:fs";
import path from "node:path";
import {createHash} from "node:crypto";
import {ssz} from "@lodestar/types";

function hex(bytes) {
  return "0x" + Buffer.from(bytes).toString("hex");
}

function sha256(raw) {
  return createHash("sha256").update(raw).digest("hex");
}

function executionHash(block) {
  const body = block.data.message.body;
  const payload = body.execution_payload ?? body.executionPayload;
  return String(payload?.block_hash ?? payload?.blockHash ?? "").toLowerCase();
}

const root = process.argv[2];
if (!root) throw new Error("usage: verify_ethereum_beacon_ssz.mjs <evidence-dir>");
const reportPath = path.join(root, "ETHEREUM-BEACON-FINALITY.json");
const report = JSON.parse(fs.readFileSync(reportPath, "utf8"));
if (report.schema !== "trinity-accord/chronicle-ethereum-beacon-finality/v1" || report.pass !== true) {
  throw new Error("unexpected or non-PASS finality report");
}
let checked = 0;
for (const claim of report.claims) {
  const forkTypes = ssz[claim.ssz_fork];
  if (!forkTypes?.SignedBeaconBlock || !forkTypes?.BeaconBlock) {
    throw new Error(`unsupported Lodestar fork ${claim.ssz_fork}`);
  }
  const raw = fs.readFileSync(path.join(root, claim.ssz_file));
  const digest = sha256(raw);
  if (digest !== claim.ssz_sha256) throw new Error(`SSZ SHA-256 mismatch block=${claim.execution_block_number}`);
  const signed = forkTypes.SignedBeaconBlock.deserialize(raw);
  const beaconRoot = hex(forkTypes.BeaconBlock.hashTreeRoot(signed.message));
  const executionHash = hex(signed.message.body.executionPayload.blockHash);
  if (Number(signed.message.slot) !== claim.beacon_slot) throw new Error(`slot mismatch block=${claim.execution_block_number}`);
  if (beaconRoot !== claim.beacon_root) throw new Error(`beacon root mismatch block=${claim.execution_block_number}`);
  if (executionHash !== claim.execution_block_hash) throw new Error(`execution hash mismatch block=${claim.execution_block_number}`);
  if (claim.provider_quorum < 2 || claim.observations.some((x) => x.finalized !== true || x.execution_optimistic !== false)) {
    throw new Error(`finality quorum mismatch block=${claim.execution_block_number}`);
  }
  const providers = new Set();
  const endpoints = new Set();
  for (const observation of claim.observations) {
    if (path.basename(observation.provider) !== observation.provider) throw new Error("unsafe provider path");
    providers.add(observation.provider);
    endpoints.add(observation.endpoint);
    const providerDir = path.join(root, "claims", String(claim.execution_block_number), observation.provider);
    const headerRaw = fs.readFileSync(path.join(providerDir, "header.json"));
    const blockRaw = fs.readFileSync(path.join(providerDir, "block.json"));
    if (sha256(headerRaw) !== observation.header_sha256 || sha256(blockRaw) !== observation.block_json_sha256) {
      throw new Error(`provider object SHA-256 mismatch provider=${observation.provider}`);
    }
    const header = JSON.parse(headerRaw);
    const block = JSON.parse(blockRaw);
    if (header.data.root.toLowerCase() !== claim.beacon_root || Number(header.data.header.message.slot) !== claim.beacon_slot) {
      throw new Error(`provider header mismatch provider=${observation.provider}`);
    }
    if (Number(block.data.message.slot) !== claim.beacon_slot || executionHash(block) !== claim.execution_block_hash) {
      throw new Error(`provider block mismatch provider=${observation.provider}`);
    }
    if (header.finalized !== true || block.finalized !== true || header.execution_optimistic !== false || block.execution_optimistic !== false) {
      throw new Error(`provider finality fields mismatch provider=${observation.provider}`);
    }
  }
  if (providers.size < 2 || endpoints.size < 2 || claim.provider_quorum !== claim.observations.length) {
    throw new Error(`independent provider population mismatch block=${claim.execution_block_number}`);
  }
  checked++;
}
if (checked !== report.summary.execution_blocks || report.summary.polygon_checkpoint_blocks !== 117) {
  throw new Error(`claim population mismatch expected=${report.summary.execution_blocks} verified=${checked}`);
}
console.log(`[BEACON SSZ OFFLINE PASS] blocks=${checked} roots=${checked} execution_payloads=${checked}`);
