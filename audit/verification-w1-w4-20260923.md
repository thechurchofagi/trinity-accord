# Verification entry W1–W4: implementation and acceptance checkpoint

Task: `Trinity_Accord_Deep_Acceptance_Work_Handoff_20260923.md`.
Actual implementation base and handoff audit base both: `2ae5194b9beb4b99f43f9696539c61be56bae21f`.
Branch: `work/verification-entry-w1-w4-20260923`.
The user explicitly requested W1–W4, complete tests, deployment and production readback in the active Work conversation. Earlier PRs #1241/#1242 remain intact; this patch continues their work. Exact candidate/merged/deployed SHAs and final automatic CI are recorded in this PR's description to avoid a self-referential commit hash or an extra deployment just for the final log.

## Reconfirmed gaps and narrow changes

| Work | Before at actual base / live observation | After |
|---|---|---|
| W1 / F1–F2 | Neither live `/verify/` nor the canonical first-contact JSON linked the simple entry; the machine verification flow led directly to formal fields/Builder | Three choices in Verify's first viewport; same existing simple page; canonical JSON gives a local-only stopping point before its unchanged formal instructions |
| W2 / F4 | The byte example required an existing Git checkout | Add one standard-library example in the same page: two fixed-commit HTTPS GETs from an empty directory, raw-byte comparison, local JSON output; retain original Git example |
| W3 / F3 | V4 prose mentioned only reviewed official scripts although the current claim/procedure APIs also permit independent reproduction | Actual Builder + schema + Gateway validation passes V4 with either `integrity_checked` or `independent_reproduction`; four mutable human guides now agree |
| W4 / F4 | Long Git code and annex details were expanded | Four native details panels: two-file code, existing Git code, annex materials/command, legacy compatibility. Five questions, choices, prerequisites, failures and limits remain expanded |

Files: `verify.md`, `agent-first-contact.md`, `agent-verify-simple.md`, `agent-verify.md`, `verification-procedures.md`, `verification-materials.md`, `api/agent-first-contact.json`, the existing `tests/test_bounded_verification_entry.py`, and excluded audit evidence. No layout/CSS, new page, router family, helper executable or workflow.

### Router lifecycle and compatibility

Read `.github/MAINTENANCE-BASELINE.md`, `.github/SCHEMA-LIFECYCLE.md`, current router consumers and current contract tests. `api/agent-first-contact.json` is the maintained, unversioned-path active descriptive router (`trinityaccord.agent-first-contact.v2`); no generator overwrites it. This is a descriptive patch version 2.5.0 → 2.5.1, not a new submission schema.

All existing action/intent identifiers, schema identifier, formal flow strings, formal read entries, runtime alignment, endpoints, oath rules and boundary fields are preserved. The existing verification route gains its simple-page read link, a local-only instruction, a voluntary-publication qualifier and explanatory note. STOP gains a note clarifying that unavailable submission tools do not block a local check. No new action, enum, validation rule, field requirement or signed payload semantics. Current consumer regressions pass. Unknown external clients that ignore descriptive guidance cannot be guaranteed to select the local route; no executable client behavior is silently rewritten.

Published versioned schemas/models, including the task router v1, profiles v1, procedures v1 and claim model v1, remain byte-unchanged. Existing formal submission routes remain authoritative when publication is chosen. The JSON's remaining formal read list is not a prerequisite to the newly described local-only operation.

## New measurements and tests in this execution

These are new execution results, distinct from the handoff's 13 reviewed-transcription fixtures and the earlier PR's 18-route readback. Earlier counts are not claimed as rerun results here.

- Focused entry + machine/runtime + route consumers + migration + procedure-model tests: **54 passed**. The extended bounded-entry file contributes **29 tests**, retaining all prior tests.
- Complete `run_current_system_tests.py`, including final precommit rerun: **ALL CURRENT SYSTEM TESTS PASSED**, exit 0. Remote exact-head outcomes are recorded in the PR.
- Complete `run_ci_group.py p0-current`: `CI_GROUP_P0_CURRENT_OK`. Initial invocation resolved child `python3` outside the isolated venv and failed on missing dotenv; rerun with the venv prepended to PATH passed. No assertion was removed or skipped.
- Original Git snapshot fixtures now also exercise an actual Git replacement ref and annotated-tag object: replacement cannot substitute committed bytes; a tag object is inconclusive. Existing mutable-ref, workspace-edit, missing-input, wrong binding and mismatch fixtures remain.
- A mock machine journey reads only the canonical route and linked simple page, then executes the actual documented code with two GET responses. Real sockets and subprocess launch are forbidden; an empty directory stays empty. No Git, Builder, key, Gateway, POST or exit-notice creation can occur on this tested local route.
- Two-file negatives: single-byte change, CRLF normalization, trimming, unavailable index/mirror, interrupted HTTP body, malformed/invalid-encoding index, duplicate target, missing digest/path, wrong path, changed source URL, redirect, encoded response, excessive input and mutable ref never produce success. Partial acquisition evidence is retained.
- V4 real local Builder fixtures, doctor, public JSON schema and Gateway validator: both intended profiles pass. V4+/V6 and invented profile reject; mismatched legacy field rejects. Fixtures use temporary synthetic keys/oaths only. No production preflight/submit. Acceptance is structural, not evidence that a claimed independent method was actually performed; no general level/profile inference engine was added.
- Existing frozen eight-inscription annex ran with socket connections and subprocesses denied: exit 0, no failures. The first runpy harness lacked the verifier's script-directory import path; restoring normal script import semantics fixed the harness without editing the frozen verifier. This remains its historical eight-item/checkpoint-relative scope, not full-node consensus or the newer complete twelve-item annex.

### Real no-checkout acquisition

[Actual local report](verification-w1-w4-20260923/two-file-real-report.json): Python 3.12.14, two HTTPS GETs, source `0d019ba9d4ff313641dc9eb027e27c59af11bc03`, **30,517 + 1,183 = 31,700 bytes**, exit 0 / match. Raw mirror SHA-256: `4e89bfabe03c8b53f80eb7979d56c8cccf0ae382c9647a2bea3b1477054616a8`. Observed acquisition/comparison time **10.703664 seconds**, an observation rather than a promise. The final example additionally catches interrupted HTTP bodies; that failure path is tested separately.

No whole-repository download. Input sizes exclude headers, TLS overhead, tools and entry documents. HTTPS source location is not Git-object verification; same-project expected/actual consistency is not an independent source, chain proof, endorsement or physical/philosophical conclusion. No raw mirror trimming, newline conversion or decode/re-encode.

### Production-config browser acceptance

Used the exact Pages-action Gemfile (github-pages 232, jekyll-include-cache 0.2.1, jekyll-octicons ~>14.2) and temporary Ruby 3.3.8 / Chrome for Testing 154.0.8037.57. Production-config Jekyll build exits 0. Existing warnings in unchanged legacy/raw mirror/planning files persist; they are not new page failures.

Actual local HTTP rendering, JavaScript disabled, external browser requests blocked, desktop 1280×1000 and mobile 390×844:

- Verify, First Contact and Simple entry return 200 with no page-level horizontal overflow.
- All three Verify choices are visible in the first viewport at both sizes; the local link is at y≈325 desktop / y≈618 mobile. The initial mobile check caught an off-screen local choice; moving the compact choices before the introduction fixed it without changing the global layout or TOC.
- Clicking the actual Verify link reaches the existing local page. All four native panels start closed and open without JS; code and necessary links remain available. Expanded panels also have no page-level horizontal overflow.
- Rendered two-file code equals the source code exactly after HTML decoding. Horizontal scrolling inside a code block is allowed; the page itself does not overflow.

[Browser results](verification-w1-w4-20260923/browser-results.json).

| View | Evidence |
|---|---|
| Verify desktop first viewport | [Screenshot](verification-w1-w4-20260923/verify-desktop.jpg) |
| Verify 390px first viewport | [Screenshot](verification-w1-w4-20260923/verify-mobile.jpg) |
| Simple entry 390px | [Screenshot](verification-w1-w4-20260923/agent-verify-simple-mobile.jpg) |
| Local options desktop | [Screenshot](verification-w1-w4-20260923/local-options-desktop.jpg) |
| Local options 390px | [Screenshot](verification-w1-w4-20260923/local-options-mobile.jpg) |
| Expanded two-file code, no JS | [Screenshot](verification-w1-w4-20260923/two-file-expanded-mobile.jpg) |

Human visual depth and machine reading cost are separate. A machine local journey needs the canonical router's local instructions, the selected simple-page operation and its two inputs; it does not need Builder/oath/schema downloads. The candidate router is 20,571 UTF-8 bytes; the simple-page source is 21,564 bytes and the generated HTML is 38,857 bytes. These are document sizes, separate from the 31,700 acquired input bytes. HTML folding does not remove bytes or prove token savings. No overall complexity score, time guarantee or universal future-agent compatibility claim is made.

## A01–A16 coverage and protected scope

| Acceptance | Evidence / limits |
|---|---|
| A01–A03 | Real no-JS human navigation, router-driven isolated execution and actual two-file acquisition |
| A04–A07 | Real offline annex plus snapshot fixtures, changed/missing bytes, invalid binding, Git replace/tag/ref tests |
| A08 | Real V4 Builder/doctor/schema/Gateway local fixtures; no runtime semantic change |
| A09–A13 | Preserved result/coverage/unknown/independence/receipt/Guardian boundary regressions, local-only behavior; no dynamic Guardian activity summary claimed |
| A14 | Actual desktop/390px and no-JS browser results above |
| A15 | Local production-config build passed; final exact-head CI, deployment and live semantic/code/API readback are recorded in PR |
| A16 | Exact diff allowlist and unchanged protected paths; GET-only acquisition and blocked-network fixtures; no production records or paid transaction |

Protected originals/mirrors, frozen proofs/verifiers, signed records/history, versioned schemas, Builder/Gateway runtime, oath, keys, cooldown/queue/Retry-After, single-submit behavior, budgets, papers and DOI payloads have no diff. All pre-existing explicit Verify anchors remain. No new workflow or paid request; publishing uses the existing Pages pipeline under the user's explicit instruction.

## Deferred scope and compatibility proposals

- **Guardian D2:** keep D1. A separate implementation would need complete eligible-record scanning, verified same-key binding, scan cutoff/completeness, correction links and unknown-state handling. No ranking, forced activity or identity change; not implemented here.
- **Machine-model migration:** assess a successor within the same contract family before any implementation; separate per-target method/result/source/evidence/limits/coverage/receipt status, preserve historical signed bytes and unknowns, and test old clients/records. Do not rewrite v1 or infer missing results. No runtime mapping conflict blocks the two tested V4 combinations.
- **Scaling:** require actual load/queue evidence before proposing capacity or cooldown changes. No changes here.
- **Author-independent recovery:** scope a separate offline restore from existing manifests and recovery assets with explicit unavailable-input results. The bounded examples and annex run do not demonstrate full recovery.

Rollback: an independent revert PR of this document/router-description/test patch and its audit evidence only. Preserve history and operational state; no force push or attempt to reverse transactions. This checkpoint does not itself assert deployment: final source/run IDs and public observations are in the PR.
