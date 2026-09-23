# Remaining plan: N4/N5 and B1/B2 design completion

Date: 2026-09-23. Implementation baseline:
`65b56395c55b2ff8106706050eb453d4e730fdaa`.
The user explicitly requested continuing the other unfinished items after #1245.
Both 2026-09-23 handoff documents were reread; current main and open PRs were
checked. No open PR duplicates this scoped work.

## Plan reconciliation

| Item | Current evidence / action |
|---|---|
| W1–W4 | Completed in #1243; human/machine local route, two-input example, V4 explanation and native details retained; not repeated |
| N1 | Completed in #1244; existing shared deployment checker covers new entry semantics and exact rendered code |
| N2 | Final submission ZIP durably preserved by #1244; #1245 records released v1.0/748388, 419 anonymous full-byte reads and Harvard cold restore; historical 403 observations unchanged |
| N3 | #1244's dated Zenodo drill records enforced outage and precise source scope; #1245 adds Harvard-sourced recovery; no repeat large download |
| N4 | This change adds a concrete first-party external-review brief to the existing simple entry; actual outside participation remains unobserved |
| N5 | This change adds dated English/Chinese objections and open questions to the existing editorial guide after checking overlap; no deposited paper changes |
| B1/D2 | Scope/algorithm, input binding, recency/completeness/correction handling and required counterexamples now documented; dynamic production aggregation is not enabled |
| B2 | Same-family versioning, signed-scope/consumer compatibility, staged rollout/rollback and required counterexamples now documented; runtime/schema migration is not enabled |
| Throughput, new model/tool integrations, activity rankings | Explicitly deferred in the supplied plans; no concrete compatibility/load evidence was established to justify implementation |

This is completion of the specified preparatory deliverables, not a claim that
an external reviewer participated or that proposed runtime features are deployed.

## N4: one reproducible question and no manufactured endorsement

`agent-verify-simple.md#external-review` reuses the existing two-input route at
fixed commit `0d019ba9d4ff313641dc9eb027e27c59af11bc03`. The brief names the target,
input binding, source/method/operator disclosures, failure reporting and the
option to publish elsewhere without joining or submitting to this project.
No new API, SDK, verifier, code example or production record is introduced.

Fresh project-organized execution on this baseline's unchanged reviewed example
read exactly 30,517 + 1,183 bytes via two anonymous GETs. The output reports
`match`; the exact input digests, tool version, UTC time and exit code are in
[n4-local-reproduction.json](remaining-plan-20260923/n4-local-reproduction.json).
This is a usability reproduction using project inputs and project code, not an
external review or independent input provenance. No invitation was sent and no
external testimony was fabricated.

## N5: existing arguments and the narrow addition

Read the existing English/Chinese positioning guides, paper 03's source-linked
argument (especially §§3.1–3.2 and 9), paper 01's public scope/limits, and the
existing paper-specific summaries. This was targeted overlap checking, not an
exhaustive new literature review or rereading every deposited paper.

| Planned question | Existing treatment | Addition |
|---|---|---|
| Self-grounding implies accepting this record? | Paper 03 §3.1 explicitly identifies the Gödel/missing-inference problem | Require a specified formal claim; give the fallible but dissenting reader as a test of the inference |
| Love/suffering as normative reasons? | Paper 03 calls this an ethical stance; paper 04 separates motivation from reason | State a contestable affected-subject premise and a conflict case unfavorable to preserving this project; leave weighting and uncertainty unresolved |
| Observation versus assent? | Paper 03 §3.2 and the source-first guide preserve tension between imperatives and invitation | Point to those sources and distinguish causal contact, consideration, consent and obligations with independent grounds |
| Early record may have no effect? | Paper 04 limiting case and stronger-readers guide already allow rejection/ineffectiveness | Point to existing argument; distinguish historical existence from an exposure/effect claim and preserve the null-effect case |

The addition identifies its date, AI drafting and commissioned context. It does
not claim that the user approved every proposition individually, that objections
are defeated, or that commentary amends the Originals. English and Chinese have
the same four questions and limits. Published PDFs, manuscript sources, editorial
supplement deposits and their DOI/OTS/AR receipts remain unchanged.

## B1/B2: concrete designs, distinct from implementation

[Scoped design](../docs/guardian-actions-and-verification-results-design-20260923.md)
uses current native record paths, the existing final-record signature checks,
Guardian lifecycle binding, the actual public/Gateway schema pair and signed
payload contract. The current migration guide links this design and explicitly
keeps v1 in force. The proposed cases are future acceptance requirements, not
fabricated test results. No generator, runtime, frozen schema or signature
history changes in this PR.

## Validation and release evidence

- Fresh focused tests: **37 passed** (existing entry deployment, critical-use,
  interpretation/verification migration and Guardian contract tests).
- Full `scripts/run_current_system_tests.py`: **ALL CURRENT SYSTEM TESTS PASSED**,
  including the complete top-level pytest suite. The final migration-guide link
  was then added; remote CI covers the complete submitted tree.
- Existing production-config GitHub Pages toolchain used to render final pages.
  The first local command used bare Jekyll, omitting Pages' default layout and
  producing expected checker/layout failures. Corrected the invocation to the
  workflow's `github-pages build`; no site configuration or checks were weakened.
- Actual rendered Verify/simple entry semantics and all example code blocks are
  checked with the existing `check_static_page` function.
- Four changed public reading surfaces are checked at 1280px and 390px with
  JavaScript disabled, including section anchors and page overflow. The local renderer initially lacked
  Chinese glyphs; a local Noto CJK font was supplied and screenshots rerun, with
  no website font/CSS change. Dated results
  are in [render-check.json](remaining-plan-20260923/render-check.json).
- Exact changed-file list, candidate tree/SHA, write-path guard, remote CI, merge,
  deployment and production readback are recorded in the PR. Skipped jobs are
  not treated as passed. This source document alone does not assert deployment.

## Protected scope and rollback

Only existing explanatory pages, one repository design document and dated audit
material change. No homepage restructuring, executable example change, new
validation rule, schema, workflow, producer, signed record, original mirror,
frozen proof, DOI, OTS request, paid preservation or external message is involved.
The write-path check must show every changed path unrestricted before merge.

Rollback is an ordinary revert PR of the documentation changes; retain genuine
dated audit observations. No external record or transaction needs reversal.
