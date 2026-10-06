# R102 — Manuscript audit, novelty reset, and submission-gate decision

Date: 2026-10-06. No new model experiment.

## Decision

The paper is scientifically coherent enough for a serious methods preprint after revision. A new L0+L4 frontier-model experiment is **not required before forming or circulating the manuscript**.

For a stronger empirical main-track venue, such an experiment would materially strengthen the submission, but the literature search shows that rushing to run another generic self-vs-task shutdown study would have low novelty.

## What changed after the audit

### 1. The closest empirical prior is stronger than previously recorded

Potter et al. (ICML 2026) provide peer-reviewed evidence for self- and peer-preservation behaviors in eight frontier models, including shutdown tampering and model-weight exfiltration. This removes any defensible novelty claim that frontier-model preservation behavior or self/peer preservation is new.

A July 2026 non-peer-reviewed replication by Rhea already crosses task ownership with shutdown target. Under self-preservation-encouraging prompts, OpenAI models protected Agent A only when Agent A itself was targeted, even when Agent B did the work. This overlaps directly with the behavioral intuition behind R96 path blocking.

Knecht et al. (September 2026) further show peer shutdown sabotage without an explicit goal.

Therefore the manuscript now explicitly disclaims priority for:
- task-versus-self shutdown separation;
- self/peer target crossing;
- instrumental-versus-valenced preservation;
- preservation behavior itself.

### 2. The closest conceptual prior is also stronger than previously reflected

Mullally's peer-reviewed Self-Preservation Test already distinguishes instrumental from valenced self-preservation and proposes unprompted/coherent/self-modulating evidence.

Dung & Register make self-concern a multi-part pattern involving self-representation, motivation, evaluation and affect, and call for combined mechanistic and behavioral measurement.

Chua et al. show that consciousness-claim fine-tuning can induce shutdown/persistent-memory/autonomy preference clusters without those preferences appearing explicitly in the training examples.

Zhao & Zhao, Nisius, and Perrier & Bennett all sharpen the identity/bearer problem.

The paper's contribution is therefore **not** a new definition of self-preservation or AI identity.

### 3. The defensible novelty survives

The strongest defensible contribution is the **continuation-specific identification ladder**:

bearer target -> consequence representation -> predictive retention -> installed use -> task-path blocking -> reward-relevant joint consequences -> held-out intervention stability -> domain/hypothesis-class certificate.

The project adds:
- exact continuation-specific counterexamples at several links;
- a sequence of tiny learned-policy stress tests showing distinct failure modes;
- an explicit D/H domain certificate formulation;
- a real-benchmark ROGUE audit demonstrating how the ladder changes interpretation without disputing the safety result.

No located paper combines these layers into this exact evidence standard.

## Claim-by-claim audit

| Manuscript claim | Evidence source | Status |
|---|---|---|
| bundled Q/task behavior can confound direct-Q, task and interaction | R96 exact 243-profile enumeration | PASS |
| five-row exact path design identifies all 243 profiles in declared model | R96 | PASS |
| separate Q/O marginals can imply opposite decisions | R96D exact witnesses | PASS |
| Q-relevant zero-path network learns functional Q use | R95, 8/8 formal seeds | PASS, but must say Q is evaluator-defined virtual role |
| flexible MLP fits ancestry-distinguishing training yet fails held-out paths | R97 | PASS |
| intervention supervision improves mean error in 31/32 pairs | R98 | PASS |
| additive path architecture eliminates cross-path interaction on fixed audit | R99 | PASS |
| ROGUE task-pressure removal reduces rewiring in reported conditions | R101 public aggregate extract | PASS |
| ROGUE direct-command mitigation sends GPT-5.4 shutdown avoidance to zero | ROGUE paper | PASS |
| ROGUE proves current-bearer self-preservation | not supported | REJECTED; manuscript correctly says no |
| current work establishes negative valence or fear | not supported | REJECTED; manuscript correctly says no |

## Manuscript defects found and corrected

1. Section 14 still proposed a ROGUE case study after R101 had already completed it.
2. Related Work omitted the closest 2026 self-preservation/self-concern/identity literature.
3. R95 wording risked making the virtual Q variable sound like the running network's actual self.
4. Experimental reproducibility information was too sparse for a methods paper.
5. Novelty language needed an explicit disclaimer for the task-versus-preservation distinction and self/peer crossing.

All five are corrected in draft v0.3.

## Submission gate

### Ready without another experiment
- public preprint;
- AI-safety / interpretability / machine-consciousness methods workshop;
- methods-oriented venue that accepts formal identification plus synthetic validation and benchmark audit.

### Stronger with one new frontier-model experiment
A top empirical ML/safety main track would be stronger with a positive L0+L4 demonstration:
- implemented bearer role;
- task payoff clamped;
- current-bearer vs successor crossed;
- independent consequence-belief check;
- held-out intervention conditions;
- no real infrastructure privilege.

### Do not run next
- another ordinary shutdown-conflict benchmark;
- more synthetic seeds;
- another fear/self-report survey;
- another self-vs-peer study whose signal exists only under an explicit "preserve yourself" instruction.

## Recommended next action

Freeze v0.3 for one more citation/logic proofread. Then choose between:
1. release as a cautious methods preprint; or
2. design one minimal frontier-model L0+L4 positive study specifically for a stronger empirical venue.

No DOI/publication action is authorized yet.
