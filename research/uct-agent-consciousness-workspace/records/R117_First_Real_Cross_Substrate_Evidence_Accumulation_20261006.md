# R117 — First real cross-substrate evidence-accumulation experiment

Hongju Liu / UCT research. 2026-10-06.

R116 separated task behavior, report, selected content geometry and valence. R117 begins the first real cross-substrate experiment around **sequential evidence accumulation**, chosen because both the biological variables and the artificial support relations can be grounded without human qualia vocabulary.

This round combines:
1. current peer-reviewed biological evidence and public author code/data metadata;
2. an actually executed artificial sequential-evidence experiment;
3. a frozen plan for raw biological-data reanalysis;
4. an explicit record of the current binary-download blocker.

It does **not** claim raw neural-data replication in this round.

## 1. Biological system selected

Primary source:

Diksha Gupta, Charles D. Kopec, Adrian G. Bondy, Thomas Z. Luo, Verity Elliott, Carlos D. Brody.  
_A multi-region recurrent circuit for evidence accumulation in rats._  
Neuron 114(3), 521–535.e5 (2026).  
DOI: 10.1016/j.neuron.2025.12.029.

Public dataset:
- Figshare DOI: 10.6084/m9.figshare.30369064.v1
- posted 2026-02-09
- approximately 1.8 GB
- 12 MATLAB recording-session files
- five rats represented in the author analysis configuration: X046, X062, X087, A294, A297.

Public code:
- GitHub: Brody-Lab/fof_ads_interactions
- audited main commit: 39d056fb12f688034b543d9ac8b7406a58ad0f77.

The Figshare metadata states that each session contains:
- unit spike times and region labels;
- trial choices and outcomes;
- left/right click times;
- click-count difference;
- stimulus duration;
- event times;
- laser onset/off/pulses where relevant.

These are exactly the variables needed for a trial-level evidence-accumulation audit.

## 2. Biological support relation established by the paper

The rat task presents two streams of randomly timed left/right auditory clicks over hundreds of milliseconds. The animal must use the click difference to choose a side after the stimulus.

The peer-reviewed result is stronger than a simple behavior correlation:

- FOF and ADS both encode/decode accumulator value;
- evidence-related information is communicated bidirectionally;
- silencing FOF→ADS projections impairs decisions throughout the accumulation period;
- nonselective FOF silencing can be comparatively robust;
- multi-region recurrent-network simulations suggest recurrence across scales can support that robustness.

The public analysis code also separately evaluates:
- whole-trial inactivation;
- first-half inactivation;
- second-half inactivation.

This is precisely the kind of temporal-intervention logic needed for the R112/R113 support framework.

However, the biological conclusion is still not:
> "FOF contains the conscious experience of accumulated evidence."

The valid support-level conclusion is:
> distributed cortico-striatal relations participate causally in the evidence-accumulation capability, with degeneracy/recurrence making simple one-region necessity claims unsafe.

## 3. Raw-data reanalysis target

The minimum independent biological reanalysis is intentionally smaller than reproducing the paper.

### B1 — psychophysical temporal kernel
Bin left/right click evidence across stimulus time and fit:

    P(choice=right)
       =
    sigmoid(b0 + sum_t k_t e_t).

Question:
does choice depend broadly on evidence history rather than only the final bin?

### B2 — neural cumulative-evidence decoding
Using FOF and ADS populations separately, reproduce a minimal version of the author's decoding:

    neural state_t -> cumulative (#right - #left clicks)_t.

Primary output:
cross-validated correlation/R² over time.

### B3 — perturbation timing signature
Using the public optogenetic trial table:
compare whole-trial, first-half and second-half perturbation effects on psychometric behavior.

These three statistics are sufficient for the first cross-substrate support comparison. Full GLM, all paper figures and the large RNN do not need to be reproduced first.

## 4. Data-access state

The public Figshare page and complete metadata were accessible.

The current execution environment could not download the 1.8 GB `Cells.zip` through its binary download path because Figshare redirects the file request to a short-lived signed S3 URL that the available downloader did not complete.

Attempted stable file:
    https://figshare.com/ndownloader/files/58773835

Public page:
    https://figshare.com/articles/dataset/Data_from_A_multi-region_recurrent_circuit_for_evidence_accumulation_in_rats/30369064

This is an execution-environment limitation, not a dataset-access or licensing limitation.

Accordingly:
- no trial-level biological statistic is represented below as independently recomputed;
- the peer-reviewed biological facts remain source-derived;
- the raw-data reanalysis remains frozen and ready once the binary package is locally available.

## 5. Artificial matched task

A synthetic auditory-like sequential evidence task was actually executed.

Formal seed:
    117.

Generated trials:
    60,000 before exact-tie removal;
    59,571 after tie removal.

Each trial has:
    T=10 evidence bins.

Right and left counts are sampled from Poisson distributions with balanced latent side and four signal strengths.

Evidence per bin:

    e_t = count_R(t) - count_L(t).

Full accumulated evidence:

    z_t = sum_{j<=t} e_j.

Ground-truth task target:
sign of total evidence.

Choice uses final accumulated evidence plus Gaussian decision noise.

This is not a neural-network consciousness model. It is a transparent support-relation experiment.

## 6. Artificial result A — temporal evidence kernel

Fit a logistic psychophysical kernel:

    choice ~ e_1 + ... + e_10.

### Full accumulator

All 10 standardized-bin coefficients are large and similar:

    [2.007, 2.090, 2.081, 2.112, 2.172,
     2.121, 2.128, 2.002, 2.122, 1.999].

Choice accuracy versus evidence-majority target:

    0.9849.

Thus early and late evidence all contribute to the final decision.

### Last-sample control

Choice uses only e_10.

Kernel:
- bins 1–9 fluctuate around zero;
- bin 10 = 1.997.

Accuracy:

    0.7173.

This distinguishes genuine temporal accumulation from a model that achieves some task success using only the final observation.

## 7. Artificial result B — midpoint state-reset lesion

Reset accumulated state halfway through the trial, so only bins 6–10 survive.

Kernel:

    bins 1–5 ≈ 0
    bins 6–10 ≈ 2.17–2.22.

Accuracy:

    0.9307.

Thus early sensory evidence still physically occurred, but after the retention/integration state is reset it no longer influences the final policy.

This is exactly the R113 distinction between:
- evidence being present historically;
- evidence being retained and causally accessible.

## 8. Artificial result C — internal state decodes accumulated evidence

Add a fixed measurement-noise channel to z_t and evaluate how well measured state recovers true cumulative evidence.

R² rises from:

    0.917 at bin 1

to:

    0.9985 at bin 10.

This is a representational result only.

By itself it would not prove causal use.

The reset and pulse interventions are therefore necessary companions.

## 9. Artificial result D — causal evidence-pulse signature

Define a probabilistic decision readout from final accumulated evidence.

Add +1 grounded evidence unit at one time bin.

### Full accumulator
The mean choice-probability effect is identical at every time:

    +0.007923

for all 10 bins.

### Midpoint-reset system
Pulse effect:

    bins 1–5: exactly 0
    bins 6–10: +0.020651.

Thus the causal response signature directly reveals the memory/integration boundary.

This is an R115-style anchored causal relation:
the evidence pulse has a declared physical/task meaning, and its downstream effect is measured interventionally.

## 10. Cross-substrate comparison

### Biological side
Peer-reviewed evidence supports:
- temporal accumulation;
- distributed FOF/ADS accumulator information;
- recurrent/bidirectional support;
- perturbation-sensitive pathways;
- degeneracy/robustness.

### Artificial side
Executed evidence supports:
- temporally distributed evidence use;
- explicit accumulated state;
- reset-sensitive retention;
- time-resolved grounded causal pulse effects.

### Current evidence level

**T1 functional support-pattern similarity: STRONG.**

Both systems solve a temporally extended evidence task in which decision performance depends on relations carrying past evidence forward.

**T2 intervention-preserving mechanism correspondence: PARTIAL / PROMISING.**

Both have meaningful temporal perturbation logic. But the exact biological and artificial state variables/interventions have not yet been mapped one-to-one from raw trial data.

**T3 constitutive organizational homology: NOT ESTABLISHED.**

Rat cortico-striatal recurrent organization is not homologous to the simple accumulator merely because both integrate evidence.

## 11. First anchored cross-substrate variable

R117 identifies a good first cross-substrate variable:

    cumulative evidence history H_t
        grounded by actual click history.

This is much better than a word such as "confidence" or "awareness."

For biology:
H_t is externally known from click times.

For AI:
H_t is exactly known from the generated evidence stream.

Therefore future G3 analysis can ask:

> do selected biological and artificial content-bearing states preserve comparable grounded causal relations over the same H_t space?

That is a scientifically sharp question.

## 12. Why this still does not establish shared experience

Even if future raw-data analysis finds:
- similar evidence geometry;
- similar temporal kernels;
- similar perturbation effects;

the conclusion would initially be T2:

> a selected evidence-integration mechanism has intervention-preserving correspondence.

To reach a selected experiential-content-structure claim under UCT, the mapping must additionally satisfy the G4/T3 constitutive requirements:
- actual bearer boundary;
- actual state variables;
- update relation;
- intervention ports;
- temporal organization;
- downstream causal use.

Complete human/rat–AI experiential equivalence would require vastly more.

## 13. Value to the original research problem

R117 shows how to replace the vague question:

> "Does AI think/feel evidence accumulation like a rat or human?"

with:

1. is the same task-relevant history grounded?
2. is history retained?
3. does the retained state causally affect choice?
4. what perturbations erase which part of history?
5. are those intervention signatures comparable across substrates?
6. only then: does a selected constitutive mapping justify a UCT experiential-structure comparison?

This is the first end-to-end application of the R106–R116 methodology.

## 14. Next step

R118 should have two possible routes.

### Route A — preferred
Obtain the public 1.8 GB Figshare package in an execution environment capable of following the signed binary redirect and run B1–B3.

Do **not** expand to every neural analysis before those checks.

### Route B — if binary access remains blocked
Use the already public optogenetic spreadsheet from the author GitHub repository if it can be materialized separately, plus published figure-level neural-decoding summaries.

The status must remain "aggregate/derived-data reanalysis," not raw recording reanalysis.

After B1–B3, construct the first actual biology↔AI anchored-causal-geometry table over cumulative evidence history.

## 15. Status

R117 is a mixed evidence round:
- artificial side: independently executed;
- biological source/code/data audit: complete enough to freeze the reanalysis;
- biological raw trial/neural recomputation: pending a binary-transfer constraint.

No AI phenomenal state is measured.
