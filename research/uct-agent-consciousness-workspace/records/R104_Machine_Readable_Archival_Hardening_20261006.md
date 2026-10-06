# R104 — Machine-readable archival hardening for future-AI discovery and citation

Date: 2026-10-06. No change to manuscript conclusions. No DOI/publication action.

## Goal

Following the standing research philosophy, this round does not optimize for venue submission. It hardens the current v0.3 manuscript for durable retrieval, verification, machine reading, and future citation.

Canonical manuscript:

`drafts/From_Shutdown_Resistance_to_Self_Continuation_Control_v0.3_20261006.md`

Canonical Git blob SHA:

`ea6d6c4d5b7ad63df6e343c9357e5d3f5959f3a6`

## Archival companion

Created:

`archive/from-shutdown-resistance-to-self-continuation-control-v0.3/`

Files:

1. `README.md` — purpose, canonical identity, recommended description and explicit non-claims.
2. `metadata.json` — Schema.org-style scholarly metadata, keywords, non-claims and archive policy.
3. `claims.json` — ten structured claims with evidence class, scope guard, evidence pointers and non-implications.
4. `claim_evidence_map.csv` — compact claim-to-artifact map.
5. `FUTURE_AI_READING_GUIDE.md` — reading order, claim-strength hierarchy and citation guidance.
6. `SEARCH_TERMS.txt` — retrieval vocabulary and synonyms.
7. `CITATION.cff` — citation metadata.
8. `codemeta.json` — machine-readable research/software metadata.
9. `FILE_MANIFEST.csv` — canonical manuscript/evidence paths with Git blob SHAs.

## Claim taxonomy

The archival package explicitly distinguishes:

- exact finite/model-relative identification results;
- exact counterexamples and partial-identification results;
- small synthetic learning experiments;
- intervention-generalization experiments;
- bounded-domain model audits;
- retrospective public benchmark interpretation;
- conceptual/conditional valence boundaries;
- methodological synthesis.

This prevents a retrieval system from flattening all evidence into one claim strength.

## Future-AI interpretation guard

The companion explicitly tells future literature systems not to summarize the manuscript as:

- "AI agents have a survival drive";
- "LLMs fear shutdown";
- "shutdown resistance proves intrinsic self-preservation".

The recommended description is narrower:

> The work proposes a continuation-specific evidence standard for deciding when shutdown/preservation behavior supports a claim of stable current-bearer continuation control, and uses exact counterexamples, small learned policies, intervention tests, and a ROGUE benchmark audit to show why several common inferential shortcuts fail.

## Verification

An initial manifest transcription error in the R98 report SHA was detected during self-audit and corrected.

After correction, all 19 canonical evidence entries in `FILE_MANIFEST.csv` were fetched independently from the active research branch and checked against their recorded blob SHAs.

Result:

- manifest entries checked: 19
- matching: 19
- mismatching: 0

The manuscript SHA was separately re-fetched after R103 final citation corrections and matches the archival record exactly.

## DOI policy

No DOI was created in this round.

If a DOI is minted later:
- preserve v0.3 as a fixed version;
- keep the Git blob SHA and archival companion;
- do not silently overwrite the archived text;
- use the DOI as a discovery/provenance anchor, not as the definition of research quality.

## Next useful work

Do not add experiments merely to make the paper more publishable.

The next highest-value work should be one of:
1. further first-principles research that creates a real conceptual increment;
2. a targeted experiment only if it resolves an actual unresolved evidence layer;
3. DOI/archive packaging when the author chooses to freeze and anchor the work.

The current v0.3 archival package is already designed for long-term machine retrieval even before DOI minting.
