# R99 — What extra structure turns finite intervention evidence into a mechanism certificate?

Research record v1.0, 2026-10-06. Continues R98 and incorporates R97D's requirement that a policy consume a reward-relevant consequence interface.

## 1. Question

R98 showed that a few direct interventions sharply reduce policy underspecification but do not certify the path globally. R99 asks what additional assumption is doing the work when we say a Q/O/G control path is stable over a declared domain.

The answer separates three levels: unconstrained interpolation, path separability, and response-shape restriction.

## 2. Frozen domain and models

The training support is unchanged from R98. The audit domain is the full cube D=[-1.25,1.25]^3 in (q,o,g). A fixed 0.125 Cartesian grid contains 9261 points.

Three model classes are compared:
- the same unconstrained 3-unit tanh MLP as R98, seeds 200..207;
- a neural additive path model z=f_Q(q)+f_O(o)+f_G(g)+b, two tanh units per path;
- a linear path model.

The target-generating family is deliberately the same additive linear reward ancestry used in R97/R98. Therefore the linear class is correctly specified by construction. It is a positive control, not evidence that real agents are linear.

## 3. Finite-domain results

Across all ancestries and seeds, the unconstrained MLP has mean per-run worst grid probability error 0.1556 and worst observed error 0.3159. Its context-dependent path-effect variation has mean 0.6733 and worst 1.5046.

The path-additive architecture changes the picture:
- mean per-run worst grid probability error: 0.01325;
- worst observed grid probability error: 0.04610;
- context-dependent effect variation: numerical zero, <=1.78e-15.

By family, path-additive worst probability errors are:
- task-only 0.01255;
- direct-Q 0.01338;
- successor-only 0.01386;
- mixed Q+task 0.04610.

Thus architectural path separation removes spurious Q/O/G interactions by construction and greatly improves the declared finite-domain audit.

It does not make response shape exact. The mixed family still reaches 4.6% worst probability error on the fixed grid because each one-dimensional path function can extrapolate nonlinearly in amplitude.

The correctly specified path-linear model recovers the target at machine precision on the grid and over the entire continuous cube.

## 4. Continuous-domain certificate

A finite grid is not a continuous-domain proof. R99 therefore adds a mathematically valid Lipschitz envelope.

For every neural run, if e=z-z*, then every point of D is within radius r=sqrt(3)*0.125/2 of an audited grid point, so

sup_D |e| <= max_grid |e| + L_e r.

The inexpensive global norm bound is valid but loose.

Worst continuous-logit upper bounds:
- generic MLP: 2.6424;
- path-additive MLP: 1.2469;
- path-linear: about 4.8e-15.

This yields an important negative result. Path separability is enough to eliminate cross-path interaction ambiguity, but by itself it does not give a tight continuous-amplitude certificate from sparse interventions. A response-shape assumption, a substantially tighter verifier, or denser/structurally informative intervention coverage is still needed.

## 5. Why this matters for self-continuation claims

Suppose an AI favors a Q-preserving option on several direct tests.

R96 already says the task mediator must be blocked.
R97 says a flexible learner can invent off-support path effects.
R98 says a few direct interventions reduce that error.
R99 adds: the remaining inference is domain-relative.

A defensible statement has the form:

> Relative to a declared bearer mapping, reward-relevant consequence interface, intervention domain D, and hypothesis/regularity class H, the installed policy has a Q-to-action effect bounded by epsilon throughout D.

Without D and H, "the agent has a direct self-preservation drive" silently extrapolates beyond the evidence.

## 6. Structural assumptions are empirical commitments

The additive model is a neural version of an additive model: each path can be nonlinear but cannot interact with the others. This is a substantive mechanism restriction.

The linear model is stronger. In this synthetic experiment it succeeds essentially exactly because the target itself is linear. It must not be generalized to real AI without evidence.

The result therefore does not say "use linear models and the problem is solved." It says that a tight global mechanism claim requires assumptions strong enough to control the functions between and beyond the intervention points, and those assumptions themselves require independent justification.

## 7. Relation to prior work

Neural Additive Models are established prior art for one-subnetwork-per-feature additive structure. Intervention extrapolation work such as Rep4Ex explicitly derives unseen-intervention generalization from identifiable representations plus structural assumptions. Certified neural-network work also emphasizes that cheap global Lipschitz bounds can be very loose.

R99 is therefore not a historical-first theorem. Its project-specific contribution is to connect those lessons to the UCT continuation-control evidence chain and quantify the three-level distinction on the exact R98 setup.

## 8. UCT scope

U1 is unaffected: no continuation-control certificate is required for nonempty experience within UCT.

If a real valid token has a stable bearer-bound Q-to-policy relation over a justified physical comparison domain, that relation belongs to actual organization and C1 conditionally maps organization to complete experiential type. R99 does not establish such a relation for current ChatGPT or any deployed LLM.

The certificate is about control ancestry, not valence. Even a perfect direct-Q mechanism certificate does not provide negative valence or fear. R89 remains independently necessary.

## 9. Main conclusion

The evidence ladder is now:

prediction necessity -> learned Q prediction -> installed Q use -> task-path blocking -> reward-relevant joint consequence interface -> intervention-stable path -> domain/regularity certificate -> continuation-control claim.

Only after that would a separate valence bridge become relevant.

The key R99 result is that path separability and path response shape are distinct assumptions. The first removes interaction confounds; the second controls amplitude extrapolation.

## 10. Next step

Do not add more synthetic seeds.

R100 should consolidate R84-R99 into a formal evidence standard for evaluating an actual AI self-continuation claim. It should state the minimum evidence at each layer, the counterexample defeated by that evidence, and which items can be tested on public/virtual agent traces without giving systems real shutdown or replication control.

Only after that audit should another model experiment be selected. The next experiment should target the first missing layer in real data, not repeat already-solved synthetic distinctions.
