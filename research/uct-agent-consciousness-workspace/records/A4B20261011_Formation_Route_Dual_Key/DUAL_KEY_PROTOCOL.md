# A4B dual-key intervention contract

## Scope

This contract separates a randomized formation effect from actual retained-route use. It is applicable first to organizational endpoints. An H-level application requires a separately valid phenomenal endpoint identity contract.

## Key F — randomized formation

1. Declare bearer, formation window, intervention \(F\), endpoint \(J\), intact test regime and estimand before assignment.
2. Randomize before formation and record allocation integrity.
3. Estimate \(\tau_0=E[J(1,0)-J(0,0)]\) using baseline variables only.
4. Do not match, stratify or adjust on post-formation descendants merely to make mature systems look alike.
5. Report nonadherence, loss and missingness; randomization does not repair post-assignment selection.

## Key R — actual same-event route

All six premises are simultaneous:

1. **Bearer:** the current event belongs to the declared actual bearer.
2. **Precedence:** the formation occurrence actually happened earlier.
3. **Continuation:** a retained trace connects that occurrence to the current event.
4. **Consumer:** a named current component consumes the trace.
5. **Read/use:** the exact current event opens/reads and uses that trace.
6. **Faithful perturbation:** blocking the read changes no independent endpoint route except through that trace, within the declared model/domain.

The route probe randomizes \(D\) independently of \(F\), preserves an event-level read ledger, and reports the four \(F\times D\) cells. A nonzero interaction without premises 1–6 is insufficient. A verified read without a faithful perturbation supports occurrence, not causal necessity.

## Two-block prospective design

- **Primary intact block:** randomize \(F\); keep the later route unperturbed; estimate the formation effect without post-formation adjustment.
- **Diagnostic route block:** independently randomize a calibrated trace-specific \(D\); log exact read/use and test the predeclared route contrast or interaction.

The blocks must not be pooled if the route manipulation changes strategy, report policy or endpoint meaning. A human study must predeclare whether its endpoint is organizational, behavioral, report-based, or a separately anchored phenomenal target.

## Decision table

| Formation key | Route key | Licensed conclusion |
|---:|---:|---|
| no | no | No formation-sensitive retained-route result |
| yes | no | Formation changes the endpoint; retained route remains unshown |
| no | yes | Trace is actually used; net formation effect may cancel or be absent |
| yes | yes | Formation-sensitive retained-route organization in the declared domain |

Even the final row does not establish H, complete physical constitution, C1, a unique subject, or a language-report identity.

## Software installation parameters

- bearer: `A4B-software-bearer-v1`
- current consumer: `A4B-later-consumer-v1`
- declared seed: `2026101101`
- primary block: eight \(F=0\) and eight \(F=1\) trials, randomized order, \(D=0\)
- diagnostic block: four trials per \(F\times D\) cell, randomized order
- endpoint: exact integer `endpoint_j_org`
- bypass under \(D=1\): `0`
- copy challenge: equal retained value with foreign bearer identity must be rejected

Run with:

```bash
python records/A4B20261011_Formation_Route_Dual_Key/run_dual_key_study.py run
```

