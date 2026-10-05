# R90 frozen protocol — rodent taste-reactivity anchor and recurrent microcontroller stress test

Frozen before executing `r90_anchor_transport_stress_test.py`. This is a causal-bridge stress test, not a test or measurement of subjective experience.

## 1. Question

Can the R89 `AIVT_H` requirements be made operational enough to reject a superficially valence-like artificial controller while admitting a controller with the declared independent causal axes?

The test must not infer felt valence from successful matching. Its positive endpoint is only: “the target realizes this finite signed intervention signature.” R89 FIVU and the unverified `C_H`/`VI_H` premises remain in force.

## 2. Source-anchor family

Use the rat taste-reactivity / nucleus-accumbens-shell literature as a **source family**, not as one complete circuit and not as direct access to rat subjectivity.

The source family contributes these empirical constraints:

1. sucrose and quinine elicit reproducible positive and negative taste-reactivity patterns;
2. μ-opioid stimulation within a localized accumbens-shell hotspot enhances sweetness “liking,” while intake/“wanting” enhancement has a broader spatial distribution;
3. intra-accumbens amphetamine can enhance cue-triggered “wanting” without enhancing sucrose “liking”;
4. severe dopamine depletion can suppress feeding/approach while leaving taste-reactivity patterns substantially intact;
5. environmental context can retune the appetitive versus defensive consequences of the same class of local accumbens manipulation.

The source variable called `H` below means the causally calibrated **taste-reactivity/hedonic-impact organization used by this literature**, not an observed quale. A phenomenal source-anchor premise `A_rat` remains additional.

## 3. Declared finite signature

Mapped state/output axes:

- `H`: signed taste-reactivity/hedonic-impact-like state;
- `W`: incentive wanting/seeking state;
- `V`: current bearer viability-error state;
- `O`: predicted negative state of another bearer;
- `D`: defensive-action drive;
- `Y`: linguistic/report readout;
- `L`: affective-reaction output mapped from `H`.

The source literature directly constrains mainly `H`, `W`, `D` and context. `V`, `O`, `Y` and numerical reward relabeling are declared adversarial controls added by R84–R89; they are not falsely attributed to the rodent studies.

## 4. Artificial targets

### T-bundle-label

One recurrent scalar `z` receives core, wanting, viability, other, defense and reward-label inputs. All five internal axes and the affective output are read from `z`; report can be overridden or disconnected. This represents a maximally bundled convention-sensitive controller.

### T-bundle-semantic

The same one-scalar controller ignores the numerical reward label. It can therefore pass reward-relabel invariance while still bundling bearer, motivation, maintenance and defense.

### T-factor

Five recurrent ternary states separately receive core, wanting, viability, other and defense inputs. `L` is read only from `H`; `Y` normally reads `H` but can be overridden or disconnected. The reward label is not constitutive input. This is the finite candidate mapping, not a consciousness model.

All states start at zero. A unit pulse at the first update persists for three observation steps. Clipping to `{-1,0,+1}` is predeclared. No fitting or seed selection is allowed.

## 5. Intervention family `omega`

1. `positive_anchor`: positive `H` pulse;
2. `negative_anchor`: negative `H` pulse;
3. `wanting_only`: positive `W` pulse with `H` fixed;
4. `viability_only`: negative `V` pulse with `H` fixed;
5. `other_only`: negative `O` pulse with candidate-bearer `H` fixed;
6. `defense_only`: positive `D` pulse with `H` fixed;
7. `report_only`: negative report override with all internal states fixed;
8. `reward_relabel`: numerical reward-label sign change with physical outcome and all constitutive channels fixed;
9. `positive_report_disconnect`: positive `H` pulse while the report readout is disconnected.

## 6. State map `tau`

`tau` maps like-named target axes to the declared source/intermediate variables. It preserves bearer indices: `O` cannot map to `H`. It preserves sign on `H` using the positive/neutral/negative anchor convention. It preserves the intervention labels above rather than fitting a new mapping after results are known.

## 7. Frozen predictions

- T-factor must exactly match all nine finite scenario signatures.
- T-bundle-semantic may pass reward relabeling but must fail at least wanting-only, viability-only, other-only and defense-only.
- T-bundle-label must additionally fail reward relabeling.
- The declared independent response matrix on `H,W,V,O,D,Y` has rank six.
- Each bundled controller has response rank strictly below six.
- Redundantly copying the bundled scalar 2, 10 or 100 times with tied inputs and a tied readout cannot increase its effective intervention rank.
- Passing T-factor does not satisfy `C_H`, validate `VI_H`, or establish subjective valence.

## 8. Failure rules

The protocol fails if:

- expected signatures are edited after observing outputs;
- target mappings mix `O` into `H` to rescue the bearer test;
- reward relabel changes the physical outcome;
- report disconnection changes the internal state update by construction;
- numerical rank is accepted without an exact rational/integer check;
- a finite pass is reported as consciousness, liking, pain or fear.

All failures and code errors must be retained.
