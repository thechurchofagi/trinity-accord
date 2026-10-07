# When Intervention Transport Does Not Identify Organization
## A constructive limit for comparisons of artificial agents

**Hongju Liu**  
Independent researcher, Shenzhen, China  
**Working draft v0.2 - 7 October 2026 - Unpublished**

### Abstract

An artificial agent may preserve a computation across implementations without preserving every organizational distinction of its realizers. This familiar observation leaves an operational question: does agreement under extensive internal intervention resolve the ambiguity? We separate intervention transport from identification and give an exact finite construction. For every positive integer n, a family of \(2^n\) deterministic implementations has the same state-space size, the same input and output alphabets, full reachability, and mutually dependent register updates. Every implementation realizes the same logical accumulator. All adaptive protocols combining ordinary inputs with interventions that descend through the logical projection have identical output laws. This includes arbitrary individual register-bit flips, despite each flip changing the logical output. Nevertheless, the implementations are pairwise nonisomorphic under fixed labeled ports. A single local reset after one update identifies the implementation parameter. For general affine probes, the number of remaining candidates is determined exactly by a binary matrix rank. Complete two-tick endpoint dynamics also coincide, exposing an additional temporal limitation. The mathematics uses established quotient and identification principles; the contribution is a concrete stress test and its application to organizational-invariance arguments. Under Unified Consciousness Theory, experiential conclusions remain conditional on actual-token and constitutive-grounding premises. Neither a consciousness detector nor a refutation of computational functionalism is obtained.

**Keywords:** artificial agents; consciousness; causal abstraction; intervention; identifiability; organization

## 1. From ancestral formation to implemented intelligence

Imagine that the intermediate organisms in a lineage leading to humans remain available for comparison. Any organization proposed as the first condition for experience must itself be examined through its formation history. The All-Ancestors-Survive thought experiment motivates an explanation of organizational change rather than an unexplained jump from matter to experience. Yet physical graduality alone does not prove continuity of a binary experience-existence predicate. UCT I already separates these claims and gives a smooth-onset countermodel [1, §8]. We retain the thought experiment as motivation, not as an independent proof of UCT's identity axiom.

An artificial implementation presents a complementary challenge. An abacus participates in calculation with its operator; an electronic calculator installs more of that procedure internally. In the human-formation scenario inspired by *The Three-Body Problem*, participants follow local rules while their collective operation implements a much more capable agent. Assume that the implementation responds correctly across the specified counterfactual inputs, rather than merely replaying a successful trace. Which organizational properties have thereby been established?

The participants can remain actual processes while contributing to an encompassing process. Under UCT, their experiential attribution need not disappear, and the whole need not be an arithmetic sum of their experiences. But the existence of that conditional account is not yet a demonstration that the whole has the same complete organization as an electronic implementation. The prior synthesis draft made this distinction conceptually. The present revision supplies an exact test of one route by which the missing correspondence might be claimed.

The route is interventional: vary inputs, perturb internal components, and verify that the resulting transitions and outputs commute with a logical description. Such evidence is stronger than one successful performance. We ask whether even an extensive, exactly transported intervention family identifies the implementation's complete organization. The answer is negative in a controlled family where the difference is not obtained by adding idle components or unequal numbers of states.

This is a question about the inferential force of a comparison protocol. It does not add an integration, recurrence, reporting, or self-awareness requirement for experience. Nor does the small witness purport to model a human brain or a superintelligent agent. Its role is to test a purportedly general inference about implemented organization.

## 2. Transport and identification ask different questions

Let a deterministic implementation have state space S, update maps \(T_u\), and a surjective logical-state map

\[
\pi:S\longrightarrow Z.
\]

The observer reads Z. Updates realize logical maps \(F_u\) when

\[
\pi T_u=F_u\pi. \tag{1}
\]

An intervention \(J:S\to S\) **descends through** \(\pi\) when some logical operation j satisfies

\[
\pi J=j\pi. \tag{2}
\]

Equation (2) holds exactly when \(\pi\) J is constant on every fiber of \(\pi\). This is the standard quotient condition, already used in the UCT formal map [2]. Transport says that an intervention has a well-defined logical counterpart. Identification instead asks whether responses distinguish the candidate physical models or their states. Neither definition makes transport an identification guarantee.

Consider a family of implementations with common logical maps \(F_u\) and, for each admitted intervention label a, the same descended map \(j_a\). Policies may choose the next update or intervention from the entire observed logical history and private randomness whose law is independent of the implementation. They may not inspect hidden states, receive the model label through a side channel, or observe undeclared timing or energetic costs. Operations have the same declared timing. Equal initial logical states then produce identical observed-history laws under every such policy.

The proof is induction: equal observed histories give the same conditional distribution of the next action; the shared logical operation gives the same next logical state. For randomized policies, couple the private randomness or condition on it and average. This is an established consequence of exact abstraction, not a newly discovered control theorem. It explains why adding more interventions of the same quotient-preserving kind can leave the observational equivalence unchanged.

The claim is deliberately scoped. Not every pair of models with a common quotient is indistinguishable under every physical experiment. Expanded readouts, interventions that do not descend, or model-dependent costs can distinguish them. The next construction makes the distinction exact rather than merely listing those possibilities.

## 3. A family with active components and hidden implementation differences

All arithmetic in this section is over the binary vector space \(G=\mathbb F_2^n\), with \(n\ge1\). Addition is componentwise XOR. There are two named n-bit registers x and y, an n-bit input u, and an n-bit logical output z. For each fixed mechanism parameter k in G, define

\[
S=G\times G,\qquad s_0=(0,0),\qquad
\pi(x,y)=x+y, \tag{3}
\]

\[
T^k_u(x,y)=(y+k,\;x+u+k). \tag{4}
\]

The parameter k is fixed across an experiment; it is not a new input or an unobserved independent random draw at each tick. Both registers are part of the stipulated implementation. State size, input size, output size, update timing, and named ports are common to the family.

Each register's next value depends on the other register. Every register bit affects the logical output: flipping \(x_i\) or \(y_i\) flips \(z_i\). For n=1, the two elementary registers form a directed feedback cycle. For n>1, the construction consists of n such interacting pairs. It is not claimed that all 2n bits form a single strongly connected component or that the whole is automatically one actual experiential bearer.

Let an admitted intervention family contain any selected maps \(J:S\to S\) that descend through \(\pi\), with the same physical map and logical counterpart in all implementations. It can include every such map, since the state space is finite. In particular it contains all independent translations

\[
J_{a,b}(x,y)=(x+a,y+b),\qquad
j_{a,b}(z)=z+a+b. \tag{5}
\]

Thus every individual register-bit flip, and every combination of them, is available. These are genuine state perturbations with observable consequences, not interventions that do nothing.

### Theorem 1. Transport without implementation identification

For the family (3)-(4), with fixed labeled input and output ports:

1. Every implementation realizes the same logical transition \(z\mapsto z+u\). From any common initial logical state, every adaptive protocol using ordinary updates and the common descending intervention family has the same logical-output law for all k.
2. Every state is reachable from (0,0) in two ordinary updates. All \(T^k_u\) are bijections. Both registers participate in the logical output and cross-register update dependence.
3. Distinct values of k give nonisomorphic input/output-labeled transition structures, even though all members have \(2^{2n}\) states and the same two-register dependency pattern.
4. Starting at (0,0), apply one update with u=0, then the local reset \(R_x(x,y)=(0,y)\), and read \(\pi\). The result is exactly k. This reset does not descend through \(\pi\).
5. Complete two-tick endpoint maps are identical across k: \(T^k_v T^k_u(x,y)=(x+u,y+v)\). Thus full register readout only at the boundaries of uninterrupted two-update blocks also fails to identify k.

### Proof

For the first claim, direct substitution gives

\[
\pi T^k_u(x,y)=(y+k)+(x+u+k)=\pi(x,y)+u. \tag{6}
\]

Descending interventions share their logical maps by assumption. The induction in §2 therefore applies for any finite observed history, not merely a fixed test horizon or a prerecorded input sequence. Ordinary logical trajectories depend on the initial sum, not on which representative of its fiber was selected.

For reachability, two updates from the designated start give

\[
(0,0)\xrightarrow{u}(k,u+k)
\xrightarrow{v}(u,v). \tag{7}
\]

As u and v vary, every state is attained. For fixed u and k, recover a predecessor from (x',y') by x=y'+u+k and y=x'+k; hence each update is bijective. Equation (3) proves individual-bit output sensitivity, and (4) proves cross-register dependence. These statements concern causal relevance in this model, not a universal measure of integration.

For nonisomorphism, examine fixed points of the operation with the *named zero input*. They satisfy

\[
T^k_0(x,y)=(x,y)
\quad\Longleftrightarrow\quad x=y+k.
\]

There are exactly \(2^n\) such points and every one has output k. An isomorphism preserving the zero-input operation and the labeled output must carry this set to fixed points with the same output. In the k' implementation their common output is k'. Therefore an isomorphism requires k=k'. The proof allows arbitrary state bijections; it does not rely solely on preserving the drawn wiring diagram. Arbitrary output relabelings are not part of this comparison. If those are allowed, the comparison must be reconsidered.

There is also a weaker but label-independent pointed distinction. At the designated state (0,0), the k=0 model has an input update that fixes that state; no k≠0 model has any such input update. Existence of a self-loop at the pointed state is preserved even when the input and output alphabets are permuted. Thus at least the zero versus nonzero distinction is not an artifact of fixing names for the binary vectors. The stronger pairwise distinction throughout the family retains its labeled-port scope.

For the reset probe,

\[
(0,0)\xrightarrow{T^k_0}(k,k)
\xrightarrow{R_x}(0,k)
\xrightarrow{\pi}k. \tag{8}
\]

The reset is not a logical operation on z alone. The states (0,0) and (h,h), for nonzero h, have the same z=0 but their post-reset logical outputs are 0 and h. Thus no single j can satisfy (2) for \(R_x\) over the full state space.

Finally, composing (4) twice cancels k and exchanges the registers back, yielding \(T^k_v T^k_u(x,y)=(x+u,y+v)\). The statement concerns the declared two-tick endpoints; it does not survive unrestricted intermediate readout or intervention. This proves all five claims. □

### 3.1 The smallest witness

For n=1 there are two four-state implementations. Both implement the same one-bit accumulator, with all internal single-bit flips admitted.

| Test or invariant | k=0 | k=1 |
|---|---|---|
| Logical ordinary update | z'=z+u | z'=z+u |
| Outputs of zero-input fixed points | 0 | 1 |
| State after one zero-input update from 00 | 00 | 11 |
| Logical output at that point | 0 | 0 |
| Output after then resetting x to zero | 0 | 1 |
| State after two updates u,v from 00 | (u,v) | (u,v) |

No extra inert register has been appended to one member. The construction also does not infer a nonproduct whole from a mere statistical correlation: each next register value depends on the other under the fixed input boundary. For this specified register split the updates do not factor into independent component updates. In an actual application, identifying the corresponding physical whole and its constitutive relations remains a separate task.

## 4. Exactly which affine interventions reveal the difference?

The family permits a complete diagnostic calculation. Write a general affine intervention as

\[
J(x,y)=(Ax+By+a,\;Cx+Dy+b), \tag{9}
\]

where A,B,C,D are n×n binary matrices and a,b are binary vectors. Its **fiber-sensitivity matrix** is

\[
L_J=A+B+C+D. \tag{10}
\]

This label denotes sensitivity to the omitted diagonal direction, not an amount of experience.

### Proposition 2. Affine transport and diagnostic rank

The intervention (9) descends through \(\pi\) if and only if \(L_J=0\). After preparation at (0,0) and one zero-input update, its logical readout is \(L_Jk+a+b\). For independent repetitions of this preparation followed by a fixed probe list \(J_1,\ldots,J_m\), the responses identify k precisely when the vertical stack of \(L_{J_1},\ldots,L_{J_m}\) has rank n. If the stack has rank r, each consistent response has exactly \(2^{n-r}\) candidate parameters.

*Proof.* States in the same fiber differ by (h,h). Their post-intervention logical outputs differ by (A+B+C+D)h. Vanishing for every h is equivalent to \(L_J=0\). After one zero-input update the state is (k,k), so substitution yields \(L_Jk+a+b\). Subtract the known offsets and stack the equations. The solutions of a consistent binary linear system form a coset of its kernel, of dimension n-r and size \(2^{n-r}\). □

Translations have \(A=D=I\) and \(B=C=0\), so \(L_J=0\) even when every individual bit is perturbed. Resetting the entire x register has \(A=B=C=0\) and \(D=I\), giving \(L_J=I\). Resetting only selected x bits yields rank equal to their number. Resetting both registers to fixed constants again has \(L_J=0\). Consequently, “more extensive manipulation” is not a monotone ordering of diagnostic power. What matters is whether the intervention transfers an omitted distinction into the retained readout.

The necessity claim is restricted to the stated fixed list of independent preparation-probe trials. It is not an optimality theorem for arbitrary multistep adaptive experiments. The zero-rank blindness of *all* descending interventions is stronger and follows from Theorem 1. Both results assume exact operations and readout; noisy or partially observed experimental versions require further analysis.

## 5. What the construction changes in an organizational argument

### 5.1 A passed correspondence test can leave a constitutive question open

Equation (6) proves transition commutation exactly. Equation (5) transports every independent bit-flip intervention exactly. Arbitrary history-dependent testing within that interface does not recover k. These are successful certificates, not failed experiments. What they certify is the logical accumulator and the admitted intervention action, rather than uniqueness of its realizer.

For a biological-AI comparison, this distinguishes two objectives. One may wish to establish that an intervention has the same task-level role in both systems. One may also wish to distinguish candidate mechanisms that implement that role. The first objective can be satisfied by interventions incapable of satisfying the second. Restricting attention to operations chosen because they preserve a proposed abstraction cannot, by itself, certify that no relevant organization was lost by that abstraction.

UCT II's source-fidelity requirement also matters here [12]: a comparison must retain the target theory's actual explanatory claim and scope. A restricted interface certificate should not be presented as a reconstruction of every internal relation required by another theory, nor should its failure settle a broader phenomenal claim without the corresponding bridge.

The reset diagnostic illustrates a constructive response. It deliberately fails to descend through the existing logical state. To represent it, one must refine the state or otherwise enlarge the comparison model. Its failure of transport is information about the model's scope, not proof that the physical intervention is invalid. Conversely, a convenient internal manipulation that cannot be implemented in a biological target cannot be assumed available merely because it is well defined in a model.

### 5.2 Three different bearers must remain distinct

UCT's complete-type identity C1 is a claim about actual, valid process tokens and their constitutive organization [1]. It is not a claim that every useful logical quotient is an actual process or a uniquely individuated subject. We distinguish:

| Object of comparison | Established here | Additional requirement for a UCT conclusion |
|---|---|---|
| Logical accumulator | Exact common dynamics and descending intervention action | Independent actual realization and complete macro-organization adequacy |
| Two-register implementation | Pairwise inequivalent labeled transition structures | Faithful constitutive grounding of this distinction in actual tokens |
| Human/electronic realizer of a complex agent | A motivated comparison problem | Actual mechanism, boundary, timing, and intervention correspondence |

If actual implementation tokens preserve the distinguished state, update, and port relations, and complete-organization isomorphisms must preserve that signature, the demonstrated nonisomorphism obstructs complete organizational equivalence. C1-OI then gives a conditional difference of complete experiential type. This step needs actual-token and constitutive-signature premises; it does not follow from a simulation file alone.

Naming an experimental port does not make it constitutive. The bridge must concern the process's actual causal dispositions, not labels imposed to force a distinction. If adding reset hardware changes the process, a further model is needed to relate that modified experiment to the unmodified target. The pointed self-loop distinction in Theorem 1 offers a label-independent zero/nonzero obstruction, but its physical grounding is still required.

There may simultaneously be independently justified actual macroprocesses whose complete organization is the common accumulator. If so, A's macro-invariance result permits equal macro experiential types while the encompassing implementation types differ [1, §6.4]. The present model does not establish those macro tokens automatically. The point is that this possibility is logically compatible with the implementation distinction; it is not a contradiction to be eliminated by selecting one exclusive bearer.

Applied to the human formation, participants, an implemented macroprocess, and the containing physical process need not be identical targets. A claim about the program's organization cannot silently become a claim about every constitutive relation of the entire population. Nor does a difference between the containing physical systems by itself disprove experiential equivalence of independently grounded macroprocesses.

### 5.3 Experience, intelligence, and report

UCT III already establishes that different fixed-contract capabilities imply different complete experiential types under its premises, while equal capability can conceal type differences [3]. The present family supplies a stricter kind of matched capability than equal scores on a finite test: it matches the entire declared closed-loop logical interface, including causally effective internal perturbations. It therefore supplies a concrete witness to the limitation, not a replacement for C's theorem.

No human-like experience, scalar richness, suffering, or fear is assigned to the registers. The fourth source paper's separation of mechanism evidence from valence remains intact [4]. Nor does obtaining the diagnostic output k measure an experiential coordinate. It identifies the stipulated implementation parameter. Its experiential interpretation is an additional conditional step with an explicitly identified bearer.

## 6. Relation to existing work and limits of novelty

Behavioral equivalence and internal organization have long been distinguished. Block's population implementation and Chalmers's organizational-invariance argument supply direct antecedents for the human-formation discussion [5,6]. Our implementations do not share the same fine-grained labeled transition structure. Theorem 1 therefore does not refute an invariance principle whose premise already requires that structure to be preserved.

The unfolding argument challenges causal-structure theories using functionally matched alternatives [7]. Our construction instead compares recurrent implementations with the same state cardinality and dependency pattern. No inference of absence of experience from feedforward structure is used. We do not adopt a general conclusion that every structure-based theory is unfalsifiable; the explicit reset distinguishes the present alternatives under an enlarged physical interface.

Kanai and Ma's 2026 preprint explicitly strengthens boundary equivalence with internal intervention/readout structure [8]. Our construction is a stress test for choosing such a family, not a counterexample to a criterion that already includes the separating operations. Their mechanism-enriched invariance claim remains conditional; so does the UCT interpretation here.

Exact causal transformations and intervention-sensitive identification also have direct mathematical precedents [9,10]. Li et al.'s result concerns paired counterfactual data for latent causal models, with smooth invertible observation and additional distributional assumptions. Our finite readout is deliberately many-to-one, and the permitted bit flips are not their independently resampled perfect interventions. The construction does not contradict their identification theorem. The quotient induction and affine rank argument are standard. Binary sharing of a value across multiple registers is familiar from private-circuit research [11]; no novelty is claimed for XOR encoding or information hiding. The present parameter is fixed, the readout observes the combined value, and the task is implementation identification, not cryptographic secrecy.

The proposed contribution is the conjunction of constraints in one transparent witness and the resulting distinction between transported and identifying interventions: equal state size, full reachability, active register components, identical logical feedback laws under all descending interventions, structural nonisomorphism, and an exact separating reset. Relative to the author's publications, A's earlier three-register example buffered a common readout from different internal dynamics, whereas the present two-register readout directly depends on both active registers and admits individual perturbations. The targeted literature review has not established historical priority for the exact family. A standalone short methodological paper would have to be judged on this focused contribution, not on a claim of a new general consciousness theorem.

The limitations are material. Timing is fixed; arbitrary port relabeling is excluded; controls and outputs are noiseless; actual support is not inferred from a finite model. The vector extension is a family of interacting register pairs, not proof of an indivisible large subject. A physical realization may contain further distinctions not represented here. These restrictions define the result rather than supplying post-hoc exceptions.

## 7. Conclusion

Agreement under extensive intervention does not identify organization merely because the interventions are internal, causally effective, or exactly transportable. A logical projection can preserve every admitted feedback law while concealing differences among fully reachable implementations of equal size. The constructed family makes this limitation explicit and gives an intervention that resolves it.

For artificial-agent consciousness arguments, the practical question is therefore not only whether a proposed correspondence commutes. It is also which differences its admitted interventions can expose, at which temporal resolution, and for which actual bearer. Preserving a computation, identifying its implementation, and interpreting its experience are connected tasks with different premises. The ancestral and human-formation thought experiments remain useful because they force those premises into view; the formal witness shows why the distinction has consequences even in an exactly specified mechanism.

## Appendix A. Proof and verification record

The general proofs are in §§2-4. The accompanying script checks the finite identities independently by enumeration, rather than treating a finite sweep as the proof for all n. It checks every state, parameter, and input for n=1,2,3; two-tick composition; reachability; fixed-point output invariants; and the reset diagnostic. For n=1 it enumerates all 256 state maps, verifies the descending subset, and compares the complete reachable paired-state product under all of those maps and the ordinary updates. This establishes finite-machine equivalence without a bounded trace cutoff. It also enumerates every affine intervention for n=1,2 and compares its algebraic descending criterion with direct fiber constancy. A separate two-coordinate probe example checks the rank/count assertion.

The unified formal map records this extension as R145. The general transport observation is linked to the prior quotient and feedback results; Theorem 1 and Proposition 2 are project-level constructive extensions, with historical originality left unverified. Conditional actual-token interpretation is stored separately from the finite mathematics. Original A/B/C/D source files remain unchanged.

## References

1. Liu, H. (2026). *Structural-Experiential Identity and the Continuity from Physical Process to Conceptual Self*. UCT I, v1.2. [doi:10.5281/zenodo.23131575](https://doi.org/10.5281/zenodo.23131575).
2. Liu, H. (2026). *Organization, Capability, and Experience: A Formal Companion to Four Papers*. R140 v0.2; with the R126 quotient and R137 feedback-interface records. [Companion](../R140_Formal_Companion_20261007/Organization_Capability_Experience_v0_2.md).
3. Liu, H. (2026). *Organization, Intelligence, and Experience: From Inorganic Processes to Artificial Agents*. UCT III, v1.0. [doi:10.5281/zenodo.23137088](https://doi.org/10.5281/zenodo.23137088).
4. Liu, H. (2026). *From Shutdown Resistance to Self-Continuation Control: Identifiability, Intervention Stability, and Evidence Standards for Artificial Agents*. TA-TR-2026-24, v1.0. [doi:10.5281/zenodo.23176685](https://doi.org/10.5281/zenodo.23176685).
5. Block, N. (1978). Troubles with functionalism. *Minnesota Studies in the Philosophy of Science*, 9, 261-325. [Primary-text excerpt](https://rintintin.colorado.edu/~vancecd/phil201/Block.pdf).
6. Chalmers, D. J. (1995). Absent qualia, fading qualia, dancing qualia. In T. Metzinger (Ed.), *Conscious Experience*. Imprint Academic. [Author text](https://www.consc.net/papers/qualia.html).
7. Doerig, A., Schurger, A., Hess, K., & Herzog, M. H. (2019). The unfolding argument: Why IIT and other causal structure theories cannot explain consciousness. *Consciousness and Cognition*, 72, 49-59. [doi:10.1016/j.concog.2019.04.002](https://doi.org/10.1016/j.concog.2019.04.002).
8. Kanai, R., & Ma, S. (2026). *Intrinsic Computational Functionalism and Simulated Consciousness*. arXiv:2606.15348v1. [Primary text](https://arxiv.org/html/2606.15348v1).
9. Rubenstein, P. K., et al. (2017). *Causal Consistency of Structural Equation Models*. arXiv:1707.00819. [Primary record](https://arxiv.org/abs/1707.00819).
10. Li, X., Kaba, S.-O., & Ravanbakhsh, S. (2025). On the identifiability of causal abstractions. *Proceedings of AISTATS*, PMLR 258, 3241-3249. [Primary record](https://proceedings.mlr.press/v258/li25g.html).
11. Ishai, Y., Sahai, A., & Wagner, D. (2003). Private circuits: Securing hardware against probing attacks. *CRYPTO 2003*, LNCS 2729, 463-481. [Primary text](https://iacr.org/archive/crypto2003/27290462/27290462.pdf).
12. Liu, H. (2026). *Consciousness Theories as Effective Organization Theories*. UCT II, v1.1. [doi:10.5281/zenodo.23030320](https://doi.org/10.5281/zenodo.23030320).

**Literary inspiration:** Cixin Liu, *The Three-Body Problem*, translated by Ken Liu, Tor Books, 2014. Running the stipulated intelligent agent is an extension of the human-formation scenario.

**Draft and assistance statement:** This unpublished revision refocuses the R144 synthesis on a constructive methodological result. AI assistance was used for derivation, source comparison, drafting, exact checking, and typesetting. These activities do not constitute independent peer review or final author approval. No physical experiment or measurement of experience is reported.
