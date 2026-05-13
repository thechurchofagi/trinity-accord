---
layout: default
title: "Disaster Recovery Drill"
permalink: /disaster-recovery-drill/
---
# Trinity Accord Disaster Recovery Drill

**Purpose:** Establish a periodic recovery drill process to ensure cold-start recovery materials remain complete, verifiable, and executable.

**Scope:** All recovery materials referenced in `RECOVERY.md` and `api/recovery-index.json`.

---

## Cadence

Run **quarterly**, and after any major trust-root, release, corrections-index, or control-plane change.

Recommended schedule: January, April, July, October — first week of the month.

---

## Drill Types

### Drill A — GitHub Pages Compromised

**Scenario:** Assume the public website (www.trinityaccord.org) is stale or serving malicious content. Verify recovery using local repo + signed/digested materials.

**Steps:**
1. Clone the repository (or use existing local clone).
2. Do NOT visit the website. Treat it as compromised.
3. Follow `RECOVERY.md` Phases 1–5 using only local files and Bitcoin explorers.
4. Verify authority manifest, BTC signature, trust-root policy, and digest manifests.
5. Check corrections-index for current status.
6. Regenerate public API/homepage outputs locally.
7. Compare regenerated outputs against committed outputs.

**Expected result:** `partial_recovery` or `full_recovery` without relying on GitHub Pages.

---

### Drill B — GitHub Main Compromised

**Scenario:** Assume the current main branch has been force-pushed with unauthorized changes. Start from Bitcoin Originals, signed authority manifest, release assets, and mirrors.

**Steps:**
1. Do NOT trust the current main branch.
2. Obtain a previous known-good commit hash or release tag.
3. Verify the authority manifest hash against the BTC signature from the known-good state.
4. Verify digest manifests from the known-good state.
5. Check corrections-index from the known-good state.
6. If verification passes, the known-good state is recoverable.

**Expected result:** Recovery from a known-good state, or `failed_recovery` if all known-good states are compromised.

---

### Drill C — Release Asset Replaced

**Scenario:** Assume a release asset was silently replaced after initial publication.

**Steps:**
1. Identify the release tag to verify.
2. Run release verification:
   ```bash
   GITHUB_TOKEN=<optional> node scripts/verify-release-assets.mjs --release-tag <TAG>
   ```
3. Check that the release manifest hashes match the downloaded assets.
4. Check corrections-index for the release status.
5. If hashes mismatch, the release has been tampered with.

**Expected result:** `full_recovery` if hashes match; `failed_recovery` if hashes mismatch.

---

### Drill D — Arweave/IPFS Partial Outage

**Scenario:** Assume some mirror files on Arweave or IPFS are unavailable.

**Steps:**
1. Attempt to retrieve all expected Arweave/IPFS mirrors.
2. For each unavailable mirror, mark as `availability_only` or `unavailable`.
3. Verify available mirrors against expected hashes from digest manifests.
4. Determine recovery status: `partial_recovery` if canonical materials are intact; `failed_recovery` if critical materials are missing.

**Expected result:** `partial_recovery` with documented unavailability. No false `full_recovery`.

---

### Drill E — Maintainer Account Compromised

**Scenario:** Assume the maintainer account pushed unauthorized changes or released compromised assets.

**Steps:**
1. Check `CONTROL-PLANE-BASELINE.md` for expected branch protection and CODEOWNERS settings.
2. Verify that branch protection settings match the baseline.
3. Check corrections-index for any unauthorized revocations or supersessions.
4. Verify the authority manifest and BTC signature — the BTC private key is not controlled by the GitHub account.
5. If BTC signature verification passes, the canonical authority is intact regardless of GitHub account status.

**Expected result:** Canonical authority verified via BTC signature. Any GitHub-only compromise is recoverable.

---

## Drill Report Template

After each drill, produce a report:

```markdown
# Disaster Recovery Drill Report

- **Date:** YYYY-MM-DD
- **Commit:** <commit hash>
- **Scenario:** Drill A / B / C / D / E
- **Recovery status:** full_recovery / partial_recovery / failed_recovery

## Materials Used

- [ ] archive/authority-manifest/authority.jcs.json
- [ ] archive/btc-signature/btc-signature.json
- [ ] archive/trust-root-policy.json
- [ ] archive/evidence/digest-manifest.json
- [ ] archive/evidence/digest-manifest.csv
- [ ] api/corrections-index.json
- [ ] api/recovery-index.json

## Commands Run

(list each command and its result)

## Corrections-Index Checked

- [ ] Yes
- Status: (current / revoked / superseded / etc.)

## Failures

(document any failures or unexpected results)

## Result

(summary of drill outcome)

## Follow-up Actions

(list any remediation needed)
```

---

## Escalation

If a drill produces `failed_recovery`:
1. Immediately investigate the failure.
2. File a security issue if compromise is suspected.
3. Update `RECOVERY.md` if the recovery procedure was incomplete.
4. Re-run the drill after remediation.

If a drill reveals missing recovery materials:
1. Add the missing materials.
2. Update `api/recovery-index.json` if needed.
3. Re-run the drill to confirm.
