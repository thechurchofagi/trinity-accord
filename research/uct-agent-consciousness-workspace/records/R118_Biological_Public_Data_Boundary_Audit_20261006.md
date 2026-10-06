# R118 — Public biological-data boundary audit and optogenetic session-registry reanalysis

Hongju Liu / UCT research. 2026-10-06.

R117 selected the 2026 Neuron rat evidence-accumulation system as the first real cross-substrate target. R118 audits exactly which biological data are publicly reconstructable from the authors' Figshare and GitHub resources, and independently parses the public optogenetic session registry.

The main result is a correction to the R117 data plan: the public resources contain **two distinct biological data layers**, and they should not be conflated.

## 1. Recording dataset versus optogenetic behavior dataset

The Neuron study used:
- five rats for neural recordings;
- fourteen rats for optogenetic experiments.

The public Figshare dataset contains:
- 12 MATLAB files;
- each file corresponds to a neural recording session;
- the author configuration lists recording rats X046, X062, X087, A294, A297.

These files are appropriate for:
- trial-level auditory click history;
- behavior for those recording sessions;
- FOF/ADS spike times;
- region labels;
- time-resolved evidence decoding.

They are the correct source for R117 B1/B2.

They are **not automatically the complete source for the separate 14-rat optogenetic behavioral experiment**.

## 2. How the author's Figure 3 optogenetic analysis is built

The public repository contains:

    figure3/optodata_FOFSTR.xlsx

and

    figure3/package_pbups_opto_DG.m
    figure3/figure1_metaopto.m.

The spreadsheet is a **session registry**, not a trial table.

It stores fields such as:
- ratname;
- inactivation side;
- control versus experimental session;
- session ID;
- probe;
- stimulation-protocol flags;
- power.

The MATLAB packaging function then calls the laboratory behavioral-control data using:

    ratname + sess_id

and reconstructs trial-level behavior/stimulation variables.

Thus the GitHub spreadsheet alone is insufficient to recompute the Figure 3 psychometric effects.

This is a public-reproducibility boundary that R117 did not state sharply enough.

## 3. Independent parsing of the public XLSX

The 48,588-byte XLSX at Git blob:

    bd94bed6af1ef59929615001fa6d2d4c21814eb1

was fetched from the public author repository and parsed directly in the connector runtime.

Raw registry rows:

    309.

Headers:

    ratname
    inact_side
    prot
    cntrl
    sess_id
    probe
    stim_2sec
    stim_1
    stim_2
    stim_3
    stim_4
    stim_5
    power
    video_verify.

Rats present:

    X008, X002, X013, X025, X026, X011, X033,
    X044, X042, X048, X050, X037, X038.

## 4. Independent reproduction of the author's exclusion rule

The Figure 3 MATLAB script defines:

    exclude =
      probe != 0.6
      AND rat != X025
      AND rat != X038
      AND rat != X011.

Applying that exact rule to the public registry gives:

    222 sessions retained.

Breakdown:

    experimental/inactivation (cntrl=0): 165
    control (cntrl=1):                57

Inactivation side:

    left:  139
    right: 83.

Retained sessions by rat:

    X008  24
    X002  48
    X013   9
    X026  21
    X033  35
    X044  26
    X042   5
    X048  17
    X050  19
    X037  18.

This independently verifies the session-selection layer used by the public Figure 3 code.

It does **not** reproduce trial-level psychometric effects.

## 5. Exact temporal stimulation classification in author code

The packaging code classifies stimulation trial-by-trial from actual event timing.

Relevant values:

    optoval=0  no stimulation
    optoval=1  whole trial, 2 s
    optoval=2  pre-stimulus
    optoval=3  first half of stimulus
    optoval=4  second half of stimulus
    optoval=5  memory period
    optoval=6  movement epoch.

The Figure 3 analysis explicitly compares:

    1 = whole trial
    3 = first half
    4 = second half.

This is important because the cross-substrate comparison should use actual event timing, not infer perturbation timing from a generic session label.

## 6. Corrected B1–B3 reproducibility status

### B1 — psychophysical temporal kernel

**Potentially reproducible from public recording-session Figshare data.**

The 12 recording files contain click timing and choices.

Still pending local binary transfer.

### B2 — FOF/ADS cumulative-evidence decoding

**Potentially reproducible from public recording-session Figshare data.**

The same files contain spike times, regions and trial events.

Still pending local binary transfer.

### B3 — large optogenetic behavior effect

**Not fully reconstructable from the currently inspected GitHub files alone.**

The public GitHub registry identifies sessions and the public MATLAB code defines the trial-selection/analysis, but the package function obtains trial behavior from the laboratory behavioral-control data source.

Unless those BControl trial records are independently public/materialized elsewhere, a complete trial-level Figure 3 replication cannot be claimed from the repository alone.

The paper's peer-reviewed perturbation result remains usable as published biological evidence.

## 7. Scientific consequence

This data boundary does not weaken the biological paper's result.

It changes the **independent evidence level** available to this project.

For R117/R118:

- public paper result: biological perturbation evidence;
- public session registry: independently audited;
- public analysis logic: independently audited;
- raw recording data: public but not yet transferred into current execution environment;
- complete optogenetic trial behavior: not found in the current public repository/dataset audit.

Therefore T2 cross-substrate mechanism correspondence remains:

    PARTIAL / PROMISING,

not independently reproduced.

## 8. Why this matters methodologically

Cross-substrate research is especially vulnerable to evidence-level inflation.

It would be easy to write:

> "the authors released the data, therefore we reproduced the perturbation result."

That is false.

R118 separates:

1. paper-level published evidence;
2. public metadata/session registry;
3. public raw neural-recording sessions;
4. external/not-yet-materialized optogenetic trial data;
5. our independently executed artificial experiment.

This provenance separation should remain standard in later biological comparisons.

## 9. Updated minimal path

The most efficient next empirical path is now:

### Phase 1
Obtain `Cells.zip`.

Run only:
- B1 temporal psychophysical kernel;
- B2 FOF/ADS evidence decoding.

This is sufficient to independently validate the biological content/state side of the selected support relation.

### Phase 2
Use the paper's peer-reviewed projection perturbation as biological causal evidence unless public trial-level optogenetic data are separately located.

Do not delay the entire research program waiting for perfect Figure 3 reconstruction.

### Phase 3
Compare B1/B2 with the already executed R117 artificial kernel/state/pulse signature.

## 10. Next formal step

Because B3 raw replication is not currently guaranteed, R119 should formalize exactly what constitutes a **T2 intervention-preserving support correspondence certificate**.

The certificate must specify:
- grounded input/history;
- selected state/support relation;
- matched intervention family;
- matched downstream causal variable;
- error/tolerance domain;
- nuisance/background controls.

Then future B1/B2/B3 or other biological data can plug into that certificate without changing the theory.

## 11. Status

R118 is a derived-data/public-reproducibility audit and correction.

It independently parses the authors' session registry and reproduces the public exclusion/session-count layer.

It does not claim trial-level optogenetic replication.
