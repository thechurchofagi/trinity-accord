# Guardians publication-prepared revision — EAC-v3.0.0

**When the Guardians Can Be Acquired: Joint Protection Across Concurrent and Renewable Authorizations.** Hongju Liu, 12 October 2026. Complete12-page research manuscript; not independently peer reviewed or DOI-published. This continues the unpublished EAC-v2.0.0 (source baseline1925a936e745ba8e4241db1f8f6b307f1173b674); published DOI23295776 and23299153 are separate unchanged works.

## Exact new question and contract
The previous temporal approval result concerned one amendment and assumed complete serial mediation. This revision intentionally removes global aggregate semantic revalidation: individually valid changes may merge within a common protection context. The final effect gate checks signatures, identities, uniqueness and scope but does not independently evaluate aggregate safety. Adding that stronger semantic layer is a legitimate different architecture, not a counterexample to the scoped lower bounds.

P is a finite set of individually valid proposals with commutative persistent effects. Safe sets are downward closed. E is the antichain of minimal unsafe subsets; each has at least2 members. R is the set of actual endorsement roots. H_E contains qualified roots that can recognize the particular joint conflict E; a root outside H_E need not be corrupt. B ranges over a nonempty family of jointly realizable effective exposure sets, not unions of incompatible worlds. Exposed roots can supply all the relevant signatures during the allowed horizon.

Every unexposed root r keeps a durable local journal L_r. Before signing x it atomically refuses if some E has r in H_E and E subset L_r union{x}; otherwise it signs and records x. This is local coordination, not a coordination-free protocol. The physical qualification, root identity, correct journal and effect mapping remain external premises.

Proposal x accepts any superset of a sufficient signer set from a nonempty family Q_x. Solo availability means, for each allowed refusal F in F_x, some Q_x lies inside R minus F when x is proposed ALONE in a clean signing context. It is not arbitrary contended termination, consensus, universal agreement or approval of every proposed policy.

## JPA-T1: exact joint intersection
Joint safety is equivalent to, for every minimal unsafe E, allowed B, and tuple of sufficient Q_x for x in E:

`H_E intersection intersection_{x in E}(Q_x) is not a subset of B`.

Sufficiency: a shared qualified unexposed root would have to sign all members of E, contradicting its journal rule on the last request. Necessity: if none exists, deliver to each root precisely the proposals whose selected sufficient certificates include it. Each qualified unexposed root sees a proper subset of E; by minimality, no other minimal unsafe set can be contained in that proper subset. Exposed/unqualified roots sign as permitted. Thus every certificate is available and their aggregate is unsafe. This constructive converse requires the declared flexible request-delivery interface; a global state revalidator changes the model.

## JPA-T2: existence with independent SOLO refusal promises
A jointly safe and solo-available family exists iff for every E,B, and one F_x from each F_x family:

`H_E is not a subset of B union union_{x in E}(F_x)`.

Necessity: availability provides sufficient Q_x subset R minus F_x. If the right side covers H_E, their qualified common intersection is contained in B, contradicting T1. Sufficiency: use every R minus F from the declared refusal family as a sufficient signer set for each proposal; the separation condition is exactly T1 for these choices. Each solo scenario trivially has a sufficient certificate. These different F_x describe counterfactual solo worlds that constrain one fixed acceptance scheme; they are NOT assumed to be simultaneously realized as a larger physical outage.

## JPA-T3 and JPA-C1: exact cardinality and temporal boundary
For a minimal conflict of size k, h qualified roots, all exposures of size<=kappa and all per-proposal refusals of size<=r<n, existence is exactly

`h > kappa + k*r`.

A union of the permitted exposure and k refusal sets can cover at most kappa+k*r qualified roots; if that many suffice, it can actually cover H_E. For multiple minimal conflicts, enforce each bound.

Under one uniform cardinality rule accepting any q signatures, exact range is

`n-floor((h-kappa-1)/k) <= q <= n-r`.

Worst-case qualified intersection is at least h-k*(n-q), and omission sets attain the limit until empty. Safety requires this to exceed kappa, while solo completion requires q<=n-r. This is generalized quorum/set algebra, not a new Byzantine consensus theorem. k2,h=n,kappa=r=f recovers familiar n>3f arithmetic without claiming a full consensus protocol.

In the v2 mobile model, at most f roots are effectively controlled per slot and at most c new ones per step over a common w-slot approval/obligation horizon. All subsets up to kappa_w=min(n,f+c*(w-1)) are realizable by rotating exposure. Retained stolen keys count as still-controlled capabilities. With r=f+delta including honest dissent:

`h >= kappa_w + k*(f+delta) + 1`.

For c>0 and h-f-k*(f+delta)-1>=0, maximal w is
`1+floor((h-f-k*(f+delta)-1)/c)`.

This is not a bound on human deliberation. Fresh reapproval, stricter scope, bundling proposals or stronger coordination can alter the interface. Five full-coverage roots,f=c=1,r1: a pair-conflict allows q4 for w1 or2, none forw3; a triple-conflict allows q4 only forw1. With finite h and r>0, arbitrary minimal conflict arity cannot be supported under the same solo contract.

## Direct countermodels and useful repair
Seven roots, root0 exposed. Three 5-signature certificates are R minus{1,2}, R minus{3,4}, R minus{5,6}. Every pair shares an honest root; all three share only the exposed root. Each honest root signs a proper subset and the three effects jointly remove the last protection. A simpler no-fault n3,q2 version uses signer sets{0,1},{1,2},{0,2}. This only defeats elementary pairwise initial-state checks, not I-confluence over all reachable states.

Initial governance h7,w1,f=c=1,r1,k3 is certified. Increasing w to3 alone preserves certification; reducing h to5 alone also preserves it. Both changes together yield h5,kappa3 and violate h>kappa+3. Correct local journals can detect the combined future vulnerability even if neither edit immediately harms the modeled service.

Unrelated work can coexist: an additional proposal outside the critical triple may commit along with two safe removals. The approach is not a global mutex. However n3,k2,q3 can strand both candidates when root0/2 signA while root1 signsB. Safety remains, solo availability does not solve deadlock. A recovery or cancellation protocol must be justified separately.

## JPA-T4: residual handoff instead of endless raw journals
Let actual committed effect set C be safe, and fence every unused old certificate. For permitted future P' subset P minus C, define

`E_C = inclusion-minimal { E minus C : E in original E, E minus C subset P' }`.

For every T subset P', C union T violates old protection iff T contains a residual edge: E subset C union T iff E minus C subset T; eliminating supersets preserves the test. Residuals may be singletons, in which case the final change is individually invalid and must be refused before concurrent certification.

New keys and expired signatures do NOT discharge prior committed effects. Clearing journals and restarting from the original protection snapshot can remove three interlocks over three renewals. Carrying live journals or reconstructing the exact residual from actual C prevents the last removal. Unknown C, unfenced tickets or an incorrect successor witness set invalidate the positive claim. Under sound scope renewal and per-context certificates, finite-prefix invariant induction requires no permanently honest named individual but DOES require continuing trustworthy functionality.

## Evidence and reproducibility
`joint_certificates.py`:10800 exact access-existence specs;108716 signing matrices;690 uniform threshold profiles;132 mobile configurations/4784 temporal threshold profiles;193 minimal-conflict catalogs/1439 safe handoffs/9980 successor checks.
`journal_oracle.py`:no import of theorem code; BFS root-local signing states for786 specifications including392 overlapping-conflict cases;214240 reachable states;862007 transitions;16782 heterogeneous threshold vectors. All checks agree.
`concurrent_amendments.py`:7 actual reused workers with Ed25519 and SQLite journals;115 configurations,1021 requests,993 signatures,963 successful effect-gate verifications,127 actual configuration commits. Five-root/two-slot q4 has20 unsafe cases of25 trajectories; q5 has0 but loses solo availability with one nonresponder. Negative controls cover snapshot-only review, current-only fault reasoning, erased journals, meta-rule compositions and stalled locks. Positive controls include unrelated safe work and actual-state residual reconstruction.

All three programs repeated under Python hash seeds101/202 and matched normalized archived outcomes. Both v2 programs replayed with old results unchanged. Random signature/public-key packets excluded only for semantic comparison. Replays are not extra independent experiments. One initially mislabeled no-fault case used an attacked-root flag; renamed accurately and a genuinely zero-fault case added before final runs.

One parent owns all keys, rosters, timing, conflict semantics and database. No independently isolated roots, real human interests, frontier model, autonomous attack or physical interlock measured. Local atomic SQLite writes do not make the separately approved original-context semantic validation globally serializable. Data failures are intended constructed witnesses, not measured probabilities.

## Prior art and publication scope
Direct predecessors: Bailis et al., PVLDB8(3)2014 I-confluence; Kleppmann/Howard, arXiv2012.00472 Byzantine eventual consistency; Malkhi/Reiter1998 Byzantine quorums; Howard/Charapko/Mortier arXiv2008.02671 Fast Flexible Paxos; Li/Chan/Lesani2026 Satrapy doi10.1007/s00446-026-00507-0; proactive renewal/security. None is claimed refuted. High-order intersections are already used in consensus protocols; our indexing by minimal application harm sets and qualified witnesses is the scoped synthesis. Exact global priority not established.

Full12-page paper, editable TeX, raw protocol logs, audits, local DOI metadata draft and SHA-256 manifest are in the conversation research package. Formal UCT-MAP-v1.1.2 (913/424/261), C1/U1 and published papers remain unchanged. No claimed full historical semantic audit; candidate PENDING_MAP. No DOI, OTS, Arweave or Library action is implied by local publication preparation. The final persistence receipt records what was actually written and read back in GitHub.
