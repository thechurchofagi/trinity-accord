# Exact finite classification proof

## Proposition

Among deterministic Boolean pairs `r=f(x,a)`, `y=g(r,a)`, exactly four recover `y=x` for every input. Exactly two are nontrivially bearer-centred and two are anchor-insensitive.

## Proof

Fix `a`. Recovery of both target values requires `g_a(f_a(0))=0` and `g_a(f_a(1))=1`; therefore `f_a(0)` and `f_a(1)` are distinct. A bijection on one bit is either identity or complement, so for a unique `c_a`, `f_a(x)=x XOR c_a`. Its only inverse is itself, hence `g_a(r)=r XOR c_a`.

Choosing `c_0,c_1` independently yields four pairs. If `c_0=c_1`, changing `a` at fixed `x` changes neither the route code nor the consumer law. If `c_0!=c_1`, changing `a` flips `r`, and co-flipping `r` and `a` leaves `g(r,a)` unchanged. The latter two pairs meet the nontrivial bearer-centred contract in this finite view. No other perfect pair exists by the sectionwise inverse argument. QED.

## Computational cross-check

`check_bearer_coordinate.py` exhausts all `16*16=256` pairs and confirms the four-pair normal form, the `2+2` split, shared route use, the separating anchor and joint-compensation contrasts, and a constant-route vacuity counterexample. `EXACT_RESULTS.json` records the full four-pair table.

The proof is general only for this declared one-bit deterministic class. The program is a cross-check of that proof, not an argument about arbitrary dimensions, noisy systems, actual body frames or experience.
