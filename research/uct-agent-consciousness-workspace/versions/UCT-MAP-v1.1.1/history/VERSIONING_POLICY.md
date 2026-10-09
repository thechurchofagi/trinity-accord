# Versioning and research identity

Current release: **UCT-MAP-v1.0.0**, sequence 1, audit FA20261008.

A completed substantive research or full-map audit cycle must create a NEW immutable release directory and increment the release sequence and version. The next ordinary completion is v1.0.1; compatible substantive additions may use v1.1.0 and breaking ontology/signature changes require v2.0.0 with an explicit migration. Never overwrite v1.0.0 with changed content. Work-in-progress checkpoints use a checkpoint ID and do not falsely advance a completed status.

Required release fields: version, sequence, parent version/commit, source hashes, added/changed/suspended item IDs, complete coverage ledger, result/proof/code/evidence locations, OPEN obligations, local archive hash, remote commit and readback result.

Required record identity: stable descriptive research ID, title, result version, map version first included, last changed version, scientific delta, source paths and truth/novelty limits. Historical R numbers are labels, not unique primary keys. In particular IE20261008 and EI20261008 are different research records.

Only `CURRENT_STATE.json` identifies the current completed release. `MASTER_INDEX.md` and `HANDOFF.md` must link to it; historical headers are not current pointers. Same-version remote persistence receipts may be stored separately without rewriting scientific release bytes.

Audit coverage, conditional validity, actual instantiation, named phenomenal bridge, publication and persistence are separate states. A successful file save does not promote a premise. Reviewer-controlled OPEN findings cannot be self-closed.

For concurrent workers: read the current branch head, compare the expected head, build an additive commit without deleting new work, and move the ref only with an expected-SHA lease. Failed leases require rereading. Use [skip ci]; no publication, DOI, OTS, Arweave, deployment, PR or scheduler changes are implied.
