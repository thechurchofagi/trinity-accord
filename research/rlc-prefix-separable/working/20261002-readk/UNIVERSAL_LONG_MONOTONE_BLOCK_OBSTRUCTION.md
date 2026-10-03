# Every ranking admits an unbounded consecutive monotone block

Research route audit, 2026-10-03. The original constant-density total-run
target remains open. This elementary construction excludes a maximum-length
shortcut; it is not an upper bound on run complexity.

## Theorem

For every \(n\ge1\) and every bijective ranking
\(\rho:Q_n\to\{0,\ldots,2^n-1\}\), there is a positive generic additive
scan containing a consecutive strictly increasing rank block of \(n\)
vertices. No prefix-separability hypothesis is needed.

**Proof.** Write \(e_i\) for the coordinate unit vertices, \(B=2^n\), and
\[
 \delta_i=B\rho(e_i)+2^i,\qquad
 A=1+\sum_i\delta_i,\qquad w_i=A+\delta_i.
\]
All weights are positive integers. The scores of the layer \(|x|=k\) lie
in \([kA,kA+A-1]\), so cardinality layers are separated. For two distinct
vertices in the same layer, score equality would require
\[
 B\sum_i\rho(e_i)(x_i-y_i)=-\sum_i2^i(x_i-y_i).
\]
The right side has magnitude below \(B\). Thus both sides vanish, and
binary encoding forces \(x=y\), a contradiction. The full scan is generic.
Its first nonzero layer is exactly the \(n\) one-hot vertices. For them,
ordering \(\delta_i\) agrees with ordering \(\rho(e_i)\), because their
distinct integer ranks contribute multiples of \(B\) and the perturbations
have total range below \(B\). This consecutive layer is strictly increasing
in rank, as required. \(\square\)

## Implication and precise limitation

No proposed family of rankings, paired or otherwise, can prove the main
target by showing a dimension-independent bound on the maximum length of
every monotone segment of every additive scan. That property is impossible
for **every** family. The theorem applies to forward Gray ranks as well.

It does not exclude a bounded **average** segment length or positive total
turn density. The constructed protected block has only \(n\) of the
\(2^n\) vertices. A proof of many turns must use a global counting or
packing argument, allowing exceptional long runs.

The mechanism is a familiar elementary affine-independence/cardinality
separation construction, not a claimed new general theory. Its contribution
to this research is the precise all-ranking exclusion of the newly tested
local shortcut. `verify_universal_long_monotone_block.py` verifies all
arbitrary cube rankings through dimension three, all normalized paired
rankings in dimensions four and five, and larger forward-Gray examples.

Next action: return to selected-parent global turn budgets under repeated
cube differences, or a provable conditioning scheme. Do not infer a small
total run count from the one long monotone block.
