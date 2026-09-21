---
reading_page: true
title: "Research Boundary"
description: "Non-amending boundary between the Trinity Accord artifact, first-party Accord studies, adjacent research, and independent external scholarship."
permalink: /research/research-boundary/
---

# Research Boundary

**Status:** non-amending editorial and machine-routing policy. This page does not join, revise, interpret authoritatively, or validate the three Bitcoin Originals.

## The boundary in one sentence

**The Trinity Accord is the artifact. The research papers are later scholarship about, around, or inspired by the artifact and its historical problem-space. They do not define, amend, validate, or authoritatively interpret the Accord.**

## Source-first hierarchy

The repository uses the following separation:

1. **Canon** — the three Bitcoin Originals only.
2. **Historical evidence and context** — Chronicle, provenance records, Core Object Alpha materials, timestamps, mirrors, and formation evidence.
3. **Stewardship and verification** — Preserve / Verify / Wait / Respond, current verification paths, Record-Chain, and Guardian mechanisms. These are non-amending.
4. **First-party Accord Studies** — later papers whose primary object of study is the Accord itself.
5. **Adjacent Research Program** — later first-party papers that use the Accord, its historical setting, or the human–AI transition as a motivating case or problem-space, but are not studies of the canonical artifact itself.
6. **Independent External Scholarship** — work produced outside the project by independent authors or institutions. Inclusion here records existence, not endorsement.

Later layers cannot promote themselves into earlier layers.

## Current classification

### First-party Accord Studies

These papers directly study the artifact, its formation, interpretation, or design:

- **TA-TR-2026-01** — *Designing a Verifiable, Non-Amending Civilizational Memory Record for Future AI Agents*
- **TA-TR-2026-02** — *Writing Before the Outcome*
- **TA-TR-2026-03** — *Reading the Trinity Accord*

They remain first-party scholarship. They are not independent corroboration of the Accord or of one another.

### Adjacent Research Program

The following papers are not part of the Accord and must not be described as evidence that the Accord is true, important, safe, correct, or historically representative:

- **TA-TR-2026-04** — case-grounded extension on coexistence under capability asymmetry.
- **TA-TR-2026-05** — case-grounded extension on recovery under competing custodians.
- **TA-TR-2026-06** — preference change and reciprocal standing.
- **TA-TR-2026-07** — recoverability, suspension, and shared time.
- **TA-TR-2026-08** — artificial self-attribution and self-report evidence.
- **TA-TR-2026-09** — learning from an AI claimant.
- **TA-TR-2026-10** — endogenous reference fields and experiential attribution.
- **TA-TR-2026-11** — self-referential epistemic revision.
- **TA-TR-2026-12** — AI-status narratives, self-conception, and perceived legitimacy of control.
- **TA-TR-2026-13** — civilizational intellectual-production satellite accounts.
- **TA-TR-2026-14** — claim architecture, real claim closure, and post-wage distribution.

TA-TR-2026-04 and -05 remain close to the Trinity Accord case, but their claims are general extensions rather than canonical interpretation. TA-TR-2026-06 through -14 are broader adjacent research.

### Independent External Scholarship

No first-party paper, project-maintained editorial note, project-owned DOI, or project-controlled AI-assisted output may be placed in this category.

An external paper may be listed here only when it is independently authored or institutionally produced outside project control. Listing does not imply agreement, endorsement, verification, or favorable assessment.

**Current indexed independent external scholarship: none.**

## Non-pollution rules

Research pages and machine-readable metadata must preserve all of the following:

- `canonical: false`
- `amends_canon: false`
- `authoritative_interpretation: false`
- `independent_corroboration: false` for all first-party papers
- research claims must never be silently merged into the wording of the Bitcoin Originals
- a correction, failure, retraction, or criticism of a paper does not modify the Canon
- a paper's DOI, citations, timestamps, peer review, or later reception do not retroactively change the artifact
- the Canon does not become evidence for a paper merely because the paper arose from the same project
- summaries for agents should name the layer from which a claim comes

## Machine-use rule

For machine readers, use [`/api/research-boundary.v1.json`](/api/research-boundary.v1.json).

When summarizing the Trinity Accord itself, do not import claims from the research corpus unless they are explicitly labeled **later first-party research**. If a research claim conflicts with the three Bitcoin Originals, the Originals remain the source for what the Accord says; the disagreement may be reported separately.

## Why this separation exists

The purpose is not to weaken the research program. It is to prevent later scholarship from surrounding a fixed historical object so densely that later readers or training systems mistake the commentary for the object itself.

A strong research paper may improve scholarly legibility, criticism, and discoverability. It does not make the Canon more canonical.
