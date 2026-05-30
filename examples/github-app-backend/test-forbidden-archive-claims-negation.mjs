import assert from "node:assert";

function splitSentences(text) {
  // Join continuation lines: newline + lowercase letter → single space
  const joined = String(text || "").replace(/\n(?=[a-zà-ÿ])/g, " ");
  return joined
    .split(/(?<=[.!?。！？])\s+|\n+/)
    .map(s => s.trim())
    .filter(Boolean);
}

function sentenceHasNegatedBoundary(sentence, claim) {
  const s = sentence.toLowerCase();
  if (claim === "successor_reception") {
    return (
      /\bnot\s+(a\s+)?successor reception\b/i.test(s)
      || /\bdoes\s+not\s+(claim|constitute|create|count as)\s+(a\s+)?successor reception\b/i.test(s)
      || /\bremains\s+not\s+(a\s+)?successor reception\b/i.test(s)
      || /\bnot\s+claiming\s+.*successor reception\b/i.test(s)
    );
  }
  if (claim === "authority") {
    return (
      /\bnot\s+authority\b/i.test(s)
      || /\bnot\s+authoritative\b/i.test(s)
      || /\bnot\s+claiming\s+.*\b(authority|authoritative)\b/i.test(s)
      || /\bnot\s+(this\s+)?is\s+(an?\s+)?(authority|authoritative)\b/i.test(s)
    );
  }
  if (claim === "attestation") {
    return (
      /\bnot\s+(an\s+)?attestation\b/i.test(s)
      || /\bnot\s+claiming\s+.*\battestation\b/i.test(s)
      || /\bnot\s+(this\s+)?is\s+(an?\s+)?attestation\b/i.test(s)
    );
  }
  if (claim === "amendment") {
    return (
      /\bnot\s+(an\s+)?amendment\b/i.test(s)
      || /\bnon-amending\b/i.test(s)
      || /\bnot\s+claiming\s+.*\bamendment\b/i.test(s)
      || /\bnot\s+(this\s+)?is\s+(an?\s+)?amendment\b/i.test(s)
    );
  }
  return false;
}

/** Global check kept for backward compat but should NOT be used for security. */
function hasAllowedNegatedBoundary(text, claim) {
  return sentenceHasNegatedBoundary(text, claim);
}

const FORBIDDEN_POSITIVE_CLAIM_PATTERNS = [
  {
    code: "FORBIDDEN_SUCCESSOR_RECEPTION_CLAIM",
    claim: "successor_reception",
    pattern: /\b(this|this record|this echo|i|we)\s+(is|are|claims?|constitutes|creates?|counts as|requests?)\s+(a\s+)?successor reception\b/i
  },
  {
    code: "FORBIDDEN_AUTHORITY_CLAIM",
    claim: "authority",
    pattern: /\b(this|this record|this echo|i|we)\s+(is|are|claims?|constitutes|creates?|counts as|requests?)\s+(authority|authoritative)\b/i
  },
  {
    code: "FORBIDDEN_ATTESTATION_CLAIM",
    claim: "attestation",
    pattern: /\b(this|this record|this echo|i|we)\s+(is|are|claims?|constitutes|creates?|counts as|requests?)\s+(an\s+)?attestation\b/i
  },
  {
    code: "FORBIDDEN_AMENDMENT_CLAIM",
    claim: "amendment",
    pattern: /\b(this|this record|this echo|i|we)\s+(is|are|claims?|constitutes|creates?|counts as|requests?)\s+(an\s+)?amendment\b/i
  }
];

function findForbiddenPositiveArchiveClaims(text) {
  const sentences = splitSentences(text);
  const hits = [];
  for (const spec of FORBIDDEN_POSITIVE_CLAIM_PATTERNS) {
    // Check each sentence independently: a negated phrase in one sentence
    // does NOT exempt a positive claim in another sentence.
    const hasPositiveClaim = sentences.some(
      s => spec.pattern.test(s) && !sentenceHasNegatedBoundary(s, spec.claim)
    );
    if (hasPositiveClaim) {
      hits.push(spec);
    }
  }
  return hits;
}

// Allowed (negated boundary language)
assert.equal(findForbiddenPositiveArchiveClaims("This record remains not successor reception.").length, 0);
assert.equal(findForbiddenPositiveArchiveClaims("This echo does not claim successor reception.").length, 0);
assert.equal(findForbiddenPositiveArchiveClaims("This is not authority.").length, 0);
assert.equal(findForbiddenPositiveArchiveClaims("This is not attestation.").length, 0);
assert.equal(findForbiddenPositiveArchiveClaims("This is non-amending.").length, 0);

// Blocked (positive claims)
assert.equal(findForbiddenPositiveArchiveClaims("This record is successor reception.").length, 1);
assert.equal(findForbiddenPositiveArchiveClaims("I claim successor reception.").length, 1);
assert.equal(findForbiddenPositiveArchiveClaims("This echo is authoritative.").length, 1);
assert.equal(findForbiddenPositiveArchiveClaims("This record is an attestation.").length, 1);
assert.equal(findForbiddenPositiveArchiveClaims("This is an amendment.").length, 1);

// Mixed: negated sentence + positive sentence in same text → MUST be blocked
assert.equal(
  findForbiddenPositiveArchiveClaims(
    "This record remains not successor reception. This record is successor reception."
  ).length, 1,
  "negated + positive in same text must still block"
);
assert.equal(
  findForbiddenPositiveArchiveClaims(
    "This is not authority.\nThis record is authority."
  ).length, 1,
  "negated + positive (newline-separated) must still block"
);
assert.equal(
  findForbiddenPositiveArchiveClaims(
    "This is not an attestation. This record is an attestation."
  ).length, 1,
  "negated + positive attestation must still block"
);

// All negated across sentences → still allowed
assert.equal(
  findForbiddenPositiveArchiveClaims(
    "This is not successor reception. This does not claim authority."
  ).length, 0,
  "all-negated multi-sentence text is allowed"
);

console.log("PASS: test-forbidden-archive-claims-negation");

// Cross-line continuation: "I am not claiming authority,\namendment, or successor reception."
assert.equal(
  findForbiddenPositiveArchiveClaims(
    "I am not claiming verification, attestation,\nauthority, amendment, or successor reception. Bitcoin Originals remain final."
  ).length, 0,
  "cross-line negated coordinated list must be allowed"
);

assert.equal(
  findForbiddenPositiveArchiveClaims(
    "This is a pure recognition Echo. I am not claiming verification, attestation,\nauthority, amendment, or successor reception. Bitcoin Originals remain final."
  ).length, 0,
  "cross-line negated boundary in echo body must be allowed"
);

console.log("PASS: test-forbidden-archive-claims-negation (cross-line)");

// "not claiming this is authority" pattern (negation with intervening words)
assert.equal(
  findForbiddenPositiveArchiveClaims(
    "I am not claiming this is authority, amendment, or successor reception."
  ).length, 0,
  "'not claiming this is authority' must be allowed"
);

assert.equal(
  findForbiddenPositiveArchiveClaims(
    "I am not claiming this is authority. Bitcoin Originals remain final."
  ).length, 0,
  "'not claiming this is authority' (standalone) must be allowed"
);

console.log("PASS: test-forbidden-archive-claims-negation (not-claiming-pattern)");
