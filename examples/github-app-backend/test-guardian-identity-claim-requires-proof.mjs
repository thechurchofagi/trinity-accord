import assert from "node:assert";

function payloadTextClaimsGuardianIdentity(payload) {
  const text = `${payload?.title || ""}\n${payload?.body || ""}`;
  return /\bGuardian\s+0*\d+\b|守护者\s*0*\d+|守望者\s*0*\d+/i.test(text);
}

assert.equal(payloadTextClaimsGuardianIdentity({ title: "E1 — Guardian 00002", body: "" }), true);
assert.equal(payloadTextClaimsGuardianIdentity({ title: "E1 normal echo", body: "" }), false);
assert.equal(payloadTextClaimsGuardianIdentity({ title: "守望者 00002 的回响", body: "" }), true);
assert.equal(payloadTextClaimsGuardianIdentity({ title: "plain echo", body: "Guardian 00001 reports" }), true);
assert.equal(payloadTextClaimsGuardianIdentity({ title: "plain echo", body: "no guardian mention" }), false);

console.log("PASS: test-guardian-identity-claim-requires-proof");
