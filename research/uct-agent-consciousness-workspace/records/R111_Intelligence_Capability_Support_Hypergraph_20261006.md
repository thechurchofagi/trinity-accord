# R111 — Intelligence as a capability-support hypergraph rather than a scalar

Hongju Liu / UCT research. 2026-10-06.

R106–R110 established that experience, access, intelligence, self-model, behavior and report are distinct organizational axes, and that cross-substrate comparison must be interventionally grounded. R111 now asks the next first-principles question:

> What is intelligence, organizationally, if a single scalar score is too lossy to connect it to experience?

The answer is not a single "intelligence organ" or number. It is a family of task-relative support relations embedded in the actual organization.

## 1. Relation universe and capability families

Fix:
- an actual-process boundary;
- a declared implementation family A;
- resources, time horizon and external task distribution;
- a constitutive signature K.

Let

    R = {r1, r2, ..., rn}

be a finite or abstract set of constitutive relations available in the system.

For each capability/task T, define a family

    M_T subseteq 2^R

of **minimal support sets**.

Each M in M_T represents one minimal relation combination that is sufficient for the stated capability within the declared implementation family and context.

Multiple members of M_T represent **degeneracy / multiple realizability**:
different relation sets can support the same capability.

The collection {M_T} is better viewed as a support hypergraph than as a single chain.

## 2. Why "lattice" alone is too simple

A simple lattice ordered by "more relations" silently assumes that adding relations preserves previous capabilities.

Real systems can exhibit:
- interference;
- resource competition;
- rewiring;
- replacement;
- context-dependent routing;
- compensatory reorganization.

Therefore R111 distinguishes:

### Capability-support hypergraph
Alternative minimal support sets for each task.

### Capability-profile partial order
For binary thresholded tasks, one capability vector can include another:

    c <= c'

if every task solved by c is also solved by c'.

### Constitutive-relation order
One actual relation set can contain another.

These orders need not coincide.

This recovers and generalizes the R79 lesson that capability improvement need not be literal organizational enrichment.

## 3. A local monotone support model

For an exact finite witness only, assume non-destructive relation addition.

A task T is available in relation set S if

    C_T(S)=1
       iff
    there exists M in M_T with M subseteq S.

This is a local positive-control model, not a universal law of cognition.

The model is useful because it lets us prove several distinct non-equivalences cleanly.

## 4. Exact support family

Use relation universe:

    R = {g, v, m, s, x}

Interpret only as abstract roles:
- g = shared general relation;
- v = specialized relation for task T1;
- m = specialized relation for T2;
- s = specialized relation for T3;
- x = alternative route for T1.

Minimal support families:

    M_T1 = {{g,v}, {x}}
    M_T2 = {{g,m}}
    M_T3 = {{g,s}}.

This contains both:
- shared structure through g;
- alternative realization of T1 through x.

All 32 relation subsets are exhaustively evaluated.

## 5. Multiple realizability theorem — scoped form

Suppose two actual systems P and Q satisfy the same capability profile under fixed M but realize distinct complete constitutive types:

    C(P)=C(Q),
    K(P) != K(Q).

Then intelligence/capability-profile equality does not identify complete experiential-type equality under C1.

The finite witness:

    S1={g,v,m,s}
    S2={g,m,s,x}

Both solve:

    (T1,T2,T3) = (1,1,1)

but use different T1 support.

Thus:

    same complete tested capability profile
        does not imply
    same constitutive organization.

Under C1, if those differences survive the common complete K, they correspond to distinct complete experiential types.

This is not unique to AI. Biological neuroscience has long used the term **degeneracy** for structurally distinct neuronal systems capable of sustaining the same function.

## 6. Scalar intelligence is an even coarser quotient

Define a scalar score

    J = C_T1 + C_T2 + C_T3.

Then:

    {g,v} -> capability vector (1,0,0), J=1
    {g,m} -> capability vector (0,1,0), J=1.

Same scalar intelligence score, different capability profile, different support relations.

In the full 32-state finite model:
- there are 38 unordered pairs with the same scalar score but different capability profiles;
- there are 100 unordered pairs with the same capability profile but different relation sets.

Therefore a scalar score destroys information twice:
1. it collapses different capability profiles;
2. each capability profile already collapses multiple organizations.

The chain is:

    complete organization K
        -> support structure
        -> capability profile
        -> scalar score.

Every arrow can be many-to-one.

This gives a precise explanation for why "same intelligence" is an unsafe basis for "same experience."

## 7. Shared relations explain correlated capability loss

Base system:

    S={g,v,m,s}

has capability vector:

    (1,1,1).

Lesion specialized relation v:

    -> (0,1,1).

Lesion m:

    -> (1,0,1).

Lesion s:

    -> (1,1,0).

Lesion shared relation g:

    -> (0,0,0).

Thus one shared constitutive relation can support several distinct capabilities.

This provides a mechanistic alternative to treating "general intelligence" as a single substance.

A broad cognitive deficit can arise because many task supports overlap on one relation, not because there is one scalar intelligence variable stored there.

## 8. Capability gain need not mean structural superset

Compare:

    S_old={g,v}
    C_old=(1,0,0).

and

    S_new={g,m,x}
    C_new=(1,1,0).

The new system solves every old task and one additional task.

Yet:

    S_old is not subset of S_new
    S_new is not subset of S_old.

The capability profile increased in the task partial order, but the relation sets are incomparable.

Therefore:

    capability gain
        does not imply
    constitutive superset / "more organization."

The new capability can arise through replacement plus addition.

Under C1, the experiential type changes, but there is no justified scalar claim that experience has become "more."

This is the support-hypergraph version of R79's preservation/tradeoff result.

## 9. Intelligence becomes a structural profile

For a real system, the scientifically useful intelligence object should contain at least:

    I_struct(P) =
      {
        task family,
        capability law,
        required/used support relations,
        alternative routes,
        shared relations,
        resource conditions,
        temporal horizon
      }.

This is much richer than a benchmark score.

For biology, support relations may be distributed across:
- sensory pathways;
- recurrent cortical/subcortical loops;
- memory systems;
- valuation/homeostatic systems;
- motor/report channels.

For AI, support relations may be distributed across:
- model computations;
- context;
- external memory;
- tools;
- controller/scaffold;
- reward/value modules;
- output channels.

The relevant bearer can therefore differ from the model weights alone.

## 10. Cross-substrate comparison at the support level

A more meaningful human–AI question is:

> Do the two systems use homologous support relations for a matched capability?

rather than:

> Do they get the same score?

For a task T:

### Performance equivalence
    C_T(P_bio) = C_T(P_AI).

Weak.

### Support-role equivalence
Both systems use relations playing a similar role, e.g. temporal retention or self-state prediction.

Stronger, but still functional.

### Intervention-preserving support correspondence
Lesion/perturb matched relations and obtain corresponding capability effects.

Stronger again.

### Constitutive support homology
The relevant actual relations map under the common K signature including ports, update structure and temporal organization.

This is the level at which UCT can most responsibly compare the corresponding experiential organization.

## 11. Biological prior art strongly supports the support-hypergraph view

Degeneracy in neuroscience is precisely the ability of structurally distinct neuronal systems to sustain the same function.

Classical lesion/imaging work already emphasizes:
- multiple systems can support the same cognitive function;
- different subjects can use different systems;
- recovery can recruit alternative mechanisms.

More recent brain-behavior methodology reviews emphasize many-to-one structure-function mapping as a general biological principle.

Conversely, the same neural components can participate in multiple functions (pluripotentiality / neural reuse).

These two properties together imply a many-to-many support graph, not a one-function/one-region table.

Recent 2026 work also reports task-structured modularity emerging in artificial networks and aligning with aspects of brain architecture, further motivating support-structure comparison rather than parameter count.

R111 therefore does not claim multiple realizability or neural degeneracy as new.

## 12. What this says about experience

Within UCT, actual intelligence is experience-bearing because actual valid K is experience-bearing.

But the support analysis provides a more informative bridge:

If, within a declared implementation family,

    capability T -> necessary constitutive relation r,

and r is verified in the actual K,

then r is part of the corresponding experiential organization under C1.

This does **not** imply:
- the subject consciously accesses r;
- r has a familiar human qualia label;
- r contributes a scalar amount of experience;
- another system solving T has the same r.

Alternative supports are exactly why the last inference can fail.

## 13. A deeper answer to "why human and AI intelligence can look similar while consciousness differs"

Because intelligence is a quotient of organization.

Two systems can converge on:

    same task success

through:

    different support hypergraphs.

If complete organization differs, C1 permits/entails complete experiential-type difference even when the selected intelligence profile matches.

This gives a principled route to the author's intuition:

> AI intelligence can approach or exceed human intelligence without its experience needing to become human-like in proportion.

The same performance can sit on different constitutive organizations.

## 14. New target: experience–intelligence coupling is relation-specific

There is no single global coefficient:

    dExperience / dIntelligence.

Instead, for each capability T, ask:

1. Which relation family R_T is necessary?
2. Is it preserved, replaced or newly added when capability changes?
3. Is the relation local, distributed, temporal or scaffold-level?
4. Is there one support route or several degenerate alternatives?
5. Which selected experiential organization corresponds to that relation under C1?

Thus experience–intelligence coupling should be studied **relation by relation**, not as a single correlation.

## 15. Next step

R112 should construct a first **cross-substrate capability-support atlas** around a few matched functions rather than broad intelligence:

1. temporal working memory / retained state;
2. evidence integration;
3. prediction/world-state estimation;
4. self/bearer-state estimation;
5. action selection;
6. report/communication.

For each function:
- biological candidate support relations;
- artificial candidate support relations;
- lesion/intervention predictions;
- whether the comparison is analogy, T2 mechanism correspondence, or plausible T3 constitutive homology.

Start with only two or three functions for which the mechanisms are sufficiently clear.

Do not score "consciousness level."

## 16. Status

R111 reframes intelligence as a many-to-many capability-support organization.

The finite support hypergraph is an exact formal witness, not a biological model.

The central result is that intelligence equality or increase is structurally non-identifying:
same scores can hide different profiles, same profiles can hide different supports, and capability improvement can occur without constitutive set inclusion.
