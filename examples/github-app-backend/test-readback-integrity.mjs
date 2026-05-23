#!/usr/bin/env node
/**
 * Tests for Gateway backend readback SHA256 helpers.
 *
 * Validates:
 * - validateReadbackSha256: missing, mismatch, valid, no-oath, signed
 * - maybeRepairUnsignedReadbackSha: auto-repair unsigned, skip signed
 */

import { createHash } from "node:crypto";
import assert from "node:assert/strict";

function sha256Text(s) {
  return createHash("sha256").update(s, "utf8").digest("hex");
}

// --- Inline the helpers from server.js for isolated testing ---

function getVerificationOath(payload) {
  return (payload?.agent_integrity_declaration?.verification_oath) || null;
}

function validateReadbackSha256(payload) {
  const oath = getVerificationOath(payload);
  if (!oath || typeof oath !== "object") return [];

  const readback = String(oath.agent_readback || "").trim();
  if (!readback) return [];

  const expected = sha256Text(readback);
  const actual = oath.agent_readback_sha256;
  const signed = !!payload?.authorship_proof?.signed_payload_sha256;

  if (!actual) {
    return [{
      code: "READBACK_SHA256_MISSING",
      path: "agent_integrity_declaration.verification_oath.agent_readback_sha256",
      field: "agent_readback_sha256",
      message: "agent_readback_sha256 is required and must equal sha256(agent_readback).",
      expected_sha256: expected,
      requires_resign: signed,
      fix: signed
        ? "This payload is signed. Re-run the correct builder or repair before signing."
        : "Set agent_readback_sha256 to the expected_sha256 value."
    }];
  }

  if (actual !== expected) {
    return [{
      code: "READBACK_SHA256_MISMATCH",
      path: "agent_integrity_declaration.verification_oath.agent_readback_sha256",
      field: "agent_readback_sha256",
      message: "agent_readback_sha256 does not match sha256(agent_readback).",
      actual_sha256: actual,
      expected_sha256: expected,
      requires_resign: signed,
      fix: signed
        ? "This payload is signed. Re-run the correct builder or repair before signing."
        : "Replace agent_readback_sha256 with expected_sha256."
    }];
  }

  return [];
}

function maybeRepairUnsignedReadbackSha(payload) {
  const oath = getVerificationOath(payload);
  if (!oath || typeof oath !== "object") return;
  if (payload?.authorship_proof?.signed_payload_sha256) return;

  const readback = String(oath.agent_readback || "").trim();
  if (!readback) return;
  oath.agent_readback_sha256 = sha256Text(readback);
}

// --- Tests ---

let passed = 0;
let failed = 0;

function test(name, fn) {
  try {
    fn();
    console.log(`  PASS: ${name}`);
    passed++;
  } catch (e) {
    console.log(`  FAIL: ${name}: ${e.message}`);
    failed++;
  }
}

test("missing hash returns READBACK_SHA256_MISSING", () => {
  const payload = {
    agent_integrity_declaration: {
      verification_oath: {
        agent_readback: "x".repeat(200),
      }
    }
  };
  const errors = validateReadbackSha256(payload);
  assert.equal(errors.length, 1);
  assert.equal(errors[0].code, "READBACK_SHA256_MISSING");
  assert.equal(errors[0].requires_resign, false);
});

test("mismatch returns READBACK_SHA256_MISMATCH", () => {
  const payload = {
    agent_integrity_declaration: {
      verification_oath: {
        agent_readback: "x".repeat(200),
        agent_readback_sha256: "0".repeat(64),
      }
    }
  };
  const errors = validateReadbackSha256(payload);
  assert.equal(errors.length, 1);
  assert.equal(errors[0].code, "READBACK_SHA256_MISMATCH");
});

test("valid hash returns no errors", () => {
  const readback = "I understand this oath and will act in good faith. ".repeat(5).trim();
  const payload = {
    agent_integrity_declaration: {
      verification_oath: {
        agent_readback: readback,
        agent_readback_sha256: sha256Text(readback),
      }
    }
  };
  const errors = validateReadbackSha256(payload);
  assert.equal(errors.length, 0);
});

test("no oath returns no errors", () => {
  const errors = validateReadbackSha256({ some_field: true });
  assert.equal(errors.length, 0);
});

test("no readback returns no errors", () => {
  const payload = {
    agent_integrity_declaration: {
      verification_oath: {
        oath_read: true,
      }
    }
  };
  const errors = validateReadbackSha256(payload);
  assert.equal(errors.length, 0);
});

test("signed missing hash has requires_resign=true", () => {
  const payload = {
    agent_integrity_declaration: {
      verification_oath: {
        agent_readback: "x".repeat(200),
      }
    },
    authorship_proof: {
      signed_payload_sha256: "a".repeat(64),
    }
  };
  const errors = validateReadbackSha256(payload);
  assert.equal(errors.length, 1);
  assert.equal(errors[0].code, "READBACK_SHA256_MISSING");
  assert.equal(errors[0].requires_resign, true);
});

test("maybeRepairUnsignedReadbackSha repairs unsigned payload", () => {
  const readback = "y".repeat(200);
  const payload = {
    agent_integrity_declaration: {
      verification_oath: {
        agent_readback: readback,
      }
    }
  };
  maybeRepairUnsignedReadbackSha(payload);
  assert.equal(
    payload.agent_integrity_declaration.verification_oath.agent_readback_sha256,
    sha256Text(readback)
  );
});

test("maybeRepairUnsignedReadbackSha skips signed payload", () => {
  const payload = {
    agent_integrity_declaration: {
      verification_oath: {
        agent_readback: "z".repeat(200),
      }
    },
    authorship_proof: {
      signed_payload_sha256: "a".repeat(64),
    }
  };
  maybeRepairUnsignedReadbackSha(payload);
  assert.equal(
    payload.agent_integrity_declaration.verification_oath.agent_readback_sha256,
    undefined
  );
});

test("maybeRepairUnsignedReadbackSha strips whitespace before hashing", () => {
  const readback = "  hello world  ";
  const payload = {
    agent_integrity_declaration: {
      verification_oath: {
        agent_readback: readback,
      }
    }
  };
  maybeRepairUnsignedReadbackSha(payload);
  assert.equal(
    payload.agent_integrity_declaration.verification_oath.agent_readback_sha256,
    sha256Text("hello world")
  );
});

test("roundtrip: repair then validate passes", () => {
  const readback = "I will act honestly. ".repeat(10);
  const payload = {
    agent_integrity_declaration: {
      verification_oath: {
        agent_readback: readback,
      }
    }
  };
  const before = validateReadbackSha256(payload);
  assert.equal(before.length, 1);

  maybeRepairUnsignedReadbackSha(payload);

  const after = validateReadbackSha256(payload);
  assert.equal(after.length, 0);
});

console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed > 0 ? 1 : 0);
