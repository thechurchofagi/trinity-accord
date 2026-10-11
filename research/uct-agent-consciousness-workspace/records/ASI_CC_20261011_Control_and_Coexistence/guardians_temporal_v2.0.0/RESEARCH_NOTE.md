# When the Guardians Can Be Acquired — EAC-v2.0.0
## Temporal Representation and Renewable Authorization in Multi-Agent Governance

Hongju Liu, 12 October 2026. Revised research manuscript, 11 pages, not peer reviewed or DOI published. This continues the unpublished guardians paper ASI-CC-v1.0.0, NOT a new revision of the separately published persistent-effects/admission work (DOI 23299153) or diagnosis/standby work (DOI 23295776). Exact baseline Git commit 4feb7e97a29555423a95765a339eca3f2d6bf86b; original guardian TeX Git blob 1b7c22e0c0640d3d04d60624e8cc6861f9c9adb5.

## Problem and non-substitution requirements
A static acquired-permission closure can miss temporal certification: one attacker can visit different effective signing roots while already signed approvals remain usable. Independently, a vote majority does not establish that each retained human-protection clause had qualified rejection witnesses. Current control, usable historical evidence, signature identity, real control ancestry, protected-clause coverage and decision availability are separate objects.

The contribution is a scoped temporal representation condition plus explicit cases in which its assumptions matter. Mobile adversaries, proactive renewal, quorum separation and hitting-set mathematics are inherited, not new primitives. No need to settle AI subjecthood before this operational analysis. No conclusion that artificial experience or moral interests are absent.

## Complete declared model
For one parent-state-bound amendment descriptor x, R is the finite set of actual effective endorsement roots. Every retained protection/actual violation pattern j has qualified rejectors H_j. While not exposed, these roots refuse any violating descriptor. Outside H_j the model permits endorsement despite this violation. B is a family of JOINTLY realizable usable corrupt-endorsement sets, not an arbitrary union of incompatible histories. F is a family of withholding sets for eligible proposals: the other roots provide timely agreement. Honest dissent can be included in F and is not corruption.

The verifier accepts when the signer set contains a sufficient set Q in an acceptance family. Cryptography, complete effect mediation, honest receipt times, state binding and reliable root identification are prerequisites. No extra omniscient semantic oracle is hidden in this endorsement-only layer.

If primitive clauses can only be violated jointly, use H_V = union of their witness sets, and pattern-specific exposure families as needed. Inventing separately possible violations can wrongly produce an impossibility result. The cardinality examples assume the listed isolated violations are realizable.

## TRA-T1: necessary and sufficient separation
A sound and conditionally available acceptance rule exists iff for every admitted j,B,F,

`H_j is not a subset of B union F`.

The largest family of individually sufficient sound signer sets is

`Q* = { Q nonempty : Q intersects (H_j minus B) for every admitted j,B }`.

Proof: a violation of j can be endorsed by B together with all non-witnesses; therefore every sufficient set must contain an honest relevant rejector outside B. If availability requires a set inside R minus F and all relevant nonexposed witnesses are in F, no such set exists. Conversely, under the separation condition the full available set R minus F is a sound sufficient set for every allowed refusal pattern. This proves both directions. It is validity of one proposal, not Byzantine total-order consensus.

## TRA-P1 / TRA-T2: exact duration and representation boundary
Assume n roots, at most f<n effectively controlled in a slot, at most c<=f newly controlled roots from one slot to the next, and endorsements remain usable for a common w-slot ballot. Every subset of size at most

`kappa = min(n, f + c*(w-1))`

can be accumulated; none larger can. Necessity is counting newly visited roots; attainment rotates roots without exceeding f. Retained stolen signing keys remain effective control: clearing a host flag does not remove them from this count.

Permit up to f+delta total withheld votes on an eligible proposal, delta including legitimate non-fault disagreement. Let h be the minimum witness-set size for the actual violation cases. Then some sound and conditionally live rule exists iff

`h >= kappa + f + delta + 1`.

Uniform thresholds are exactly

`n-h+kappa+1 <= q <= n-f-delta`.

Proof: kappa exposure roots and f+delta refusing roots can cover H_j iff its size is at most their sum. Apply TRA-T1. When feasible, a violating proposal can get n-h non-witness votes plus kappa corrupted-witness votes; an eligible proposal may only have n-f-delta votes. Structured quorum rules can save signatures but cannot evade the exact separation obstruction.

If c>0, the maximum window is `1+floor((h-2*f-delta-1)/c)` when the numerator is nonnegative. This is the lifetime of jointly usable corrupt evidence, not a ban on thoughtful deliberation; fresh reapproval or a new root/evidence interface changes the bound.

Five full-coverage roots, f=c=1,delta=0: w1 permits q2..4; w2 q3..4; w3 only q4; w4 no q. Three authentic approvals collected at separate instants can bypass q3 without three simultaneous corruptions. Requiring all five votes prevents that attack at w4 but blocks a legitimate proposal with one allowed holdout.

## Representation and institutional-change witnesses
Seven roots; A watched by {0,1,2}, B by {3,4,5}, root6 not a sound witness for either. Even with no corrupt root, reviewers3..6 can approve an A-violating amendment according to their narrower remit. Under a one-slot f1 assumption, two votes from EACH triple are sound and available and may need only4 signatures; a uniform rule needs6. Widening the window to2 makes h3 insufficient against accumulated2 plus one holdout. Approving the window change merely because it causes no immediate physical harm can create a vulnerability in the next ballot.

TRA-P2: with valid per-ballot certificates, old-rule authorization of each successor, preserved actual claims, fresh scoped roster/endorsements, complete serial mediation and correctly re-established effective control bounds, every finite prefix of accepted amendments preserves the stated invariant. No named guardian must remain sound forever. This inherits proactive-security logic and invariant induction. It does NOT remove continuing trustworthy functionality or prove all real humans will agree. It does NOT establish physical root independence, a distributed enrollment mechanism or unbounded real-world safety.

## Executed evidence
`temporal_representation.py` exhaustively considers all128 access-structure families on3roots across325125 exposure/refusal/witness specifications; direct existence matches TRA-T1. Temporal DP checks170 parameter configurations and2115 threshold profiles; explicit enumeration of3633 trajectories in48 small configurations agrees. Included negative control for joint-only violation patterns.

`signed_amendments.py` performs actual Ed25519 signatures and SQLite commits.418 configurations,1419 generated signed messages,1427 successful verifications (some packets reused),207 commits including65 intentionally unsafe negative-control commits. At n5,w3, q3 accepts60 of125 invalid trajectories, q4 accepts0; q4 completes125 of125 eligible cases with one final holdout. Ten fresh-key epochs visit all5roots over time, reject all10 invalid proposals and complete all10 eligible changes. All keys, receipt slots, root mapping and database are provided by one parent. No real AI, independent hardware or human legitimacy measurement.

The exact source and semantic output repeated under PYTHONHASHSEED101/202 agree after removing only random signature packets. All three original guardians scripts were rerun and match their archive JSONs. Counts are not multiplied by repeats.

## Status, prior art and continuation
Direct predecessors: Herzberg et al., CRYPTO1995, doi10.1007/3-540-44750-4_27; Castro/Liskov, TOCS2002, doi10.1145/571637.571640; Malkhi/Reiter, Distributed Computing1998, doi10.1007/s004460050050; Li/Lesani, arXiv2304.02156v2; Acemoglu/Egorov/Sonin, AER2012; Zhu/Wang, arXiv2610.00347v1. A scoped explicit certificate and application are claimed, not a new majority theorem or verified worldwide originality.

Formal UCT-MAP-v1.1.2 remains unchanged (913/424/261); coverage baseline UCT-PUB-v1.0.33. Full historical semantic review and full publication corpus audit incomplete; PENDING_MAP. No DOI/OTS/Arweave action.

Next scientifically important validation: establish which actual changing human/tool roots can reliably reject each retained human-protection violation, how long their approvals remain usable, and whether successor enrollment preserves those facts. The current cryptographic simulator cannot supply that causal/legitimacy bridge merely by labeling nodes independent.
