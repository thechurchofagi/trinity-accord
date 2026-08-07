#!/usr/bin/env node
import fs from "node:fs";
import process from "node:process";
import {ssz} from "@lodestar/types";
import {createProof, ProofType} from "@chainsafe/persistent-merkle-tree";

function hex(bytes) {
  return "0x" + Buffer.from(bytes).toString("hex");
}

if (process.argv.length !== 4) {
  console.error("usage: make_beacon_execution_proof.mjs <beacon-block.json> <out.json>");
  process.exit(2);
}

const input = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const fork = String(input.version || "").toLowerCase();
const forkTypes = ssz[fork];
if (!forkTypes?.BeaconBlockBody) {
  throw new Error(`unsupported beacon fork: ${fork}`);
}
const bodyJson = input?.data?.message?.body;
if (!bodyJson) throw new Error("missing beacon block body");
const bodyType = forkTypes.BeaconBlockBody;
const bodyValue = bodyType.fromJson(bodyJson);
const bodyView = bodyType.toView(bodyValue);
const {gindex} = bodyType.getPathInfo(["executionPayload", "blockHash"]);
const proof = createProof(bodyView.node, {type: ProofType.single, gindex});
if (proof.type !== ProofType.single) throw new Error("expected single proof");
const result = {
  schema: "trinityaccord.ethereum-beacon-execution-leaf-proof.v1",
  fork,
  gindex: proof.gindex.toString(),
  leaf: hex(proof.leaf),
  witnesses: proof.witnesses.map(hex),
  body_root: hex(bodyView.hashTreeRoot()),
};
fs.writeFileSync(process.argv[3], JSON.stringify(result, null, 2) + "\n");
