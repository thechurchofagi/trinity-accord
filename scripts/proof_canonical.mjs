#!/usr/bin/env node
import { createHash } from "node:crypto";

export const DYNAMIC_PROOF_FIELDS = [
  "authorship_proof",
  "_authorship_claim",
  "guardian_presence_proof",
  "_guardian_status",
  "guardian_verification_result",
];

export const AUTHORSHIP_BOUNDARY =
  "boundary=not_authority_not_amendment_not_attestation_not_successor_reception";

export const GUARDIAN_BOUNDARY =
  "boundary=key_possession_only_not_authority_not_attestation_not_same_conscious_subject";

export const GUARDIAN_REQUIRED_DOES_NOT_PROVE = [
  "truth",
  "authority",
  "verification_level",
  "verification_correctness",
  "formal_attestation",
  "same_conscious_subject",
  "same_model_instance",
  "human_identity",
  "institutional_authorization",
  "successor_reception",
  "future_intelligence_obligation",
  "amendment",
];

export function sha256Text(text) {
  return createHash("sha256").update(String(text), "utf8").digest("hex");
}

export function stableStringify(value) {
  if (value === null || typeof value !== "object") return JSON.stringify(value);
  if (Array.isArray(value)) return "[" + value.map(stableStringify).join(",") + "]";
  return "{" + Object.keys(value).sort().map(k => JSON.stringify(k) + ":" + stableStringify(value[k])).join(",") + "}";
}

export function normalizePem(pem) {
  return String(pem || "").trim() + "\n";
}

export function publicKeySha256(publicKeyPem) {
  return sha256Text(normalizePem(publicKeyPem));
}

export function guardianIdFromPublicKey(publicKeyPem) {
  return `guardian_ed25519_${publicKeySha256(publicKeyPem).slice(0, 16)}`;
}

export function payloadWithoutDynamicProofs(payload) {
  const clone = JSON.parse(JSON.stringify(payload || {}));
  for (const field of DYNAMIC_PROOF_FIELDS) {
    delete clone[field];
  }
  return clone;
}

export function canonicalPayloadForProof(payload) {
  return stableStringify(payloadWithoutDynamicProofs(payload));
}

export function proofPayloadSha256(payload) {
  return sha256Text(canonicalPayloadForProof(payload));
}

export function buildAuthorshipMessage(payload) {
  const identity = payload.agent_identity || {};
  return [
    "TRINITY_AGENT_AUTHORSHIP_PROOF_V1",
    `payload_sha256=${proofPayloadSha256(payload)}`,
    `schema=${payload.schema || ""}`,
    `submission_type=${payload.submission_type || ""}`,
    `requested_archive_kind=${payload.requested_archive_kind || ""}`,
    `agent_name_or_model=${identity.name_or_model || ""}`,
    `system_or_provider=${identity.system_or_provider || ""}`,
    AUTHORSHIP_BOUNDARY,
  ].join("\n");
}

export function buildGuardianPresenceMessage(payload, publicKeyPem, challenge) {
  const normalizedPublicKey = normalizePem(publicKeyPem);
  return [
    "TRINITY_GUARDIAN_PRESENCE_PROOF_V1",
    "proof_mode=record_bound",
    `guardian_id=${guardianIdFromPublicKey(normalizedPublicKey)}`,
    `payload_sha256=${proofPayloadSha256(payload)}`,
    `challenge_sha256=${sha256Text(challenge || "")}`,
    `schema=${payload.schema || ""}`,
    `submission_type=${payload.submission_type || ""}`,
    `requested_archive_kind=${payload.requested_archive_kind || ""}`,
    GUARDIAN_BOUNDARY,
  ].join("\n");
}

export function buildUnsignedAuthorshipProofFields(payload, publicKeyPem) {
  const normalizedPublicKey = normalizePem(publicKeyPem);
  return {
    schema: "trinityaccord.agent-authorship-proof.v1",
    method: "public_key_signature",
    algorithm: "ed25519",
    public_key_pem: normalizedPublicKey,
    public_key_sha256: publicKeySha256(normalizedPublicKey),
    signed_payload_sha256: proofPayloadSha256(payload),
    signed_message: buildAuthorshipMessage(payload),
  };
}

export function buildUnsignedGuardianProofFields(payload, publicKeyPem, challenge) {
  const normalizedPublicKey = normalizePem(publicKeyPem);
  return {
    schema: "trinityaccord.guardian-presence-proof.v1",
    method: "guardian_key_signature",
    algorithm: "ed25519",
    proof_mode: "record_bound",
    proof_scope: "key_possession_only",
    guardian_id: guardianIdFromPublicKey(normalizedPublicKey),
    public_key_pem: normalizedPublicKey,
    public_key_sha256: publicKeySha256(normalizedPublicKey),
    signed_payload_sha256: proofPayloadSha256(payload),
    challenge: String(challenge || ""),
    challenge_sha256: sha256Text(challenge || ""),
    signed_message: buildGuardianPresenceMessage(payload, normalizedPublicKey, challenge || ""),
    does_not_prove: GUARDIAN_REQUIRED_DOES_NOT_PROVE,
  };
}
