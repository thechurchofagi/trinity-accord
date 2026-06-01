#!/usr/bin/env node
export {
  DYNAMIC_PROOF_FIELDS as DYNAMIC_GUARDIAN_PROOF_FIELDS,
  GUARDIAN_REQUIRED_DOES_NOT_PROVE as REQUIRED_DOES_NOT_PROVE,
  sha256Text,
  stableStringify,
  normalizePem,
  publicKeySha256,
  guardianIdFromPublicKey,
  payloadWithoutDynamicProofs as payloadWithoutGuardianProof,
  canonicalPayloadForProof as canonicalPayloadForGuardianSignature,
  proofPayloadSha256 as guardianPayloadSha256,
  buildGuardianPresenceMessage,
  buildUnsignedGuardianProofFields,
} from "./proof_canonical.mjs";
