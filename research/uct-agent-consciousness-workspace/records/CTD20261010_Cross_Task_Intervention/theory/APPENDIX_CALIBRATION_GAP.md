# Appendix: exact local calibration gaps under an unknown monotone measurement map

**Status:** prospective measurement lemma, with exhaustive finite checks. It is optional supporting theory for the cross-task intervention paper, not a second empirical result. No current bodily-familiarity measure or UCT-specific experience scale is validated by this appendix.

## A1. Why monotonicity is not a quantitative sensitivity guarantee

Suppose a verified mechanism change is hypothesized to change a selected scalar target from \(x\) to \(y>x\). Let \(h\) map that coordinate to the mean of a predeclared readout. Even if \(h\) is strictly increasing, \(h(y)-h(x)\) can be arbitrarily small. This remains true after calibrating the instrument at two points outside the target interval, or at only one point inside it. A large global dynamic range therefore does not by itself guarantee local sensitivity to the predicted change.

For example, on the ordered domain \(0,1,2,3,4,5,6\), let

\[
h_\eta=(0,\tfrac12-\eta,\tfrac12-\eta/2,\tfrac12,
\tfrac12+\eta/2,\tfrac12+\eta,1),\qquad0<\eta<\tfrac12.
\]

Every \(h_\eta\) is strictly increasing. All retain the exact calibrations \(h(0)=0\), \(h(3)=1/2\), \(h(6)=1\), but the change between target positions 1 and 5 is \(2\eta\to0\).

This is a specific local-sensitivity problem, distinct from the signed binary marker transport problem in project record R201. The general significance of a measurement map is established prior work, including Loftus (1978), state-trace analysis, and work on experiment-based calibration. No new general measurement principle is claimed.

## A2. Finite model and assumptions

Let \(h\) be nondecreasing on a finite ordered set containing the target values \(x,y\) and calibration positions \(a_1,\ldots,a_J\). Independent calibration supplies interval constraints

\[
h(a_j)\in[l_j,u_j].
\]

Assume these constraints are jointly feasible. Define the propagated lower and upper envelopes

\[
L(z)=\max_{j:a_j\leq z}l_j,\qquad
U(z)=\min_{j:a_j\geq z}u_j,
\]

with the usual extended-real conventions when no anchor is available on a side. Finite endpoint ranges may be added as boundary anchors when independently justified.

The *positions* of the calibration anchors relative to the target must be independently defended. In psychophysics, physical stimulus intensity is observable, whereas the latent experiential intensity corresponding to that stimulus is a further interpretation. An instrument calibrated on stimulus values is not automatically calibrated on a putative bodily-familiarity coordinate. This lemma cannot supply its own target meaning, orientation, anchor order, or transport premise.

## A3. Sharp interval for a predicted contrast

### Theorem A1

For \(x<y\), the complete feasible interval of \(D=h(y)-h(x)\) is

\[
\boxed{
D\in\left[
\max\{0,L(y)-U(x)\},\;U(y)-L(x)
\right].}
\]

For \(x=y\), the contrast is identically zero. For \(x>y\), reverse and negate the interval. Infinite bounds are permitted if the available calibration gives no finite bound.

**Proof.** Monotonicity and the anchors imply

\[
L(x)\leq h(x)\leq U(x),\qquad
L(y)\leq h(y)\leq U(y),\qquad h(x)\leq h(y).
\]

These inequalities yield the displayed lower and upper contrast bounds. Conversely, adding any pair \((v_x,v_y)\) satisfying these three restrictions as exact new anchors preserves joint feasibility: each original anchor's lower bound remains below every later upper bound. A monotone extension is constructed by taking the running maximum of the lower bounds through the enlarged ordered set.

For the minimum, choose \(v_x=U(x)\) and \(v_y=\max\{U(x),L(y)\}\). Feasibility ensures \(U(x)\leq U(y)\) and \(L(y)\leq U(y)\). The resulting difference is exactly the displayed lower bound. For the maximum, choose \(v_x=L(x)\) and \(v_y=U(y)\). Convex combinations of feasible nondecreasing functions remain feasible and fill every intermediate contrast. Unbounded or nonattained extended endpoints are interpreted as suprema or infima. \(\square\)

If the anchor constraints admit at least one strictly increasing function, the strictly increasing functions are dense in the nondecreasing feasible set: mix any feasible nondecreasing function with an arbitrarily small positive weight on a strictly increasing feasible function. The same formulas therefore give the sharp infimum and supremum under strict monotonicity. An endpoint need not be attained by a strict function.

### Corollary A1: two internally placed separated anchors

An informative positive lower contrast bound exists precisely when

\[
L(y)>U(x).
\]

In a finite feasible anchor system this requires two anchor constraints with

\[
x\leq a_j<a_k\leq y,\qquad l_k>u_j.
\]

Conversely such a pair forces \(h(y)-h(x)\geq l_k-u_j>0\).

**Proof of necessity.** Choose anchors attaining \(L(y)=l_k\) and \(U(x)=u_j\). Their positions satisfy \(a_k\leq y\) and \(a_j\geq x\). If \(a_k\leq a_j\), monotone feasibility would require \(l_k\leq u_j\), a contradiction. Thus \(x\leq a_j<a_k\leq y\). \(\square\)

This is a minimum number of independently constrained calibration positions for a positive local lower bound *under only monotonicity*. A separately justified derivative lower bound, a parametric response law, or other structural information can change the requirement. Calling these two anchors an experimentally minimal design without specifying the available information would be too broad.

## A4. A sharp robustness threshold for a rescue contrast

Fix the main intervention stratum \(I\) and compare two rescue conditions \(R=0,1\) there. The readout map \(h_I\) may differ across main-intervention strata, but is assumed stable across the scored rescue comparison or to deviate only within an independently justified budget.

Consider two declared hypotheses:

- \(T_0\): the selected target is invariant to the rescue, so its bridge contribution to the paired contrast is zero.
- \(T_+\): the rescue changes the target from \(x\) to \(y>x\), whose bridge contrast has calibrated lower bound \(\lambda=L(y)-U(x)>0\).

Let the observed mean paired contrast be

\[
\Delta=h_I(y)-h_I(x)+\beta,\qquad|\beta|\leq\varepsilon.
\]

Here \(\varepsilon\) bounds the *whole paired-contrast* nuisance term. It may include independently bounded direct rescue-to-readout effects or readout-map drift. A bound of \(\zeta\) on each individual cell would only imply a paired-contrast bound of \(2\zeta\); the factor of two must not be silently dropped.

Under \(T_0\), the admissible contrast interval is \([-\varepsilon,\varepsilon]\). Under \(T_+\), it starts at \(\lambda-\varepsilon\). The two closed sets are separated precisely when

\[
\boxed{\lambda>2\varepsilon.}
\]

If a deterministic readout-estimation tolerance \(r\) is also added to each model's contrast set, the sufficient and sharp interval-separation condition becomes \(\lambda>2(\varepsilon+r)\). These are uniform identification statements over the declared closed uncertainty class, not p-values.

**Boundary twin.** At \(\lambda=0.4\) and \(\varepsilon=0.2\), let \(T_+\) have unperturbed readout means \((0.3,0.7)\) and nuisance changes \((0,-0.2)\). Let \(T_0\) have invariant readout means \((0.3,0.3)\) and nuisance changes \((0,+0.2)\). Both have observed means \((0.3,0.5)\). Taking independent Bernoulli reports at these means makes every finite replicated observation law identical. The same calibrated map may be used in both models: in \(T_+\) the target traverses the two anchor states, whereas in \(T_0\) it remains at the lower state. No sample size resolves this overlap without reducing the nuisance class or adding information.

**Strict monotonicity without a gap is not enough.** If \(\lambda\) has no positive uniform lower bound, arbitrarily compressed strict maps approach an invariant-endpoint model. Any positive direct-path budget can then hide the predicted change. Even with zero bias, no fixed finite sample size gives a uniform error guarantee over arbitrarily compressed maps. For a binary readout, Bernoulli \(1/2+\delta\) approaches Bernoulli \(1/2\) as \(\delta\to0\), and their fixed-sample product laws converge. This is a standard statistical indistinguishability argument; the new application is the explicit local calibration obligation in a consumer/rescue protocol.

## A5. Exhaustive finite verification

`calibration_bounds_check.py` enumerates all 3,003 nondecreasing functions on the seven-point domain with values in \(\{0,0.1,\ldots,1\}\) and boundary values 0 and 1. It checks all 49 ordered target pairs under each of five calibration scenarios, for 245 exact formula checks. The actual minimum and maximum are obtained from the enumerated functions independently of the envelope formula. Every feasible integer-grid contrast between those extremes is present.

For the target interval from position 1 to position 5:

| Calibration beyond the exterior endpoints | Admissible functions | Sharp contrast interval |
|---|---:|---:|
| None | 3,003 | [0, 1] |
| One exact interior point, \(h(3)=0.5\) | 441 | [0, 1] |
| Two exact interior points, \(h(2)=0.3,h(4)=0.7\) | 80 | [0.4, 1] |
| Interior bands \(h(2)\in[0.2,0.4],h(4)\in[0.6,0.8]\) | 672 | [0.2, 1] |
| Overlapping bands \(h(2)\in[0.2,0.6],h(4)\in[0.4,0.8]\) | 1,424 | [0, 1] |

All checks pass. The script also generates strict compression witnesses, the exact contamination-boundary twin, and a finite-sample Bernoulli indistinguishability illustration. These are model calculations, not data about actual subjective experience.

## A6. Relation to the main empirical result and remaining limits

The main paper's proportional and ordinal distances describe how much a fitted cross-task width table must change to satisfy two measurement models. This appendix asks a different downstream question: what calibration guarantees that a specified mechanism-induced change will survive a bounded nuisance path at the readout? Both concern measurement assumptions, but the latter does not turn an uncalibrated width, PSE, JND, ownership rating, or familiar-mineness judgment into a common experiential unit.

A PSE is a point on a fitted comparison-response curve; a JND is a discrimination-width quantity under its specified convention and model. Standard sensory psychophysics and the self-touch literature show why these quantities should be estimated and interpreted separately. Neither provides a universal measure of ownership, agency, or UCT familiar-mineness. The present actual-data analysis need not claim that its endpoints instantiate the latent anchor structure of this appendix.

Project records R200 and R201 already require signed experiential semantics and quantified transport tolerances. The additional, narrower content here is the exact *location-sensitive* monotone calibration bound: calibration at the wrong positions gives no local lower sensitivity even when global calibration is perfect. If the relevant anchors or nuisance bound are unavailable in a real installation, the proper result is an unresolved calibration premise, not an absence-of-experience inference.

## References additional to the main module

- Kilteni, K., Engeler, P., & Ehrsson, H. H. (2020). *Efference copy is necessary for the attenuation of self-generated touch*. iScience, 23, 100843. https://doi.org/10.1016/j.isci.2020.100843. Primary publisher record verified; illustrates the use of distinct sensory magnitude and discrimination measures in this research area.
- Wichmann, F. A., & Hill, N. J. (2001). *The psychometric function: I. Fitting, sampling, and goodness of fit*. Perception & Psychophysics, 63, 1293–1313. Author-hosted original paper: https://courses.washington.edu/matlab1/pdf/Wichmann_Hill_2001a.pdf. Primary methodological precedent for fitting and diagnostic obligations.
- Bach, D. R. (2025). *Experiment-based calibration in psychology: Foundational and data-generating model*. Journal of Mathematical Psychology, 127, 102950. https://doi.org/10.1016/j.jmp.2025.102950. Publisher abstract and author institutional publication record verified. This is close prior work on experimental calibration of latent psychological targets; the anchor-envelope calculation above is not a claim to have invented that field.

Useful source handles: `turn29search1`, `turn29search20`, `turn41search0`, and `turn41search1`. The main module supplies Loftus, state-trace, and isotonic-regression references.
