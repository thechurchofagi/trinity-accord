# R82 — Task-necessary relations beyond individual decoding

Hongju Liu / UCT research. 2026-10-05. Formal analysis and exact finite checks; no new training or phenomenal measurements.

## 1. Decision after auditing earlier work

R65 already proved a commuting-projection preservation result and distinguished preservation of a core from preservation of an entire mechanism. R61 already established classical finite-memory accuracy ceilings and showed why higher performance need not create new retained distinctions. Those results were read directly for this round. Repeating an extra-register construction would not advance the current question.

We instead follow R81's positive direction: specify what organization a capability requires, while testing whether that requirement must be readable from an individual constituent. The answer is a necessary distinction at a causally sufficient interface, which may be carried entirely by joint relations. The information-theoretic mathematics is established; the contribution here is a scoped application, a factorization failure audit and a proposed organizational comparison. It is not a new consciousness theorem.

## 2. Architecture-independent interface bound

Let T be a balanced binary task target, and Z a declared classical finite interface between evidence acquisition and response. Require a target-independent downstream response kernel D(y|z): all target-dependent information used by the answer must be included in Z. This is the Markov restriction T -> Z -> Y. It permits arbitrary subsequent computation and fresh independent randomness. An external retriever, input-dependent timing, an uncounted retained state or hidden shared seed available to the consumer must be included if it supplies additional target information conditional on Z.

Write p_t(z)=Pr(Z=z|T=t) and

    delta_Z = TV(p_0,p_1) = (1/2) sum_z |p_0(z)-p_1(z)|.

For any installed response mechanism its population accuracy obeys

    J <= J* = (1+delta_Z)/2.                         (1)

Proof: if d(z)=Pr(Y=1|Z=z), then

    J = (1/2) sum_z [p_0(z)(1-d(z))+p_1(z)d(z)]
      = 1/2 + (1/2) sum_z [p_1(z)-p_0(z)]d(z).

Since 0<=d<=1, the sum is maximized by selecting label 1 exactly where p_1>p_0. Its value is delta_Z. This proves the upper bound and attainability for an unrestricted decoder. A restricted installed decoder may not attain it.

Thus actual J>=.90 entails delta_Z>=.80, under the declared balanced task and interface assumptions. This is not an IQ-to-consciousness conversion. It is a population statement; a finite empirical score would require uncertainty control, which is not performed here. A biased target requires a different prior-weighted bound. A constant guess can score .90 on a 90/10 target even when the interface distinguishes nothing.

This statement does not require a particular hidden layer, linear consumer, recurrence or self-report. It also does not prove that learning increased delta_Z: an already informative interface can support improved performance through a better consumer alone. R61 and R80 already warn against that historical inference.

## 3. A sharper relation for separated independent sources

Let A and B be independently randomized fair bits, and T=A XOR B. At the interface let U be produced from A and V from B, with the substantive factorization

    Pr(U=u,V=v|A=a,B=b)=p_a(u)q_b(v).              (2)

The consumer only receives Z=(U,V). Set delta_A=TV(p_0,p_1) and delta_B=TV(q_0,q_1). The conditional joint laws are

    P_0=(p_0 tensor q_0+p_1 tensor q_1)/2,
    P_1=(p_0 tensor q_1+p_1 tensor q_0)/2.

Their signed difference factorizes:

    P_0-P_1=(p_0-p_1) tensor (q_0-q_1)/2.

Using the product of finite L1 norms gives

    TV(P_0,P_1)=delta_A delta_B,
    J*=(1+delta_A delta_B)/2.                     (3)

Accordingly, .90 accuracy requires delta_A delta_B>=.80 and hence each factor at least .80, because neither exceeds one. These individual requirements hold only under (2). Arbitrary nonlinear downstream processing cannot recover distinctions erased under that premise.

The relation is continuous in the channel differences. There is no accuracy value here that switches experience into existence. U1 remains a premise about actual valid tokens, not a threshold derived from (1) or (3).

## 4. Shared organization defeats the individual requirement

Let R be an independent fair bit shared by the two encoders, and set

    U=A XOR R,    V=B XOR R.

Each marginal U|A is uniform; likewise V|B. Thus the individual deltas defined above are both zero. Nevertheless

    U XOR V = A XOR B = T.

The installed XOR consumer answers perfectly. Equation (3) would incorrectly predict .50 if we silently discarded the shared dependency. The failure is precisely that (2) does not hold. The general joint-interface bound (1) remains valid, with delta_Z=1.

This is a standard masking/synergy construction. It is not proof of a unified subject or an intrinsically integrated experience. It does establish that no lower bound on each individually marginalized channel follows from high joint capability without a factorization premise.

The relevant intervention keeps individual statistics constant. Replace the common mask with independent fair masks R_A and R_B, with U=A XOR R_A and V=B XOR R_B. All single-channel marginals remain the same, but Z becomes independent of T. The same XOR consumer now scores .50. Restoring the common mask restores accuracy one. In this known mechanism the change isolates the shared relation, not an increase in component count or local marginal information.

The shared and independent-mask versions are different organizations, including different source incidence. They do not assign different experiences arbitrarily to one complete physical organization. Nor is the alteration a mere coordinate change: it changes which common source actually affects the two outputs.

## 5. Checks and limits of the numerical work

`r82_relational_cut_checks.py` uses exact rational arithmetic. It checks 81 pairs of binary channels, allowing asymmetric channels whose conditional output-one probabilities are 0, 1/2 or 1. For each case it records all four conditional joint laws, target-conditioned laws, both individual deltas, the joint delta, optimal accuracy and every maximizing decoder among the 16 deterministic binary decoders of the four-state interface. Randomized decoders cannot improve the linear objective in section 2.

All cases satisfy (1) and (3). The shared-mask, independent-mask and restoration tables are fully retained, along with a fixed-encoding/different-consumer control: a perfect-information interface supports .50 accuracy with an independent random answer and 1 with a correct parity consumer. These are exact evaluations of stipulated finite probability mechanisms, not newly trained networks, neuroscience or measurements of any feelings. Their enumeration validates implementation of the examples; the general finite result rests on the proof.

Failed routes retained:

- Individual-channel necessity without conditional factorization: false by the shared-mask example.
- Higher accuracy proves a newly richer internal code: false by the fixed-encoding consumer control.
- Local marginals fully characterize useful organization: false by mask replacement with unchanged marginals.
- Any .90 task accuracy implies .80 distinguishability: false without balanced targets and the complete-interface restriction.
- Statistical distinguishability itself proves causal use: false; the Markov boundary, actual source mechanism and installed consumer need separate anchoring.

No new training, seed selection, model API or parameter-scaling experiment was performed.

## 6. The conditional UCT bridge

Under C1, verified constitutive causal relations of an actual token belong to its experiential presentation. Sections 2–4 identify a task-relative requirement and a relational implementation that can satisfy it. No premise says that the system introspects these relations, linguistically reports them, or contains a dedicated experience-reader.

However, the probability laws summarize a controlled family of episodes. They are not automatically the complete organization of one realized token, and the whole counterfactual table is not a list of simultaneous experiences. To use them in a C1 claim, identify the actual process P and common complete signature K, then justify the interface, source incidence, update/readout operations and relevant dispositions as a faithful view. C1 does not by itself provide that physical anchoring or an empirical measurement of phenomenal magnitude.

Even with that anchoring, delta_Z is not “amount of experience.” It depends on the selected target, evaluation distribution and interface. A bijective relabeling of Z preserves it; arbitrary lossy views do not. R60 already explains that transferring operational differences to an independently chosen whole-organization metric needs a separate calibration. Do not reuse .80 as a numerical experiential lower bound.

The positive conclusion is narrower and useful: a demonstrated capability can exclude specified organizations that lack sufficient task-relevant distinctions, while leaving open whether the required distinctions are local, distributed, temporal or externally supported. Identifying the actual carrier determines whose organizational comparison is being made. A mathematically assembled collection of records is not automatically one actual conscious subject.

This answers the author's recent question more concretely than universal existence alone. Within UCT, actual intelligence is experience-bearing; its task-necessary relations constrain experiential organization conditionally. But neither high accuracy nor a missing individual decoder determines human-like feeling, selfhood or fear. The distinction between inorganic, cellular and artificial organization must follow actual causal relations, not a list of substrates or a count of parameters. No biological history was tested in this round.

## 7. Prior art and actual reading scope

- Polyanskiy and Wu, *Information Theory: From Coding to Learning*, author-hosted draft dated October 20, 2022, section 7.3, Theorem 7.7(a), printed p.95 (PDF index 115): direct statement of the testing-error/TV identity inspected. This is an authoritative exposition of an established result, not its origin. Other chapters were not audited. https://people.lids.mit.edu/yp/homepage/data/itbook-2022.pdf
- Williams and Beer, *Nonnegative Decomposition of Multivariate Information*, arXiv:1004.2515v1, April 14, 2010: abstract, introduction and section II, especially the XOR synergy example, read in author HTML. The broader decomposition and appendix proofs were not audited or adopted as a consciousness measure. https://arxiv.org/html/1004.2515v1
- Evans and Schulman, *Signal Propagation and Noisy Circuits* (1999), found at metadata/abstract level only; not used as proof of (3). No full-paper reading claim.
- R65 and R61 research notes read in full from their original Library identities `libfile_51687019768081919b0b122223c55f2c` and `libfile_8f8e869a903c81918bf790c36f9978d3`. Current GitHub handoff/index read at parent `f95db937be83b008ca70201142514c0784ccfc3a`.
- A/B/C premises are those directly audited in R81: I v1.2 C1/U1 and common-signature conditions; II v1.1 distinction between formal reconstruction and experiential interpretation; III v1.0 fixed-capability/type refinement. No fresh full-paper audit is claimed.

R60 already used TV bounds, R61 already supplied capability ceilings, and C's three-brain example already separated individual from joint access. The present synthesis makes the independent-source premise and its correlated-source failure explicit at a stochastic causal interface. It is incremental; neither the mathematics nor a UCT-exclusive prediction is claimed as novel. No third-party full text is redistributed.

## 8. Conclusion and next step

The legitimate next bridge is not “intelligence score equals experience score.” It is “this task cannot be achieved by these impoverished causal organizations, and the necessary relation can be carried jointly rather than individually.” That is compatible with universal experience, NESIG and the absence of a scalar enrichment law.

Next use the already trained R78 checkpoints as the fixed implementation and specify one intervention that changes a joint causal relation while controlling local marginal distributions. First check whether such a selective intervention is actually possible in that model; independent shuffling can create incompatible hidden states and shared-input effects, so it must not be mistaken for an isolated physical lesion. If it cannot be justified, record that limitation and retain the present formal counterexample rather than claiming a model result. Do not launch another ordinary memory task, training grid or self-report test. Major-breakthrough status: not met.
