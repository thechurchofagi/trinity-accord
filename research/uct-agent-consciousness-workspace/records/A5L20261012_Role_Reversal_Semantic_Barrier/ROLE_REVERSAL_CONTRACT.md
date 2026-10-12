# A5L role-reversal contract

## Typed variables

- `P in {0,1}`: actual physical contact/position coordinate.
- `Q in {0,1}`: prospectively grounded role assignment. Changing `Q` reverses the role while holding `P` and nuisance cue `C` fixed.
- `C in {0,1}`: nuisance cue, fully crossed with `P,Q`.
- `X = P xor Q`: grounded structural role coordinate.
- `R=P`, `A=P`, `Z=P`: A5K physical route and two direct physical references, all preserved under `Q`.
- `H`: selected experience-target law, independently ranged over `P, notP, C, notC, X, notX, 0, 1`.
- `E`: measured endpoint, generated from either direct `X` or `H`, possibly with a binary complement orientation.

## Premise layers

1. **GR**: `Q` is grounded in an actual role reversal, not a renamed label.
2. **VR**: every `P x Q x C` cell is observed and `X=P xor Q` reverses at fixed `P,C`.
3. **KEEP_R**: the same actual `R=P` route remains installed.
4. **KEEP_P**: direct `A=P` and `Z=P` remain available.
5. **F**: endpoint `E=X` in all eight cells.
6. **TS**: the endpoint source is target-sensitive `H`, excluding the direct-`X` writer.
7. **SH**: independently constrain the target-law shape to `H in {X,notX}`.
8. **CO**: prospectively fixed common orientation selects the positive rather than complement pole.

`GR all_of VR all_of KEEP_R all_of KEEP_P all_of F` does not entail `TS`. `TS` is a separate source/measurement premise. In the declared family, `TS all_of SH` leaves the global complement pair and `CO` selects `H=X`.

## Stop condition

If no independent evidence supplies `TS`, stop at the positive organizational result that an actual grounded `X` coordinate has been constructed while `R` and direct `P` remain available. Do not redescribe this as calibration of `H_tip`.
