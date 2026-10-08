# AC20261009 — Action-Port Calibration and Task-Relative Self-Model Sufficiency

**Result:** AC-RESULT-v1.0.0, 9 October 2026. **Method:** MGTD v1.0.1. **Project:** Hongju Liu's UCT experience–intelligence–self research; substantial AI-assisted derivation, checking and writing. **Baseline:** UCT-MAP-v1.0.0 / FA20261008; live branch inspected at 11607e7edd2893252aef362f2ac3a4195bc3d566. **Map status:** PENDING_MAP / AUDIT_INCOMPLETE. This is a versioned scoped research result, not a completed UCT-MAP-v1.0.1 or a new paper release. R185 remains pending and is not an established premise.

## 1. Goal and prior-paper inheritance

The question is not whether a calculator can operate outside all experience: C1/U1 already commit UCT to experience for admitted actual processes. The question is which action-relative organization is needed for which control competence. This study separates knowing an elementary update law, identifying the actual action-to-effect connection, retaining the relevant distinctions, and actually using them. None is equated with familiar phenomenal mineness.

R146:SELF_TARGET_SUFFICIENCY already gives a general factorization criterion. R147:ROUTING_MODEL/ROUTING_LIMIT already separate sensed, acted-on and containing body, and show that synchrony can conceal rewiring. OO/RC study task access and joint use. The new application here computes exact residual ambiguity, goal-specific attainable control, calibration budgets and task-relative sufficient retained-state counts. The synchrony warning and coding principle are not claimed new.

## 2. Explicit finite contract

There are n>=2 command ports and n observable effect ports. An unknown, fixed bijection pi maps each command to its effect. Binary commands u obey x_next=x XOR P_pi u; the controller observes changes y=P_pi u. The full unknown is pi, not the generic update rule. Noiselessness, bijectivity and fixed connections are assumptions, not facts about brains.

For probability claims pi is uniform over n! possibilities. A calibration policy can use prior responses and independent randomness; condition on its random seed. A later goal is independent of the wiring. After calibration, a fixed installed decoder receives the transcript and goal g and issues ONE terminal command, with no extra test-time observation or hidden source of wiring information. The memory theorem below counts all pi-correlated information accessible to that decoder, including weights, hardware settings, accessible plant state or external records. An analyst's successful decoding is not automatically actual controller use.

## 3. AC1: exact residual wiring classes, including adaptive probes

For k probes define command signature c_i=(u_i^1,...,u_i^k) and effect signature d_j=(y_j^1,...,y_j^k). Since d_pi(i)=c_i, equal-signature command classes A_c and effect classes B_c have equal sizes m_c. The compatible wirings are precisely independent bijections A_c -> B_c. Thus

    number of compatible wirings = product_c m_c!.

Proof: every observed equation forces this matching. Conversely any such set of bijections reproduces all response vectors. In an adaptive policy, the same observed prefix and conditioned policy seed yield the same next probe by induction, so compatibility also implies the same actual calibration transcript. The likelihood is equal for all compatible pi under the uniform prior, giving a uniform posterior on this product class.

Equal values are not identical physical occurrences, and the count is not a number of subjects.

## 4. AC2: exact goal-dependent control law

For goal g, let r_c be the number of requested active effects in B_c. The optimal one-shot success is

    p*(g|h) = product_c [1 / binomial(m_c,r_c)].

Proof: selecting a different number of commands in A_c cannot produce g. With exactly r_c selected, an unknown uniform within-class bijection maps them uniformly onto the r_c-subsets of B_c, so the prescribed subset is attained with probability 1/binomial(m_c,r_c). The unknown bijections are independent between classes. A concrete decoder selects any fixed r_c-subset of A_c in each class and attains the bound. Random mixtures cannot exceed a deterministic optimum.

Consequences:

    uniform singleton goals: J_single = c/n,
    uniform all 2^n binary goals: J_pattern = product_c(m_c+1)/2^n,
    all-zero or all-one goal: success = 1,

where c is the number of nonempty signature classes. The full-pattern average follows because binomial(m_c,r) equally weighted goals cancel the reciprocal success for each r=0,...,m_c. Perfect all-on control can therefore coexist with poor individual localization.

## 5. Calibration budgets and an explicit four-port witness

Unrestricted parallel binary calibration gives at most 2^k signatures. Thus

    max J_single(k)=min(2^k,n)/n;
    minimum rounds for full wiring identification=ceil(log2 n).

Assigning distinct binary codewords to ports attains the bounds. Adaptivity cannot evade the same terminal signature count. This is an established permutation-identification coding principle, not new mathematics.

For the uniform full-pattern battery, the best class sizes are balanced. Let c=min(2^k,n), q=floor(n/c), r=n-cq. Then

    max J_pattern(k)=(q+2)^r (q+1)^(c-r)/2^n.

Proof: moving one member from a class of size a to one of size b, with a>=b+2, increases (a+1)(b+1) by a-b-1. Splitting a nontrivial class also increases the product, so use as many classes as allowed and balance them.

For n=4:

| Probes in command-port order | Remaining wirings | Best singleton success | All-on success |
|---|---:|---:|---:|
| none | 24 | 1/4 | 1 |
| 1111 then 1111 | 24 | 1/4 | 1 |
| 0011 then 0011 | 4 | 1/2 | 1 |
| 0011 then 0101 | 1 | 1 | 1 |

The last two schedules have the same two-round budget and four activated command occurrences, but different distinctiveness. This does not assert equality of every physical resource. With at most ONE activated port per round, at most k ports obtain nonzero signatures; at least n-k are indistinguishable. Exact recovery therefore needs n-1 rounds and is attained by testing n-1 distinct ports, using bijectivity to infer the last. The logarithmic parallel bound cannot be imported into constrained biological movements without checking admissibility.

## 6. AC3: exact task-relative retained-state requirement

Fix a goal family G. The encoder m(pi) may assume the wiring has first been learned, but it must leave enough information for a fixed decoder d(m,g) to issue the correct inverse action for every pi and g, without further pi-dependent information. Define

    pi ~_G pi' iff P_pi^-1 g = P_pi'^-1 g for all g in G.

Let b_1,...,b_s be the sizes of the effect-port classes having identical task-incidence signatures (g_j) over all g in G. Then

    M_min(G)=n! / product_l b_l!.

Proof: two wirings encoded to the same decoder state must require the same action for every admitted goal; otherwise one fixed answer fails. Conversely their equivalence class is a sufficient message. Effect-port permutations preserving every goal act only within the identical-incidence classes, giving a stabilizer of size product b_l!. Each wiring equivalence class has this size, and division of n! yields the exact count. This is factorization plus finite symmetry counting, not a new foundational inference rule.

Examples:
- all-on/all-off alone: M_min=1;
- one fixed singleton goal: M_min=n;
- any of n singleton goals: M_min=n!;
- r predeclared singleton goals: M_min=n!/(n-r)!;
- one prescribed r-element effect pattern: M_min=binomial(n,r).

For n=4, the first three need 1,4,24 distinguishable wiring-dependent decoder states; 24 requires at least five fixed-length binary bits. Calibration rounds are not memory bits: each round observes n channels. The theorem counts wiring information, not every possible total system state or consciousness amount. It allows distributed, compiled or weight-encoded use and does not require a linguistic 'I' representation.

## 7. Covariance, fixed-J and experience limits

Rename command labels by alpha and effects by beta. Transport pi'=beta*pi*alpha^-1, commands by P_alpha and goals/observations by P_beta. Then

    P_pi' P_alpha u = P_beta P_pi u.

The signature and task-equivalence results are invariant under consistent relabeling. Physically rewiring the plant while keeping the learned decoder fixed is a different operation.

UCT application needs independently admitted actual tokens, common complete K/time/boundaries, grounded ports and occurrences, installed observation/calibration/use, and agreement between the finite model and the relevant actual law. Only a genuine difference of the SAME actual capability profile J licenses inherited C:P1 under C1. Comparing different k budgets changes J. A poor executed calibration schedule does not imply inferior maximum capability if both systems can optimize freely. One candidate fixed-budget comparison instead fixes two different installed two-round calibration circuits and the same permitted downstream decoder class, tasks and time.

None of the mathematical observations identifies familiar mineness, pain, fear, anatomical ownership or a unique subject. A tool or another device can be controlled through the same mathematics. This preserves the original R147 limit rather than defeating it. Under U1/P3, independently persisting local processes retain nonempty experience when downstream identification or access fails. Detailed local type need not remain unchanged. Calibration, report and control are not basal-experience gates.

## 8. Failure controls, tests and novelty

A nonuniform n=2 prior placing 90% on identity permits 90% uncalibrated success, outside the uniform formula. Rewiring after calibration can defeat a stale decoder. Extra feedback, an excluded wiring-dependent device state or outside storage changes the one-shot/memory contract. Noisy, nonlinear, many-to-one or changing connections are outside these exact theorems.

The expanded standard-library verifier was actually executed: 367 probe matrices, 3,099 posterior histories, 46,948 brute-force goal/command optimization checks, 289 task-family state-count checks and 1,728 recoding equalities. Adaptive two-round cases n=2,3 and explicit failure controls passed. Arithmetic is integer/Fraction. The compact independent core checker in this directory corroborates key examples; it does not purport to reproduce every expanded count. No actual human, animal or language-model experiment was performed.

Bongard et al. (2006) and Hu et al. (2025) already study robotic self-modeling. Chen et al. (June 2026) study proprioceptive–visual self-other distinction without identity labels and use the learned geometry for control. Their operational selfhood is not phenomenal selfhood. Their inspected abstract/methods do not establish an exactly synchronized-indistinguishable-distractor guarantee; our warning is about extending the scope, not alleging their experiments are wrong. Prior permutation-recovery work supplies the binary signature principle.

The narrower project contribution is the connected calibration-ambiguity, goal-specific success and retained-state analysis, grounded in UCT's original fixed-J and local-persistence constraints. The exact package's historical priority is UNVERIFIED. It is future paper material, not an independently established consciousness breakthrough.

## 9. Map, provenance and honest completion boundary

Candidate map: 26 typed claims, 11 conditional AND rules and 8 non-deductive links. It adds no old-node conclusion and does not reactivate suspended rules. All 1,278 frozen old items were mechanically inventoried; the inspection union has 748 nodes and 354 active conditional routes, with no duplicate IDs, unresolved deductive premise IDs or new cycles. This inspection union is NOT the completed map.

Relevant old semantic anchors were reread. A fresh full all-item semantic review of every old statement and source has NOT been completed. Therefore AC remains a disabled pending module, the existing completed UCT-MAP-v1.0.0 is preserved, and no v1.0.1 map release is claimed. Actual and named-phenomenal bridges remain OPEN. R185 was inspected but not enabled or used as an established premise.

The downloadable expanded package UCT_Action_Calibration_20261009 includes the longer English note, all verifier code/results, exact frozen baseline evidence, per-ID mechanical scan and candidate review. This repository checkpoint is a self-contained compact presentation, not a byte-identical copy of that archive. Saving it does not certify truth, originality, whole-map integration or publication. No DOI/OTS/AR, scheduler or published-paper mutation is authorized.

## 10. Primary sources and read scope

1. Bongard J, Zykov V, Lipson H. Resilient machines through continuous self-modeling. Science 314 (2006), 1118–1121. DOI 10.1126/science.1133687. Primary abstract/metadata read.
2. Hu Y, Chen B, Lipson H. Egocentric visual self-modeling for autonomous robot dynamics prediction and adaptation. npj Robotics 3 (2025), 14. DOI 10.1038/s44182-025-00031-6. Publisher abstract read; subsequent full retrieval failed.
3. Chen Y, Gao T, Ge Y, Ban S, Wang Y, Xiong H, Zeng W, Zhu W. Proprioceptive–visual correspondence enables self-other distinction in humanoid robots. arXiv:2606.13222v1 (11 June 2026). Primary HTML abstract, methods and discussion read; no data rerun. https://arxiv.org/html/2606.13222v1
4. Li C, Lo K-T. Optimal quantitative cryptanalysis of permutation-only multimedia ciphers against plaintext attacks. Signal Processing 91 (2011), 949–954. DOI 10.1016/j.sigpro.2010.09.014; arXiv:0912.1918. Primary abstract/publisher summary read.
5. Jolfaei A, Wu X, Muthukkumarasamy V. On the security of permutation-only image encryption schemes. IEEE TIFS 11 (2016), 235–246. DOI 10.1109/TIFS.2015.2489178. Institutional primary record read, not a full theorem-level comparison.
6. Liu H. UCT I v1.2, UCT III v1.0, UCT-MAP-v1.0.0 and MGTD v1.0.1. Frozen recovery archive SHA256 063eea5a817f1868004f5bfe51e4bbf4f741dac32a6427fa75fb61eb0df636bb. Relevant prior nodes are cited above and in MAP_EXTENSION.json. Original UCT theory and code identities are not reauthored as new results here.
