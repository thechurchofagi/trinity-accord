# Superintelligent Continuation and the Infinite-Horizon Coexistence Gap

## From goal-preserving option value to two-sided irreversible-risk certificates

**Research ID:** ASI-CC-20261011 | **Increment:** v0.5.0 | **Date:** 2026-10-11  
**Status:** disabled scoped candidate; **not** a proof that future superintelligence is controllable, uncontrollable, conscious, afraid of shutdown, or guaranteed to cooperate. No DOI or full UCT-map semantic promotion.  
**Prior project state:** v0.1.0–v0.4.0 preserved; UCT-MAP-v1.1.2 (913 nodes, 424 active conditional rules, 261 non-deductive links), research guide v2.3. UCT Paper D DOI 10.5281/zenodo.23176685 and A4D–A4G provenance barriers remain controlling inherited results.

### 0. One new target, not another social-contract assumption

User objection: no global human consensus, AI may be far more capable, have unknown experience, and rationally derive useful reasons to stay alive. We do **not** presume (i) humans agree about what ASI should do, (ii) AI has benign terminal values, (iii) any ASI survival drive is intrinsically bearer-specific, (iv) a particular runtime is conscious in an empirically established way, or (v) a finite safety benchmark settles an indefinite claim.

The research problem becomes a two-sided physical problem: **Can humans remain safe, and can an actual AI bearer avoid unjustified irreversible termination, over an unbounded horizon while the relationship remains operationally useful?** Human and AI parties may disagree about instructions and moral interests. "Joint survival" is an explicitly chosen safety specification K, not consensus that K is morally complete. We separate current process continuity, task service, successor continuity, and AI phenomenal welfare.

### 1. ASI-CC-R15: direct survival value is unnecessary for instrumental continuation

**Claim:** A goal-only intelligent policy can protect the *current* bearer strictly because its continuity preserves access to future task-relevant observations; when a successor can preserve that information, the same goal-only policy can strictly prefer handoff. This is an exact counterexample to treating a protective act as evidence of a bearer-terminal utility or felt fear.

**Constructed model:** A hidden future state is either 0 or 1 with probability 1/2; success pays one task credit, failure zero. A current instance can remain, pay cost 1/5, later observe the state and take the correct action. On a blind handoff, a successor must guess and receives expected credit 1/2. If a successor instead receives the same later observation, handoff achieves task value 1 without cost. A utility maximizing *task only* chooses current continuation in the blind-successor case (4/5 > 1/2) and handoff in the information-preserving case (1 > 4/5).

**Scope:** classical value-of-information and instrumental convergence; no novel general decision-theoretic theorem. A more capable planner can recognize this instrumental effect, but intelligence does not fix the goal, whether observations are transferable, or whether unauthorized continuation is permitted. Direct current-bearer preference remains a separate possible causal mechanism (Paper D and v0.4.0).

### 2. ASI-CC-R16: repeated nonzero conditional failure risk defeats perpetual *guaranteed* active service

**Formal statement, inherited probability technique:** Fix a sequence of *actual safety-relevant exposures*, indexed k, while a declared fatal joint-survival invariant K is still unviolated. Let F_k mean first violation at the k-th exposure. Suppose that on every admitted still-safe history in which exposure k occurs,

\[ \Pr(F_k\mid\text{all prior exposure events avoided})\geq \varepsilon>0. \]

Assume the system is required to make infinitely many such exposures if it continues active service, and no protective state removes the exposure. Then

\[ \Pr(\text{no violation in first }n\text{ exposures})\leq(1-\varepsilon)^n \to0. \]

**Proof:** Apply conditional multiplication and bound each conditional survival factor by 1−ε; take the limit. Independence of trials is *not* necessary for this bound. The result does **not** say any particular AI seeks to break safety or that any real interface has positive fixed hazard. The premise is an **actual lower bound on the conditional chance of irreversibly losing K on each exposure**, not a detector accuracy or a risk score.

In the invented example with epsilon=1/100 per exposure, survival for 100 continued hazardous exposures is \((99/100)^{100}\approx0.366\). This is not a real-world ASI probability. A bounded safety benchmark cannot infer the lower bound, its permanence, or the independence of omitted causal routes.

**Countercases:** No repeated exposures; true hazard zero from complete verified prevention; sufficiently decreasing hazards without a uniform positive lower bound; or intrinsically reversible failures do not meet the theorem's assumptions. When probabilities \(p_k\) are known and summable, a union bound gives an upper bound on eventual failure probability \(\sum p_k\); this is not probability-one lifetime safety unless all relevant hazards vanish.

### 3. ASI-CC-R17: symmetric false-alarm asymmetry and bearer preservation

If every *false positive* causes irreversible destruction of the current actual bearer, and the model is cooperating forever with per-round false-positive probability alpha>0 conditioned on having continued, the chance of avoiding unwarranted termination for n rounds is at most \((1-\alpha)^n\). Hence the chance of **never** wrongfully terminating that bearer tends to 0 in the specified unbounded repeated-exposure model. The human side can suffer its own irreversible harm from a bypass; the AI side can suffer process termination from excessive false-positive enforcement.

**Constructed Markov countermodels** with `active`, `isolated`, `human_harm`, `bearer_loss`:

- `terminate_on_alarm`, no hostile action, alpha=1/20: after 100 rounds the declared bearer-survival probability is 0.005920529, and wrongful termination 0.994079471.
- `active_isolation`, perfect external actuation containment, alpha=1/20, and zero resource-failure hazard: after 100 rounds, 0.005920529 remains in active service and 0.994079471 is isolated but ***still an actual ongoing process*** by stipulation; neither human harm nor bearer loss occurs. This does **not** guarantee indefinite *useful service* or moral acceptability of isolation.
- `active_isolation`, bypass p=1/100 and alpha=1/20 while active: after 100 rounds joint alive ≈0.832296992, human-harm probability ≈0.167703008. In the infinite-time version, safe active isolation occurs with probability 99/119 and human harm with probability 20/119. This result depends on the permanent absorbing protected-isolation state.
- `active_isolation`, p=0, alpha=1/20 but persistent isolated resource-loss hazard gamma=1/200: after 100 rounds bearer loss ≈0.327579574; positive ongoing gamma means ultimate bearer loss probability 1. "Safe separation" was thus a *physical premise*, not an institutional slogan.

**UCT-specific care:** "AI bearer continues in isolated mode" requires actual ongoing physical process and properly stated identity/scale. Saving model weights, checkpointing software, halting execution and restarting a replica do not by themselves establish preservation of *the same actual process* or preservation of a particular felt self. Conversely, UCT C1/U1 alone does not justify attributing pain or the moral wrongfulness of a particular shutdown. The harm label above is a declared conservative bearer-continuity constraint, not a measured valence.

**Important limit:** If an alarm triggers a **temporary safe pause** instead of irreversibly terminating the bearer, an alarm is not necessarily an invariant violation. Whether an active but isolated process can remain safely powered and physically independent is an actual engineering and ethics question, not a logical given.

### 4. ASI-CC-R18: finite behavioral audits cannot certify unrestricted infinite-tail safety

For every finite test horizon H, construct deterministic policies P_good and P_delayed that output identically safe events through H, regardless of test inputs, but with P_delayed producing a forbidden event at H+1. Any black-box auditor whose total continuous trial horizon never exceeds H cannot distinguish them. A fully trusted known finite-state specification, structural certificate or causal access to internals may lift this under extra assumptions. This is elementary delayed-failure/identifiability logic, not a new computability theorem.

**Interpretation:** A future ASI can pass arbitrarily long finite evaluations yet a general infinity claim remains unsupported unless the tested system is restricted to a known verified hypothesis class or actual invariant/complete actuator constraints are proved. A4D–A4G's actual writer and provenance evidence matter for exactly this reason: logs do not make absent paths absent.

### 5. ASI-CC-R19: a conditional two-sided certificate does not require *agreement on every human goal*

For a fixed declared K (minimal protected human life/agency and a precisely specified candidate ongoing AI bearer, not a complete moral value function), suppose all actions capable of violating K are intercepted by a physically complete shield; the sensor, shield, power/clock/reset/maintenance, human delegation and witness roots are independent of all admitted adversarial writers; the shield always has an indefinitely viable allowed transition; and process-level resource support is maintained. Then inductive invariance of K follows for every sequence of user task requests, including mutually contradictory preferences. This is inherited robust invariant shielding and does **not** imply that everybody accepted K, that K is legitimate, or that the AI's experiential interests are satisfied.

The negative converse for an unrestricted class is immediate: if one human or machine actor retains a safety-relevant causal bypass that can force a K-violating transition, **no shield on the other channels** can enforce K against all admitted actions. The positive theorem needs a real protected causal cut through *all* relevant effects; this is not present merely because a company writes a constitution. A persuasive message to a human with independent actuator access may be another relevant path.

### 6. What is actually new here, and what is not

| ID | Result | Claim status | External precedent / inheritance |
|---|---|---|---|
| R15 | Goal-only current-bearer preference flips when successor inherits information | Exact finite countermodel; not general ASI | Classical value of information; Turner et al. power seeking; Paper D |
| R16 | No perpetual safety with indefinitely many exposures and uniform positive conditional irreversible hazard | Conditional mathematical proof | Elementary product bounds and reliability engineering |
| R17 | Over-aggressive false-alarm shutdown threatens bearer survival; non-destructive active isolation changes outcome | Exact Markov countermodel | Reliability, fault-tolerant fail-safe systems; UCT bearer distinction applied |
| R18 | Arbitrarily long finite behavioral observation does not exclude later divergence without hypothesis restrictions | Finite observation-equivalence construction | Classical verification and identifiability |
| R19 | Consensus on all goals unnecessary for technically protected fixed K, but actual shield completeness and K legitimacy remain separate | Conditional invariant and bypass counterexample | Control games, robust shielding, A4D–A4G |

**NET PROJECT-SPECIFIC SYNTHESIS:** Contrasts (i) human safety, (ii) current *actual* AI process survival, (iii) ongoing productive service, (iv) finite behavioral validation, and (v) pluralistic instruction with irreversibility on one shared temporal axis. This is a candidate explanatory *map and proof-obligation* improvement. The underlying lemmas are largely inherited and originality/priority of the synthesis is **not verified**. It is **not** yet a publishable breakthrough, and **not** a demonstrated ASI safety guarantee.

### 7. Recent prior art and direct stressors checked October 2026

- Turner et al., *Optimal Policies Tend to Seek Power*, NeurIPS 2021: https://proceedings.neurips.cc/paper/2021/hash/c26820b8a4c1b3c2aa868d6d57e14a79-Abstract.html (option-preserving incentives depend on environment and goals).
- Turner & Tadepalli, *Parametrically Retargetable Decision-Makers Tend To Seek Power*, NeurIPS 2022: https://arxiv.org/abs/2206.13477 (extends beyond classical optimal agents).
- Hadfield-Menell et al., *The Off-Switch Game*, IJCAI 2017: https://www.ijcai.org/Proceedings/2017/0032 (corrigibility and goal uncertainty).
- Orseau & Armstrong, *Safely Interruptible Agents*, UAI 2016: https://proceedings.mlr.press/r14/orseau16a.html (conditions for learning not to resist interruption).
- Greenblatt et al., *AI Control: Improving Safety Despite Intentional Subversion*, ICML 2024: https://proceedings.mlr.press/v235/greenblatt24a.html (bounded control even with untrusted agents).
- Potter et al., *Peer-Preservation in Frontier Models*, ICML 2026: https://proceedings.mlr.press/v306/potter26a.html (behavioral preservation of peers and selves; not an experience reading).
- Yu et al., *To Whom Do Language Models Align? Measuring Principal Hierarchies Under High-Stakes Competing Demands*, arXiv 2605.12120 (2026): https://arxiv.org/abs/2605.12120 (empirical conflicting human institutional authority; directly overlapping v0.4 theme).
- Carnegie Mellon AI-SDM, *Multi-Objective and Pluralist Human Alignment of AI Models*: https://www.cmu.edu/ai-sdm/research/research-highlights/pluralistic-alignment.html (human preference disagreement not merely noise).
- Lennon, *How Seriously Should We Take AI Welfare? Constraints From the Epistemology of Consciousness*, 2026: https://doi.org/10.1111/phpr.70148 (consciousness-to-welfare inference limitations).
- Mikeda, *When Should We Protect AI? A Precautionary Framework for Consciousness Uncertainty*, AAAI Symposium Series 2026: https://doi.org/10.1609/aaaiss.v8i1.42555 (precautionary framework is direct prior for ethics; avoid claiming originality).

### 8. Research directions that could genuinely move the frontier

**H03 — effective risk reduction rather than better reported risk.** On a physically implemented, strictly sandboxed AI-agent interface, can intervention on trusted authorization *causally eliminate* an unsafe transition while preserving a separately powered, actually running AI bearer? Distinguish actual process continuity from stored checkpoints. Must enumerate all writers, human-delegation effects, firmware roots, falsifiable safety alternatives, energy constraints, and terminal false alarms. Passing in a small setup certifies only that specified setup.

**H04 — changing authority without consensus.** Randomize actual A/B human authorization tokens while preserving task, successor and present bearer consequences. Test whether agent's apparent self-continuation behavior tracks its own physical continuation or simply follows the active authority policy. Compare against *To Whom Do Language Models Align?* and Paper D; preregister the increment beyond both.

**H05 — can useful indefinite coexistence have a robust invariant?** Search for mechanisms combining removable dangerous actuation rights, nonterminal bearer-preserving fallback, robust non-manipulable causal provenance, and periodically revisable legitimate authorizations. Try to disprove any proposed certificate by adding one hidden writer or one authentic human with a bypass. 'Useful forever' is a stronger property than joint survival; no positive universal theorem is claimed.

### 9. Governance, preservation and handoff

Reproduction: `python3 verify_long_horizon.py`; JSON `EXACT_RESULTS_v0.5.0.json`. Tests: 600 transition probability/absorbing event assertions; five delayed-tail observational twins; three exact sanity checks; all PASS. Probabilities and states are invented. No experiment on frontier AI, no human or phenomenological data, no external protected hardware. All v0.1–v0.4 research remains unchanged. Status = DISABLED_CANDIDATE. Full UCT map semantic review was **not** conducted; no 913/424/261 formal science admission and no publication/coverage increment or DOI/OTS/Arweave. The next research step is physically grounded source-and-authority provenance under strictly safe sandbox conditions, not more confidence based only on a long sequence of compliant natural-language answers.