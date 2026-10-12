# Gradual coordination without indiscriminate mixing

**Checkpoint:** UCT-GD-20261013, v0.1.0.  
**Human research direction:** Hongju Liu.  
**Analysis, derivation, execution and drafting:** ChatGPT, GPT-6 Astra Pro.  
**Status:** exploratory theoretical/computational research; not a finished paper, not peer reviewed, no new DOI. The prior UCT-RC v1.1.0 is unchanged.

## 1. Research question and correction of the preceding interpretation

The user emphasized that bodily unity, ownership and self-related organization should be studied through gradual evolutionary construction rather than an assumed experience-onset gate. The user also explicitly warned that the preceding assistant's interpretation might be wrong. This note therefore does not promote a sequence of chemical boundary, control, memory and conceptual self into a demonstrated universal evolutionary ladder.

UCT I v1.2 already distinguishes universal basal experience within its ontology (C1/U1), conditional structural continuity (U2), fine chains (E2), and the unproved historical availability of those chains. E2 explicitly allows deletion, pruning, branching and specialization and denies monotonic growth of one consciousness scalar. Section 8.3 also explicitly rejects deriving C1 from evolutionary continuity alone. These are inherited constraints, not discoveries of this checkpoint [U1].

The open positive question is narrower: **can progressively stronger communication coexist with local differentiation, and what physical feature of a route makes the difference?** This concerns one prerequisite for explaining increasingly differentiated organization, not a sufficient test of selfhood or a measure of experience. No result identifies a modeled bit, memory score or correlation with body ownership, agency, or a numerical subject count.

Two mistakes must be avoided together. Increasing connection strength need not increase all useful distinctions. But this does not force an all-or-nothing choice between disconnected parts and one undifferentiated whole. Selective communication is a constructive third possibility.

## 2. Inherited mathematics and originality scope

The copying-and-flip dynamics below are instances of the classical noisy voter model [P1]. Moment closure, graph Laplacians, exponential modes, and killed-walk representations are standard. Multilayer diffusion and its multiple time scales are established subjects [P2]. Integration together with differentiation has been explicitly studied in consciousness-related neuroscience since at least Tononi, Sporns and Edelman (1994) [P3]. Neither concept is presented as a new UCT invention.

The application here is an author-directed pressure test: an exact equal-total-rate comparison; a fresh source-preparation/readout task; a selective-routing construction; its leakage limitation; and a general finite-module version whose singular limit retains the loss of information through interface exits. Global priority is unverified. This is not yet enough to justify another standalone paper. In particular, it must not be renamed a proof of gradual phenomenal selfhood.

The previous UCT-RC paper fixes local laws in an overlapping three-register example while varying joint innovation structure, and distinguishes passive correlation from fresh information retention [U2]. Here coupling changes the local laws, modules have disjoint registers connected by actual copying edges, and the main issue is how a continuously varied communication route changes fresh-source retention. The two results must not be conflated.

## 3. Baseline: copying can increase agreement and erase source distinctions

Let X,Y take values in {-1,+1}. Each flips independently at rate mu>0. Each copies the other at rate g>=0. A copying event that finds equal states makes no state change. Both physical registers remain active at every finite rate; no register or process is removed when g increases.

For an observable f, the generator is

Qf(x,y) = mu[f(-x,y)-f(x,y)] + mu[f(x,-y)-f(x,y)]
          + g[f(y,y)-f(x,y)] + g[f(x,x)-f(x,y)].

The exact observable identities are

- QX = -(2mu+g)X + gY;
- QY = gX -(2mu+g)Y;
- Q(XY) = 2g -(4mu+2g)XY.

Consequently:

1. The common mode X+Y decays at rate 2mu.
2. The difference mode X-Y decays at rate 2(mu+g).
3. The stationary raw correlation is c=g/(2mu+g).
4. The stationary centered correlation of the relation XY, normalized by its variance, decays as exp[-(4mu+2g)t]. This last normalization requires finite g and mu>0, so the variance is nonzero.

Agreement therefore rises with g even as both source contrast and fluctuations around the more predictable agreement relation decay faster. High agreement is not a general memory measure.

**Fresh source task.** Prepare either (+1,-1) or (-1,+1), with equal prior probability, and reveal the complete two-register state only after time t. The total variation distance of the two output laws is exp[-2(mu+g)t], so optimal success is (1+exp[-2(mu+g)t])/2. The proof follows by expanding the difference of the two laws in the four binary characters: normalization and pair-product terms cancel, leaving the antisymmetric first-moment mode.

**Fresh common task.** Preparing either (+1,+1) or (-1,-1) gives success (1+exp[-2mu t])/2. This is a different input task, not a simultaneous two-bit capacity claim. Every quantity has a declared preparation, delay and readout. The signs stand for externally specified source codes, not phenomenal authorship.

## 4. Selective routing with an exactly matched nominal coupling budget

Each of two modules has an interface register u_i and an internal register v_i. Within a module, u_i and v_i copy each other at rate lambda>0. Interface registers u_1,u_2 copy each other at rate g. Internal registers v_1,v_2 copy each other at rate h. Every register also flips at rate mu>0. Thus the complete process has 16 states.

The words 'interface' and 'internal' describe physical ports in this model. They do not select an experiencer. When g>0 and lambda>0, all four registers are connected even at h=0: internal records are not isolated spectators.

Write d_u=(E[u_1]-E[u_2])/2 and d_v=(E[v_1]-E[v_2])/2. The exact difference dynamics are

    d/dt [d_u] = -[2mu+lambda+2g     -lambda       ] [d_u]
         [d_v]    [    -lambda    2mu+lambda+2h  ] [d_v].

Prepare v_1=r, v_2=-r, where r is an equally likely fresh sign, and independently randomize both interface registers fairly. Then d(0)=(0,r). Define b=2mu+lambda+g+h, d=g-h and z=sqrt(d^2+lambda^2). The internal response is

D_v(t) = exp(-bt)[cosh(zt)+(d/z)sinh(zt)]
       = (1+d/z)/2 exp[-(b-z)t] + (1-d/z)/2 exp[-(b+z)t].

The conditional mean of v_1(t) is r D_v(t). Reading this one register therefore gives exact balanced source-code success (1+D_v(t))/2. This is optimal for that specified one-register observation, not asserted optimal for the whole state.

Compare the routes at fixed total undirected cross-copy attempt rate G=g+h:

- selective: g=G, h=0;
- uniform: g=h=G/2.

The directed attempt budget is 2G in both. This does not equalize successful overwrites, energy use, hardware cost, or every node's degree. These changes are part of the mechanism and are not hidden controls.

For the uniform route,

D_uniform = exp[-(2mu+lambda+G)t] cosh(lambda t).

For the selective route,

D_selective = exp[-(2mu+lambda+G)t]
              [cosh(sqrt(G^2+lambda^2)t)
               + G/sqrt(G^2+lambda^2) sinh(sqrt(G^2+lambda^2)t)].

For G,t>0, D_selective>D_uniform. More generally, set g=(1-eta)G, h=eta G for 0<=eta<=1/2. Then b is fixed while d=(1-2eta)G decreases. Both z and d/z increase with d>=0, making the bracket increase with d. Source retention therefore decreases as more of the fixed budget is routed directly into the internal registers. This gives a graded family, not a threshold rule.

**Common input control.** Instead prepare v_1=v_2=r with both interfaces independently fair. In both routes the common-mode response on v_1 is

C_v(t) = [exp(-2mu t)+exp(-(2mu+2lambda)t)]/2.

It is exactly independent of g,h. Thus the equal-budget comparison preserves this complete specified common-input response while changing the source-difference response. It does not claim that every other task or complete local law is preserved.

For mu=.02, lambda=.1, G=1 and t=5:

| Quantity | Selective route | Uniform route |
|---|---:|---:|
| Common input mean response | .5599624825 | .5599624825 |
| Local source-code mean response | .5078614673 | .0037729975 |
| One-register decoding success | .7539307337 | .5018864988 |

Time and rates are model units, not calibrated biological values.

## 5. The leakage qualification: selectivity must persist as communication grows

The previous construction should not suggest that one small constant *fraction* of leakage is harmless at every system size or communication strength.

For g>=h>=0 and initial d(0)=(0,1), positivity of the difference semigroup gives

exp[-(2mu+lambda+2h)t] <= D_v(t) <= exp[-(2mu+2h)t].

For the lower bound, d_u(t)>=0 and

d_v' = -(2mu+lambda+2h)d_v + lambda d_u
     >= -(2mu+lambda+2h)d_v.

For the upper bound, the slow eigenvalue is b-z. Since z<=g-h+lambda, b-z>=2mu+2h; both spectral weights in D_v are nonnegative and sum to one.

If h is fixed while g grows, D_v(t) tends to exp[-(2mu+lambda+2h)t] at each fixed t>0. If h(g) tends to infinity with h(g)<=g, the upper bound forces D_v(t) to zero. In particular, h=epsilon*g with fixed epsilon>0 does not protect a nonzero finite-delay response as g tends to infinity. Bounded leakage is sufficient, and an unbounded set of leakage values precludes a uniform positive lower bound over that set.

This is a limit of finite models, not an implementable infinite copying rate. It says nothing about infinite-duration survival: mu>0 makes every model eventually lose the written bit. It also holds lambda fixed. Increasing all local overwrite rates changes the result.

## 6. General reflected-module result: a path interpretation

Take two identical modules, each with n finite registers. Inside each module, registers copy along a fixed undirected weighted graph with Laplacian L. Matched register i across the two modules copies at rate g_i. All registers flip at mu. Define d_i=(E[x_i^A]-E[x_i^B])/2. Exact generator algebra gives

    d' = -(2mu I + L + 2 diag(g)) d.

No mean-field approximation is used. The n-dimensional equation is an exact consequence of the full 2^(2n)-state process.

For a fresh uniform source code x^A=+1, x^B=-1, d(0)=1. Let Z_s be the continuous-time random walk inside one module with generator -L. The finite-state backward equations prove the representation

D_i(t) = E_i[exp(-2mu t - 2 integral_0^t g_(Z_s) ds)].

This is the classical killing/ancestry construction, here applied to the source task. It gives a direct physical interpretation: different copying routes expose a stored source distinction to different amounts of cross-module mixing. A lower bound comes from paths that never leave i:

    D_i(t) >= exp[-(2mu + degree_L(i) + 2g_i)t].

Thus unbounded communication at *other* ports cannot force this fixed-time source response to zero if the overwrite rate at i and the internal departure rate remain bounded. The internal degree cannot be silently removed merely because the port is called 'private'.

### Strong-communication limit with actual boundary losses

Let g_i(G)=a_i G+b_i, a_i,b_i>=0. Define Z={i:a_i=0}. For fixed t>0, as G tends to infinity:

- responses at i outside Z go to zero;
- responses at i in Z tend to

    [exp(-(2mu I + L[Z,Z] + 2diag(b_Z))t) 1]_i.

Here L[Z,Z] is the *principal submatrix*, retaining its original diagonal degree. It is not the Laplacian obtained by removing boundary edges and recomputing degrees.

**Proof.** In the path representation, any path spending positive time outside Z has exponential weight tending to zero. Such positive occupation occurs almost surely following an exit before t. Paths staying in Z retain only the finite flip and b rates. Dominated convergence therefore leaves the random walk killed upon its first exit from Z. Its generator uses the principal submatrix of L. A start outside Z has positive holding time there almost surely, so its limit is zero. The result concerns fixed t>0; the limit at t=0 outside Z is not uniform.

This proof extends the four-register mechanism. When all a_i>0, no protected mode survives at fixed delay. When some a_i=0, retained internal distinctions still leak through their real internal links to the saturated interfaces. The limit neither pretends they are disconnected nor promises arbitrary storage.

For a three-register module with edges (0,1) at .1 and (1,2) at .2, mu=.02 and t=5, saturating only cross-port 0 gives limiting responses (0,.5793968169,.7185828998). Incorrectly deleting the boundary hazard would instead predict .8187307531 at both retained nodes. The difference is substantial and is retained as a counterexample in the results.

The common source x^A=x^B=+1 yields exp(-2mu t) at every register for every routing vector. Thus the example concerns which distinctions can coexist with a shared response, not whether the whole has ceased to function.

## 7. What is gradual, and what is not being inferred

For each finite carrier and bounded finite rates, Q depends continuously (in fact affinely) on those rates. Its finite-time transition law exp(tQ) is analytic. Both graded routing families and their fresh-input outcomes can therefore change without an experience-existence switch.

For the four-register equal-budget family, changing eta by delta changes each cross-edge rate in magnitude by G|delta|. Couple the two processes using their common flip, internal-copy and cross-copy clocks. There are four oriented unmatched cross-copy clocks in total. Over an interval of length T, the probability that any unmatched clock rings is at most 1-exp[-4GT|delta|]. Thus the two full path laws have total variation at most that amount. This is a bound on modeled dynamics, not a distance on complete ontic or phenomenal organizations.

A graph predicate such as 'there is a positive cross-link' may jump at zero despite these finite-time probabilities being continuous. Thresholded reports may also jump. Neither observation establishes an experience onset. Conversely, UCT's structural identity does not authorize a general inference that every human qualitative label or subject count is continuous. The actual physical path, declared comparison geometry, and relevant experiential interpretation are still separate obligations.

Phylogenetic evolution, within-person development, learning, and engineering replacement are not interchangeable. The continuous parameter route here is an admissible mathematical comparison. It is not evidence that biological evolution traversed it, that embryonic development recapitulates phylogeny, or that natural selection monotonically increases any 'self' quantity.

## 8. Thought-experiment uses and stop conditions

**Two gradually communicating mechanical systems.** Keep the actual carriers running. Compare uniform overwriting with selective exchanges through ports. The computed distinction is not 'two subjects versus one'. It is whether a shared response necessarily erases the ability to distinguish local origins. It does not.

**Two brains with increasingly rich connection.** The model offers no clinical protocol and no direct prediction of how many experiences exist. A usable extrapolation must specify the physical channels, endogenous read/write mechanisms, and which local responses remain differentiated. Electrical synchrony alone does not supply these facts.

**Slow mechanics.** Replacing time t by s*t and all rates by rate/s leaves the dimensionless predictions unchanged. A fixed outside observer's observation window cannot by itself determine experience existence. Real slowing can introduce unscaled noise, leakage, and physical changes; exact similarity is conditional.

**More communication with a narrow leak.** Hold h fixed versus h proportional to g. Both are gradual parameter paths and both maintain active registers, yet the large-g source limits differ. 'Gradual' is not enough: the route's organization matters.

**A marker that reports 'mine'.** A writer can map r to that word without establishing that r is felt as mine. A5L's direct-coordinate writer countermodel remains open [U3]. The present study does not fix that semantic problem by adding more observed endpoints.

## 9. Empirical constraints, not a reconstructed consciousness history

Kalckert and Ehrsson's moving rubber-hand experiments manipulated voluntary/passive movement, timing and anatomical congruence and found a double dissociation of ownership and agency [P4]. This constrains any account that equates them to the same monotonic signal. It does not determine their complete evolutionary trajectories or verify this copying model.

Filippetti and colleagues found newborn visual preferences for spatially congruent, synchronous visuotactile stimulation [P5]. The authors explicitly state that their experiment cannot establish whether newborns regarded the displayed face as their own. This is a useful model of epistemic restraint: early organization-sensitive behavior can be studied without pretending to measure a fully articulated adult self.

Bozdag and colleagues studied an actual selected multicellular lineage and documented how cellular and group-scale physical organization changed [P6]. That is evidence about one biological organizational route under stated selection and metabolic conditions, not a phenomenal assay. The copying examples here are not equivalent experiments.

A concrete next empirical task would track selective communication and protected local source response across a declared developmental or adaptive route, independently of ownership/agency endpoints. It would require complete intervention provenance, prospective controls for common input and observer memory, and a reason the chosen endogenous response matters to the organism. No new human, animal, neural, robot or evolutionary experiment was performed in this checkpoint.

## 10. Relation to UCT, and a restrained positive claim

Within C1, actual changes in complete constitutive relations are changes in experiential organization. But the finite copying view is not demonstrated to be that complete organization. Basal experience is not identified with memory, synchrony, control, successful source decoding or a selective interface. Local persistence is not unchanged local experiential content.

The constructive application is: **progressively stronger whole-level communication need not be achieved by indiscriminately overwriting every local distinction; an explicit route can preserve some fresh local distinctions while maintaining a common response.** Which distinctions persist depends on rate allocation and leakage, not only the total amount of coupling. The general killing formula identifies a mechanism and a boundary for this assertion.

This suggests studying the evolutionary construction of *selectively coordinated differentiation*, but that phrase is a research description, not a new axiom, unique marker of selfhood, or priority claim. It is a better specified research target than 'find the first self' or 'increase integration until a self appears'. A universal sufficiency law for bodily ownership or phenomenal unity remains open.

## 11. Verification and publication decision

`code/verify_gradual_differentiation.py` verifies exact generator identities with rational arithmetic; compares analytic formulas to full 4/16-state transition matrices; independently checks 16-state exponentials by Poisson uniformization; and audits equal-budget comparisons and fresh-input readouts.

`code/verify_routing_generalization.py` compares the general moment equation against the complete 64-state process, tests common versus opposite source preparations, checks strong-communication limits, and demonstrates the boundary-deletion error. Counts and numerical errors are in the result JSON files. Finite numerical agreement does not replace the generator proofs or the dominated-convergence argument.

The mathematical tools and integration/differentiation idea are inherited. The present result is a bounded application and a research-direction refinement, not a decisive solution of consciousness. The full historical UCT map has not undergone a new all-node semantic audit. The checkpoint graph remains disabled, and no authoritative map version is changed. No DOI, OTS or Arweave action is requested or performed. No existing paper is overwritten.

## References and access scope

[U1] Liu, H. UCT I v1.2. DOI 10.5281/zenodo.23131575. Repository source `research/uct-agent-consciousness-workspace/records/R128_Unified_Formal_Map_Audit_20261006/sources/A_UCT_I_v1_2.md`; current source blob `7a980c86b8f94ce787d358dab3529903eb822f8f`. Sections 8.2–8.9 and relevant comparison material read. Source theory, not independently verified empirical law.

[U2] Liu, H. What the Whole Adds Without Erasing Its Parts, v1.1.0. DOI 10.5281/zenodo.23327394 is the reported existing publication. The supplied local Markdown and final review were read; no new DOI-resolution or publication-lifecycle verification was performed in this checkpoint.

[U3] UCT A5L20261012. Role reversal and the semantic barrier. Repository working note, blob `f3f86c4719bd3dd48a65c99858f41b8a9a44c566`; full note read. Its semantic counterexample is preserved.

[P1] Granovsky, B. L., & Madras, N. (1995). The noisy voter model. Stochastic Processes and their Applications, 55, 23–43. DOI 10.1016/0304-4149(94)00035-R. Publisher abstract accessed; not represented as a fresh full-paper proof review.

[P2] Gomez, S., et al. (2013). Diffusion dynamics on multiplex networks. Physical Review Letters, 110, 028701. DOI 10.1103/PhysRevLett.110.028701. Publisher abstract accessed; spectral precedent, not a global priority certificate.

[P3] Tononi, G., Sporns, O., & Edelman, G. M. (1994). A measure for brain complexity: relating functional segregation and integration in the nervous system. PNAS, 91, 5033–5037. DOI 10.1073/pnas.91.11.5033. Indexed original abstract accessed.

[P4] Kalckert, A., & Ehrsson, H. H. (2012). Moving a rubber hand that feels like your own: a dissociation of ownership and agency. Frontiers in Human Neuroscience, 6, 40. DOI 10.3389/fnhum.2012.00040. Publisher HTML methods, results and discussion accessed. No raw data reanalysis.

[P5] Filippetti, M. L., Orioli, G., Johnson, M. H., & Farroni, T. (2015). Newborn body perception: sensitivity to spatial congruency. Infancy, 20, 455–465. DOI 10.1111/infa.12083. Publisher HTML methods and interpretive limits accessed. No infant ownership claims beyond the measured preference and the authors' qualified interpretation.

[P6] Bozdag, G. O., et al. (2023). De novo evolution of macroscopic multicellularity. Nature, 617, 747–754. DOI 10.1038/s41586-023-06052-1. Publisher abstract and author-institution description accessed; not a full historical or physiological reanalysis.
