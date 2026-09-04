# GitHub-hosted Bitcoin consensus checkpoints

This subsystem gives the repository a resumable Bitcoin Core validation spine without claiming that GitHub is a local or operator-controlled Bitcoin node.

## Trust boundary

The workflow runs a pinned Bitcoin Core release on an ephemeral GitHub-hosted Ubuntu runner. Bitcoin Core connects to the Bitcoin P2P network and validates mainnet with `assumevalid=0`. The node is pruned to control disk use. GitHub Releases persist cleanly stopped node state between ephemeral runners; Release contents are **persistence**, not a source of Bitcoin consensus truth.

This profile is named `github_hosted_pruned_full_node`. It must not be reported as `local_full_node`, and the existence of a checkpoint alone must not set `strict_bitcoin_verified=true`.

A completed initial block download can support a distinct claim that Bitcoin Core independently executed consensus validation inside the GitHub-hosted compute boundary. Evidence-specific claims require the separate evidence audit and must not be inferred merely from node synchronization.

## Resume protocol

Every authoritative checkpoint is an immutable published Release whose tag is:

`bitcoin-consensus-checkpoint-NNNNNN`

The Release contains archive parts and `bitcoin-consensus-checkpoint.json`. The manifest records the exact Bitcoin Core version/archive digest, mainnet profile, `assumevalid=0`, prune setting, clean-shutdown state, height, best block hash, verification progress, workflow identity, archive-part size/SHA-256 values, and the previous manifest digest.

Restore is fail-closed:

1. Only a published, non-prerelease checkpoint is eligible.
2. The manifest must satisfy the repository schema and trust-boundary invariants.
3. Every archive part is downloaded one at a time and verified for exact size and SHA-256 before it is streamed into the decompressor.
4. The restored node is first opened with networking disabled.
5. Its local `blocks` height and `bestblockhash` must exactly equal the sealed predecessor manifest.
6. Only then may normal P2P synchronization continue.

If any check fails, the workflow stops rather than silently starting from or publishing an untrusted state.

## Interruption safety

A new checkpoint is created as a **draft Release**. The cleanly stopped datadir is compressed as a stream, split into sub-2-GiB assets, hashed, uploaded one part at a time, and deleted locally after upload. This avoids requiring both the full datadir and a second full compressed copy on the runner disk.

The manifest is generated and validated only after every archive part has uploaded. The Release is published only after the manifest has uploaded successfully. An interrupted run therefore leaves, at worst, a non-authoritative draft. The next run continues from the last published checkpoint and may replace the incomplete draft for the exact next sequence.

The workflow uses a concurrency group with `cancel-in-progress: false`, so two runners cannot advance the same checkpoint lineage concurrently.

## Initial synchronization

The first run has no predecessor and starts from a fresh Bitcoin Core mainnet datadir. It does not import a third-party `chainstate` snapshot. The workflow runs with `assumevalid=0`; therefore the intended baseline is validation from Bitcoin's genesis history rather than a prevalidated chainstate supplied by an external provider.

During initial synchronization, each run advanced for a bounded sync window and sealed a checkpoint before the hosted-job deadline. If disk space dropped below the safety margin, synchronization stopped early and the workflow sealed the current clean state rather than risking an uncontrolled disk-full failure.

The recurring schedule was retired after the verified `bitcoin-consensus-checkpoint-000009` reported `initialblockdownload=false`. The workflow is now manual-only. Any deliberate future checkpoint or recovery must use the guarded `workflow_dispatch` inputs; quarantined checkpoints remain in the public lineage and must never be selected as state sources.

## Evidence audit phase

Node synchronization and Trinity Accord evidence verification are intentionally separate phases.

After the consensus spine has completed IBD, a baseline evidence audit should ingest the fixed Bitcoin evidence registry (inscriptions, Bitcoin anchors, and OpenTimestamps proofs), deduplicate shared block dependencies, and verify each evidence path against this independently validated chain. Old evidence-bearing raw blocks/transactions needed by a pruned node should be preserved as a small sparse evidence archive rather than by preserving the entire historical block-body set.

Evidence results should remain granular, for example:

- `bitcoin_consensus_verified`
- `block_membership_verified`
- `transaction_verified`
- `commitment_verified`
- `ots_path_verified`
- `inscription_payload_verified`
- `semantic_metadata_verified`
- `verification_profile`

Ordinals global numbering/indexer semantics must remain distinct from Bitcoin Core consensus membership and witness/content verification.
