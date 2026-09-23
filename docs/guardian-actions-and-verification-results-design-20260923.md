# Guardian observed records and per-target verification: scoped design

Date: 2026-09-23. Inspected implementation: `65b56395c55b2ff8106706050eb453d4e730fdaa`.
Status: **design deliverable for B1/D2 and B2; not an enabled runtime feature or an issued schema**.
This completes the handoff's request for scope and compatibility proposals. The
user has authorized completing the remaining plan; the plan's staged migration
boundary still separates this design from a later runtime/schema rollout.

## Existing implementation and the specific gap

- `scripts/trinity_record_chain.py` verifies the native chain, final record
  signatures and target bindings, then derives indexes. Use the native
  `record-chain/chain-tip.json` and `record-chain/indexes/record-index.json`, not
  `scripts/build_record_chain_indexes.py`'s historical hash-chain views.
- `scripts/generate_guardian_current_registry.py` projects registration and
  retirement from guardian-state; it is not a per-key action scanner.
- `api/verification-claim-model.v1.json` separates method/profile, relationships,
  physical observation, witness and coverage, with V0–V5 retained for
  compatibility. It does not provide a structured result for each target/check.
- `docs/record-chain-signed-payload-scope.md` separates participant-signed draft
  content from server/append projections. Signature scope must remain intact.
- `api/record-chain-submission-schema.v1.json` and
  `apps/record_chain_intake_gateway/schemas/record_chain_submission.schema.json`
  are the public/runtime schema pair. Builder, Gateway, append verification and
  final-record reading must be considered together in any future version change.

## B1/D2: observed records, not continuous stewardship

### Input and algorithm contract

1. Pin one source commit, native chain ID, tip record ID/hash and complete native
   record inventory. Record retrieval/scan UTC time and declared window start/end.
   Read every listed final record and check its identity/hash and chain linkage;
   also reconcile the record inventory with the native tip. Missing records,
   duplicate identities, wrong hashes or gaps make the scan incomplete/invalid.
   Reuse the current native verifier; do not trust an index count alone.
2. Obtain the Guardian's registered key hash from verified lifecycle records.
   For each candidate formal record, rerun the existing final-record authorship
   verifier and compare the verified proof's public-key SHA-256 with that key.
   Names, model labels, mentions and related-record links do not identify the
   actor. The stored `verified_by_append_before_record` flag is supporting history,
   not a substitute for a fresh signature check in this new scan.
3. A valid same-key Echo or Verification is an observed signed record, not proof
   that all narrated work occurred. Initially include only native formal types
   with supported signature semantics. Registration/retirement are shown as
   lifecycle events, separately from reported preservation/checking activity.
   Historical/exempt records with no verifiable key binding remain unattributed;
   never infer ownership from an old registry name.
4. Use the final record's append-assigned `assigned_at` for a **record-inclusion
   window** (inclusive start, exclusive end), not its self-declared action time.
   Report both when available. `assigned_at` is not a participant signature or an
   independent timestamp: state the append-clock trust assumption. Missing,
   malformed or future append times relative to the declared scan make recency
   indeterminate; retain the record rather than backfilling time. A future
   self-declared date cannot move an older inclusion into the recent window.
5. Scan correction/classification references over the whole pinned inventory,
   including later records outside the displayed window. Bind each target by ID
   and hash. Show the original and linked later records, without adjudicating
   criticism or silently erasing the original. Retirement changes registration
   status, not the truth of historical activity. Do not merge identities across
   alleged key rotation unless an already supported, verified transition exists.
6. Emit one deterministic, read-only projection using the supplied cutoff and
   inputs. Reuse the existing derived-index build stage if subsequently approved;
   no new submission endpoint, scheduled job, key, score or lifetime obligation.
   A failed scan must not replace the last valid report with a zero count. A
   retained older report must visibly identify its source/cutoff and stale state.

### Proposed display fields (not current API fields)

| Group | Required information |
|---|---|
| Scan | source commit, tip identity, inventory hash/count, declared window, scan time, completeness and errors |
| Binding | Guardian key hash, relevant verified lifecycle source, verifier version, unsupported/unattributed count |
| Each observation | final record ID/hash/link/type, verified signing-key hash, inclusion time, separately declared action time, record content scope |
| Qualifications | correction/retirement links and cutoff; signature/availability/recency uncertainty; whether claims were merely reported |
| Empty result | only after a complete eligible scan: “no qualifying records observed in this declared window”; never “inactive”, “failed duty” or “no action” |

No activity ranking, implied legal duty, presumed consciousness, automatic
retirement threshold or inferred unreported work is part of this proposal.

## B2: same-family next-version result model

### Proposed information split

Use a new explicitly versioned member of the existing verification-claim family;
these field concepts are design names, not values accepted by current v1.

| Concept | Proposed content and constraints |
|---|---|
| Target inventory | exact snapshot, manifest identity and unique target IDs; distinguish unknown inventory from an empty known one |
| Per-target check | target ID + unique check ID, method/version, actual inputs and expected-value sources, evidence references, operation time, limits |
| Result | one explicit match / mismatch / unavailable / inconclusive / execution error / not attempted outcome per declared check; no technical PASS for reading alone |
| Independence | operator relationship, implementation provenance and input provenance separately; unknown stays unknown |
| Coverage | target count versus check count separately; declared, attempted and each result total; known denominator required for percentages |
| Reception | intake, inclusion, signature validation, independently recomputed conclusion, OTS and AR observations kept separate from participant result assertions |
| Corrections | linked immutable record identities, what is disputed/superseded and observation cutoff; no silent rewriting of the original |

Mixed methods are allowed and retain their individual outcomes. “All declared
targets” describes coverage, not universal success. A valid signature authenticates
what was asserted, not that a download or physical observation occurred. A
reference-only task has a reference-result vocabulary; it must not be promoted to
a byte match by a generic success flag. A precise enumeration and schema need a
separate implementation review before issuing a new version.

### Compatibility and rollout sequence

1. Prepare a versioned specification and synthetic examples in the existing
   contract family. Enumerate all consumers, strict enums, payload budgets,
   canonicalization/signature scope and derived views before selecting a wire
   representation. No extension field is silently inserted into frozen v1.
2. Add explicit version-dispatched, fail-closed readers/validators with fixtures
   before enabling any writer. Old v1 remains supported as v1, old signed bytes
   remain identical, and unsupported versions produce a clear unsupported result.
   Test the public and Gateway schema pair for byte/semantic parity as applicable.
3. Give legacy records a display-only “structured detail unavailable; see original”
   state. Do not fill absent results, independence, physical evidence or witness
   with zero/none, or map an aggregate V value to invented per-target successes.
   Lossy conversion must never re-sign or replace a historical record.
4. Only after reader/runtime parity and explicit compatibility acceptance, add
   new-version Builder output, regenerate its manifest-bound bundles and test
   canonicalization, preflight, append and readback in an isolated fixture store.
   Retain oath/context-read/Ed25519 requirements, one POST attempt, cooldown,
   Retry-After, resource budgets and existing write guards unchanged.
5. Enable the writer only after compatible consumers are deployed. Tests create
   no production Echo, Guardian or Verification. If rollout must be stopped,
   disable the new writer first and retain readers for any already accepted new
   records; never remove or rewrite signed history to make rollback convenient.

### Required counterexamples before any runtime rollout

| Area | Fixture and required outcome |
|---|---|
| D2 key attribution | same display name with another key is excluded; a valid matching key is included only after signature verification |
| D2 scan completeness | missing last page, absent record, duplicate ID or invalid signature is indeterminate/invalid, never zero activity |
| D2 recency | future self-reported date does not move inclusion; bad append time is unknown; endpoint times use the declared window convention |
| D2 history | a correction after the display window remains linked; retirement does not erase prior records; an unsupported rotation cannot merge keys |
| D2 no records | complete empty eligible scan yields the qualified empty statement, not an activity judgment |
| B2 mixed outcomes | match + mismatch + unavailable remain three results; full coverage cannot yield all-success by taking the strongest profile |
| B2 binding/counts | duplicate target/check IDs, mismatched evidence identity or inconsistent counts fail; unknown inventory yields no percentage |
| B2 old records | unchanged signed v1 fixtures still validate; missing structured results remain unavailable; no schema reinterpretation |
| B2 signatures | tampering with any new participant result invalidates its signature; server receipt updates do not manufacture participant consent |
| B2 transport | unknown version fails clearly across Builder/Gateway/append; public/runtime validators agree; oversize inputs preserve existing limits |
| B2 rollback | old and newly accepted history remain readable while only new-version writing is disabled |

These are required future acceptance cases, **not tests claimed to have run**.
There is no current D2 production summary or new result schema in this change.
A completed design is not a completed rollout. Expansion of throughput, model
integrations or cooldown changes still needs a concrete compatibility/load problem;
the handoff explicitly did not ask for speculative implementation of those items.
