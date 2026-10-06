# R119 — T2 intervention-preserving support-correspondence certificate

Hongju Liu / UCT research. 2026-10-06.

R110 introduced three levels of cross-substrate evidence:

- T1 — functional dissociation similarity;
- T2 — intervention-preserving mechanism correspondence;
- T3 — constitutive organizational homology.

R117/R118 exposed the need to make T2 precise enough that biological and artificial data can be inserted into the same test without:
- mistaking coordinate/unit changes for mechanism changes;
- or mistaking matched baseline behavior for matched mechanism.

R119 provides that certificate.

## 1. Selected support mechanism

For a capability T, define a selected support mechanism:

    M = (X, Z, U, I, Y, tau, N)

where:

- X — externally grounded input/history domain;
- Z — selected internal/support state;
- U — transition/update relation;
- I — declared intervention family and physical/causal ports;
- Y — downstream causally relevant output law;
- tau — temporal alignment/horizon;
- N — nuisance/background conditions over which the claim is intended to hold.

This is not the whole complete K.

A T2 claim concerns a selected mechanism.

## 2. Candidate correspondence

Between biological mechanism M_A and artificial mechanism M_B specify in advance:

    phi_X : X_A -> X_B
    phi_Z : Z_A -> Z_B
    phi_I : I_A -> I_B
    phi_Y : Y_A -> Y_B
    phi_tau : tau_A -> tau_B.

The maps must be grounded by experimental meaning and actual ports.

They must not be chosen solely because they maximize post-hoc geometric similarity.

## 3. T2 certificate components

A T2 certificate over domain D and nuisance set N should report a **vector**, not one averaged score.

### C0 — grounding consistency
Matched x values must refer to the same declared external/task relation.

For evidence accumulation:
the grounded object can be cumulative click/evidence history, not a latent embedding label.

### C1 — baseline behavioral correspondence

For matched x and nuisance n:

    d_Y(
      phi_Y[P_A(Y|x,n)],
      P_B(Y|phi_X(x),n)
    ) <= epsilon_base.

This is necessary but weak.

### C2 — transition commutation

For matched states and inputs:

    d_Z(
      phi_Z[U_A(z,x)],
      U_B(phi_Z(z),phi_X(x))
    ) <= epsilon_update.

This asks whether the selected support state evolves correspondingly.

### C3 — intervention transport

For matched intervention i:

    d_Y(
      phi_Y[P_A(Y | x, do(i), n)],
      P_B(Y | phi_X(x), do(phi_I(i)), n)
    ) <= epsilon_int.

This is the core T2 criterion.

An intervention correspondence that ignores coordinate/port transformations is invalid.

### C4 — temporal correspondence

The interventions must play corresponding temporal roles.

Examples:
- first-half perturbation ↔ first-half perturbation;
- memory-delay reset ↔ memory-delay reset;
- not simply same wall-clock number.

### C5 — nuisance/background stability

The above bounds should be checked across declared nuisance conditions:
- task difficulty;
- initial state;
- resource condition;
- side/laterality;
- session/subject/model seed where relevant.

### C6 — anti-triviality / mapping discipline

The correspondence should be:
- predeclared or independently motivated;
- low-complexity relative to the mechanism;
- tied to actual parts/ports;
- tested against plausible negative-control mappings.

An arbitrarily flexible learned alignment can make mechanism claims vacuous.

## 4. Why use a certificate vector rather than one scalar

A single average score can hide failure.

For example:
- baseline behavior may match perfectly;
- intervention response may be completely wrong.

Or:
- average intervention error may be low;
- one critical temporal window may fail.

Therefore report:

    C_T2 =
    (
      epsilon_base,
      epsilon_update,
      epsilon_int,
      temporal failures,
      nuisance failures,
      mapping assumptions
    ).

Do not collapse this into a "mechanism similarity score" unless the downstream use justifies the aggregation.

## 5. Exact positive control — coordinate-scaled accumulators

System A:

    z_{t+1} = z_t + e_t
    P(Y=1) = sigmoid(z_T).

System B:

    w_{t+1} = w_t + 2e_t
    P(Y=1) = sigmoid(w_T/2).

State mapping:

    phi_Z(w)=w/2.

Input grounding is identical.

Matched state intervention:

    do(z=c)
      <->
    do(w=2c).

Across all 16 length-4 evidence sequences e_t in {-1,+1}:

    baseline maximum output-probability error = 0.

Transition commutation:

    maximum state error after mapping = 0.

Across 80 matched interventions:
16 sequences × 5 clamp values,

    matched intervention maximum output-probability error = 0.

Thus raw coordinate scale can differ while the selected causal mechanism is exactly corresponding.

## 6. Why physical/intervention port transport matters

Apply the same **numeric** clamp to both systems instead:

    do(z=c)
    do(w=c)

rather than do(w=2c).

Now:

    maximum output-probability mismatch = 0.122459
    mean mismatch = 0.056535.

The mechanism did not change.

The experimenter used the wrong correspondence between intervention ports.

This finite witness directly reinforces Paper A/R77's port-aware requirement:

> numerical equality of interventions is not physical/causal equivalence.

Cross-substrate biology–AI work must match intervention meaning, not raw units.

## 7. Exact negative control — baseline equivalence without T2

Reuse R108:

System A:
    direct XOR.

System B:
    decomposed OR/AND/NOT XOR.

Natural truth tables are exactly identical.

But internal clamp signatures differ.

Direct XOR internal clamp family produces only:

    0000
    1111.

Decomposed XOR contains additional signatures:

    0111
    1110.

Therefore baseline behavior correspondence passes, but a complete matched internal intervention family cannot preserve the declared parts/ports.

This is a clean T2 rejection.

## 8. T2 is still weaker than T3

Even a perfect selected-mechanism T2 certificate does not prove whole-system constitutive homology.

Two organisms/agents may share one intervention-preserving accumulator mechanism while differing in:
- memory;
- self-model;
- valence;
- report;
- body/scaffold;
- physical substrate;
- other coupled dynamics.

Thus T2 supports a **selected support correspondence**.

T3 requires a much richer constitutive mapping in the common K signature.

Under UCT:
- T2 can motivate a selected experiential-organization hypothesis;
- T3/G4 is the stronger basis for selected experiential-structure homology;
- complete experiential identity requires complete organizational correspondence.

## 9. R117 evidence-accumulation instantiation

For the selected rat/AI accumulation study:

### X
Grounded cumulative click/evidence histories.

### Z
Biology:
selected FOF/ADS population evidence state.

AI:
explicit accumulator state z_t.

### I
Biology:
whole/first-half/second-half neural/pathway perturbations.

AI:
state reset, evidence pulse, and future pathway interventions.

### Y
Choice probability / psychometric behavior.

### tau
Stimulus-relative evidence time.

### N
Difficulty, side, trial/session/subject/model condition.

Current status:

- C0: well defined.
- C1 AI: measured.
- C2 AI: exact by construction.
- C3 AI: measured.
- C1–C3 biology: source paper supports relevant relations, but independent raw-data certificate is incomplete.
- T2 final status: PARTIAL / PROMISING.

This is a much more precise status than "rat and AI both accumulate evidence."

## 10. Cross-substrate falsification criteria

A proposed T2 correspondence should fail if any of the following occurs:

1. matched baseline behavior but intervention signatures disagree beyond epsilon_int;
2. support-state mapping fails transition commutation;
3. mapping works only under one difficulty/subject but not declared N;
4. temporal intervention correspondence is inconsistent;
5. correspondence requires arbitrary post-hoc nonlinear remapping with no part/port justification;
6. a negative-control mapping performs equally well;
7. claimed support state is decodable but its intervention does not affect the selected capability.

This makes T2 falsifiable.

## 11. Relation to causal abstraction

Causal abstraction is strong prior art for intervention-preserving mappings.

R119 does not claim that concept as new.

Its role in the UCT program is more specific:
- bind the abstraction to R107 Tier-0 physical/causal ports;
- bind state variables to R113 verified capability support;
- bind content comparison to R115 grounding;
- keep E latent until constitutive interpretation.

This prevents cross-substrate experiential claims from resting on a free-form alignment.

## 12. Next step

R120 should use R119 to define the first **experience–intelligence bridge theorem schema**.

The desired statement is not:

    intelligence level J -> consciousness level E.

Instead:

    capability T
      -> verified support family R_T
      -> T2/T3 cross-substrate relation status
      -> conditional selected experiential-organization statement.

The theorem schema should specify:
- what follows inside one system;
- what transfers between systems;
- what fails under multiple realization;
- what remains unknowable without T3/G4.

This would consolidate R106–R119 into a root-level answer to the user's original question.

## 13. Status

R119 turns T2 from a verbal level into an explicit intervention-sensitive, coordinate-aware certificate.

The exact mathematics is elementary and causal-abstraction ideas have strong prior art.

The project-specific value is to make the cross-substrate UCT bridge auditable and falsifiable.
