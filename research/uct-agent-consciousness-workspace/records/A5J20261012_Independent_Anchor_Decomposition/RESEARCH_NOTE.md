# A5J Research Note — Independent-Anchor Decomposition

## Result in one sentence

Factorially separating physical contact `P` from nuisance cue `C`, and obtaining two channels that both follow `P`, excludes a direct-`C` explanation but does not establish an independent phenomenal anchor: in the declared finite family, target identity `H=P` additionally requires a semantic source-diversity premise and a common-orientation premise, neither of which is supplied by channel multiplicity or accuracy.

## Objects kept distinct

- `P`: actual contact location in the fixed same-participant/tool calibration domain.
- `C`: a nuisance mechanical or sequence cue independently crossed with `P`.
- `H`: a selected particular experiential-location target, not basal experience or a report.
- `Z,A`: two observed channels, each selecting `H`, `P`, or `C` and optionally complementing the selected bit.
- channel hardware: the physical apparatus that produces a record; it is not identical by definition to a semantic source selector.
- `Y`: any later report, pointer movement, or keypress; it remains downstream.

The problem is whether an anchor reaches an experience-internal target, not whether tool-contact position is decodable.

## Stable result A5J-D1

**ID:** `A5J-D1-INDEPENDENT-ANCHOR-DECOMPOSITION`  
**Type:** domain-bounded identification proposition with exhaustive finite proof.  
**Status:** proved for the declared model; disabled as a UCT graph premise; not a novel mathematical theorem or an empirical result.

### Full proposition

Let `P,C∈{0,1}` occur in all four factorial combinations. Let the selected target law `H(P,C)` be one of `P`, `1-P`, `C`, `1-C`, `0`, or `1`. Let each named channel `j∈{Z,A}` select one source `q_j∈{H,P,C}` and use one polarity `o_j∈{0,1}`, with output `j=q_j xor o_j`. Suppose the observed table is `Z=A=P` on every factorial cell.

Then:

1. the observation admits exactly 12 models and all six target laws;
2. the mere fact that `Z` and `A` are different named or physical channels removes no model;
3. the semantic-source-diversity premise `SD: {q_Z,q_A}={H,P}` leaves four models and target laws `H=P` or `H=1-P`;
4. the common-orientation premise `CO: o_Z=o_A` alone leaves ten models and all six target laws;
5. `SD AND CO` leaves two selector-swapped models, both with `H=P`;
6. consequently, `SD` and `CO` are individually necessary relative to the other for identification of the target law, while the named identity of the `H`-reading channel remains unidentified.

### Proof

Exhaust the six target laws, three selectors and two polarities for each channel. A direct positive `P` reader fits every target law. If `H=P`, either `H` or `P` can drive either channel with positive polarity; if `H=1-P`, either source can drive a channel but the `H` reader must complement. For `H∈{C,1-C,0,1}`, factorial variation makes `H` and `C` unable to equal `P` on every cell, so each fitting channel must read `P` directly. These cases total `4+4+1+1+1+1=12`.

`SD` forces one `H` reader and one direct `P` reader. Only `H=P` with both positive, or `H=1-P` with the `H` polarity complemented, fit, giving two channel assignments for each target law and four models. `CO` removes the complemented mixed-source pair, leaving the two assignments with `H=P`. Exhaustive counts and witnesses are in `check_anchor_decomposition.py` and `EXACT_RESULTS.json`.

### Countermodels

- **Direct-position twin:** set both channels to read `P`; any of the six `H` laws remains compatible. A second sensor does not help when both can use the same semantic bypass.
- **Complemented phenomenal twin:** one channel reads `P` positively; the other reads `H=1-P` with negative polarity. Both outputs equal `P` in all four cells despite the opposite target law.
- **Selector-swap residual:** under `SD+CO`, `Z` may read `H` and `A` read `P`, or vice versa. The target is fixed but the mechanism label is not.

## What changed relative to A5I

A5I correctly required a source-discordant calibration `D`, selector transport `S`, and orientation transport `O`. A5J shows that the proposed implementation of `D` must itself be decomposed:

1. factorial `P×C` data supply cue exclusion (`F`), not target-source inclusion;
2. an independently warranted `H` path plus a direct `P` path supplies semantic source diversity (`SD`);
3. prospective polarity alignment supplies common orientation (`CO`).

Calling `F` an “independent `H=P` anchor” would therefore be circular. `F` can defeat a direct-`C` channel. It cannot distinguish an `H` reader from a direct-`P` reader. `SD` names the missing phenomenal admission; `CO` blocks the global complement.

## Empirical scope

The held-stick literature makes the direct-physical route a live alternative rather than a contrivance. Miyazaki et al. (2010) provides a held-stick rabbit paradigm with pointer reports. Miller et al. (2018) shows that tool vibrations encode impact location, and Miller et al. (2019) reports rapid held-tool location processing and EEG decoding. Wada et al. (2020) further constrains stick-mediated rabbit effects. These findings motivate `P`/mechanical routes but do not label a channel as an infallible `H` reader. Blankenburg et al. (2006) supplies skin-rabbit/S1 evidence, not a same-instance held-tool phenomenal localizer.

## Positive design consequence

A prospective same-participant design should treat three achievements separately:

1. realize the complete `P×C` crossing and reject channels that follow `C`;
2. justify source diversity by a target-relevant cut/rescue, swap, or independently grounded bridge that can fail—different hardware is insufficient;
3. precommit polarity and test it under a manipulation that could expose complementation.

Even a successful package establishes only the declared selected-target bridge. It does not derive C1, prove a unique owner, or make decoding, language, self-modeling, integration, recursion, report, or accurate prediction a condition for basal experience.

## Direction check after result formation

The result advances the central experience–intelligence–self question by showing exactly where accurate intelligent discrimination of bodily/tool events stops short of identifying the location-content of experience. It keeps the proposed `H` inside experience, preserves actual organization and source relations, and makes the remaining phenomenal premise criticisable instead of hiding it in the word “independent.”
