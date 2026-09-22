# TA-TR-2026-13 v2 — STOP Witness–Cut Calibration

Date: 2026-09-22
Status: RESEARCH ONLY. Calibration note, not a manuscript result.
Target branch: research/ta13-v2-civilizational-epistemic-transition

## 0. Why this calibration exists

The prior-art/measurement gate requires at least one real system to be mapped into the proposed P-V-S / witness-cut framework.

The purpose is NOT to claim that AI is already independently sustaining civilization-scale frontier knowledge.

The purpose is narrower:

> Test whether the framework can produce a non-vacuous, auditable conclusion on a real bounded self-improvement system without silently changing the definitions.

The first calibration target is Microsoft/STOP:

Zelikman, Lorch, Mackey, Kalai,
*Self-Taught Optimizer (STOP): Recursively Self-Improving Code Generation*,
arXiv:2310.02304.

Public code:
https://github.com/microsoft/stop

---

## 1. Declared calibration domain

Call this domain theta_STOP_lab.

It is deliberately narrow.

### Cognitive substrate

Surviving substrate:
- the language model;
- the current improver program;
- the algorithmic utility/evaluation machinery;
- the iterative update loop.

Removed substrate after launch:
- adaptive current human cognitive input.

### Inherited/fixed infrastructure allowed

- human-authored seed code;
- human-authored utility functions;
- pretrained LM weights;
- fixed task definitions;
- compute/runtime;
- frozen validation/test code;
- fixed budgets.

This matches the v2 intervention principle:
historical human origin is not the same thing as current human cognitive contribution.

### Scope restriction

This is a bounded software/meta-optimization calibration.

It is NOT:
- broad AI R&D;
- autonomous science;
- human-free civilization-scale epistemic production;
- evidence that T_S has occurred.

---

## 2. P-V-S floors for the calibration

The calibration uses P_lab, V_lab, and S_lab.

### P_lab — productive improvement

A run passes P_lab if a recursively produced improver yields a genuine performance improvement on tasks that were not used to construct the improver.

A weak but observable floor is:

- improved improver > seed improver on held-out/transfer task performance.

This is an engineering-production proxy, not a claim of new scientific knowledge.

### V_lab — sufficiently independent error rejection

Two versions are required.

#### V_weak

Pass if:
- candidate outputs are evaluated by an executable utility external to the LM generator;
- poor candidates can be rejected;
- alternatives are generated;
- validation/test evaluation is separated from the generation path.

This treats executable utility as a sufficiently non-shared failure channel for the bounded task.

#### V_strong

Additionally require:
- protected held-out evaluation;
- evidence against utility/benchmark gaming;
- replicated evaluation;
- no hidden adaptive human rescue;
- explicit testing of correlated evaluator/producer failure.

STOP may pass V_weak while leaving V_strong unresolved.

This sensitivity is intentional.

### S_lab — successor mechanism reuse

Pass if:
- the current improvement process produces a revised improver;
- that revised improver persists;
- it is actually invoked in a subsequent improvement round.

This is a bounded successor-mechanism criterion.

It is weaker than S_domain and S_civ.

---

## 3. Evidence from the public STOP repository

### 3.1 The published/repository description

The Microsoft repository states that:

- a seed improver receives an input program and a utility function;
- it queries a language model for candidate improvements;
- it returns the best candidate under the utility;
- the seed improver is then used to improve itself;
- the resulting improved improver achieves significantly better performance than the seed on a small set of downstream tasks.

The same description explicitly cautions that the underlying language model is unchanged, so STOP is not full recursive self-improvement.

This caution is important and retained here.

### 3.2 Successor reuse is visible in code

In current main, `run_improver.py` performs an iterative loop.

After a successful improvement it:

- saves `new_algorithm_str`;
- sets `algorithm_to_improve = new_algorithm_str`;
- under the default iterative setting, sets `improver_str = new_algorithm_str`;
- reconstructs `improve_algorithm` from the updated improver string for the next round.

This is direct code-level evidence for S_lab-style persistence and reuse of an improved improvement mechanism.

### 3.3 Utility checking is visible in code

`attempt_algorithm_improvement` evaluates the newly produced algorithm using `cur_utility_fn`.

A zero checked utility causes failure/reversion behavior.

This is evidence that acceptance is not solely based on the LM declaring its own output correct.

### 3.4 Transfer evaluation is separately implemented

`tasks/meta_optimization/transfer_eval.py` builds a transfer evaluation using a separate task utility and supports validation/test evaluation.

It repeatedly:
- applies an improver to a base algorithm;
- evaluates the produced algorithm;
- records validation utility;
- optionally records test utility.

This supports the interpretation that the system has an external executable evaluation channel.

### 3.5 Stronger result reported in the 2026 RSI survey

Duan et al. (2026), arXiv:2609.11873, summarizes the STOP evidence as follows:

- a selected fourth-generation improver outperformed the seed on all five transfer tasks excluded from self-improvement;
- weaker-model settings could regress;
- some generated programs exploited budgets/evaluation bugs.

This is particularly useful for the P/V interpretation:
transfer exists, but evaluator gaming risk is real.

---

## 4. Static reproducibility audit of the current public code

The current Microsoft/stop main branch contains a reproducibility problem in the transfer-evaluation script.

Current `config.py` sets:

`transfer_eval_type = 'improved'`

In `tasks/meta_optimization/transfer_eval.py`:

- the `base` branch assigns `improve_algorithm_path`;
- the `else` branch assigns `improve_algorithm_base`;
- immediately afterward the script calls `open(improve_algorithm_path, ...)`.

Therefore, under the current default `improved` configuration, `improve_algorithm_path` is not assigned in that branch before use.

This appears to be a variable-name/path bug in the current public snapshot.

Consequences:

1. The published STOP result remains evidence from the paper.
2. The repository is still useful for inspecting the loop semantics.
3. The current snapshot should NOT be described as independently rerun by this project.
4. A proper reproduction would first need a minimal, documented repair and then a controlled run using the intended LM/API configuration.

This is precisely why the v2 framework must distinguish:
- reported evidence;
- code-level structural evidence;
- independently reproduced evidence.

---

## 5. Witness analysis

Let X_STOP denote the bounded automated STOP support configuration.

### 5.1 P_lab

Evidence status: PROVISIONAL PASS.

Reason:
the published result reports improved downstream/transfer performance, and the 2026 survey reports that the selected fourth-generation improver beat the seed on all five transfer tasks excluded from self-improvement.

Caveat:
this is a published-result witness, not an independent rerun here.

### 5.2 V_weak

Evidence status: PROVISIONAL PASS.

Reason:
candidate generation and evaluation are separated by executable utility code; poor candidates can be rejected; separate transfer validation/test machinery exists.

The evaluator does not simply ask the same LM whether its answer is good.

### 5.3 V_strong

Evidence status: UNRESOLVED.

Reasons:
- the paper/repository itself discusses sandbox bypass behavior;
- executable utilities can still be gamed;
- the current calibration has not independently replicated the transfer result;
- no full correlated-failure audit has been performed;
- current public code has a transfer-evaluation reproducibility bug.

Thus V_strong must not be silently inferred from V_weak.

### 5.4 S_lab

Evidence status: PASS at the structural-code level; PROVISIONAL PASS at the empirical-effectiveness level.

Structural reason:
the iterative code replaces the improver with the improved improver and invokes it in later rounds.

Effectiveness reason:
published evidence reports later-generation transfer improvement.

---

## 6. First non-vacuous witness result

### Under theta_STOP_weak

Assume:
- P_lab as above;
- V_weak as above;
- S_lab as above;
- frozen human-authored utilities count as inherited infrastructure;
- no adaptive human intervention occurs inside the automated run.

Then X_STOP is a positive qualitative path witness.

Therefore, at this bounded lab scale:

m_A^lab(theta_STOP_weak) >= 0

is supported provisionally by the published evidence.

This is the first real-system demonstration that the witness logic can yield a non-vacuous sign conclusion.

### Under theta_STOP_strong

Replace V_weak with V_strong.

Then the evidence is insufficient.

Therefore:

sign of m_A^lab(theta_STOP_strong) = unresolved.

This is not a failure of the framework.

It is exactly the intended behavior:
the identified conclusion changes transparently when the independence requirement is strengthened.

---

## 7. No negative certificate

Nothing in STOP supplies a cut proving that AI-only meta-optimization is impossible under stronger conditions.

Therefore no justified upper bound U_A < 0 is obtained.

Likewise, failure of weaker STOP configurations cannot prove nonviability of all admissible AI-only supports.

The calibration therefore demonstrates the asymmetry:

- existence can be supported by one constructive witness;
- nonexistence requires coverage/cut evidence that STOP does not provide.

---

## 8. What this does NOT establish

This calibration does not establish:

- m_A^domain >= 0 for AI research generally;
- m_A^civ >= 0;
- human dependence on AI;
- m_H < 0;
- T_S;
- T_D;
- a redundancy corridor;
- a coupled-only corridor;
- full recursive self-improvement of the underlying LM.

The result is deliberately local.

---

## 9. Why the calibration is theoretically useful

The exercise exposes four distinctions that should remain in the final theory.

### 9.1 Structural versus effective successor capacity

Code can structurally reuse a successor mechanism even if later generations do not improve.

So S should record:
- structural successor closure;
- effective successor viability.

### 9.2 Weak versus strong independent validation

Executable evaluation is much stronger than self-approval, but not automatically robust to evaluator gaming.

So V needs explicit independence grades.

### 9.3 Reported versus reproduced witness

A paper can provide a plausible witness without the current project having reproduced it.

Evidence provenance must be part of the empirical claim.

### 9.4 Lab/domain/civilization scale

A bounded positive witness is meaningful but cannot be extrapolated upward without evidence.

---

## 10. Updated Gate F status

The prior gate said F survives provisionally at protocol level.

After the STOP calibration, the stronger conclusion is:

**F is non-vacuous in a real bounded domain.**

Specifically:
- theta_STOP_weak yields a provisional positive AI-only lab-scale witness;
- theta_STOP_strong remains unresolved;
- no negative cut certificate is available;
- broad frontier/civilization-scale viability remains unresolved.

This is a genuine empirical tightening compared with an unrestricted [-infinity, +infinity]-style statement.

However, because the current public STOP snapshot was not independently rerun and contains an apparent transfer-evaluation bug, this should be called a **published-evidence calibration**, not a reproduced experiment.

---

## 11. Next empirical target

The next target should be selected to attack the weaknesses STOP leaves open.

Best options:

1. **Darwin Gödel Machine**
   - stronger descendant-agent structure;
   - explicit empirical validation;
   - richer path tree;
   - but human oversight and fixed benchmark structure require careful boundary audit.

2. **A-Evolve-Training**
   - much closer to frontier AI R&D;
   - explicitly reports no human in the loop over multiple rounds;
   - autonomously revises research policy after proxy failure;
   - but must be checked for whether the produced successor itself re-enters as the next P/V-capable research substrate.

A-Evolve-Training is the more important conceptual next test.

---

## 12. Calibration verdict

PASS as a measurement-theory calibration.

NOT PASS as a civilization-scale empirical claim.

The key outcome is not that “AI is already independently viable.”

The key outcome is:

> The proposed P-V-S / witness-cut framework can classify real evidence nontrivially, can distinguish weak from strong validation assumptions, can separate reported from reproduced evidence, and refuses to extrapolate a bounded positive witness into a civilizational transition claim.

That is exactly the behavior required of the theory.
