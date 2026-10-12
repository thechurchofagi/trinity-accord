# A5I Research Note — The Calibration-Transport Barrier

## Result in one sentence

A frozen channel that is accurate on veridical tool contacts does **not** thereby become a target-specific readout of tool-rabbit experience: if target location and physical/cue location were co-aligned during calibration, an experience-reading channel and a cue-reading channel are observationally identical there, and either a context switch or a polarity switch can reproduce the transfer output.

## Objects kept distinct

- `P`: actual distal contact location in the veridical context `V`.
- `X`: sequence/cue location in the illusion context `I`.
- `H_c`: the selected particular experiential-location target in context `c`; it is neither basal experience as such nor a verbal report.
- `C_c`: an experimentally available contextual cue (`C_V=P`, `C_I=X` in the ordinary calibration).
- `Q_c in {H,C}`: which source class the measurement channel selects.
- `o_c in {0,1}`: the channel orientation.
- `Z_c`: channel output; the proposed bridge datum.
- `Y`: a later report or keypress, which remains downstream and is not used to define `H`.

This note concerns the validity of a bridge to a particular experiential target. It does not add a condition for basal experience and does not decide whether any present assistant is conscious.

## Stable result A5I-D1

**ID:** `A5I-D1-CALIBRATION-TRANSPORT-BARRIER`  
**Type:** domain-bounded identification proposition; exact finite proof.  
**Status:** proved for the declared binary model; not a global UCT theorem and not a claim of mathematical novelty.

### Full proposition

Let `V` contain binary actual contacts `P`, with `H_V=C_V=P`, and let the observed calibrated output be `Z_V=P`. Let `I` contain binary sequence positions `X`, with `C_I=X`, and let the transfer output be `Z_I=X`. In `I`, allow `H_I` either to track `X` with either pole or to be invariant. Let `Z_c` read either `H_c` or `C_c`, with a context-indexed binary orientation.

Then:

1. the observations alone admit 12 exact models and all four target hypotheses (`tracking:0`, `tracking:1`, `invariant:0`, `invariant:1`);
2. ordinary freezing of the fitted function does not exclude a model with `Q_V=H`, `Q_I=C`, and invariant `H_I`;
3. in this domain, the conjunction of all three premises below leaves exactly one model, `H_I=X` with the same target source and orientation in both contexts:
   - **D — source-discordant calibration:** calibration independently fixes `Q_V=H`, rather than merely fitting a condition where `H_V=C_V`;
   - **S — selector transport:** `Q_I=Q_V`;
   - **O — orientation transport:** `o_I=o_V`;
4. each premise is individually necessary relative to the other two: dropping D leaves 5 models, dropping S leaves 5, and dropping O leaves 2.

### Proof

The checker exhausts target kind, target parameter, selectors, and orientations. In `V`, because `H_V=C_V=P`, exact `Z_V=P` forces only `o_V=0`; it cannot select between `Q_V=H` and `Q_V=C`. In `I`, `Q_I=C,o_I=0` fits `Z_I=X` for any target hypothesis (four models), while `Q_I=H` fits the two tracking hypotheses by matching orientation to the target pole. Multiplying by the two observationally equivalent `V` selectors yields 12.

D removes the cue selector in `V`; S transports that source choice; O transports the already fixed positive orientation. Their conjunction therefore leaves `Q_V=Q_I=H`, `o_V=o_I=0`, and only `H_I=X`. The checked witnesses show why every two-premise subset fails. See `check_context_transport.py` and `EXACT_RESULTS.json`.

### Counterexamples

- **Context switch:** calibration reads `H`, illusion readout reads `X` directly, and `H_I` is invariant. All observed outputs are unchanged.
- **Co-aligned cue channel (drop D):** both contexts read their contextual cue with fixed orientation; `H_I` is invariant.
- **Polarity switch (drop O):** both contexts read `H`, but `H_I=1-X` and the channel flips orientation in `I`.

### Thought-experiment role

The copy/swap family is used as a **countermodel generator**: keep every recorded calibration and transfer value fixed while varying the hidden selector or its pole. The ancestor/formation family is used as a **non-retroactivity check**: later acquisition of a stable tool channel cannot change what earlier actual process constituted an earlier experience. The abacus/calculator and human-implemented-agent families are **scope checks**: externally correct decoding or implementation by another system does not establish actual target ownership.

## What the empirical literature does and does not supply

Miyazaki et al. (2010) supplies a held-stick rabbit effect with pointer reports; it does not supply a target-specific neural channel. Blankenburg et al. (2006) links skin rabbit trials to somatotopic S1 activity, but its localizer is not a held-tool target localizer. Miller et al. (2019) is directly relevant because held-tool impact location was decodable from EEG and attributed to vibratory patterns, while related work by Miller et al. (2018) showed that tool mechanics themselves encode impact location. Those positive results sharpen, rather than dissolve, the barrier: a frozen decoder can faithfully read an actual mechanical cue without thereby reading the location of a particular experience in an illusion trial.

## Positive design consequence

The next experiment should not merely train on real impacts and test on rabbit sequences. It needs an explicit `all_of(D,S,O)` contract:

1. **D:** within the calibration family, factorially cross actual impact location `P` with a nuisance sequence/mechanical cue `C`, and require the preregistered `Z` to follow `P` rather than `C`. This is evidence against a direct cue route, not by itself proof that `Z=H`.
2. **S:** predefine what makes the measurement path the same source selector across `V` and `I`; same electrodes, weights, and participant are insufficient if the represented variable can change with context.
3. **O:** freeze and prospectively test the direction/pole, rather than choosing a label permutation after viewing illusion data.
4. Cross the response mapping as in A5H, but keep it downstream: it blocks fixed-key policies, not direct `X -> Z` paths.
5. Include a cue-only/bypass contrast that can make the proposed target channel fail. If the channel simply follows the nuisance cue when actual target anchoring is dissociated, the target-specific claim is rejected.

Even if every item passes, the result remains a bridge claim about the selected target in the declared domain. It neither derives C1 nor turns classifier success into a basal-experience requirement.

## Direction check after result formation

The result returns to the experience–intelligence–self question by locating a concrete explanatory debt in a proposed bodily mineness bridge: accurate intelligent discrimination of tool events is not yet identification of where an experience is located or felt-as-mine. The advance is therefore a sharper separation of organisation, target experience, and report—not a new performance benchmark.
