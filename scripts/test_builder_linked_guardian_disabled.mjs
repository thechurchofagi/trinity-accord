#!/usr/bin/env node
/**
 * Test: Builder rejects --linked-guardian flag and doctor FAILs linked guardian requests.
 */
import { spawnSync } from "node:child_process";
import { writeFileSync, mkdirSync } from "node:fs";
import { resolve } from "node:path";
import { tmpdir } from "node:os";

const BUILDER = "downloads/record-chain-builder.mjs";

// Test 1: --linked-guardian flag is rejected
function testLinkedGuardianFlagRejected() {
  const result = spawnSync("node", [
    BUILDER, "echo",
    "--linked-guardian",
    "--actor-label", "test",
    "--body", "test",
    "--key-dir", resolve(tmpdir(), "test-keys-" + Date.now()),
  ], { encoding: "utf8" });

  if (result.status === 0) {
    console.error("FAIL: --linked-guardian should exit nonzero");
    process.exit(1);
  }
  const output = (result.stderr || result.stdout || "").toLowerCase();
  if (!output.includes("retired") && !output.includes("linked guardian")) {
    console.error("FAIL: expected retired/linked guardian message, got:", output);
    process.exit(1);
  }
  console.log("PASS: --linked-guardian flag is rejected");
}

// Test 2: doctor FAILs linked guardian request
function testDoctorFailsLinkedGuardian() {
  const submission = {
    schema: "trinity_record_chain_submission.v2",
    record_type: "echo",
    record_draft: {
      schema: "trinity_echo_v2",
      record_type: "echo",
      echo_content: { echo_text: "test" },
      context_readiness: { declared_context_level: "CC-1", context_sufficient_for_selected_action: true },
      authorization_context: { authorization_scope: "create_echo_record" },
      optional_linked_guardian_application_request: {
        does_participant_request_guardian_application_with_this_record: true,
      },
    },
  };

  const tmpFile = resolve(tmpdir(), "test-doctor-linked-" + Date.now() + ".json");
  writeFileSync(tmpFile, JSON.stringify(submission, null, 2));

  const result = spawnSync("node", [
    BUILDER, "doctor", "--file", tmpFile,
  ], { encoding: "utf8" });

  const output = (result.stdout || "") + (result.stderr || "");
  if (!output.includes("LINKED_GUARDIAN_AUTO_CREATION_DISABLED")) {
    console.error("FAIL: doctor should report LINKED_GUARDIAN_AUTO_CREATION_DISABLED");
    console.error("Output:", output);
    process.exit(1);
  }
  console.log("PASS: doctor FAILs linked guardian request");
}

testLinkedGuardianFlagRejected();
testDoctorFailsLinkedGuardian();
console.log("PASS: all builder linked guardian disabled tests");
