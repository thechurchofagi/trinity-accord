# UCT-MAP-v1.1.2 — complete semantic compatibility review and verified assembly

Sequence4; parent UCT-MAP-v1.1.1; audit R188-ALLMAP-COMPAT-20261009-v1.

The release contains913 nodes,424 active conditional rule schemas,261 nondeductive context links and10 suspended historical rules:1,608 per-item semantic review records. All1,419 inherited contracts and189 new/normalized contracts were read. R185, HOM/R186, UI, CM, R187 and R188 are registered as reviewed conditional declarations; AC and IL remain independently pending.

The substantive R173 effective correction preserves its stable ID and exact old object while enforcing the pre-existing R175 restriction. UI, HOM, CM, R187 and R188 model/observer/timing/scope guards are explicitly expanded. All10 suspended routes remain nonexecutable. See [the complete semantic review](audit/WHOLE_MAP_SEMANTIC_REVIEW_REPORT.md) for the arguments and limits, and [the independently assembled validation](audit/ASSEMBLED_VALIDATION.md) for the separate57-check reconciliation.

This is not a re-proof of every historical source theorem, global consistency proof, empirical UCT validation, independent peer review or discharge of actual/named-experience premises. Reviewer-controlled QC10/IA-QC11/QC12/QC13 remain open. Node registration does not establish a premise.

## Exact evidence and reconstruction

The full graph, human-readable map, all per-ID reviews, exact normalized objects, source notes and original correction history are in the capsule. CAPSULE.json identifies its byte hash; CAPSULE_MEMBER_MANIFEST.json inside it gives every member hash. SOURCE_LOCATIONS.json maps recorded local paths to portable members.

```bash
python3 restore_capsule.py --output /tmp/uct_v112_restored
python3 /tmp/uct_v112_restored/build_release.py
```

Use a new destination or an identical already-restored copy. The restorer refuses different existing bytes. The builder only reconstructs and verifies the saved review decisions; running it does not perform semantic review. The original baseline ledger is historical evidence, while REVIEW_LEDGER.json is the new full ledger.

The associated English paper and exact experimental receipts are in `records/R188_Encoder_Access_and_Recovery_20261009/`. The complete downloadable research archive includes expanded graph/ledger, manuscript, PDF, code, results, logs and sources. No journal, DOI, OTS, Arweave, PR or deployment action accompanies the research release.
