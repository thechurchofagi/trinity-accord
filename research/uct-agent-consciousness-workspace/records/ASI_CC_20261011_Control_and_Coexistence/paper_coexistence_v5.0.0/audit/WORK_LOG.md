# Work log — 2026-10-11, PR-v5.0.0

**Objective.** Adversarially audit PR4's credibility under forged evidence, common-cause backup failure and unseen effective bypass; revise the paper only on a demonstrable knowledge increment. UCT Research Guide v2.3 remains controlling; current scientific baseline UCT-MAP-v1.1.2; publication coverage baseline UCT-PUB-v1.0.33. The research concerns human-authorized tool revocation with preserved human service, not assumed AI personhood.

**Inherited.** PR1 authentic/history/joint release; PR2 bounded exit/resource; PR3 subject-neutral deterministic networks; PR4 exact evidence/backup message frontier C(n,r,k) and negative controls. Prior results unchanged.

**Actions and exact results.**
1. Read PR4 full 14-page manuscript, its source and critical review; specifically verified that it already includes misleading sensor and bypass trials. Scoped new question to actual upstream root rather than message count.
2. Checked primary papers: Fawzi et al. 2014 sensor/actuator attack; Andersson&Dán 2026 active sensor false-data recovery; Terekhov et al. 2026 monitor attacks; Greenblatt et al. 2024 AI control; Arike et al. 2026 information-access and monitoring. These establish direct predecessors.
3. Derived the root-lifted source-cell/physical-capacity/serial-effect certificate. For the one-root-compromise and four-route model, derived exact 1-root impossible / 2 roots need8 universal backup slots / >=3 roots need3 under a one-bit per-root truthful group sensor. Proof explicitly bounds observation timing, shared memory and after-commit adaptation.
4. Ran `src/root_frontier.py`: 5,432 separate root/capacity fault profiles and 408 report/attack cases in 12 constructions; 4 positive scoped architectures, 8 with explicit counterexample failures. Verified correlated bank and gate failures, common master, one-reporter failure and a hidden bypass.
5. Ran `src/root_pareto.py`: 7,380 capacity vectors enumerated, frontier [None,8,3,3] for roots1..4.
6. Ran `src/independent_oracle.py`: separate direct enumeration over all 16 pre-arm subsets in each observation cell for all the same 7,380 capacity vectors; frontier and positive design counts match the first proof checker.
7. Ran `src/role_protocol.py`: ten real fixed-role subprocesses reused across 408 synthetic attack configurations; 3,156 authentic HMAC-bearing role messages. Three-root co-installation and two-root 4+4 design pass all stipulated single-root fault cases; shared sensing, reserve, veto roots and hidden bypass exhibit explicit failure traces. Software provenance is not physical independence.
8. All scripts rerun after the corrected count and nominal-capacity field. Program hashes, full raw records, and source paths will be listed in `MANIFEST.json`.
9. Drafted self-contained PR-v5 revision, new references, claim ledger, negative cases, Chinese handoff. No published paper, DOI, OTS or Arweave triggered. Full UCT semantic audit not completed.

**Result status.** Exact conditional finite theorem/countermodels plus simulated-role protocol evidence. Mathematical mechanisms inherited from fault-tolerant control, error correction, matching and imperfect-information decision theory. Scoped root-cost discontinuity for the declared concrete architecture is a genuine new manuscript increment, with unverified global priority. Not a real-world ASI controllability claim.

**Next experiment.** Verify actual fault-root independence and complete effect paths on one bounded physical testbed with separate power, firmware and control owners; compare stateful after-failure inspection against the pre-commit fixed action theorem. Do not claim a physical certificate from HMACs or Linux PIDs alone.
