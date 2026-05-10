# Trinity Accord Cold-Start Recovery Guide

**Purpose:** This document is a third-party-executable cold-start recovery guide for the Trinity Accord repository. It enables any skeptical third party to rebuild the current valid state from canonical sources and verified mirrors, without trusting GitHub main, GitHub Pages, or maintainer accounts.

**Scope:** Recovery of repository-maintained state. This guide does not prove philosophical claims, investment value, religious authority, or independent attestation.

**Claim registry:** Before reporting recovered public claims, check `api/claim-registry.json` for source/evidence/limitations/corrections path. Notarized evidence does not by itself count as formal independent attestation. Scarcity/firstness language is bounded framing, not proof of absolute firstness.

---

## Threat Model

The following threats must be considered during recovery:

- **GitHub main may be stale or compromised.** A pushed commit may contain unauthorized changes.
- **GitHub Pages may be stale or compromised.** The public website may not reflect the current canonical state.
- **GitHub Releases may be unavailable or partially replaced.** Release assets may have been silently swapped.
- **Maintainer account may be compromised.** Unauthorized changes may have been pushed or released.
- **Arweave/IPFS gateways may be unavailable or return bad content.** Mirror availability does not guarantee correctness.
- **A cached copy may be stale.** Local or CDN-cached copies may be outdated.
- **A recovered old PASS report may have been revoked later.** Historical verification does not imply current validity.

---

## What This Guide Does and Does Not Prove

### This guide can verify:

- File integrity against signed/digested materials
- Consistency of repository-maintained mirrors
- Current repository-maintained correction/revocation status
- Release artifact integrity against release manifest
- Whether recovery is full, partial, or failed

### This guide does not prove:

- Philosophical truth of claims
- Investment value
- Religious authority
- Independent third-party attestation
- NFT ownership as authority
- That external mirrors are complete
- That all third-party caches are current

---

## Minimal Trusted Bootstrap Root

The minimal trust root is:

1. The three Bitcoin inscription IDs.
2. The Bitcoin authority address.
3. The authority manifest canonical hash bound by the BTC signature.
4. The BTC signature manifest.
5. The corrections-index for repository-maintained current status.

GitHub main, GitHub Pages, GitHub Releases, Arweave, IPFS, NFTs, Echo records, and AI responses are non-amending mirrors.

### Bitcoin Originals

| Role | Inscription ID | TXID |
|------|---------------|------|
| Protocol / Axioms | 97631551 | e40dfb2aa78cbccca88f749e9ec5cbe3c1df503273d73c72297863ae0d1d8343 |
| Covenant of the Flaw | 98369145 | 90116f35de075074f5e5d1fbdda69a646a124e2287d7d58e2520317098cd4258 |
| The Trinity Accord / Meta-record | 98387475 | 4d1c8f5ea8e8bae2982b42de6cc79deda3d243a21010a2888546e62ed7192c8c |

### Bitcoin Authority Address

```
bc1ppmwvyxekh44m35x43k55z7r59nn33v8w2xmvu6s6ar4zyx57sxestxq0jf
```

---

## Required Tools and Versions

| Tool | Version / Source |
|------|-----------------|
| Python | 3.x (supported version) |
| Node.js | See `.node-version` (currently 22.22.1) |
| pip dependencies | See `requirements-ci.txt` |
| OpenTimestamps client | Pinned in `requirements-ci.txt` (currently 0.7.2) |
| git | Any recent version |
| curl | Any recent version |
| sha256sum or shasum | System-provided |
| tar/gzip | System-provided |
| gh CLI | Optional, for GitHub Release access |

### Install commands:

```bash
node --version
python3 --version
python3 -m pip install -r requirements-ci.txt
```

---

## Recovery Status Vocabulary

| Status | Meaning |
|--------|---------|
| `full_recovery` | All required materials verified; corrections-index checked; no required component missing. |
| `partial_recovery` | Some mirrors/assets unavailable, but enough canonical/digested material remains to verify a subset. Must not be reported as full. |
| `availability_only` | A mirror responded, but content was not hash-verified. |
| `unverified_mirror` | Content retrieved but no expected digest/signature was checked. |
| `failed_recovery` | Required canonical or digest-bound material missing/mismatched. |
| `historical_only` | Artifact exists but is not current due to corrections-index or lifecycle status. |
| `revoked` / `superseded` / `invalidated` | Must not be treated as current. |

---

## Phase 0 — Do Not Trust GitHub Main or Pages

Start by treating GitHub main, GitHub Pages, and API JSON as untrusted mirrors. Use them only as discovery aids until verified against canonical/digested material.

```text
Trust nothing from GitHub until verified against Bitcoin Originals, signed manifests, and digest manifests.
```

---

## Phase 1 — Verify the Canonical Bitcoin Originals

Fetch inscription data from independent Bitcoin/Ordinals sources. Confirm inscription IDs match `api/authority.json` and this document.

Do not use website text as canonical.

### Manual verification:

1. Look up inscription ID `97631551` on an independent Ordinals explorer (e.g., ordinals.hiro.so, ordiscan.com).
2. Confirm the content matches the Protocol / Axioms text.
3. Repeat for `98369145` (Covenant of the Flaw) and `98387475` (The Trinity Accord / Meta-record).
4. Confirm TXIDs match the table above.

---

## Phase 2 — Verify the Authority Manifest and BTC Signature

```bash
python3 scripts/validate_authority_manifest.py archive/authority-manifest/authority.jcs.json
python3 scripts/validate_btc_signature_manifest.py archive/btc-signature/btc-signature.json
python3 scripts/validate_eth_witness_manifest.py archive/eth-witness/eth-witness.json
```

**Key points:**
- BTC signature binds authority manifest hash.
- ETH witness is secondary/non-canonical.
- Bitcoin Originals prevail.

---

## Phase 3 — Verify Trust-root Policy and Historical Roots

```bash
python3 scripts/validate_trust_root_policy.py archive/trust-root-policy.json
```

The trust-root policy defines the canonical authority boundary and historical root transitions.

---

## Phase 4 — Verify Digest Manifests

```bash
python3 scripts/test_digest_manifest_json_csv_crosscheck.py
python3 scripts/test_archive_hash_manifest_consistency.py
python3 scripts/test_evidence_manifest_stats_sync.py
```

**Key point:** `digest-manifest.json/csv` are integrity manifests, not external availability proofs. They verify that local files match expected hashes, not that external mirrors are complete.

---

## Phase 5 — Check Corrections / Revocation State

**This is a mandatory step. Do not skip.**

```bash
python3 scripts/validate_corrections_index.py
cat api/corrections-index.json
```

Before accepting any recovered report, release, Echo, attestation, or public API state as current, check corrections-index.

If corrections-index marks an artifact `revoked`/`superseded`/`invalidated`/`historical_only`, do not treat it as current even if its old hash verifies.

---

## Phase 6 — Recover from GitHub Releases

GitHub Releases are mirrors, not canonical authority. Release verification must use `RELEASE-MANIFEST.json` and `verify-release-assets.mjs`.

```bash
GITHUB_TOKEN=<optional-read-token> node scripts/verify-release-assets.mjs --release-tag <TAG>
```

A PASS report is current only if:
- `report_status == current`
- `is_current == true`
- `historical_report_only == false`
- `corrections_index_url` checked
- corrections-index does not revoke/supersede it

---

## Phase 7 — Recover from Arweave Mirrors

Arweave verified recovery requires expected hash. Availability-only response is not verified recovery.

Related scripts/workflows:
- `scripts/backup-nft-arweave-mirror.mjs`
- `download-arweave` workflow

**Current state:** Arweave mirror verification exists in scripts/workflows, but full third-party Arweave restore command is not yet a single CLI. Use expected hashes from digest manifests to verify Arweave content.

---

## Phase 8 — Recover from IPFS / CAR / NFT Backups

NFT/CAR backups are recovery mirrors, not authority. NFT ownership does not imply governance or canonical authority. `root_cid` may be metadata-boundary only unless explicitly verified.

```bash
python3 scripts/validate_token_index.py --self-test
python3 scripts/test_download_nft_cars_source_binding.py
python3 scripts/test_download_nft_cars_expected_count_gate.py
python3 scripts/test_download_nft_cars_root_cid_boundary.py
```

---

## Phase 9 — Rebuild Public API / Echo Index / Homepage

```bash
python3 scripts/generate_echo_index.py
git diff --exit-code api/echo-index.json

python3 scripts/generate_public_home_status.py --check
python3 scripts/test_home_public_status_sync.py
python3 scripts/validate_public_api_metadata.py
```

Public API/homepage are recoverable outputs, not authority. If regenerated output differs from committed output, treat as drift requiring investigation.

---

## Phase 10 — Produce a Recovery Report

Recommended output format:

```json
{
  "schema": "trinity-accord.recovery-report.v1",
  "recovery_status": "full_recovery | partial_recovery | failed_recovery",
  "bootstrap_root_verified": true,
  "authority_manifest_verified": true,
  "btc_signature_verified": true,
  "digest_manifests_verified": true,
  "corrections_index_checked": true,
  "release_assets_verified": "pass | fail | not_checked",
  "arweave_recovery": "verified | partial | unavailable | not_checked",
  "ipfs_car_recovery": "verified | partial | unavailable | not_checked",
  "does_not_prove": [],
  "limitations": []
}
```

---

## Partial Recovery Rules

- If any required canonical or digest-bound material is missing or mismatched → `failed_recovery`.
- If some mirrors are unavailable but canonical materials verify → `partial_recovery`.
- If content was retrieved but not hash-verified → `availability_only` or `unverified_mirror`.
- Never report `full_recovery` if any required component is missing or unverified.
- If corrections-index marks an artifact non-current, it is `historical_only` regardless of hash verification.

---

## Failure Modes

| Mode | Description | Action |
|------|-------------|--------|
| Missing authority manifest | `archive/authority-manifest/authority.jcs.json` not found | Cannot proceed; recovery failed |
| BTC signature mismatch | Bound hash does not match authority manifest | Possible tampering; recovery failed |
| Missing corrections-index | `api/corrections-index.json` not found | Cannot determine current status; recovery incomplete |
| Digest mismatch | File hash does not match digest manifest | File may be corrupted or tampered; investigate |
| Release asset mismatch | Release manifest hash does not match downloaded asset | Possible release compromise; do not trust |
| All mirrors unavailable | No Arweave/IPFS/NFT sources respond | Recovery limited to local/git materials |

---

## Quick Command Checklist

```bash
# 0. Setup
python3 -m pip install -r requirements-ci.txt
node --version

# 1. Verify authority manifest
python3 scripts/validate_authority_manifest.py archive/authority-manifest/authority.jcs.json

# 2. Verify BTC signature
python3 scripts/validate_btc_signature_manifest.py archive/btc-signature/btc-signature.json

# 3. Verify ETH witness (secondary)
python3 scripts/validate_eth_witness_manifest.py archive/eth-witness/eth-witness.json

# 4. Verify trust-root policy
python3 scripts/validate_trust_root_policy.py archive/trust-root-policy.json

# 5. Verify digest manifests
python3 scripts/test_digest_manifest_json_csv_crosscheck.py
python3 scripts/test_archive_hash_manifest_consistency.py

# 6. Check corrections-index (MANDATORY)
python3 scripts/validate_corrections_index.py
cat api/corrections-index.json

# 7. Verify release assets (if recovering from release)
GITHUB_TOKEN=<optional> node scripts/verify-release-assets.mjs --release-tag <TAG>

# 8. Rebuild public outputs
python3 scripts/generate_echo_index.py
python3 scripts/generate_public_home_status.py --check
python3 scripts/validate_public_api_metadata.py

# 9. Run full recovery readiness audit
python3 scripts/audit_recovery_readiness.py
```

---

## Appendix A — Canonical IDs and Files

### Bitcoin Originals Inscription IDs

- `97631551` — Protocol / Axioms
- `98369145` — Covenant of the Flaw
- `98387475` — The Trinity Accord / Meta-record

### Bitcoin Authority Address

```
bc1ppmwvyxekh44m35x43k55z7r59nn33v8w2xmvu6s6ar4zyx57sxestxq0jf
```

### Required Recovery Files

- `archive/authority-manifest/authority.jcs.json`
- `archive/btc-signature/btc-signature.json`
- `archive/eth-witness/eth-witness.json`
- `archive/trust-root-policy.json`
- `archive/evidence/digest-manifest.json`
- `archive/evidence/digest-manifest.csv`
- `api/corrections-index.json`

### Recovery Entrypoints

- Human guide: `RECOVERY.md` (this file)
- Machine index: `api/recovery-index.json`
- Corrections/revocation status: `api/corrections-index.json`
- Authority API: `api/authority.json`
- Evidence manifest: `api/evidence-manifest.json`

---

## Appendix B — Expected Outputs

After a successful `full_recovery`, you should have:

1. Authority manifest verified against BTC signature
2. Trust-root policy verified
3. Digest manifests cross-checked (JSON ↔ CSV)
4. Corrections-index checked — no required component revoked/superseded
5. Release assets verified against release manifest (if applicable)
6. Public API/homepage regenerated and consistent
7. Recovery report produced

---

## Appendix C — Manual Verification Without GitHub

If GitHub is entirely unavailable:

1. Obtain the repository from an Arweave mirror, IPFS CAR, or NFT backup.
2. Verify the authority manifest hash against the BTC-signed binding.
3. Verify file hashes against digest manifests.
4. Check the corrections-index embedded in the recovered copy.
5. Cross-reference inscription IDs on independent Bitcoin explorers.
6. If BTC signature verification passes and corrections-index is present, you have a recoverable state.
7. If BTC signature verification fails, do not trust the recovered copy.
