# A4T Proof and Exact Finite Certificate

## Model

At each of two adjacent interfaces, exactly one boundary mode holds:

- `N`: no established stitch;
- `I`: one actual occurrence is physically relayed across the boundary;
- `T`: an actual conversion consumes the upstream occurrence and produces a numerically distinct successor.

Let `V_sc,V_cw` record value equality only. These observation bits do not constrain the ontic mode in the finite abstraction. Hence there are `3 * 3 * 2 * 2 = 36` valid worlds.

Define `route := mode_sc != N AND mode_cw != N` and `strict_identity := mode_sc == I AND mode_cw == I`.

## Proposition 1 — strict identity is not necessary

There are four coherent boundary-mode pairs: `(I,I)`, `(I,T)`, `(T,I)` and `(T,T)`. Only `(I,I)` satisfies strict identity at both boundaries. The other three are directed routes containing at least one transduction. Thus strict identity is sufficient in this abstraction but not necessary.

## Proposition 2 — value equality does not identify lineage

Condition on `V_sc=V_cw=1`. The fiber still contains all nine boundary-mode pairs. Four satisfy `route`; five do not. Therefore value equality at both interfaces entails neither relay nor transductive lineage.

## Proposition 3 — conditional path composition

Represent each local link as a directed path segment in one actual event graph. A relay identifies the adjacent segment endpoint as one grounded occurrence; a transduction adds a directed edge from the upstream occurrence through the conversion event to the successor occurrence. If both boundary stitches exist, ordinary path concatenation yields a directed path from anchor to write. If either stitch is `N`, the local segments need not compose.

This is standard directed-graph reasoning applied to the UCT route contract, not a new graph theorem. It establishes no physical instance by itself.
