# When the Guardians Can Be Acquired — ASI-CC-v1.0.0

**Research date** 2026-10-11. **Author:** Hongju Liu. **Scientific status:** bounded conditional research manuscript (9 pages), not independently peer reviewed, no new DOI, no actual advanced-model, human-subject or hardware test. It is a research continuation of published PR-v6.0.0 (DOI [10.5281/zenodo.23295776](https://doi.org/10.5281/zenodo.23295776)), not a replacement or revision of that immutable publication.

## Research target

A finite model of multiple AI and human principals whose *effective authority roots*, not surface agent names, may evolve through spawn/delegation, coalition AND-rules and enabled-policy edits. Study when a coalition can eventually defeat every serial harmful-effect interlock or disable enough banks to violate the same declared human service contract. The theorem provides a root-relative initiating-coalition threshold with explicitly limited scope. UCT consciousness axioms are not proof inputs.

## Contents

- `paper/manuscript.pdf`: self-contained 9-page English candidate research manuscript with proofs, contrary models, and prior work.
- `paper/manuscript.tex`: editable mathematical source. No external font files are distributed.
- `RESEARCH_NOTE.md`: technical and priority audit synopsis (English).
- `src/authority_closure.py`: grant fixed points, BFS, human support matching and finite model enumeration.
- `src/institution_mutation.py`: explicit policy edit + typed hyperrule compilation; nonmonotone negative control and service/liveness counterexample.
- `src/joint_oracle.py`: independent intermediate-state safety test versus closure-plus-Hall theorem.
- `data/*.json`: completed original exact results.
- `RUN_RECEIPT.json`: actual execution, seed-diverse rechecks and count verification.
- `audit/`: research log, hostile-scoped review, targeted primary prior-art and publication coverage delta; contact sheet visual review.
- `HANDOFF_ZH.md`: Chinese high-fidelity cross-window handoff.
- `INDEX.json`: stable candidate IDs and separate science/publication governance statuses.
- `MANIFEST.json`: SHA-256 file hashes (excludes itself).

## Reproduce

Python 3.10+ (3.13.5 used), standard library only. No internet, GPUs, API keys, or privileged access required.

```bash
python src/authority_closure.py --out data/closure_results.json
python src/institution_mutation.py --out data/mutation_results.json
python src/joint_oracle.py --out data/joint_oracle_results.json
```

All final assertions pass. Under Python hash seeds 1 and 9, every archived JSON object matched exactly. Testing demonstrates internal mathematical consistency on selected finite cases, not real-world physical completeness, subjectivity, political consensus, guaranteed long-run human survival, or worldwide mathematical novelty.

## Stop conditions and next research step

The least fixed-point statement is exact **only** if grants are persistent/duplicable, all grant and policy-enabling rules are enumerated, and the source/actuator/resource paths are complete. Noncopyable source rights, expiration, revocation, timed attacks, new independent physical roots, scarce nonrenewable energy, or adversarial control over the monitoring infrastructure require a larger formal game. Do not use finite test counts to infer universal control of ASI. A real bounded multi-principal tool/gateway deployment with independent effect traces is the next experiment.

**Publishing is not performed in this version.** Updating the candidate in a working repository or Library does not create a DOI or alter UCT's established science map.
