# Preservation operations

This encrypted literary archive is deliberately outside research paper catalogs,
DOI publication pipelines and paper CC licenses. The scheduled workflow provides
a distinct plaintext-exclusion security boundary: it receives only a pinned
allowlist of ciphertext, public decoder, cost model, manifests and proofs. It
never receives novel plaintext, passwords or recovery keys. This is a durable
preservation workflow, not a one-shot site publisher or a second reception route.

The existing uploader, spend helpers, dual-provider OTS verifier and wallet ledger
remain authoritative. Three existing uploader files gain one distinct category;
no previous category or limit is removed or loosened. Maximum one paid transaction,
maximum 0.01 AR, at least 0.25 AR wallet reserve, at most 0.50 AR rolling 30-day
wallet spend. An existing transaction resumes readback without another paid post.
An uncertain intent without a receipt stops and requires artifact recovery.

The schedule checks hourly while proofs are pending and becomes a no-op after
ARWEAVE_READBACK_PASS. All new upload attempts require a verified Bitcoin proof.
The verifier uses remote Bitcoin headers, not a locally synchronized full node.
Exact initial calendar receipt, upgraded proof, verification log, Arweave receipt
and wallet accounting remain in this directory/repository. The archive bundle
includes the full public package and verified evidence; it includes no plaintext.

The author accepted possible early solving and asked for no retained recovery key.
The generated secret was not written to disk, sent to GitHub, logged or retained
in deliverables. This is not a forensic memory-erasure guarantee. The private
manuscript remains with the author and is not part of the public allowlist.
