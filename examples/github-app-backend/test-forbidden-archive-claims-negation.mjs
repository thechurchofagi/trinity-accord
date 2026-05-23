import assert from "node:assert";

function hasAllowedNegatedBoundary(text, claim) {
  const t = String(text || "").toLowerCase();
  if (claim === "successor_reception") {
    return (
      /\bnot\s+(a\s+)?successor reception\b/i.test(t)
      || /\bdoes\s+not\s+(claim|constitute|create|count as)\s+(a\s+)?successor reception\b/i.test(t)
      || /\bremains\s+not\s+(a\s+)?successor reception\b/i.test(t)
    );
  }
  if (claim === "authority") {
    return /\bnot\s+authority\b/i.test(t) || /\bnot\s+authoritative\b/i.test(t);
  }
  if (claim === "attestation") {
    return /\bnot\s+(an\s+)?attestation\b/i.test(t);
  }
  if (claim === "amendment") {
    return /\bnot\s+(an\s+)?amendment\b/i.test(t) || /\bnon-amending\b/i.test(t);
  }
  return false;
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
  const hits = [];
  for (const spec of FORBIDDEN_POSITIVE_CLAIM_PATTERNS) {
    if (spec.pattern.test(text) && !hasAllowedNegatedBoundary(text, spec.claim)) {
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

console.log("PASS: test-forbidden-archive-claims-negation");
