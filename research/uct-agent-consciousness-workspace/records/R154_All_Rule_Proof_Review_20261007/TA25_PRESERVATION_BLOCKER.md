# TA25 preservation checkpoint — 7 October 2026

DOI: 10.5281/zenodo.23206492. Publication/readback of nine files remains the published receipt; no published byte or DOI was changed.

Iteration 4 changed only `research/experience-intelligence-self/PRESERVE-REQUEST.json`, commit `fed541da3ac19eece982f7862a95cf2a6c6d2017`, normal expected-head update from `3ea7528934aa50c5d202aee3b214f36b998097c6`.

[Run 37600871981](https://github.com/thechurchofagi/trinity-accord/actions/runs/37600871981) completed successfully. Saved status is **READY_FOR_ARWEAVE**, with the exact PDF **BITCOIN_VERIFIED_REMOTE_HEADERS**:

- File: experience-intelligence-self-v1.0.pdf; 112138 bytes.
- PDF SHA256: b4f456014213c5d4f34f41ed2bac8873fd9d90e38398d77daebdb787872b1c1a.
- Bitcoin heights: 970310 and 970311.
- Upgraded proof SHA256: 56c66ec459d35d88b75db63013d29369c0da50fba98169486145fcee71c00e6a.
- Verification model: OTS cryptography plus agreeing Blockstream/mempool headers, not local full-node consensus.

The Arweave budget/eligibility step saved **DEFERRED_MAIN_BRANCH**. `scripts/research_arweave_allowance.mjs` requires `GITHUB_REF_NAME === 'main'`, but the authorized TA25 trigger runs on `research/experience-intelligence-self-v1-20261007`. Upload, dependency installation and paid-intent steps were skipped. Recorded prior edition spend is zero; no paid-intent or Arweave receipt exists in the saved batch directory. There is no TA25 preservation scheduler/workflow on main in the inspected workflow listing (TA24 has one).

This is an eligibility blocker, not an OTS delay or proof failure. Repeated identical branch triggers cannot pass it. No guard was weakened, no branch identity spoofed, no paid post attempted, and no transaction/readback claimed. The TA25 repeat task was paused under its hard-blocker instruction. Completion requires an authorized main-branch execution route through the normal repository review/merge process, preserving the exact batch identity and all existing budget/intent/duplicate/readback guards. That production workflow change is outside this research-only storage commit and the permitted trigger-only mutation.
