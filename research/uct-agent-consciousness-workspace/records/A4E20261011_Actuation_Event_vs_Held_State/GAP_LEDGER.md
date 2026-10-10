# A4E gap ledger

## A4E-G1 — level probe does not witness a current commit

- **Location:** A4D AWC post-arbitration/pre-plant probe clause.
- **Impact:** device-relative current target-route evidence; downstream R172/R173 application remains blocked.
- **Counterexample:** `q=s-`; no-write and target-write both end at `s+=q`.
- **Corrected:** require a verified anti-current challenge or a physically bound commit event.
- **Unresolved:** no actual hardware event witness is installed.

## A4E-G2 — change does not identify source

- **Location:** A4E-C1 attribution step.
- **Impact:** a detected write cannot alone establish target consumer use.
- **Counterexample:** hidden writer and target writer both set `q` when `q!=s-`.
- **Corrected:** A4D writer completeness remains a simultaneous premise.
- **Unresolved:** physical inventory, cut and non-target isolation remain uninstalled.

## A4E-G3 — richer actuator dynamics

- **Location:** finite hold-or-write transition law.
- **Impact:** analog drift, stored energy, autonomous dynamics or asynchronous commits can invalidate the binary inference.
- **Counterexample:** actuator changes after the probe without a declared writer commit.
- **Corrected:** protocol requires a frozen device-specific transition law and clock boundary.
- **Unresolved:** no selected hardware platform or validated law.

## A4E-G4 — phenomenal target

- **Location:** route evidence to familiar bodily/action mineness.
- **Impact:** no inference to `H_way`, `B_fam` or a unique subject.
- **Counterexample:** reflex or purely functional route with identical event evidence.
- **Corrected:** explicit phenomenal stop.
- **Unresolved:** independent target identity and measurement bridge.
