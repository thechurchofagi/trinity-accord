# Token-Coherent Route-Stitching Contract

## 1. Target and correction

A4R correctly required three actual, bearer-bound links and closure of three bypasses. Its Boolean certificate, however, represented only local link actuality and bypass status. It did not separately encode whether adjacent links share the same numerically particular sample occurrence and the same numerically particular command occurrence. This file makes that type/occurrence obligation explicit.

The correction is narrow. It does not defeat A4R's non-identification result. It narrows A4R's conditional sufficiency claim: the three-link conjunction is sufficient only when shared occurrence variables are part of the link definitions, or when explicit stitching predicates are also satisfied.

## 2. Fixed domain

Fix one actual bearer process (P), interval (I=[t_0,t_3]), complete signature (K), declared physical boundary (B), clock/order relation (\prec_I), ports, and lineage policy. Every predicate below is evaluated for this same tuple. An abstract graph or equal-valued trace is not thereby an actual installation.

Let:

- (a): physical anchor occurrence;
- (x_s): sample occurrence produced by the sampler;
- (x_c): sample occurrence consumed by the controller;
- (u_c): command occurrence produced by the controller;
- (u_w): command occurrence consumed by the writer;
- (e): plant-write occurrence.

Define local actual links:

[
L_s(a,x_s),qquad L_c(x_c,u_c),qquad L_w(u_w,e).
]

Define (SameOcc_{P,I,K,B}(z,z')) as numerical identity of one actual occurrence under the fixed physical boundary, ports, order and lineage policy. It is stronger than equality of value, bit pattern, label, memory address in an abstract model, hash, or structural type.

Define the two stitches:

[
X_{sc}:=SameOcc(x_s,x_c)land x_sprec_I x_cland PortBind_{sc}(x_s,x_c),
]
[
X_{cw}:=SameOcc(u_c,u_w)land u_cprec_I u_wland PortBind_{cw}(u_c,u_w).
]

Then:

[
ActualCoherentRoute(a,e):=L_sland X_{sc}land L_cland X_{cw}land L_w.
]

If the local-link predicates are defined with literally shared occurrence variables—(L_s(a,x)land L_c(x,u)land L_w(u,e))—the two (X) obligations are type/definition checks, not new empirical laws. If the link predicates are established independently, the stitches require evidence.

## 3. Stable claims

### A4S-C1 — TOKEN-STITCHING-NECESSITY

- **Type:** CORRECTION / PROPOSED_NEW_RESULT.
- **Claim:** In a model where the three local links quantify their boundary occurrences independently, (L_sland L_cland L_w) does not entail one actual end-to-end route. Cross-link occurrence stitching or syntactically shared occurrence variables is additionally required.
- **Domain:** the fixed (P,I,K,B) above.
- **Premises:** independent link-boundary variables; token identity distinguished from type/value equality (UCT I P6).
- **Proof:** A4S-C2 supplies finite countermodels.
- **Status:** proved for the declared Boolean abstraction; disabled as a general physical premise.
- **Cannot infer:** that every physical implementation fails, that token identity alone yields agency experience, or that C1 is empirically true.

### A4S-C2 — THREE-LINK-TRUTH-NONCOMPOSITION

- **Type:** FINITE_COUNTEREXAMPLE.
- **Claim:** Among the four worlds with (L_s=L_c=L_w=1), three lack a coherent route because at least one stitch is false.
- **Proof:** exhaustive enumeration of the five Boolean coordinates gives 32 worlds, four local-three worlds, and one coherent-route world.
- **Counterexamples:** sample fork ((X_{sc},X_{cw})=(0,1)); command fork ((1,0)); double fork ((0,0)).
- **Status:** exact in the declared model; not an exhaustive model of physical alternatives.

### A4S-C3 — STITCHED-SUFFICIENCY-IN-DECLARED-MODEL

- **Type:** CONDITIONAL_RESULT.
- **Claim:** In the declared five-predicate abstraction, (L_sland X_{sc}land L_cland X_{cw}land L_w) is sufficient for (ActualCoherentRoute).
- **Proof:** definitional expansion.
- **Status:** exact but model-relative; actual satisfaction is unverified.

### A4S-C4 — VALUE-EQUALITY-NONIDENTITY

- **Type:** INHERITED_APPLICATION.
- **Claim:** Equal sample/command values do not entail numerical occurrence identity.
- **Source:** UCT I v1.2 P6's token/type distinction, applied to boundary events.
- **Status:** inherited distinction; application is new to the A4R route audit.

### A4S-C5 — C1-CONDITIONAL-INTERPRETATION

- **Type:** UCT-CONDITIONAL-INTERPRETATION.
- **Claim:** If the stitched route belongs to one admitted actual (P) in complete (K), C1 maps that actual organization into (\Phi_K(P)). This does not establish the independent phenomenal bridge (H_{cf}), a feeling of agency/ownership, a conceptual self, a report, fear, or C1's empirical truth.
- **Status:** conditional; (H_{cf}) remains OPEN.

## 4. Thought experiments

1. **Copy/swap/memory family — sample fork.** A sampler emits occurrence (x_s). A copier produces value-equal (x_c) and the controller consumes the copy while the original is diverted. All local devices operate; (X_{sc}=0). Fixed: bearer shell, values, timing envelope. Varied: numerical sample occurrence.
2. **Copy/swap/memory family — command fork.** The controller emits (u_c); a replay injector supplies value-equal (u_w) to the writer. (X_{cw}=0). Fixed: observable command value and plant write. Varied: command lineage.
3. **Abacus/calculator/human implementation.** One person reads a bead configuration while another independently reconstructs the same number for the next step. Equal arithmetic state does not itself make one physical computation route. This attacks value-level composition, not intelligence or experience.
4. **Ancestor/formation and nested-process family.** During formation of a larger agent, a sample link in one persisting sub-process and a write link in an overlapping sub-process may both be actual without one stitched route. This preserves nested/overlapping actual processes and avoids inventing a unique extra owner.

## 5. Explanatory payoff and limit

The positive bodily/action relation now has an explicit compositional shape: not merely local sensitivity and output, but one token-coherent actual route inside a declared bearer. That advances the organizational account of an action-related “for-this-bearer” relation. It remains a physical/structural candidate bridge. It is not a basal-experience gate and does not by itself identify the phenomenal character of “mine,” “I did it,” or any verbal report.
