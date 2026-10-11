# Proof and Countermodel Record

## Proposition A4S-C2

Let the model vocabulary be five independent Booleans (L_s,L_c,L_w,X_{sc},X_{cw}). Define (T=L_s\land L_c\land L_w) and (R=T\land X_{sc}\land X_{cw}).

There are (2^5=32) valuations. Fixing (T=1) fixes three coordinates and leaves the two stitches free, so exactly (2^2=4) valuations satisfy (T). Exactly one sets both stitches to one and therefore satisfies (R). The other three are countermodels to (T\Rightarrow R).

This is a complete proof for the Boolean abstraction. It is not a theorem that five Booleans exhaust physical routes.

## Joint satisfiability witness

The valuation ((L_s,L_c,L_w,X_{sc},X_{cw})=(1,1,1,1,1)) witnesses joint satisfiability. It does not witness an actual device because no physical occurrences were inspected.

## Direction check

- Valid: stitched route (RRightarrow T).
- Valid by definition in this model: all five predicates (Rightarrow R).
- Invalid: (TRightarrow R).
- Invalid: equal boundary values (Rightarrow X_{sc}) or (X_{cw}).
- Invalid: (RRightarrow H_{cf}), report, conceptual self, or basal experience.

## Failure retained

An attempted stronger claim—“closing A4R's three bypasses plus making all three local links actual uniquely identifies the route”—fails unless boundary-token identity is already included in the local-link syntax. A4S records this as a correction rather than silently redefining A4R.
