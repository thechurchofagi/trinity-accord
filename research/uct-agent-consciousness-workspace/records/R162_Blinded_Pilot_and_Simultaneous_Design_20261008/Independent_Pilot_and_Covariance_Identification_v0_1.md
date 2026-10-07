# Independent Pilot Freezing and Covariance Non-Identification

## A practical uncertainty contract for the R161 body/tool protocol

Version 0.1, 8 October 2026. Research checkpoint; not a published edition, ethics approval, recruitment plan, executed pilot, or recommendation to expose participants.

## 1. Question and bounded result

R161 supplied a concrete crossed protocol and valid confirm/exclude/unresolved logic, but its distribution-free planning audit was impractical. This round asks whether existing data can justify the joint uncertainty model required by the eight conditional simple effects and, if not, what design would prevent the covariance model from being tuned on the same outcomes that it later classifies.

The result has four parts.

1. Public primary datasets exist for the visuomotor/localization components and for a tendon-vibration/visual-context component, but no inspected source jointly observes the exact four R161 conditions, both R161 readouts, and the active-versus-bony-site vibration contrast in the same participants.
2. Separate marginal datasets cannot identify the cross-block covariance needed for dominance-margin precision. This is a mathematical non-identification result, not merely an incomplete search report.
3. A separate, effect-blind external pilot running the exact protocol can estimate the joint nuisance covariance and completion/fidelity rates. Pilot participants are not pooled into the confirmatory analysis, and the pilot may not emit confirm/exclude labels.
4. Conditional on a complete participant-vector Gaussian model and a frozen plan, Bonferroni Student intervals provide a simple simultaneous-coverage fallback. Independent pilot selection preserves unconditional coverage by iterated probability. This is a conditional design theorem, not evidence that the Gaussian model or protocol is true.

No practical confirmatory sample size is asserted because no exact-protocol pilot has been run.

## 2. The required participant-cluster object

For each participant completing the exact R161 protocol, let the bounded signed contrast vector be

\[
W_i=(B^B_{0i},B^B_{1i},T^B_{0i},T^B_{1i},B^T_{0i},B^T_{1i},T^T_{0i},T^T_{1i})\in[-1,1]^8.
\]

The superscript names the intervention whose two levels are contrasted; the subscript is the fixed level of the other intervention; the first letter names the body or tool readout. For example,

\[
B^B_{ri}=Z_{B,i}(q=1,r)-Z_{B,i}(q=0,r).
\]

The population signed effects are \(\theta=\mathbb E[W_i]\). R161 uses their magnitudes and the conservative aggregation

\[
a=\min_r|\theta(B^B_r)|,\quad
x=\max_q|\theta(T^B_q)|,
\]

with the symmetric \(b,y\) pair for the tool predicate.

The required nuisance object is therefore the full participant-cluster covariance

\[
\Sigma=\operatorname{Cov}(W_i)\in\mathbb R^{8\times8},
\]

not eight unrelated standard deviations. The correlations matter because the terminal inequalities compare target and cross effects.

## 3. Audit of available component data

The source audit found three public data routes.

| Primary source | Public route stated by source | R161 components observed | Missing for R161 joint covariance |
|---|---|---|---|
| Ruttle et al. 2016 | OSF `4v6md` | 30-degree rotated cursor, no-cursor reaches, proprioceptive hand localization, repeated participants | No tendon-versus-bony intervention; no full `q × r` crossing |
| Mostafa et al. 2019 | OSF DOI `10.17605/OSF.IO/ZFDTH` | visual-proprioceptive discrepancy, active/passive localization and open-loop reaches | No tendon-versus-bony intervention; different training groups and no full R161 crossing |
| Le Franc et al. 2020 | DANS DOI `10.17026/dans-znu-5fyx` plus PLOS supporting spreadsheets | 100 Hz wrist-tendon vibration under three visual contexts; repeated angular and rating responses | No bony-site `q=0` contrast, no 30-degree cursor-mapping factor, no R161 no-cursor tool readout; primary outcomes include subjective illusion reports |

These sources can inform apparatus, endpoint range, trial burden, marginal variability and failure modes. They cannot supply \(\Sigma\) for the exact R161 vector. The OSF file endpoints were not directly enumerable through the available research interface in this round; the primary articles' data-availability statements and methods were inspected. No raw file was silently treated as analyzed.

## 4. The covariance-borrowing obstruction

### Proposition R162-P1: separate marginals do not identify dominance precision

Partition a required contrast pair as \((U,V)\), where one component study observes only \(U\) and another observes only \(V\), on disjoint participants. Even exact knowledge of both marginal laws does not generally identify \(\operatorname{Cov}(U,V)\).

**Witness.** Let both marginals have mean zero and variance one. For every \(\rho\in[-1,1]\), the covariance matrix

\[
\Sigma_\rho=
\begin{pmatrix}
1&\rho\\
\rho&1
\end{pmatrix}
\]

is positive semidefinite and has the same two marginals. Yet

\[
\operatorname{Var}(U-V)=2-2\rho
\]

ranges from zero to four. Thus the same marginal source record is compatible with radically different precision for a dominance difference. Replacing \(U,V\) by blocks yields the same obstruction for missing cross-block entries of \(\Sigma\). \(\square\)

Consequently, pooling standard deviations from the three component studies and setting unknown correlations to zero is an additional modeling assumption. It is not a fact extracted from those datasets. Sensitivity over a correlation range is useful for planning stress tests but cannot certify power.

## 5. External pilot freeze contract

Define a separate pilot sample \(P\) and confirmatory sample \(C\).

### 5.1 Pilot requirements

The pilot must:

1. run the exact four-session R161 protocol, both readouts, the same normalization and all six fidelity gates;
2. use a disjoint participant set from the confirmatory sample;
3. return only nuisance information: the joint covariance estimate, variance upper bounds, completion/attrition rates, artifact rates, gate pass/fail summaries and model-diagnostic summaries;
4. keep condition means and R161 confirm/exclude classifications hidden from the scientific decision team until the confirmatory plan is irrevocably frozen;
5. freeze the contrast order, signs, `epsilon`, familywise `alpha`, target planning clearances, missingness target, covariance model, critical-value method, maximum confirmatory sample, code and seed policy;
6. return `PILOT_INVALID_PROTOCOL` if any R161 gate fails, and `DESIGN_NOT_FEASIBLE` if the precision target would require more than the predeclared maximum sample.

Neither status is `BODY_DOMINANT_EXCLUDED`, `neither`, no mineness, or no experience. A redesigned apparatus or analysis is a new protocol version.

The pilot is **external** in the inferential sense: its participants are not reused in the primary confirmatory intervals. This sacrifices efficiency to remove an otherwise nontrivial random-sample-size calibration problem. A later internal-pilot version would require a separately proved/adaptively calibrated test and must not inherit this result by name.

### 5.2 Simultaneous pilot variance precision

Under the explicit working model that complete participant vectors are i.i.d. multivariate Gaussian, let \(S_j^2\) be a pilot marginal variance and \(\nu=n_P-1\). A one-sided variance upper bound is

\[
U_j=\frac{\nu S_j^2}{\chi^2_{\alpha_v/m,\nu}},\qquad m=8.
\]

The union bound gives simultaneous coverage at least \(1-\alpha_v\) for all eight marginal variances. If the pilot precision target is that every upper bound be at most \(\kappa\) times its observed variance, then require

\[
\frac{\nu}{\chi^2_{\alpha_v/m,\nu}}\le\kappa.
\]

For \(m=8\), \(\alpha_v=.05\), and \(\kappa=2\), the smallest complete-pilot size is 36. This is a covariance-precision design point, not a proposed confirmatory sample size, and it is conditional on the Gaussian variance law.

## 6. Frozen confirmatory intervals

Assume the confirmatory sample consists of \(N\) independent, complete, i.i.d. multivariate Gaussian vectors \(W_i\). For component \(j\), use

\[
I_j=\bar W_j\pm t_{1-\alpha/(2m),N-1}\frac{S_j}{\sqrt N}.
\]

Each marginal interval has error at most \(\alpha/m\); therefore the union bound gives

\[
\Pr\{\theta_j\in I_j\text{ for all }j\}\ge1-\alpha
\]

without assuming independence among components. Correlation-aware max-\(t\) or participant-cluster bootstrap intervals may be more efficient, but they are an optional later protocol version unless their small-sample calibration is independently validated and frozen.

Transform any signed interval \([l,u]\) to a magnitude interval by

\[
\mathcal A([l,u])=
\begin{cases}
[0,\max(|l|,|u|)],&l\le0\le u,\\
[\min(|l|,|u|),\max(|l|,|u|)],&\text{otherwise}.
\end{cases}
\]

If \(\theta\in[l,u]\), then \(|\theta|\in\mathcal A([l,u])\). Applying this componentwise preserves simultaneous coverage. R161's min/max aggregate bounds and three-way decision can then be applied without post-hoc cell selection.

## 7. Planning clearance and sample-size screen

Let the frozen planning scenario specify \(a_*\), \(x_*\), and \(\epsilon\), without claiming that they are true. If every magnitude interval has half-width at most \(h\), sufficient clearance for confirmation is

\[
h<a_*-\epsilon,
\qquad
2h<a_*-x_*-\epsilon.
\]

Hence one may freeze

\[
h_*<\min\{a_*-\epsilon,(a_*-x_*-\epsilon)/2\}.
\]

Given simultaneous pilot variance upper bounds, a normal-screen approximation is

\[
N_{screen}=
\left\lceil
\max_j \frac{z^2_{1-\alpha/(2m)}U_j}{h_*^2}
\right\rceil.
\]

The final planned \(N\) must be recomputed with the Student critical value and the frozen cap. At \(\alpha=.05\), \(m=8\), \(h_*=.05\), and illustrative standard deviations `.10,.15,.20,.25,.30`, the normal screen gives `30,68,120,187,270`. These numbers demonstrate sensitivity to variance; they are not a sample-size recommendation because no exact-protocol pilot variance exists.

Power cannot be guaranteed for true parameters arbitrarily near the decision boundary. An unresolved result at the maximum feasible sample is scientifically admissible and must not be converted into exclusion.

## 8. Why independent freezing matters

Independence is not itself a coverage theorem. The missing bridge must be stated separately:

**Planwise coverage premise.** For every pilot record (p) in the declared support and every frozen plan (g(p)), the interval procedure applied to independent confirmatory data has conditional simultaneous coverage at least (1-\alpha) under the declared model and target population. In the simple fallback of §6 this premise is discharged only under complete i.i.d. multivariate-Gaussian participant vectors, the fixed Bonferroni Student family, the frozen contrast order and all six R161 gates. Other interval families, missingness rules or adaptive reuse require their own proof.

### Proposition R162-P2: conditional coverage transports through an independent pilot

Let \(\mathcal P\) be the pilot record, let \(g(\mathcal P)\) choose a frozen confirmatory plan, and suppose that for every plan in the range of \(g\), the confirmatory interval family satisfies

\[
\Pr_\theta\{\theta\in I_{g(\mathcal P)}(C)\mid\mathcal P\}\ge1-\alpha.
\]

Then

\[
\Pr_\theta\{\theta\in I_{g(\mathcal P)}(C)\}
=
\mathbb E_\theta[
\Pr_\theta\{\theta\in I_{g(\mathcal P)}(C)\mid\mathcal P\}
]
\ge1-\alpha.
\]

The planwise premise includes disjoint confirmatory data or another valid conditional-calibration theorem. “Independent” and “blinded” as labels are not sufficient: a misspecified interval remains misspecified on independent data.

**Reuse counterexample.** On 100 equiprobable outcomes, each of two fixed tail tests rejects on five outcomes, so each has size `.05`. If an analyst looks at the same outcome and chooses whichever tail contains it, the adaptive rule rejects on ten outcomes and has size `.10`. This does not model the proposed pilot; it proves why same-data selection requires a valid adaptive correction.

## 9. Missingness and gate boundaries

The simple Student proof applies to complete eight-component participant vectors. Defining the primary population as four-session completers is mathematically clear but scientifically narrower than the recruited population. Extending to all randomized participants requires a separately frozen missingness model, weighting/imputation rule and sensitivity analysis. Neither missing-at-random nor covariance transport from completers is supplied by C1 or by the component datasets.

Participant-level nonresponse must not be deleted merely because it weakens an effect. Safety exclusions, device faults and trial artifacts need outcome-independent rules. Protocol-level failure of a fidelity gate still blocks classification. Attrition beyond a predeclared feasibility bound produces `DESIGN_NOT_FEASIBLE` for the intended population, not a substantive negative.

## 10. Relation to UCT and felt mineness

The covariance and pilot results concern scientific comparison across actual trial tokens. They do not create one common \(h\), identify complete neural organization, or turn a population mean into a within-experience relation.

Conditional on each actual token and A:C1, physically grounded internal relations retain their tokenwise structural interpretation. The external pilot improves whether a finite physical role can be estimated without post-hoc rescue. It does not establish \(B_{min}\), familiar ownership \(F_O\), basal experience, or a unique owner.

## 11. Retained thought experiments

- **Ancestor/formation.** Early organisms can possess tendon-sensitive localization before any rotated-tool learning. Variance estimation of those capacities does not make either a gate for basal experience. Role: formation-order and gate test.
- **Abacus/calculator.** Equal final answers can hide different participant-level covariance between body and tool contrasts. Marginal performance cannot identify joint precision. Role: covariance non-identification witness.
- **Human-realized agent.** Measuring one subgroup's body response and another subgroup's tool response does not create a joint bearer or a cross-person covariance. Role: actual-cluster and bearer test.
- **Copy/swap/memory.** Copy marginal records and swap their unobserved pairing. Every marginal file remains identical while the dominance-difference variance changes. Role: exact joint-identification counterexample; no phenomenal-transfer claim.

## 12. Contribution, failures and next question

The substantive advance is to replace “find a pilot variance” with a typed impossibility and a nonleaking design contract. Public component data cannot identify the required joint covariance; an exact-protocol, independent pilot can estimate it without consuming the confirmatory error budget, provided the final conditional procedure is valid for every frozen plan.

Open failures remain: Gaussianity is unverified; the pilot does not cure pathway impurity; four-session completion may be poor; no missingness model is validated; no practical effect clearance or maximum sample is ethically chosen; Bonferroni intervals may still be wide; and no `B_min/F_O` bridge is supplied.

The next exact question is whether the exact R161 apparatus can meet the six gates and yield a stable eight-dimensional covariance in a small, ethically reviewed feasibility pilot. Before any human work, a simulation protocol should stress-test the frozen complete-vector Student method and candidate missingness extensions under skew, clipping, attrition and order effects. This repository does not authorize recruitment.

## 13. Sources and attribution

- UCT I v1.2 §§8.11–8.14, 10.1–10.3, 11, 12.1–12.4 and 14.6–14.10 supply the physical-witness, bridge, no-rescue and self/subject boundaries.
- Ruttle et al. 2016, DOI `10.1371/journal.pone.0163695`, and OSF `4v6md` supply a public rotated-cursor/localization component source.
- Mostafa et al. 2019, DOI `10.1371/journal.pone.0221861`, data DOI `10.17605/OSF.IO/ZFDTH`, supply a public discrepancy/localization component source.
- Le Franc et al. 2020, DOI `10.1371/journal.pone.0242416`, data DOI `10.17026/dans-znu-5fyx`, supply a public tendon-vibration/visual-context component source.
- Chi et al., *Internal Pilot Design for Balanced Repeated Measures* (2018; PMCID `PMC5768471`) show that nuisance-covariance re-estimation can protect power but that random sample size and small pilot designs require explicit type-I calibration; their balanced Gaussian model does not validate the present protocol.
- Kieser and Friede (2000), DOI `10.1002/(SICI)1097-0258(20000415)19:7<901::AID-SIM405>3.0.CO;2-L`, is prior work on variance-based internal-pilot recalculation with type-I control.
- Max-`t`, Bonferroni/union bounds, Student intervals, Gaussian variance intervals and the tower property are established methods. The project contribution is their typed use to block covariance borrowing and same-data protocol rescue in this UCT application.
