# R113 — Causal support identification: necessity, degeneracy, readout and correlation

Hongju Liu / UCT research. 2026-10-06.

R112 built a first cross-substrate atlas. R113 addresses the methodological bottleneck underneath that atlas:

> How do we know that an observed relation is actually part of the support for a capability rather than a redundant route, downstream readout, permissive gate, or mere correlate?

This is necessary before capability-support structures can be responsibly mapped into experiential organization under C1.

## 1. Why simple lesion logic fails

Two common inferences are invalid.

### Invalid inference A
    lesion r -> no measured deficit
    therefore r is irrelevant.

False when:
- another degenerate route compensates;
- the task/context does not require r;
- the lesion is bypassed;
- the readout is insensitive.

### Invalid inference B
    lesion r -> deficit
    therefore r encodes the target content.

False when r is:
- a generic gate;
- energy/resource support;
- an upstream enabling pathway;
- a motor/report bottleneck.

Causal support and representational content are distinct claims.

## 2. Operational categories

For a declared capability T, task family M, bearer and background organization K:

### 2.1 Background-relative indispensable support
A relation r is indispensable in the tested background if disabling r while preserving declared controls degrades T and no active alternative route in that background compensates.

This is weaker than universal metaphysical necessity.

### 2.2 Alternative sufficient support
A relation set S is sufficient relative to background B if restoring/retaining S in B permits T above criterion.

Sufficiency is always background-relative.

### 2.3 Degenerate support
Two nonidentical support sets S1 and S2 are degenerate for T if either can support T under the declared background.

Then individual lesion of one route can show no deficit even though the route genuinely participates.

### 2.4 Shared permissive support
A relation can be necessary across many tasks without carrying task-specific content.

Example: a common gate, power source, clock or communication bottleneck.

### 2.5 Downstream readout
A relation changes report/output expression while the selected core capability remains intact.

### 2.6 Mere correlate
A relation covaries with task variables but intervention on it does not alter the capability or its causal support, under the tested domain.

"Correlate" remains domain-relative; failure to detect an effect is not proof of absolute irrelevance.

## 3. Exact transparent system

Target:
    XOR truth table 0,1,1,0.

Relations:
- g = shared gate;
- r1 = route 1 computing XOR;
- r2 = alternative route 2 computing XOR;
- h = report head;
- c = task-correlated but disconnected signal.

Core task output:

    y = g AND (r1 OR r2),

where an active route produces the correct target bit and an inactive route produces 0.

Report:

    report = h AND y.

Correlate:

    c copies the target when active but has no path to y or report.

All 2^5=32 relation subsets are enumerated.

## 4. Minimal support sets

Perfect core task accuracy has exactly two minimal support sets:

    {g, r1}
    {g, r2}.

Perfect report accuracy has exactly:

    {g, h, r1}
    {g, h, r2}.

The correlate c appears in no minimal support set.

This cleanly separates:
- g: shared indispensable/permissive relation;
- r1/r2: degenerate alternative routes;
- h: downstream report-specific support;
- c: correlate without causal task support.

## 5. Why single lesions misclassify degenerate routes

Start from all relations active.

Lesion r1 alone:
    r2 compensates
    core accuracy remains 1.0.

Lesion r2 alone:
    r1 compensates
    core accuracy remains 1.0.

A naive single-lesion study would conclude both routes are unnecessary.

But lesion both r1 and r2:
    core accuracy falls to 0.5.

And either route together with g is enough for perfect task performance.

Thus:

> zero single-lesion effect does not imply zero causal support.

This is the exact logic of degeneracy.

## 6. Shared gate is necessary but not content-specific

Lesion g:

    core accuracy -> 0.5
    report accuracy -> 0.5.

Thus g is in every minimal support set.

But g does not compute XOR content; it merely permits route output to reach the core task output.

Therefore:

    necessity
        does not imply
    content representation.

This distinction is crucial for consciousness research. A brain region or AI component whose lesion abolishes a report or task may be a necessary access/gating relation rather than the locus of the relevant experiential content.

## 7. Report head is downstream support

Lesion h:

    core accuracy remains 1.0
    report accuracy falls to 0.5.

Thus h is:
- necessary for this report criterion;
- unnecessary for the selected task core.

This is the causal version of R108's report-head surgery and the biological no-report caution.

A report bottleneck should not be promoted into a general experience gate.

## 8. Correlate is not support in the tested system

Relation c exactly tracks the target when active.

Therefore observationally:

    c is perfectly task-correlated.

But disable c:

    core accuracy unchanged;
    report accuracy unchanged.

c is not present in any minimal support set.

Thus perfect decodability/correlation is insufficient to establish causal use.

This recovers a central lesson from mechanistic interpretability and R80/R95 in a minimal exact system.

## 9. The correct intervention protocol

For candidate relation r and capability T:

### Step 1 — Define the capability and boundary
Specify task distribution, resource conditions, bearer, time horizon and output criterion.

### Step 2 — Establish observational association
Show that r contains/covaries with task-relevant information.

This is only a screening step.

### Step 3 — Single intervention
Disable/replace r with matched controls.

A deficit supports causal relevance in that background.
No deficit does not end the analysis.

### Step 4 — Search for compensation
Identify alternative routes and perform combinatorial interventions.

If:
    lesion r1 no deficit
    lesion r2 no deficit
    lesion {r1,r2} deficit,

then r1 and r2 are degenerate supports.

### Step 5 — Restoration / sufficiency-with-background
Restore candidate route(s) in a deficient background.

State the background explicitly; never claim context-free sufficiency.

### Step 6 — Separate core from readout
Measure selected internal/core capability independently of motor/report channel.

### Step 7 — Test domain transfer
Repeat under changed context, resource constraints and task variants.

A support relation can be context-specific.

### Step 8 — Only then map to UCT organization
If the relation is actual, constitutive and represented in the common K, it belongs to experiential organization under C1.

Do not map a mere decoder correlate or an experimenter's label into E.

## 10. Support taxonomy is richer than "necessary/sufficient"

For complex adaptive systems, binary necessity/sufficiency language can be misleading.

The more useful object is:

    Support_T(K,M) =
      {
        indispensable shared relations,
        degenerate route families,
        context-specific supports,
        downstream readouts,
        correlates,
        compensatory mechanisms
      }.

This is a process/organization description rather than a one-node label.

Recent neuroscience commentary has made a similar point: complex functions arise from jointly sufficient conditions and overlapping networks, so perturbation results should be interpreted within explicit background conditions rather than as absolute necessity/sufficiency claims.

## 11. Consequence for biology

Biological lesion studies must allow for:
- degeneracy;
- rapid compensation;
- chronic reorganization;
- shared bottlenecks;
- measurement/readout failures.

Therefore:
- no lesion deficit does not prove a region is uninvolved;
- lesion deficit does not prove experiential content is located there;
- stimulation-induced behavior does not prove complete sufficiency for the natural process.

This aligns with classical neural degeneracy and modern systems-neuroscience cautions.

## 12. Consequence for AI

AI gives an unusual advantage:
we can often access and intervene on internal variables directly.

But the same logical errors remain:
- probe decodability is not causal use;
- ablation can be compensated;
- a final-layer bottleneck may look "necessary" but only be a readout;
- alternate circuits can implement the same computation.

The R113 protocol should therefore be applied to:
- memory paths;
- evidence integration paths;
- self-state paths;
- tool/scaffold state;
- report heads.

## 13. Consequence for experience–intelligence coupling

The UCT bridge should use **causal support relations**, not correlated neural/AI features.

For capability T:

    verified support relation r_T
      + actual K anchoring
      + C1
        =>
    r_T is part of the token's experiential organization.

This is stronger than:

    feature decodes T
      =>
    experiential relevance.

But even verified support does not tell us:
- human-like qualia;
- valence;
- introspective access;
- experience magnitude.

## 14. New distinction: support content versus support access

A relation can contribute to capability in at least two conceptually different ways:

### Content-bearing support
Carries task-relevant distinctions.

### Access/permissive support
Allows those distinctions to influence downstream computation or output.

g in the exact witness is permissive.
r1/r2 are content-bearing computational routes.
h is report access/readout.

This distinction should be added to the R112 atlas.

It may help interpret biological cases:
- posterior perceptual representations versus frontal/report access;
- memory content versus retrieval access;
- self-state representation versus action/readout.

It also prevents "causally necessary" from automatically becoming "phenomenal content carrier."

## 15. Next step

R114 should apply the support-identification taxonomy back to the three R112 atlas functions.

For each:
- temporal working memory;
- evidence integration;
- bearer estimation;

construct a support diagram with:
- content-bearing relation;
- access/permissive relation;
- degenerate alternatives;
- readout;
- candidate correlates;
- matched lesion predictions.

Then compare whether the biological literature actually identifies the same category or merely a correlation.

This will tell us where cross-substrate T2 correspondence is genuinely plausible.

## 16. Status

R113 provides an exact support-identification protocol and transparent failure cases.

It is not a new general theory of causation. Necessity/sufficiency, degeneracy, causal abstraction and intervention logic are established prior art.

Its project value is to define exactly which organizational evidence is strong enough to enter the UCT experience–intelligence bridge.
