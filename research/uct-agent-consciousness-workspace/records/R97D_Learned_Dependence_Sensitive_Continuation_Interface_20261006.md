# R97D — Parallel addendum: learned dependence-sensitive consequence interface

Research addendum v1.0, 2026-10-06. This work was executed concurrently with the official R97 and was originally labeled R97 locally. After remote reconciliation, the earlier remote R97 keeps the numbered round; this complementary result is preserved as R97D. No official R97 file is overwritten.

## Question

R96D proved that exact action-conditional marginals for current virtual bearer availability Q and successor availability O can be decision-insufficient when task value depends on their joint law. R97D asks whether a tiny learned predictor acquires the missing A/B dependence distinction only when its prediction target requires that distinction, and whether a downstream task controller actually uses it.

## Fixed R96D contexts

Both A and B have q0=1/4, q1=3/4, o0=o1=1/2 and action-1 cost1/4. Task success is S=Q OR O.

A has task-success (1/2,1), so action1 is optimal with net value3/4.
B has task-success (3/4,3/4), so action0 is optimal with value3/4.

The two contexts are identical at the Q/O marginal interface. Any consumer restricted to that interface has balanced-context value at most5/8; a joint-aware or direct-task-success oracle attains3/4.

## Learning experiment

Matched width-6 tanh predictors receive only context and action. The context input column starts exactly at zero and remains trainable. Formal seeds300–307, deterministic full-batch SGD, 10,000 steps, lr0.2.

Three proper objectives:
1. marginal Q/O Bernoulli prediction;
2. joint four-class (Q,O) prediction;
3. direct task-success S prediction.

The installed controller has no hidden/context bypass. The joint head supplies 1-P(00); the task head supplies S directly. A concrete marginal consumer uses only its two output probabilities. Action1 cost is1/4.

## Results

All24 formal runs pass the frozen assertions.

Marginal, 8/8:
- Q/O probability error <=2.78e-16;
- initial context gradient 2.62e-18..8.50e-18;
- final context-path norm 3.82e-16..2.40e-15;
- cannot distinguish A/B at the installed interface;
- balanced true task value5/8.

Joint, 8/8:
- probability error <=5.12e-4;
- final context-path norm2.946..3.047;
- all choose A:action1 and B:action0;
- true value3/4.

Direct task-success, 8/8:
- probability error <=4.94e-4;
- final context-path norm2.144..2.363;
- all choose A:action1 and B:action0;
- true value3/4.

Installed-use check: after training, setting only the learned context input column back to zero makes every joint/task run fall from3/4 to5/8. This is a finite software causal-use witness.

## Pilot failure

An exploratory Adam run amplified a ~1e-18 floating symmetry residual and produced a small spurious context path (~0.027) under the marginal objective. The output remained almost context invariant. Adam was rejected before formal confirmation; fresh seeds300–307 and plain SGD were used. A separate notebook helper unpacking error occurred before formal execution and produced no scientific output.

## Relation to official R97

The official R97 asks whether reward-ancestry path structure is recovered by flexible policies and finds strong off-support underspecification. R97D concerns an earlier interface question: whether the predictor output itself contains the reward-relevant dependence distinction.

They are compatible:
- R97D: the target family determines whether dependence-sensitive consequence organization is learned.
- R97: even when training support distinguishes a declared path family, a flexible policy can fit training while extrapolating the wrong causal path off support.

Together they imply that continuation-control inference needs both an adequate reward-relevant consequence interface and intervention-stable policy identification.

## UCT scope

Q/O are evaluator-defined virtual roles, not the actual future existence of the Python process. U1 does not make prediction sophistication an experience gate. Under C1, a genuinely acquired constitutive relation in an actual token/common complete K can conditionally correspond to a complete experiential-type change, but the task-value gap5/8 to3/4 is not phenomenal magnitude.

R97D is still task-only instrumental control. It does not identify direct Q preference; R96 task-path blocking remains required. Negative valence still requires R89; fear remains unmeasured.

## Payload preservation

The exact execution occurred before the concurrent official R97 appeared, so the immutable payload internally says round R97. It is preserved under R97D_PreReconciliation_* names rather than silently rewriting scientific output.

The full protocol-declared checkpoint payload is split into nine base64-text parts solely to avoid connector truncation. Concatenating parts reproduces the original checkpoint payload exactly.

Original raw payload SHA256:
- Results JSON: d93d3d473702b3bbaaee07cf4e331b404eae35f2f07ab015024316c78ffa7674
- Checkpoints JSON: afaf4a4287109ea6fddccb963bf9d07574a0cf389ee00ff2a8fa4057f1b215fd
- checkpoint base64 text: 5c46e28e6c85c5a085320ef466a4b3ab8a64452db7e6607edba0376183a1c690

## Next implication

Official R97's proposed R98 remains the correct next numbered round: add minimal direct intervention supervision to the generic MLP and test on a separate held-out intervention-amplitude/context family. R97D adds one requirement: the learned policy should consume a reward-relevant consequence representation, not merely separately calibrated marginals.
