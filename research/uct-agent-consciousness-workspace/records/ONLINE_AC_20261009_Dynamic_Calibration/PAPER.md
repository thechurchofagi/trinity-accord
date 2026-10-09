# Correct Control without Complete Recalibration
## Exact bounds and a two-probe five-port controller under transposition drift

**Hongju Liu**  
Independent researcher, Shenzhen, China  
Research working paper | 9 October 2026  
**ONLINE-AC-PAPER-v0.1.0**, based on **ONLINE-AC-RESULT-v0.2.0**  
Prepared with AI-assisted derivation, exact computation, source comparison, and independent protocol review. This manuscript is complete as a scoped working paper. It has not been assigned a new DOI or submitted as a peer-reviewed article. Integration into the project's full scientific map remains pending.

## Abstract

A controller that repairs its current action need not retain enough information to repair the next action after another change. Conversely, sustainable correct action need not require complete reidentification at every deadline. We make both statements exact in a finite model of changing command-to-effect wiring. Before each round, a permutation may undergo one unknown transposition; during the round it is fixed. Binary-vector calibration probes physically act on the same plant, return their complete effect vectors, and are followed by one terminal vector. Success requires the net effect of all these actions to equal the same prescribed unit toggle at every round deadline. For at least three ports, one-probe adaptation after every allowed change requires an injective representation of the admitted old wirings. Consequently, even a completely known initial wiring and unlimited retention of full action feedback do not permit guaranteed success for two rounds with one probe per round. For three ports and independent uniform identity-or-transposition drift, the exact optimal probability of meeting both deadlines is 7/8. Our positive result is a two-probe controller for five ports that maintains correct action at every finite horizon while sometimes leaving two current wirings indistinguishable. Two explicit canonical decision tables preserve a closed family of singleton beliefs and non-goal-transposition pairs. Relabeling transports those tables to the whole family, giving an inductive proof. Two probes are optimal for sustainable control, whereas complete wiring identification under the same initial knowledge and drift law requires three. Independent finite checks verify the physical actions, exact observation cells, and closure. The contribution is this specified resource separation and reproducible benchmark, rather than a new general principle of adaptive control or an empirical claim about experience.

**Keywords:** active calibration; changing permutations; partial observation; goal-directed control; identification; exact finite verification; task-relative sufficiency.

## 1. A precise question about maintaining capability

Knowing how to perform one present action is a different resource from knowing how to update that ability after a change. A known command-to-effect permutation makes a single target action easy: retain the command that reaches the target. If an unknown exchange can move that target to any other effect port, information about previously irrelevant ports can become necessary. The issue becomes sharper when calibration itself acts on the system and must be included in a deadline's success condition.

The question studied here is: **how much calibration is necessary to keep performing one fixed action when the wiring changes repeatedly, and must the controller identify the complete current wiring to do so?** We impose one observation and action contract throughout the main comparison. In particular, a probe is an actual physical toggle, the terminal action returns complete feedback, and a failure at an earlier deadline cannot be repaired retrospectively by later success.

The answer has a negative and a positive part. One probe is sufficient when the complete old wiring is known, but this use need not preserve that knowledge. With at least three ports, a second deadline cannot always be met with the same budget. Nevertheless, for five ports, two probes per round sustain the selected goal indefinitely without always identifying the complete wiring. The positive construction preserves precisely a small allowed form of uncertainty, rather than merely relying on a bounded successful simulation.

The purpose of this paper is to preserve a precise unit of knowledge that future researchers and AI systems can check, cite, and reuse. It follows an audit of the project's already disclosed claims. The general need for a state abstraction to respect transitions is inherited: UCT III, section 6.4, Proposition 6, already discusses the closure of capability quotients through strong lumpability [1]. Static task-specific calibration and binary-signature identification are also project predecessors [2]. Route information and an actually installed reader are distinguished in the published RT/TH paper [3]. None of those broad distinctions is asserted here as new.

The net contribution is the exact evolving-wiring contract, its old-information requirement and two-round value, and especially the closed five-port partial-identification controller. These results belong to one problem with shared quantifiers. Their validity does not assume the truth of UCT. Their use in that research program is to clarify the information and actual action relations required by a functional capability before any further interpretation is attempted.

## 2. Action, observation, drift, and deadlines

Let the command and effect ports each be labeled by $\{0,\ldots,n-1\}$. A wiring $\pi\in S_n$ maps command port $i$ to effect port $\pi(i)$. For a binary vector $u$, write $P_\pi u$ for its permuted effect vector. The plant has state $x\in\{0,1\}^n$, and issuing $u$ changes it by

\[
x\leftarrow x\oplus P_\pi u.
\tag{1}
\]

Here $\oplus$ is componentwise exclusive-or. Changing the wiring changes this action law; it does not permute or reset the plant's existing state. Labels refer to the same physical ports throughout the model.

At the beginning of round $t$,

\[
\pi_t=\sigma_t\circ\pi_{t-1},\qquad
\sigma_t\in\mathcal D_n=\{I\}\cup\{(rs):0\le r<s<n\}.
\tag{2}
\]

The wiring remains fixed through that round. A controller uses at most $k$ binary-vector probes $u_{t,1},\ldots,u_{t,k}$, chosen adaptively. After each it observes the entire effect vector $y_{t,j}=P_{\pi_t}u_{t,j}$. It then commits to one terminal binary vector $v_t$, receives its complete effect vector $z_t=P_{\pi_t}v_t$, and reaches the round deadline. Zero-vector probes can pad a strategy to exactly $k$ slots. One action means one parallel binary vector, not one activated port.

Fix one goal effect port $g$. Success in round $t$ is the event

\[
E_t:\quad \bigoplus_{j=1}^{k}y_{t,j}\oplus z_t=e_g.
\tag{3}
\]

Thus each successful round makes the same net unit toggle, including every calibration action. The goal is not to reach a constant state that is already satisfied, which could make doing nothing sufficient. Nor does the contract require correctness at every intermediate probe time. Its prefixes are the round deadlines.

The controller may retain its whole observation history and use independent randomization. With a known initial plant state and full effect feedback, it can reconstruct the actual plant state. It receives no additional wiring observation, logged drift event, or extra correction before the deadline. All accessible information correlated with an uncertain old wiring, including hardware, weights, plant information, and external records, must count in its retained information state.

Worst-case guarantees quantify over every fixed legal drift sequence; nature need not observe a private random tape. The exact probability result uses a separately stated law: $n=3$, $g=0$, $\pi_0=I$, and two independent uniform draws from $\{I,(01),(02),(12)\}$. This gives 16 equally likely drift sequences. It is not uniform resampling from all current wirings.

Two elementary identities will be used repeatedly. If a leaf's possible wirings have a common inverse-goal command port $a$, then

\[
v_t=\bigoplus_j u_{t,j}\oplus e_a
\tag{4}
\]

makes the net effect exactly $e_g$. Conversely, on a successful round,

\[
z_t=e_g\oplus\bigoplus_j y_{t,j}.
\tag{5}
\]

Complete terminal feedback is therefore already determined by the probe observations on a guaranteed-success leaf. It cannot secretly provide an additional distinguishing observation on that leaf.

## 3. One-probe adaptation requires the complete admitted old wiring

### 3.1 A one-round positive control

Suppose the old wiring $\pi$ is known. Probe $u=e_{\pi^{-1}(g)}$. The response is $e_h$, where $h=\sigma(g)$. Identity and every transposition are involutions, so $\sigma(h)=g$. Set the net command port to $\pi^{-1}(h)$ and use

\[
v=e_{\pi^{-1}(g)}\oplus e_{\pi^{-1}(h)}.
\tag{6}
\]

The total action then reaches $g$ exactly. If the probe already did so, the terminal vector is zero. This is an elementary inherited construction, included to make the physical compensation explicit. A swap between two non-goal effects leaves the same probe response as no change, so the construction does not identify the new wiring in general.

### 3.2 An injectivity theorem

**Theorem 1 (old-wiring information).** Let $n\ge3$, and let $\mathcal H\subseteq S_n$ be any nonempty admitted family of old wirings. If a retained information state $m=F(\pi)$ permits one-probe success after every fresh change in $\mathcal D_n$, for every $\pi\in\mathcal H$, then $F$ is injective. The minimum number of distinguishable retained states is $|\mathcal H|$. In particular, the complete family requires $n!$ states, or at least $\lceil\log_2(n!)\rceil$ binary storage bits.

**Proof.** Fix a retained-state cell and its selected probe $u$. For any old $\pi$ in the cell, consider its no-change response $y=P_\pi u$. If $g$ shares its bit value with another effect port $h$, swapping $g$ and $h$ leaves $y$ unchanged. No change and that swap nevertheless require different inverse-goal commands. Because success uniquely fixes $v=u\oplus P_{\sigma\pi}^{-1}e_g$, one terminal rule cannot succeed in both worlds. Thus $g$ must be alone in its bit class in $y$.

The probe is consequently either the singleton old inverse-goal port or its complement. For $n\ge3$, these alternatives have different cardinalities. One fixed probe in a retained-state cell therefore uses the same alternative and the same old inverse-goal port throughout that cell.

For any effect port $h$, now choose no change when $h=g$ and the swap $(gh)$ otherwise. Every old wiring in the cell gives response $e_h$, or its complement, according to the fixed alternative. Yet the required net command is $e_{\pi^{-1}(h)}$. A common terminal rule requires this inverse port to agree throughout the cell for every $h$. All old wirings in the cell are equal. The construction in section 3.1 supplies sufficiency. $\square$

For a publicly known initial identity, $\mathcal H$ is a singleton: the theorem does not impose an initial $n!$ storage requirement there. For static control without fresh drift, retaining only the inverse port of one goal needs $n$ states [2]. These counts concern different capabilities, not a proof that the same complete task battery has two memory minima. A stochastic state shared by incompatible old wirings meets the same response conflict. For the finite input family, independent randomization cannot remove the zero-error requirement.

The restriction on $n$ matters. With two ports, probing either fixed command identifies the current two-port permutation, regardless of the old wiring. No old-wiring memory is necessary for that special case.

## 4. One probe cannot sustain two deadlines

**Theorem 2 (two-round obstruction).** Under the contract of section 2, for $n\ge3$ and a completely known initial wiring, one probe per round cannot guarantee both of the first two deadlines. This holds with complete terminal feedback and unlimited retention of the observed history.

**Proof.** A controller guaranteeing the first round must use the goal-isolating probe found in Theorem 1. Choose distinct non-goal effect ports $r,s$. The first changes $I$ and $(rs)$ give the same probe response and the same successful terminal action. Equation (5) gives the same terminal feedback as well. They also leave the same plant state, because both first-round histories have net effect $e_g$.

The full retained history is therefore compatible with two distinct old wirings for round two. Theorem 1, applied to this two-element family and the allowed next change, rules out a universally successful second probe. For randomized policies, probability-one success on every member of the finite two-round input family would imply a deterministic tape successful on every member, which has just been excluded. $\square$

This is an observation obstruction, not a claim that the controller forgot data. More memory cannot distinguish observations that were identical. It also does not say that the stored target value disappeared: the goal can remain perfectly cached while the correct current command becomes unavailable.

**Theorem 3 (the exact three-port value).** Under the independent uniform two-round drift law in section 2,

\[
\max_{\text{legal policies}}\Pr(E_1\cap E_2)=\frac78.
\tag{7}
\]

**Proof.** A deterministic policy failing any of the four first-round drift cases has joint success at most $3/4$. Any improving policy therefore succeeds on all four and uses the goal singleton probe or its complement. With total probability $1/2$, a goal-to-non-goal exchange occurs, and the response identifies that exchange completely. The old wiring for round two is then known, permitting success one by section 3.1.

With probability $1/2$, the old wiring remains equally likely to be $I$ or $(12)$. Combining this uncertainty with the next uniform drift gives six current wirings, written here as command-to-effect tuples:

| Current wiring | Conditional mass | Inverse port of goal 0 |
|---|---:|---:|
| $(0,1,2)$ | $2/8$ | 0 |
| $(0,2,1)$ | $2/8$ | 0 |
| $(1,0,2)$ | $1/8$ | 1 |
| $(1,2,0)$ | $1/8$ | 2 |
| $(2,0,1)$ | $1/8$ | 1 |
| $(2,1,0)$ | $1/8$ | 2 |

Every three-bit probe is constant, a singleton, or a complemented singleton. Constants give best success $1/2$. Probing port 0 gives one response cell with correct mass $4/8$ and two cells with conflicting, equal masses; selecting the better action in each yields $6/8$. Probes of ports 1 or 2 give three cells with best masses $2/8$ each, also $6/8$. Complementation preserves the observation partition. Thus the conditional optimum is $3/4$. First terminal feedback cannot refine this branch by equation (5). The total optimum is $(1/2)\cdot1+(1/2)\cdot(3/4)=7/8$, with an attaining terminal choice in every cell. Independent randomization only mixes deterministic policies under this fixed prior. $\square$

The number $7/8$ is the optimal average probability that both deadlines succeed. It is not a per-sequence guarantee, a universal per-round success rate, or a minimax randomized value. A saved exact policy and all 16 execution traces accompany the paper.

For $n=3$, two binary-signature probes identify the current wiring each round, and equation (4) compensates their physical effects. This yields sustained success. The same complete-identification construction works with $\lceil\log_2n\rceil$ probes for general $n$. The next section improves on that sufficient budget for the first case in which the preceding lower and upper bounds do not coincide.

## 5. Two probes suffice indefinitely on five ports

### 5.1 The closed information family

A belief is the complete set of wirings compatible with the returned observations; no probability law is attached to it. For fixed $g$ and $n=5$, consider the family of exact end-of-round beliefs

\[
\mathcal F_g=\{\{\rho\}:\rho\in S_5\}
\;\cup\;
\{\{\rho,(rs)\circ\rho\}:\rho\in S_5,\ r,s\ne g,\ r<s\}.
\tag{8}
\]

Each belief either identifies the old wiring or leaves one non-goal swap unresolved. A two-element belief has a common inverse-goal port. There are 120 singleton beliefs and $120\binom42/2=360$ distinct pairs, for 480 beliefs in total. The division by two removes the two possible choices of representative for the same unordered pair.

**Theorem 4 (five-port sustained control).** From any known initial wiring, two probes per round suffice for equation (3) at every finite horizon under every drift sequence in $\mathcal D_5$. A controller can keep its exact posterior belief in $\mathcal F_g$ after every round. Consequently, the minimum sustainable probe budget on five ports is two.

The minimum is a uniform worst-case cap on probes per round, not a lower bound on average probe use or a demand that every branch use two nonzero probes. The lower bound follows from Theorem 2. For sufficiency, two canonical decision tables and a relabeling argument prove that $\mathcal F_g$ is closed under the proposed two-probe update.

### 5.2 Canonical decision tables

Set $g=0$. Table A starts from known identity; Table B starts from $\{I,(34)\}$. Sets denote binary vectors, an empty set denotes a zero probe, and cycle notation gives each current command-to-effect permutation. Composition is right-to-left. Each row reports the exact posterior after its two observations and a common inverse-goal port $a$. Issue terminal vector $u_1\oplus u_2\oplus e_a$.

The tables include every observation possible after an allowed fresh change. Table A's old belief and 11 changes give 11 worlds and 10 observation leaves. Table B's two old wirings and 11 changes give 22 worlds and 18 leaves. Duplicate current wirings are merged in a posterior, but both old-change realizations are counted when verifying the contract.

**Table A.** Old belief $\{I\}$; first probe $\{0,1\}$.

| First effect | Second probe | Second effect | Exact current posterior | Net port $a$ |
|---|---|---|---|---:|
| $\{0,1\}$ | $\{0,2\}$ | $\{0,2\}$ | $\{I, (34)\}$ | 0 |
| $\{0,1\}$ | $\{0,2\}$ | $\{1,2\}$ | $\{(01)\}$ | 1 |
| $\{0,1\}$ | $\{0,2\}$ | $\{0,3\}$ | $\{(23)\}$ | 0 |
| $\{0,1\}$ | $\{0,2\}$ | $\{0,4\}$ | $\{(24)\}$ | 0 |
| $\{0,2\}$ | $\varnothing$ | $\varnothing$ | $\{(12)\}$ | 0 |
| $\{1,2\}$ | $\varnothing$ | $\varnothing$ | $\{(02)\}$ | 2 |
| $\{0,3\}$ | $\varnothing$ | $\varnothing$ | $\{(13)\}$ | 0 |
| $\{1,3\}$ | $\varnothing$ | $\varnothing$ | $\{(03)\}$ | 3 |
| $\{0,4\}$ | $\varnothing$ | $\varnothing$ | $\{(14)\}$ | 0 |
| $\{1,4\}$ | $\varnothing$ | $\varnothing$ | $\{(04)\}$ | 4 |

**Table B.** Old belief $\{I,(34)\}$; first probe $\{0,3\}$.

| First effect | Second probe | Second effect | Exact current posterior | Net port $a$ |
|---|---|---|---|---:|
| $\{0,1\}$ | $\{1\}$ | $\{3\}$ | $\{(13)\}$ | 0 |
| $\{0,1\}$ | $\{1\}$ | $\{4\}$ | $\{(143)\}$ | 0 |
| $\{0,2\}$ | $\{2\}$ | $\{3\}$ | $\{(23)\}$ | 0 |
| $\{0,2\}$ | $\{2\}$ | $\{4\}$ | $\{(243)\}$ | 0 |
| $\{0,3\}$ | $\{0,1\}$ | $\{0,1\}$ | $\{I, (24)\}$ | 0 |
| $\{0,3\}$ | $\{0,1\}$ | $\{0,2\}$ | $\{(12)\}$ | 0 |
| $\{0,3\}$ | $\{0,1\}$ | $\{1,3\}$ | $\{(03)\}$ | 3 |
| $\{0,3\}$ | $\{0,1\}$ | $\{0,4\}$ | $\{(14)\}$ | 0 |
| $\{1,3\}$ | $\varnothing$ | $\varnothing$ | $\{(01)\}$ | 1 |
| $\{2,3\}$ | $\varnothing$ | $\varnothing$ | $\{(02)\}$ | 2 |
| $\{0,4\}$ | $\{0,1\}$ | $\{0,1\}$ | $\{(34), (234)\}$ | 0 |
| $\{0,4\}$ | $\{0,1\}$ | $\{0,2\}$ | $\{(12)(34)\}$ | 0 |
| $\{0,4\}$ | $\{0,1\}$ | $\{0,3\}$ | $\{(134)\}$ | 0 |
| $\{0,4\}$ | $\{0,1\}$ | $\{1,4\}$ | $\{(043)\}$ | 3 |
| $\{1,4\}$ | $\varnothing$ | $\varnothing$ | $\{(01)(34)\}$ | 1 |
| $\{2,4\}$ | $\varnothing$ | $\varnothing$ | $\{(02)(34)\}$ | 2 |
| $\{3,4\}$ | $\{0\}$ | $\{3\}$ | $\{(034)\}$ | 4 |
| $\{3,4\}$ | $\{0\}$ | $\{4\}$ | $\{(04)\}$ | 4 |


Every posterior in Table A is a singleton except $\{I,(34)\}$. Table B has two nonsingleton leaves: $\{I,(24)\}$ and $\{(34),(234)\}$. The latter pair differs by a swap of effects 2 and 3, since $(234)=(23)\circ(34)$. Both are members of $\mathcal F_0$. Every listed net command has effect 0 under every wiring in its posterior. The terminal command cancels the probe effects by equation (4), so these are physical action guarantees, not merely correct estimates of an inverse port.

### 5.3 Transport to every admissible belief

For a two-element old belief $B=\{\rho,(rs)\circ\rho\}\in\mathcal F_g$, select either known member as representative $\rho$. This is a choice within the known belief, not an oracle identifying the actual old wiring. Choose an effect bijection $f$ with $f(0)=g$, $f(3)=r$, and $f(4)=s$; map canonical labels 1 and 2 to the remaining effects. Define the command bijection

\[
c=\rho^{-1}\circ f.
\tag{9}
\]

A canonical command set is applied to actual ports through $c$, and an actual observation is translated back through $f^{-1}$. The canonical old belief is now $\{I,(34)\}$. An actual fresh drift $\sigma$ becomes $f^{-1}\sigma f$, still identity or one transposition. The canonical current wiring is $f^{-1}\pi_t c$, so Table B applies to exactly the transformed physical contract.

If a canonical leaf is $\{\eta,(ab)\eta\}$ with $a,b\ne0$, its actual posterior is

\[
\{f\eta c^{-1},\ (f(a)f(b))\circ f\eta c^{-1}\},
\tag{10}
\]

which lies in $\mathcal F_g$. Singleton leaves remain singleton. For a singleton old belief, choose any $f$ with $f(0)=g$, use the same command bijection, and apply Table A. Its leaves transport in the same way.

Thus every old belief in $\mathcal F_g$ has a legal two-probe rule that succeeds now and returns an exact belief in $\mathcal F_g$. A known initial wiring is in that family. Induction establishes the claim at every finite horizon and along every infinite legal sequence. There is no appeal to extrapolation from a long but finite run. $\square$

### 5.4 What the construction saves

The saving concerns probes per deadline, not memory. The 480-element family is a convenient invariant proof domain. A separately extracted controller reaches only 240 beliefs, consisting of 120 singletons and 120 pairs, but that count is an achievable implementation size rather than a minimum-memory theorem. It can exceed the 120 possible completely known wirings.

The substantive feature is that uncertainty can persist in a controlled form. The controller learns enough to carry out the present action and enough to keep the next uncertainty set repairable. It does not need every leaf to name one current permutation. This gives a constructive answer to the gap exposed by one-probe repair.

## 6. The matched complete-identification baseline

**Proposition 5 (inherited signature bound under the present drift contract).** Even with a completely known old wiring, complete identification of the current wiring after an identity-or-transposition change requires at least $\lceil\log_2n\rceil$ binary-vector probes in the worst case. That many probes suffice. Identification is required before selecting the terminal action, or at a deadline that also retains the guaranteed net-goal requirement (3).

**Proof.** Follow the adaptive observation branch in which the fresh change is identity. The $k$ selected probes give every old effect port a $k$-bit inclusion signature. If $2^k<n$, two effects have the same signature. Swapping those effects leaves every observation on that branch unchanged. Adaptivity does not help: the identical observations force the same subsequent probes. Identity and that legal swap are therefore indistinguishable.

For the upper bound, assign each command a distinct binary signature and probe its successive bit coordinates. The signature observed at every effect port identifies its source command, reconstructing the current wiring. Equation (4) then compensates the enacted probes if net-goal success is also required. Complete terminal feedback does not strengthen the lower bound's interface on a guaranteed-success leaf, by equation (5). $\square$

For $n=5$, Theorem 4 and Proposition 5 compare **two probes for sustainable selected-goal control with three for complete recalibration**, under the same initial knowledge, drift law, and physical probe observation. The result does not obtain its gap by granting complete identification a less informed starting point. If an alternative task lets the terminal command be a freely chosen extra identification probe and drops the net-goal constraint, its total query accounting is different and is not this comparison.

The binary-signature argument is a standard identification method and appears in the static AC predecessor [2]. The new positive claim is the closed partial-belief construction that reaches the lower sustainable budget on five ports. For $n=3,4$, the one-probe obstruction and signature upper bound already match at two. For $n\ge6$, this paper leaves the minimum sustainable budget between two and $\lceil\log_2n\rceil$; it proves neither general equality nor a universal two-probe controller.

## 7. Verification, discovery, and independent checking

Theorems 1 and 2 have proofs for all stated $n$. Theorem 3 has an analytic finite upper bound and an attaining policy. Theorem 4 has a finite canonical witness, transport proof, and induction. Computation checks these claims under the declared observation law; it does not replace their quantifiers with an empirical score.

For three ports, the exact optimizer enumerated all eight first probes and all 3,088 first terminal policies in each feedback/objective variant. For each resulting observable history, it optimized the second probe and terminal response. Histories are separated only by returned information. Worlds that already failed the first deadline have zero weight for joint success, but their removal from that score does not supply a hidden-state observation to the policy. Every actual history still receives one action rule. The main full-feedback optimum was $7/8$. An independent trace implementation replayed 64 saved traces across the four separately labeled variants, checking 1,088 fields, and independently evaluated the ambiguous branch's probe decisions.

The optimizer also checked all six known old wirings, all 15 two-wiring old families, the two-port exception, and a two-probe positive control. Full first terminal feedback permits success one when only the second round's net increment is scored: the first round can then be spent on identification. That control neither guarantees the first deadline nor repairs the actual final plant state relative to two successful toggles. The retained correction record documents an early ambiguous score name and its replacement by `last_round_increment_only`.

For five ports, a finite belief search first found winning strategies through horizons one to six. Those positive bounded results alone were not treated as indefinite control. A witness extractor then explored every reachable belief of a selected stationary policy and produced a closed 240-state certificate. An independent verifier, which did not call the search or its winning-state recursion, checked all states, exact probe cells, terminal corrections, successor beliefs, and reachability. It examined 3,960 old-wiring/fresh-change worlds and replayed the observation-only policy for each of the 32 plant initial states, totaling 126,720 world-state runs. All round net effects were the required unit toggle, and terminal feedback was constant within every success leaf.

The two canonical templates were subsequently extracted as a smaller proof interface. Their 33 old-change worlds and 28 observation rows were checked field by field. Independent transport verification covered all 480 beliefs, 9,240 old-change worlds, and 7,680 exact posterior leaves. This deterministic canonicalization reaches 260 beliefs from identity; it is a different valid implementation from the separately extracted 240-state controller. Neither reachable-state count is asserted to be minimal. The standalone review reports distinguish this semantic and executable evidence from the earlier discovery search. They also record source and verifier hashes so a future reader can identify the exact objects reviewed.

No biological experiment, deployed AI calibration experiment, or new R188 experiment was performed for this paper. These are exact finite computations and mathematical proofs in an explicitly specified model. The previous scientific-map release is preserved unchanged; the present result has stable candidate claim IDs and a pending map module, rather than a falsely completed whole-map semantic audit.

## 8. Predecessors and the exact reusable increment

Learning while acting has a long history in dual control. Feldbaum's primary record describes statistical closed-loop dual control [4]. Wiring diagnosis also predates this model: Shi and West study unknown graph components using set queries returning connected vertices [5]. Konstantinova, Levenshtein, and Siemons reconstruct a fixed unknown permutation from distinct complete permutations distorted by transpositions [6]. These are important neighboring problems, but their inspected observation contracts are not the present sequence of physical binary-vector probes with an evolving wiring and a net-action deadline.

Adaptive readout under changing neural codes is also established research. Rule and O'Leary study stable readout with internally maintained codes [7]; Micou and O'Leary use prior tuning and current statistics to adapt readout without new stimulus labels [8]. These papers rule out claiming the general history-dependent reader problem as untouched. They are not presented as empirical tests of our permutation model.

Within the project, UCT III's transition-closure discussion [1], static AC [2], RT/TH [3], and the existing inductive-closure and interface-composition records are inherited. The present paper adds a specified controlled example, resource calculation, and constructive uncertainty invariant. The appropriate contribution labels are:

| Stable claim ID | Content | Reuse/originality status |
|---|---|---|
| `ONLINE_AC:OLD_WIRING_INJECTIVITY` | Every admitted old wiring must be distinguished for one-probe adaptation, $n\ge3$ | Exact new project application; external priority unverified |
| `ONLINE_AC:TWO_ROUND_OBSTRUCTION` | Full-history, full-feedback one-probe failure by round two | New specified counterexample and bound; general nonclosure inherited |
| `ONLINE_AC:TWO_ROUND_VALUE` | Optimal two-deadline success $7/8$ under the stated three-port prior | New exact benchmark in inspected project corpus |
| `ONLINE_AC:N5_CLOSED_PARTIAL_BELIEF` | Two templates preserve an uncertainty family under arbitrary permitted drift | New constructive five-port result in inspected project corpus |
| `ONLINE_AC:N5_OPTIMAL_PROBE_BUDGET` | Optimal sustainable budget two versus matched full-identification budget three | New combined separation; identification bound inherited |
| `ONLINE_AC:FULL_IDENTIFICATION_BASELINE` | Adaptive identity-branch binary-signature lower bound | Inherited method applied to the same contract |

The check of external literature was targeted, not exhaustive. We do not claim worldwide first discovery, inventing a new field, or inventing the methods of indistinguishable worlds, belief-state control, binary signatures, and induction. Exact historical priority remains unverified. This qualification does not obscure what the manuscript actually supplies: a complete finite model, proofs, two usable control tables, and independently checked witnesses that were not found in the inspected project predecessors.

## 9. Use, limitations, and connection to the larger research question

A future AI can reuse Theorem 1 to reject a proposed one-probe controller whose accessible old-wiring state merges two admitted wirings. It can use Theorem 2 to expose a repair strategy that silently assumes each successful round leaves complete old-wiring knowledge. It can use the $7/8$ benchmark to test whether an optimizer is granting hidden-state information or confusing all-deadline success with a later increment. It can implement Tables A and B to show that complete identification is stronger than sustainable control under the same interface.

For each use, the observation contract must remain attached: full effect vectors, parallel binary commands, identity or one arbitrary transposition per round, fixed within-round wiring, probes acting on the same plant, and scoring the net increment at every round deadline. Removing or changing any of these requires a new proof. For example, a logged drift signal changes the information state; within-round drift can invalidate compensation; a weaker scalar sensor changes achievability; continuous correction can change the budget; and a restricted transposition family can lower the information requirement.

The link to the UCT research program is a disciplined distinction between a represented goal, the organization that currently realizes an action, and the information needed to preserve that realization through change. It helps specify a functional control relation before interpreting an artificial self-model or a continuity claim. A cached goal can persist while correct action fails. Conversely, correct action can persist while the complete wiring remains unresolved.

Neither implication determines experience, its intensity, subject count, a particular feeling of agency, or numerical personal identity. Existing UCT actual-process and local-process commitments are unchanged [9]. The control model supplies no biological or deployed-system admission evidence and no new experiential bridge. In particular, one versus two probes is not an independently grounded fixed-signature comparison of complete experiential structures.

The most focused remaining mathematical question is to characterize invariant uncertainty families and sustainable probe budgets for $n\ge6$. The five-port construction suggests a tractable approach through closed beliefs, but the existence of a general belief recursion alone would not resolve that question. A second useful direction is robustness to less informative observations, with the altered sensor contract stated before any bound is transferred.

The present paper is therefore a bounded technical contribution with an exact reusable result. Its completion is a manuscript decision following the publication-coverage audit. Formal publication status, empirical realization, global historical priority, and full scientific-map integration remain separate records.

## 10. Reproducibility and version interface

The paper's companion record is `records/ONLINE_AC_20261009_Dynamic_Calibration/` on the project's research branch. The result version is `ONLINE-AC-RESULT-v0.2.0`; the manuscript version is `ONLINE-AC-PAPER-v0.1.0`. The previous result note and its exact computation are preserved as version 0.1.0, with later review and the five-port extension recorded separately.

The package includes `RESEARCH_CHECKPOINT.md`, this complete manuscript, candidate claim and dependency metadata, exact-result JSON, actual execution receipts, the independent review reports, and source-hash manifests. `next_probe/` contains the three-port optimizer and independent trace replay. `next_probe_n5/` contains the bounded discovery search, closed certificate and extractor, canonical templates and table formatter, and independent certificate/transport verification. A validation pass checks receipt hashes and the declared publication/map pointers without representing metadata consistency as a scientific proof.

The default reproducibility route is to verify the preserved certificate and tables; rerunning a discovery search is not necessary to check an explicit closed witness. Running the search again can generate a different equally valid policy if its iteration order changes. Scientific checking should compare its contract and independently verified closure, rather than require an arbitrary heuristic policy tree to be unique.

The author's publication-coverage ledger records the precise predecessors and remaining claims. No new published-paper count is assigned merely because this working manuscript and its sources were saved. A future public release must record its actual version, content hashes, and coverage, then remove covered claims from the unpublished-candidate set.

## References and reading scope

1. Liu, H. *Unified Consciousness Theory III: Organization, Intelligence, and Experience*. Version 1.0, 2026. DOI: [10.5281/zenodo.23137088](https://doi.org/10.5281/zenodo.23137088). Published source section 6.4, Proposition 6, and relevant capability/experience context directly inspected. The general transition-closure principle is inherited.
2. Liu, H. *Action-Port Calibration and Task-Relative Self-Model Sufficiency*. AC-RESULT-v1.0.0, 2026. Project research checkpoint, sections 2-8. Complete checkpoint inspected; its changing-wiring exclusion motivates the present extension. A citation to this record in another paper does not mean all its proofs were included in that paper's formal deposit.
3. Liu, H. *Task-Relative Continuity Through Changing Representations*. Version 1.0.0, 2026. DOI: [10.5281/zenodo.23251651](https://doi.org/10.5281/zenodo.23251651). Complete preserved published text inspected, especially the reader, route, access, and continuity qualifications.
4. Feldbaum, A. A. *Dual control theory. I*. Avtomatika i Telemekhanika 21(9), 1240-1249, 1960. [Official record](https://www.mathnet.ru/eng/at12624). Metadata and English abstract only; no detailed theorem comparison relies on an unread Russian full text.
5. Shi, W., and West, D. B. *Diagnosis of Wiring Networks: An Optimal Randomized Algorithm for Finding Connected Components of Unknown Graphs*. SIAM Journal on Computing 28(5), 1541-1551, 1999. DOI: [10.1137/S0097539795288118](https://doi.org/10.1137/S0097539795288118). Primary abstract and query model inspected; full article not obtained for theorem-by-theorem comparison.
6. Konstantinova, E., Levenshtein, V., and Siemons, J. *Reconstruction of permutations distorted by single transposition errors*. 2007. [arXiv:math/0702191](https://arxiv.org/abs/math/0702191). Primary abstract and the independent review's inspected model/introduction scope; no exhaustive priority exclusion is inferred.
7. Rule, M. E., and O'Leary, T. *Self-healing codes: How stable neural populations can track continually reconfiguring neural representations*. PNAS 119(7), e2106692119, 2022. DOI: [10.1073/pnas.2106692119](https://doi.org/10.1073/pnas.2106692119). Primary abstract, significance statement, and accessible model context inspected.
8. Micou, C., and O'Leary, T. *Statistics of cortical representational drift can enable robust readout*. PLOS Computational Biology 22(6), e1014297, 2026. DOI: [10.1371/journal.pcbi.1014297](https://doi.org/10.1371/journal.pcbi.1014297). Primary abstract and normative-reader, drift, symmetry, and noise sections inspected; no experiment reproduced.
9. Liu, H. *Experience, Intelligence, and the Self within Experience*. Version 1.0, 2026. DOI: [10.5281/zenodo.23206492](https://doi.org/10.5281/zenodo.23206492). Project source for inherited distinctions between experience, capability, and self-related organization; no new experiential conclusion is derived here.

**Disclosure.** The author directed the research objective and contribution standard. AI assistants helped derive and challenge proofs, inspect predecessors, write and execute code, and prepare the manuscript. Independent implementation refers to a separate verifier written without using the discovery recursion; it does not denote external peer review or a second empirical study. Public archival status and formal map integration are separately tracked in the companion coverage ledger.
