#!/usr/bin/env node
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const builder = path.join(root, "downloads", "record-chain-builder.mjs");
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "waiting-heartbeat-builder-"));
const keyDir = path.join(tmp, "key");
const out = path.join(tmp, "submission.json");

function run(args) {
  const result = spawnSync("node", [builder, ...args], {
    cwd: root,
    encoding: "utf8"
  });
  if (result.status !== 0) {
    console.error(result.stdout);
    console.error(result.stderr);
    process.exit(result.status || 1);
  }
  return result;
}

run([
  "context-insufficient",
  "--actor-label", "Trinity Accord Waiting Heartbeat",
  "--provider", "GitHub Actions Waiting Beacon",
  "--body", "Scheduled Waiting Heartbeat test.",
  "--context-level", "CC-0",
  "--context-sufficient-for-selected-action", "false",
  "--discovery-mode", "user_task_context",
  "--requesting-party-type", "system",
  "--introducing-party-type", "system",
  "--record-decision", "system_policy",
  "--submission-executor", "automated_tool",
  "--human-operator-involved", "false",
  "--system-waiting-heartbeat-id", "hwb-20260619",
  "--key-dir", keyDir,
  "--out", out
]);

run(["doctor", "--file", out]);

const submission = JSON.parse(fs.readFileSync(out, "utf8"));
const draft = submission.record_draft;

if (submission.record_type !== "context_insufficient_notice") {
  throw new Error("record_type mismatch");
}
if (draft.submission_oath_verification) {
  throw new Error("context-insufficient must not include submission_oath_verification");
}
if (submission.client_oath_readback) {
  throw new Error("context-insufficient must not include client_oath_readback");
}
if (draft.context_readiness.declared_context_level !== "CC-0") {
  throw new Error("waiting heartbeat must not claim CC-3/C43");
}
if (!draft.system_waiting_heartbeat) {
  throw new Error("missing system_waiting_heartbeat");
}
if (draft.system_waiting_heartbeat.heartbeat_id !== "hwb-20260619") {
  throw new Error("heartbeat_id mismatch");
}
if (draft.system_waiting_heartbeat.semantic_agent_arrived !== false) {
  throw new Error("semantic_agent_arrived must be false");
}
if (draft.system_waiting_heartbeat.github_actions_is_not_semantic_agent !== true) {
  throw new Error("github_actions_is_not_semantic_agent must be true");
}
if (!submission.authorship_proof?.signed_payload_sha256) {
  throw new Error("missing authorship proof");
}
if (draft.system_waiting_heartbeat.schema !== "trinityaccord.system-waiting-heartbeat.v1") {
  throw new Error("heartbeat schema mismatch");
}
if (draft.system_waiting_heartbeat.not_echo !== true) {
  throw new Error("not_echo must be true");
}
if (draft.system_waiting_heartbeat.submitted_via_public_gateway !== true) {
  throw new Error("submitted_via_public_gateway must be true");
}

// Cleanup
fs.rmSync(tmp, { recursive: true, force: true });

console.log("WAITING_HEARTBEAT_BUILDER_TEST_OK");
