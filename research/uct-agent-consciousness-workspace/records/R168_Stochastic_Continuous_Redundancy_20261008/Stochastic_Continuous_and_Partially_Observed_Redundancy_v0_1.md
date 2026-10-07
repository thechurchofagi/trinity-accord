# Stochastic, Continuous, and Partially Observed Redundancy

## Sharp closure-relative bounds for effects that a finite intervention view can miss

**Round:** R168  
**Status:** exact mathematical extension and countermodels; no apparatus, participant data, ethics approval, empirical regularity certificate, C1 proof, or `B_min` validation  
**Scope:** one declared operational mediator relation, its admissible interventions, one pre-compensation time slice, and an explicitly bounded context space

## 1. Question and result

R167 proved an exact finite Boolean criterion: a candidate mediator contributes if changing it changes a declared consumer in at least one backup context. It left open stochastic outputs, continuous contexts, measurement uncertainty, and contexts visible only through a coarse interface.

R168 supplies three bounded answers.

1. Replace Boolean difference by a declared integral probability metric between interventional output laws. This preserves the distinction between contribution in some context and indispensability in every context.
2. If the contextual effect is certified `L`-Lipschitz and tested contexts have valid upper bounds, the sharp pointwise maximum compatible with those facts is the metric envelope

   \[
   E(z)=\min\!\left\{M,\inf_i\bigl(U_i+L d(z,s_i)\bigr)\right\}.
   \]

   Thus `sup_z E(z)` is a quantitative worst-case bound on undetected effect amplitude relative to the declared context space, metric, regularity constant, intervention fidelity, and upper bounds.
3. Partial observation gives no nontrivial bound by itself. A two-point hidden fiber can agree on every observed label and tested law while carrying effect zero in one compatible model and the maximum `M` in another. A useful partial-view bound requires a certified lift/section and a hidden-fiber deviation bound. Random context sampling can instead bound the *measure* of affected contexts, but not their maximum effect or nonexistence.

These results refine R167's `UNRESOLVED` state. They do not turn statistical non-detection into absence of installed use, and never into absence of experience.

## 2. Typed stochastic contextual effect

Fix one R167 episode subinterval before compensation. Let:

- `(Z,d)` be the declared metric space of physically admissible backup contexts;
- `K_0` be the declared set of mediator interventions that are safe, realizable, and fidelity-checked;
- `Q_{k,z}` be the interventional law of a declared consumer `U` under `do(k),do(z)` on the same bearer lineage;
- `F` be a fixed symmetric discriminator class of bounded measurable consumer tests.

Define the integral probability metric

\[
d_{\mathcal F}(P,Q)=\sup_{f\in\mathcal F}
\left|\mathbb E_P f(U)-\mathbb E_Q f(U)\right|,
\]

and the contextual mediator effect

\[
e(z)=\sup_{k,k'\in K_0}d_{\mathcal F}(Q_{k,z},Q_{k',z})\in[0,M].
\]

`F` is part of the claim. All bounded indicator tests recover total-variation-style discrimination up to convention; bounded 1-Lipschitz tests give a Wasserstein-style observable geometry when the required moments and metric are fixed. A weak `F` can miss a real distributional change; changing `F` after seeing results changes the claim.

Relative to `K_0`, `Z`, and `F`, the mediator has contextual distributional use iff `exists z: e(z)>0`. It is contextually indispensable only if a predeclared positive lower condition holds for every admissible `z`. Neither statement identifies a hidden neural state or familiar felt mineness.

## 3. Sharp metric-envelope theorem

Let tested actual contexts be `S={s_1,...,s_n}`. Suppose:

1. the true contextual effect satisfies `0 <= e(z) <= M`;
2. `e` is `L`-Lipschitz on the declared `(Z,d)`;
3. for every tested context, a valid bound `e(s_i) <= U_i` has been obtained under the same intervention, consumer, metric, time, and fidelity contract.

Define

\[
E(z)=\min\left\{M,\inf_i[U_i+L d(z,s_i)]\right\}.
\]

**Theorem R168-A (pointwise sharp envelope).** Every compatible effect function obeys `e(z)<=E(z)` for every `z`. Conversely, `E` itself is bounded, `L`-Lipschitz, satisfies `E(s_i)<=U_i`, and is therefore compatible with exactly these stated constraints. Hence no uniformly smaller pointwise upper bound follows without another premise.

**Proof.** Lipschitzness gives `e(z)<=e(s_i)+L d(z,s_i)<=U_i+L d(z,s_i)` for every `i`; take the infimum and cap by `M`. Each cone `U_i+Ld(z,s_i)` is `L`-Lipschitz, the infimum of same-constant cones is `L`-Lipschitz, and capping by a constant preserves that property. At a tested point, the term with `i` gives `E(s_i)<=U_i`. Therefore `E` is an admissible extremal function. QED.

The global certificate is

\[
R_{\mathrm{amp}}=\sup_{z\in Z}E(z).
\]

With a common upper bound `U_i<=eta` and fill distance

\[
h(S,Z)=\sup_{z\in Z}\inf_{s\in S}d(z,s),
\]

we obtain the simpler sharp worst-case bound

\[
\sup_z e(z)\le \min\{M,\eta+Lh\}.
\]

Dense testing is informative only relative to a justified metric and regularity constant. If `L` is unknown or the metric does not track physical route variation, `h` is not a scientific closure certificate.

## 4. Valid lower evidence and bounded refutation

Suppose a tested context also has a valid lower bound `L_i<=e(s_i)` and the predeclared meaningful-effect threshold is `tau`.

- If some `L_i>tau`, the candidate has a certified contextual effect at that actual tested context, subject to R166/R167 route and fidelity premises.
- If `R_amp<=tau`, effects above `tau` are refuted only relative to the declared `Z,d,K_0,F,L,M,S` and bound-validity premises.
- If neither holds, the result is unresolved.

The first clause is local positive evidence. The second is a closure-relative amplitude statement. It is not a proof that `e=0`, a proof of no other physical route, or evidence of no experience.

## 5. Partial-observation obstruction

Let an interface expose `x=q(z)` rather than the full actual context. Take hidden contexts `Z={a,b}` with `q(a)=q(b)=x`. Test only actual context `a`, obtaining `e(a)=0`. Two compatible models are:

\[
e_0(a)=e_0(b)=0,
\qquad
e_1(a)=0,\ e_1(b)=M.
\]

They have the same observed label, tested intervention law, and reported bound. Yet their maximum hidden effect differs by `M`. Therefore a coarse observed label and finite test alone yield no nontrivial hidden-fiber amplitude bound.

### A sufficient lift certificate

Let `q:Z->X` be the observed map. Suppose there is a declared section `r:X->Z`, constants `delta,C`, and a tested observed set `T={x_i}` such that:

\[
d_Z(z,r(q(z)))\le\delta,
\qquad
d_Z(r(x),r(x'))\le C d_X(x,x'),
\]

and `T` has observed fill distance `h_X`. Testing `s_i=r(x_i)` then gives an actual-context fill radius at most

\[
h_Z\le\delta+C h_X.
\]

Consequently, with common tested upper bound `eta`,

\[
\sup_z e(z)\le\min\{M,\eta+L(\delta+C h_X)\}.
\]

`delta` is the hidden-fiber penalty. Setting it to zero merely because two states share an observed label is an invalid substitution.

## 6. Random-context mass bound is not an amplitude bound

Metric coverage may be impractical. A different design samples contexts independently from a predeclared measure `mu`. Let

\[
A_\tau=\{z:e(z)>\tau\},\qquad p=\mu(A_\tau).
\]

If every sampled member of `A_tau` is detected with probability at least `s_min`, independently across `n` trials, then the probability of no detection is at most

\[
(1-s_{\min}p)^n.
\]

After no detections, a one-sided confidence statement may bound affected mass by

\[
p\le \min\left\{1,\frac{1-\alpha^{1/n}}{s_{\min}}\right\}
\]

at level `1-alpha`, under exactly those sampling and sensitivity assumptions.

This does not bound `sup_z e(z)`: an arbitrarily large effect can remain on a sufficiently rare or zero-`mu` context. Conversely, a large affected mass can have amplitude only infinitesimally above `tau`. Amplitude and prevalence are distinct objects and must not be merged.

## 7. R168 triage

For one named operational mediator candidate, apply this order.

1. **INVALID_PROTOCOL** if R167 token lineage, safety, intervention delivery, route audit, consumer metric, bound validity, timing, or declared regularity checks fail.
2. **CONTEXTUAL_USE_SUPPORTED** if a valid tested lower bound exceeds `tau` and the live-route audit passes.
3. **AMPLITUDE_REFUTED_RELATIVE_TO_ENVELOPE** if the sharp envelope maximum is at most `tau` and the declared actual/partial context coverage certificate is valid.
4. **AFFECTED_MASS_BOUNDED_ONLY** if random-context assumptions yield a valid bound on `mu(A_tau)` but the amplitude envelope does not refute effects above `tau`.
5. **UNRESOLVED** otherwise.

No status is a basal-experience status. A failure to establish contextual use does not negate C1 for any admitted actual organization, and a successful operational result still does not supply `B_min`.

## 8. Relation to R166–R167

R168 refines only the continuous/stochastic evidence object inside W4–W5. W1 same-token actuality, W2 independent anchor grounding, W3 actual live binding/use, and W6 bounded status discipline remain unchanged. The operational architecture must physically realize the random variables and interventions; an abstract kernel or fitted latent model cannot replace the realization map.

If every R166/R167 premise holds and R168 returns contextual support, the same declared participant–device relation receives stronger closure-relative evidence. R159 C1 transport remains a separate same-instance conditional step. No new rule runs from an envelope, probability, or test result to C1, familiar mineness, numerical identity, unique ownership, or the existence of experience.

## 9. Four preserved thought-experiment families

1. **Ancestor/formation.** A rare context may expose a primitive mediator before redundancy becomes common; low prevalence does not make the actual context unreal or make experience appear only after detection.
2. **Abacus/calculator.** A live register influences output only for a narrow operand region. Random testing can bound how common that region is; only metric/structural coverage can bound the largest missed effect.
3. **Human-realized agent.** The participant–device process can contain hidden device and bodily contexts under one observed task label. A section/fiber certificate is required; task-label equality does not collapse those nested actual states.
4. **Copy/swap/memory.** Two copied interfaces can emit identical sampled laws while an untested hidden route differs maximally. Matching memories and reports do not determine the hidden intervention fiber.

## 10. Direction and novelty audit

The IPM definition, Lipschitz extension/envelope reasoning, metric fill distance, and binomial no-hit calculation are established mathematics. R168's contribution is their explicit typed use to close R167-G7 and sharpen R167-G3 inside the UCT application map; no historical mathematical novelty is claimed.

The result keeps complete organization, finite view, stochastic abstract kernel, actual installation, partial observation, experiential counterpart, and language report distinct. Code verifies finite instances and countermodels only. It does not certify the physical metric, `L`, `delta`, sensitivity, causal exclusion, theoretical truth, or global map completeness.

## 11. Next exact question

What physically grounded metric and regularity witness can be justified for the actual controller/body-frame architecture, rather than merely assumed, and can route-level compositional structure provide a tighter closure certificate than a global Lipschitz constant?
