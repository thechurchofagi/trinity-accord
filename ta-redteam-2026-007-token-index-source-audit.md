# TA-REDTEAM-2026-007 Recovery Package / token_index Source-of-Truth Integrity Audit

## Executive Summary

- **Date**: 2026-05-10
- **Commit SHA**: `fd499dbdaa02ae49715354388e45ecb8cb852c61`
- **Auditor**: MiMo (OpenClaw sandbox)
- **Workspace status**: clean
- **Tracked diff**: clean
- **Baseline status**: 12/12 tests PASS

## Scope

Audited `scripts/download-nft-cars.mjs` (producer), `scripts/verify-dag-and-signed-cids.mjs`, `scripts/verify-full-evidence-chain.mjs`, `scripts/verify-release-assets.mjs`, and associated artifacts (`recovery-package.bin`, `token_index.json`, `digest-manifest.json`, `authority.jcs.json`, `RELEASE-MANIFEST.json`).

## Key Question

> Can malformed, ambiguous, incomplete, duplicate, or unauthenticated token_index source data cause a fully verified-looking release for the wrong expected set?

**Answer: YES.** Multiple high/critical findings confirm that the producer-side pipeline can be coerced into generating a verified-looking release from a manipulated or incomplete source-of-truth.

---

## Findings Overview

| ID | Severity | Title | Status |
|---|---:|---|---|
| SRC-TOKEN-001 | **Critical** | extractTokenIndex() selects largest JSON, no fail-closed on multiple candidates | Confirmed |
| SRC-COUNT-001 | **Critical** | Producer has no EXPECTED_NFTS enforcement; trusts token_index count | Confirmed |
| SRC-BIND-001 | **High** | recovery-package.bin not in digest-manifest; producer skips digest/authority binding | Confirmed |
| SRC-DUPTXID-001 | **High** | collectTxids() Map(txid) silently overwrites duplicate txid provenance | Confirmed |
| SRC-CAR-001 | **High** | Producer-side CAR parser has no bounds checks; catch {} hides malformed blocks | Confirmed |
| SRC-SCHEMA-001 | **Medium** | No dedicated token_index schema validator | Confirmed |
| SRC-TRACE-001 | **Medium** | RELEASE-MANIFEST.json lacks source recovery package / token_index digest | Confirmed |
| SRC-H1 | **Medium** | root_cid treated as metadata; producer never verifies it | Confirmed |

---

## Confirmed Findings

### SRC-TOKEN-001 — extractTokenIndex() selects largest JSON by key count

**Severity**: Critical
**Affected script**: `scripts/download-nft-cars.mjs`, lines 185–230
**Input / fixture**: Recovery CAR containing multiple token-index-like JSON objects
**Trusted output affected**: `tokenIndex` → drives all downstream txid collection, verification, and release manifest
**Expected behavior**: Fail closed if zero or multiple token_index-like candidates exist, or require a canonical path/CID
**Actual behavior**: Scans all CAR blocks for `{...}` objects, checks if any key's value has `metadata` or `media` child, then selects the candidate with the most top-level keys. Attacker can inject a larger decoy JSON with more keys.
**Impact**: An attacker who can substitute the recovery package can inject a larger JSON object with 176+ fake NFT entries that will be selected as the source-of-truth. The producer will then download, verify (against the fake's own expected hashes), and release a fully verified-looking backup of a wrong dataset.
**Evidence**:
```javascript
// download-nft-cars.mjs:185-228
function extractTokenIndex(carPath) {
  const raw = fs.readFileSync(carPath);
  let bestObj = null;
  let bestKeyCount = 0;
  for (const block of iterCarBlocks(raw)) {
    // ... scans for JSON objects ...
    if (isTokenIndex && keys.length > bestKeyCount) {
      bestObj = obj;        // ← LARGEST wins, no uniqueness check
      bestKeyCount = keys.length;
    }
  }
  if (bestObj) return bestObj;
  throw new Error('token_index.json not found in CAR');
}
```
**Recommended fix**: Require exactly one token_index candidate (fail if >1), or better, look up token_index by CID/path from the CAR header rather than scanning all blocks.
**Code modified**: No

---

### SRC-COUNT-001 — Producer has no EXPECTED_NFTS constant; trusts token_index count

**Severity**: Critical
**Affected script**: `scripts/download-nft-cars.mjs`, main()
**Trusted output affected**: `actual_nfts` field in manifest and release manifest; `all_verified` flag
**Expected behavior**: Producer should independently know the expected NFT count (e.g., 175) and fail if token_index provides a different count
**Actual behavior**: Producer computes `totalTokens` from `extractTokenIndex()` result and uses it directly. No `EXPECTED_NFTS` constant exists in the producer. The verifier scripts (`verify-dag-and-signed-cids.mjs`, `verify-full-evidence-chain.mjs`) enforce `EXPECTED_NFTS = 175`, but the producer does not.
**Impact**: If a substituted recovery package contains a token_index with only 174 NFTs (or 176), the producer will happily generate `all_verified=true` with `actual_nfts=174`. Downstream verifier catches this, but the release is already published.
**Evidence**:
```javascript
// download-nft-cars.mjs main() — no EXPECTED_NFTS
const index = extractTokenIndex(CAR_FILE);
const totalTokens = contracts.reduce((n, c) => n + Object.keys(index[c]).length, 0);
// totalTokens is trusted directly — no check against expected value
```
vs. verifier:
```javascript
// verify-dag-and-signed-cids.mjs:52
const EXPECTED_NFTS = 175;
// line 1345
if (totalNfts !== EXPECTED_NFTS) { err(`❌ Expected ${EXPECTED_NFTS}, found ${totalNfts}`); process.exit(1); }
```
**Recommended fix**: Add `const EXPECTED_NFTS = 175;` to producer and fail if `totalTokens !== EXPECTED_NFTS`.
**Code modified**: No

---

### SRC-BIND-001 — recovery-package.bin not bound by digest/authority chain at producer

**Severity**: High
**Affected script**: `scripts/download-nft-cars.mjs`
**Trusted output affected**: All expected values derived from token_index
**Expected behavior**: Producer should verify `recovery-package.bin` SHA-256 against `digest-manifest.json` before using it as source-of-truth
**Actual behavior**: `recovery-package.bin` is NOT listed in `digest-manifest.json` or `digest-manifest.csv`. `verify-full-evidence-chain.mjs` has zero references to recovery-package. The producer reads the file directly from a hardcoded path without any integrity check. The `archive/hash-manifest.json` does list it, but the producer doesn't consult that either.
**Impact**: If an attacker can substitute the recovery package file (e.g., via a compromised CI artifact, supply chain attack on Arweave download, or local file replacement), the entire pipeline proceeds without detecting the substitution.
**Evidence**:
```bash
$ grep -R "recovery-package.bin" archive/evidence/digest-manifest.json
# (no results)

$ grep "recovery-package" scripts/verify-full-evidence-chain.mjs
# (no results)
```
**Recommended fix**: Add `recovery-package.bin` to `digest-manifest.json`; have producer verify its SHA-256 before use.
**Code modified**: No

---

### SRC-DUPTXID-001 — collectTxids() silently overwrites duplicate txid provenance

**Severity**: High
**Affected script**: `scripts/download-nft-cars.mjs`, lines 232–255
**Trusted output affected**: `txids` Map; per-file provenance in manifest; `total_car_files` count
**Expected behavior**: If the same txid is referenced by multiple contracts/tokens/roles, all references should be preserved, or conflicting expected values should fail closed
**Actual behavior**: `txids.set(meta.txid, {...})` overwrites the previous entry. If txid X is metadata for token A and media for token B, only the last reference survives. No conflict detection for differing expected hash/size/root_cid.
**Impact**: (a) Provenance loss — manifest only shows one reference per txid. (b) If duplicate txids have conflicting expected hash/size, the last writer wins and the downloaded file may fail the wrong expected value. (c) `total_car_files` equals unique txid count, which may be less than logical NFT file count.
**Evidence**:
```javascript
// download-nft-cars.mjs:237-254
function collectTxids(index) {
  const txids = new Map();
  for (const [contract, tokens] of Object.entries(index)) {
    for (const [token_id, entry] of Object.entries(tokens)) {
      const meta = entry.metadata;
      if (meta?.txid) {
        txids.set(meta.txid, {        // ← silently overwrites
          role: 'metadata', contract, token_id, ...
        });
      }
      for (const m of entry.media || []) {
        if (m.txid) {
          txids.set(m.txid, { ... }); // ← silently overwrites
        }
      }
    }
  }
  return txids;
}
```
**Recommended fix**: Check for duplicates; if same txid has conflicting expected values, fail. Preserve `all_references` array for duplicates with matching values.
**Code modified**: No

---

### SRC-CAR-001 — Producer-side CAR parser lacks bounds checks; catch {} hides errors

**Severity**: High
**Affected script**: `scripts/download-nft-cars.mjs`, lines 160–183, 196–228
**Expected behavior**: Strict bounds checking (like TA-006 verifier parser), throw on malformed, log parse errors
**Actual behavior**:
1. `parseCarHeader()` has no `pos >= data.length` check — truncated buffer causes `undefined` bitwise ops (NaN propagation)
2. No overlong varint guard — `shift` can grow unboundedly
3. No `Number.isSafeInteger()` check (TA-006 verifier has this)
4. `extractTokenIndex()` uses empty `catch {}` — JSON parse errors are silently swallowed
5. Parser continues scanning after malformed blocks — may find a token_index in trailing garbage
**Impact**: A malformed recovery CAR may be partially parsed and still yield a valid-looking token_index. Combined with SRC-TOKEN-001, an attacker-crafted CAR with a decoy JSON after a malformed block would be accepted.
**Evidence**:
```javascript
// Producer (download-nft-cars.mjs:160-166) — NO bounds check
function parseCarHeader(data) {
  let pos = 0, shift = 0, headerLen = 0;
  while (true) {
    const b = data[pos];           // ← pos can exceed data.length
    headerLen |= (b & 0x7f) << shift; pos++; shift += 7;  // ← NaN propagation
    if (b < 0x80) break;
  }
  return pos + headerLen;
}

// TA-006 Verifier (verify-release-assets.mjs) — STRICT
function parseCarHeader(data) {
  let pos = 0, shift = 0, headerLen = 0;
  for (let i = 0; i < 10; i++) {
    if (pos >= data.length) throw new Error('Truncated CAR header varint');
    const b = data[pos]; headerLen += (b & 0x7f) * (2 ** shift); pos++; shift += 7;
    if (!Number.isSafeInteger(headerLen)) throw new Error('Unsafe CAR header varint');
    if (b < 0x80) break;
  }
  return pos + headerLen;
}
```
**Recommended fix**: Port TA-006's strict `parseCarHeader()` to producer; replace `catch {}` with logged rejections.
**Code modified**: No

---

### SRC-SCHEMA-001 — No dedicated token_index schema validator

**Severity**: Medium
**Affected script**: All scripts consuming `token_index.json`
**Expected behavior**: Validate that each NFT entry has required fields (`metadata.txid`, `metadata.car_sha256`, `metadata.car_size`, `media[].txid`, etc.) with format checks (64-hex sha256, safe positive integer size, valid contract format)
**Actual behavior**: No schema validation exists. `extractTokenIndex()` only checks for the presence of `metadata` or `media` keys to identify token-index-like objects. Missing `car_sha256`, bad hex, missing txid, etc. are only caught later (if at all) during download verification.
**Impact**: A token_index with missing or malformed expected fields passes extraction and may cause confusing downstream failures or partial downloads.
**Recommended fix**: Add a schema validation step after extraction; fail early on invalid entries.
**Code modified**: No

---

### SRC-TRACE-001 — RELEASE-MANIFEST.json lacks source digest

**Severity**: Medium
**Affected script**: `scripts/download-nft-cars.mjs`, lines 508–530
**Expected behavior**: Release manifest should include `source_recovery_package_sha256`, `source_token_index_sha256`, and `source_schema_version`
**Actual behavior**: `RELEASE-MANIFEST.json` has `source_manifest: { generator: 'scripts/download-nft-cars.mjs' }` but no source file digests. Cannot cryptographically prove which recovery package or token_index produced the expected values.
**Impact**: If a compromised release is discovered, there's no way to verify whether the producer used the correct source-of-truth.
**Recommended fix**: Add `source_recovery_package_sha256`, `source_token_index_sha256`, `token_index_entry_count`, and `generator_version` to the manifest.
**Code modified**: No

---

### SRC-H1 — root_cid never verified by producer

**Severity**: Medium
**Affected script**: `scripts/download-nft-cars.mjs`
**Expected behavior**: Clear documentation that root_cid is metadata-only, or actual CID verification
**Actual behavior**: `expected_root_cid` is written to `RELEASE-MANIFEST.json` with `cid_check_required: false`. The producer's `verifyDownloadedCarBuffer()` only checks SHA-256 and size — never computes or compares the root CID. The `does_not_prove` array mentions "CID/root/DAG correctness" but only in the context of `verify-release-assets.mjs --cid-check`.
**Impact**: A correctly sized file with matching SHA-256 but different DAG structure would pass. The release manifest may give false confidence about CID correctness.
**Recommended fix**: Add explicit field like `root_cid_verified: false` per file; make `does_not_prove` more prominent.
**Code modified**: No

---

## Negative Findings

| Test | Result | Evidence |
|---|---|---|
| `iterCarBlocks()` block boundary | ✅ Correct | `if (blockLen === 0 \|\| pos + blockLen > data.length) break;` — fails closed on block overflow |
| `verifyDownloadedCarBuffer()` hash/size | ✅ Strict | Computes SHA-256 and compares both hash and size; throws on mismatch |
| `fail > 0` blocks release | ✅ Correct | `if (fail > 0) throw new Error(...)` — refuses to package incomplete backup |
| `allVerified` gate | ✅ Correct | Requires `fail === 0 && pass === txids.size && sha256Pass === txids.size && sizePass === txids.size` |
| `totalVerifiedBytes` cap | ✅ Present | Cumulative size check against `MAX_TOTAL_BYTES` |
| TA-006 verifier-side parser | ✅ Strict | Has bounds checks, safe integer checks, throws on malformed |

---

## Source-of-Truth Binding Analysis

| Artifact | Digest manifest? | Authority manifest? | Producer enforces? | Verifier enforces? | Risk |
|---|---|---|---|---|---|
| recovery-package.bin | ❌ No | ❌ No | ❌ No | ❌ No | **High** — used as source-of-truth with no integrity check |
| token_index.json (in repo) | N/A (in repo) | N/A | N/A | ✅ count check (175) | Low |
| token_index.json (in recovery CAR) | ❌ No | ❌ No | ❌ No | N/A | **Critical** — extracted by scanning, no binding |
| digest-manifest.json | N/A | ✅ Covered by authority | ✅ Used by verifier | ✅ Used by verifier | Low |
| BTC signature | N/A | ✅ In authority chain | N/A | ✅ Checked | Low |

---

## token_index Schema Analysis

**Current state**: No schema validation. The only check is structural:
```javascript
const isTokenIndex = keys.some(k => {
  const v = obj[k];
  if (typeof v !== 'object' || v === null || Array.isArray(v)) return false;
  return Object.values(v).some(t =>
    t && typeof t === 'object' && (t.metadata || t.media)
  );
});
```

**Missing checks**:
- `contract` format (0x + 40 hex)
- `token_id` non-empty string
- `metadata.txid` format (Arweave txid = 43-char base64url)
- `metadata.car_sha256` (64 hex chars)
- `metadata.car_size` (safe positive integer)
- `media[].txid` format
- `media[].leaf_path` non-empty
- No duplicate `token_id` within a contract

---

## Multiple Candidate / Ambiguity Analysis

`extractTokenIndex()` selects the candidate with the most top-level keys. This is a "largest wins" heuristic, not a canonical resolution.

**Attack**: Place a 200-key decoy JSON in a later CAR block, each key mapping to `{ "metadata": {}, "media": [] }`. This passes the `isTokenIndex` check and has more keys than the real 175-entry token_index.

**Current behavior**: No fail-closed on multiple candidates. No uniqueness requirement. No path/CID resolution.

---

## Completeness and Count Analysis

- **Producer**: No `EXPECTED_NFTS` constant. `totalTokens` from token_index is trusted directly.
- **Verifier** (`verify-dag-and-signed-cids.mjs:52`): `EXPECTED_NFTS = 175`, enforced at line 1345.
- **Verifier** (`verify-full-evidence-chain.mjs:53`): `EXPECTED_NFTS = 175`, enforced at line 2088.
- **Gap**: Producer can generate a release with 174 NFTs and `all_verified=true`. Verifier catches it post-hoc, but the release is already live.

---

## Duplicate txid / Provenance Analysis

`collectTxids()` uses `Map(txid)` — a simple key-value map. Duplicate txids are silently overwritten.

**Scenarios tested (static analysis)**:
- Same txid used by metadata of token A and media of token B → last writer wins, provenance lost
- Same txid with conflicting expected hash/size → last writer wins, download verification may fail on wrong expected value
- Same txid with same hash/size but different root_cid → last writer wins, root_cid mismatch not detected

---

## Recovery CAR Parser Fail-Closed Analysis

| Check | Producer (`download-nft-cars.mjs`) | Verifier (`verify-release-assets.mjs`) |
|---|---|---|
| Truncated header varint | ❌ No check | ✅ Throws |
| Overlong varint | ❌ No check | ✅ Max 10 iterations |
| Safe integer overflow | ❌ No check | ✅ `Number.isSafeInteger()` |
| Block length overflow | ✅ `pos + blockLen > data.length → break` | ✅ Throws |
| JSON parse error | ❌ `catch {}` silently skips | N/A |
| Multiple candidates | ❌ Largest wins | N/A |

---

## Release Manifest Traceability

**Present**: `schema`, `release_kind`, `verification_basis`, `actual_nfts`, `total_car_files`, `contracts`, `source_manifest.generator`, per-file `role/contract/token_id/txid/expected_sha256/expected_size/expected_root_cid`

**Missing**:
- `source_recovery_package_sha256`
- `source_token_index_sha256`
- `token_index_entry_count`
- `generator_version` / git SHA
- `all_references` for duplicate txids

---

## Root CID Boundary

- `expected_root_cid` is written to manifest with `cid_check_required: false`
- Producer's `verifyDownloadedCarBuffer()` does NOT compute or check CID
- `does_not_prove` mentions CID but only in context of `verify-release-assets.mjs --cid-check`
- No machine-readable `root_cid_verified: false` field per file

---

## Test Coverage Gaps

| Scenario | Covered? | Notes |
|---|---|---|
| Multiple token_index candidates | ❌ No | No test for extractTokenIndex ambiguity |
| Missing NFT count (174 vs 175) | ⚠️ Partial | Verifier tests check count; producer has no such test |
| Duplicate txid conflict | ❌ No | No test for collectTxids overwrite |
| Duplicate txid provenance preservation | ❌ No | |
| Malformed recovery CAR fail-closed (producer) | ❌ No | Only verifier-side parser tested |
| token_index schema invalid fields | ❌ No | |
| Recovery package digest binding | ❌ No | |
| Source digest in RELEASE-MANIFEST.json | ❌ No | |

---

## Residual Risk

Even with all current TA-005/TA-006 fixes, the producer-side pipeline remains vulnerable to:

1. **Recovery package substitution** — no digest check before use
2. **token_index injection** — largest-JSON-wins heuristic exploitable
3. **Silent count manipulation** — no independent expected count in producer
4. **Provenance overwrite** — duplicate txids lose references

The verifier-side pipeline is significantly hardened (strict CAR parser, EXPECTED_NFTS enforcement, digest manifest checks), creating an **asymmetric security posture**: the producer can be tricked into generating a bad release, but the verifier should catch it. The risk window is the time between release publication and verifier execution.

---

## Recommended Next Actions

1. **Immediate** (Critical):
   - Add `EXPECTED_NFTS = 175` to `download-nft-cars.mjs` and enforce before release
   - Make `extractTokenIndex()` fail-closed on multiple candidates (>1 candidate → error)

2. **Short-term** (High):
   - Add `recovery-package.bin` to `digest-manifest.json` and verify SHA-256 before use
   - Port TA-006's strict `parseCarHeader()` to producer
   - Fix `collectTxids()` to detect and handle duplicate txids

3. **Medium-term** (Medium):
   - Add token_index schema validation
   - Add source digests to RELEASE-MANIFEST.json
   - Add `root_cid_verified: false` per-file field
   - Add test coverage for all gaps listed above

---

## Appendix: Commands Run

```bash
# Baseline tests (all PASS)
python3 scripts/test_download_nft_cars_expected_integrity.py
python3 scripts/test_download_nft_cars_tmp_cache_safety.py
python3 scripts/test_download_nft_cars_manifest_expected_actual.py
python3 scripts/test_download_nft_cars_size_limits.py
python3 scripts/test_download_nft_cars_release_manifest_v1.py
python3 scripts/test_verify_release_assets_consumes_nft_cars_manifest.py
python3 scripts/test_verify_car_parser_fail_closed.py
python3 scripts/test_verify_dag_manifest_item_defined.py
python3 scripts/test_full_evidence_chain_ots_fail_closed.py
python3 scripts/test_full_evidence_chain_eth_audit_required.py
python3 scripts/test_node_exec_no_shell_injection.py
python3 scripts/test_full_evidence_chain_cli_injection_regression.py

# Node syntax (all OK)
node --check scripts/download-nft-cars.mjs
node --check scripts/verify-dag-and-signed-cids.mjs
node --check scripts/verify-full-evidence-chain.mjs

# Source binding audit
grep -R "recovery-package.bin" archive/evidence/digest-manifest.json  # no results
grep "recovery-package" scripts/verify-full-evidence-chain.mjs        # no results
```

## Appendix: Workspace Status

```
Tracked files: clean
Tracked diff: clean
Untracked files: ta-redteam-2026-007-token-index-source-audit.md (this report)
```

## Appendix: End Checklist

```
[x] Baseline tests recorded (12/12 PASS)
[x] Source-of-truth binding checked
[x] Multiple token_index candidate behavior audited
[x] token_index schema validation audited
[x] Expected count / completeness behavior audited
[x] Duplicate txid overwrite behavior audited
[x] Recovery CAR parser fail-closed behavior audited
[x] Release manifest traceability audited
[x] Root CID boundary audited
[x] Existing tests coverage gap listed
[x] No repository files modified (tracked diff clean)
[x] git status --short recorded
[x] git diff --exit-code clean
[x] Report written to ta-redteam-2026-007-token-index-source-audit.md
```

## Appendix: Temporary Files Created

None. All audit performed via read-only static analysis and existing test execution.
