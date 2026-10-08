# MGTD Paper v1.0.0 — publishing workflow

This is a **standalone methodological preprint** by Hongju Liu, distinct from UCT theoretical papers and distinct from the UCT map's own version.

**Frozen scholarly files:** `MGTD_Method_Paper_v1.0.0.pdf`, exact SHA256 `ba85c0ff9f2bf4be9e0a29c051c2ad83d1eb72b57e0ca2ba827bd17c28dcc310`, Markdown source and the complete reproducibility ZIP. No PDF rebuild after preflight.

Author has explicitly instructed publication in the repository's order: **Zenodo DOI and public exact-byte readback → OpenTimestamps proof/Bitcoin verification → guarded paid Arweave bundle/readback.** Publishing stage never stamps pre-DOI, makes an Arweave payment, or claims peer review, originality, or empirical validation. `publication.py` uses the existing GitHub Actions `ZENODO_ACCESS_TOKEN`, stores create-once intent and refuses unknown duplicate POSTs. A separate follow-up batch must be enabled only after an actual successful Zenodo readback receipt, with the DOI and hashes obtained from it.

Publication is triggered only by an explicit authorization file commit marked `[mgtd-publish]`. If a remote POST outcome is ambiguous, stop and inspect the retained intent and live Zenodo record; do not blindly rerun. The main UCT formal-map releases, other DOI records and Trinity Accord Originals are not amended.

The PDF is the primary scholarly file; an attached full reproduction bundle is offered as methodology evidence. The manuscript discloses substantial AI assistance. New contributions are an operational synthesis, not a claim that all elements of argument maps or versioned research were invented here.
