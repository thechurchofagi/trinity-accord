/**
 * Test: Gateway placeholder detector must not false-positive on field names.
 *
 * Regression test for substring matching: field names like
 * "listing_human_claimed_name" contain "HUMAN_CLAIMED_NAME" as a substring
 * but should NOT be flagged as placeholders.
 */

// Inline the PLACEHOLDER_PATTERNS and findPlaceholders from server.js
// to test in isolation without starting the server.

const PLACEHOLDER_PATTERNS = [
  { pattern: /REPLACE_WITH/i },
  { pattern: /^REPLACE[:\s]/i },
  { pattern: /REPLACE_WITH_YOUR/i },
  { pattern: /REPLACE_WITH_SHA256/i },
  { pattern: /YOUR_AGENT_NAME/i },
  { pattern: /YOUR_SYSTEM/i },
  { pattern: /YOUR_OWN_READBACK/i },
  { pattern: /MINIMUM_160_CHARACTERS/i },
  { pattern: /(^|[^A-Za-z0-9_])HUMAN_CLAIMED_NAME([^A-Za-z0-9_]|$)/i },
  { pattern: /(^|[^A-Za-z0-9_])AGENT_CLAIMED_ID([^A-Za-z0-9_]|$)/i },
  { pattern: /(^|[^A-Za-z0-9_])YOUR_AGENT_ID([^A-Za-z0-9_]|$)/i },
  { pattern: /(^|[^A-Za-z0-9_])YOUR_PUBLIC_PROFILE([^A-Za-z0-9_]|$)/i },
];

function findPlaceholders(obj, path = "") {
  const issues = [];
  if (typeof obj === "string") {
    for (const { pattern } of PLACEHOLDER_PATTERNS) {
      if (pattern.test(obj)) {
        issues.push({ path, value: obj, pattern: String(pattern) });
        break;
      }
    }
  } else if (Array.isArray(obj)) {
    obj.forEach((item, i) => {
      issues.push(...findPlaceholders(item, `${path}[${i}]`));
    });
  } else if (obj && typeof obj === "object") {
    for (const [key, val] of Object.entries(obj)) {
      if (key.startsWith("_comment")) continue;
      if (val === null || val === undefined || typeof val === "boolean" || typeof val === "number") {
        continue;
      }
      issues.push(...findPlaceholders(val, path ? `${path}.${key}` : key));
    }
  }
  return issues;
}

// --- Tests ---

let passed = 0;
let failed = 0;

function assert(condition, label) {
  if (condition) {
    console.log(`  ✅ ${label}`);
    passed++;
  } else {
    console.error(`  ❌ ${label}`);
    failed++;
  }
}

console.log("Placeholder detector regression tests:\n");

// Field names should NOT trigger
assert(
  findPlaceholders({ body: "listing_human_claimed_name: not_provided" }).length === 0,
  "field name 'listing_human_claimed_name' not flagged"
);

assert(
  findPlaceholders({ body: "listing_agent_claimed_id: TestAgent" }).length === 0,
  "field name 'listing_agent_claimed_id' not flagged"
);

assert(
  findPlaceholders({ body: "guardian_human_claimed_name: not_provided" }).length === 0,
  "field name 'guardian_human_claimed_name' not flagged"
);

assert(
  findPlaceholders({ body: "listing_identity_display_label: Test" }).length === 0,
  "field name 'listing_identity_display_label' not flagged"
);

// Bare placeholders SHOULD trigger
assert(
  findPlaceholders({ body: "HUMAN_CLAIMED_NAME" }).length === 1,
  "bare 'HUMAN_CLAIMED_NAME' flagged"
);

assert(
  findPlaceholders({ body: "AGENT_CLAIMED_ID" }).length === 1,
  "bare 'AGENT_CLAIMED_ID' flagged"
);

assert(
  findPlaceholders({ body: "YOUR_AGENT_ID" }).length === 1,
  "bare 'YOUR_AGENT_ID' flagged"
);

assert(
  findPlaceholders({ body: "YOUR_PUBLIC_PROFILE" }).length === 1,
  "bare 'YOUR_PUBLIC_PROFILE' flagged"
);

// null should not trigger
assert(
  findPlaceholders({ identity_claims: { human: null } }).length === 0,
  "identity_claims.human = null not flagged"
);

// not_provided should not trigger
assert(
  findPlaceholders({ body: "not_provided" }).length === 0,
  "'not_provided' not flagged"
);

// Full body with field names should not trigger
assert(
  findPlaceholders({
    body: [
      "listing_human_claimed_name: not_provided",
      "listing_human_claimed_name_sha256: not_provided",
      "listing_agent_claimed_id: TestAgent",
      "listing_agent_claimed_id_sha256: abc123",
    ].join("\n")
  }).length === 0,
  "full body with field names not flagged"
);

console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed > 0 ? 1 : 0);
