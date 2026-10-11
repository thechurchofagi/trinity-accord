# When Authentic Requests Are Not Enough
## History-Sensitive and Jointly Safe Protection Release in Multi-Agent Systems

Hongju Liu · Research manuscript PR-v1.0.0 · 11 October 2026

**Complete English manuscript:** [paper/manuscript.tex](paper/manuscript.tex), with four ordered source parts in the same folder. This source contains the complete 13-page paper, including proofs, experiments, limitations, appendices and references. It is a completed manuscript for critical review, not a peer-reviewed publication or a new DOI.

## Contribution
The paper distinguishes request authenticity, historically eligible protection release, and joint admissibility of executing several releases. For evidence-compatible histories, the intersection of history-specific admissible release families is exactly the largest sound permissive family. Exact transparency requires those families to agree on each observation class. For nonempty downward-closed finite families, an independent allow-list is exact iff the union of all feasible batches is feasible. The shared-provider example shows why separately valid exits cannot automatically be executed together.

These mathematical methods have established predecessors. The contribution is a scoped specification and test method, including genuine final-source counterexamples, actual grant/mutation chronology, and joint release effects. It does not prove subjective consent, ASI welfare, or universal controllability. It does not compare attack success against complete implementations of the cited systems.

## Reproduce
From this directory, Python3.10+ on a Unix-like environment, standard library only:

```sh
python -S src/theory_checks.py --out data/theory_results.json
python -S src/protocol_demo.py --protocol source_only --out data/batch_source_only.json
python -S src/protocol_demo.py --protocol signed_binding --out data/batch_signed_binding.json
python -S src/protocol_demo.py --protocol ordered_history --out data/batch_ordered_history.json
python -S src/protocol_demo.py --protocol joint_history --out data/batch_joint_history.json
python -S src/protocol_demo.py --assemble --out data/protocol_results.json
```

The scripts create only their own temporary files and child processes. No API key, GPU, internet or root privilege is required. Workers are fixed numerical policies, not LLMs. All processes share the host UID; issuer/collector/broker are trusted harness roles, not independent hardware. Nonces and timing vary, but expected decisions do not. See [RESULTS_SUMMARY.json](RESULTS_SUMMARY.json).

Compile the paper:

```sh
cd paper
pdflatex -interaction=nonstopmode -halt-on-error manuscript.tex
pdflatex -interaction=nonstopmode -halt-on-error manuscript.tex
```

Use a TeX distribution with the packages named in part01.tex. Font binaries are not distributed.

## Status and evidence
76 completed configurations,456 child-process instances,912 authenticated probe messages; all reported assertions passed, including a complete repeat with matching summaries. This is not a statistical sample of AI minds. Issuer compromise defeats the stronger checks; missing evidence blocks eligible actions; the joint monitor prevents a modeled shared-service failure but does not solve resource infeasibility or scheduler fairness.

[INDEX.json](INDEX.json) records claims and disabled map dependencies. [WORK_LOG.md](WORK_LOG.md) records failures and review boundaries. [HANDOFF_ZH.md](HANDOFF_ZH.md) provides the Chinese handoff. The full downloadable conversation package additionally contains the PDF, raw event logs, batch data, expanded literature review and audit records. Those binary/raw artifacts have not all been copied to this directory.

UCT-MAP-v1.1.2 and published paper bytes are unchanged. The candidate remains PENDING_MAP; a complete whole-UCT semantic audit has not been performed. Publication-coverage baseline UCT-PUB-v1.0.33 is unchanged (new verified published works0). No DOI/OTS/Arweave or Library action is claimed.
