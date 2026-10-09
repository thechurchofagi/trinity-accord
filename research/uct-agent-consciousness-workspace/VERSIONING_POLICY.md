# Versioning and research identity

Current release: **UCT-MAP-v1.1.2**, sequence 4, audit R188-ALLMAP-COMPAT-20261009-v1.

A completed substantive research or full-map audit cycle must create a NEW immutable release directory and increment the release sequence and version. The next ordinary completion is v1.1.3; a compatible major batch may increment the next minor version and breaking ontology/signature changes require v2.0.0 with an explicit migration. Never overwrite v1.0.0 with changed content. Work-in-progress checkpoints use a checkpoint ID and do not falsely advance a completed status.

Required release fields: version, sequence, parent version/commit, source hashes, added/changed/suspended item IDs, complete coverage ledger, result/proof/code/evidence locations, OPEN obligations, local archive hash, remote commit and readback result.

Required record identity: stable descriptive research ID, title, result version, map version first included, last changed version, scientific delta, source paths and truth/novelty limits. Historical R numbers are labels, not unique primary keys. In particular IE20261008 and EI20261008 are different research records.

Only `CURRENT_STATE.json` identifies the current completed release. `MASTER_INDEX.md` and `HANDOFF.md` must link to it; historical headers are not current pointers. Same-version remote persistence receipts may be stored separately without rewriting scientific release bytes.

Audit coverage, conditional validity, actual instantiation, named phenomenal bridge, publication and persistence are separate states. A successful file save does not promote a premise. Reviewer-controlled OPEN findings cannot be self-closed.

For concurrent workers: read the current branch head, compare the expected head, build an additive commit without deleting new work, and move the ref only with an expected-SHA lease. Failed leases require rereading. Use [skip ci]; no publication, DOI, OTS, Arweave, deployment, PR or scheduler changes are implied.


## Binding output policy (canonical guide v2.3 §§0,8A)
Every substantive user-visible research result requires a versioned WORK_LOG.md, HANDOFF_ZH.md, exact code/test receipts, map ledger and GitHub readback (or explicit failures), separate research result and completed-map version identities. The root guide already contains this requirement and takes precedence.

## Publication coverage versions

[UCT-PUB-v1.0.0](PUBLICATION_COVERAGE.json) is the first immutable publication coverage release. It is independent of UCT-MAP-v1.1.2. Its ledger and shards bind exact work/deposit identities, formal disclosures, body comparison scope, residual assessments and source evidence. Advance the coverage version when claims/publication evidence/assessments change; retain the preceding snapshot. Metadata-only coverage, guide or citation changes do not increment the scientific-map version.

Every current log, handoff, registry and map entry must cite the same coverage version and a change record or an explicit checked no-change reason. Working research, formal publication, reserved DOI and preservation are different states. A same-label different DOI deposit remains a separate publication record of the same work. A new pending checkpoint is not a completed map release.
