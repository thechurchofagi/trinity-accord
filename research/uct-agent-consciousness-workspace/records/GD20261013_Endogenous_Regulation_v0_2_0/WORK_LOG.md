# Work log — UCT-GD v0.2.0

Date: 2026-10-13. Request: continue substantive research, not merely plan or add papers. Parent: GD v0.1.0 at commit 2cbcf7167794c9d6a9ee4432c52a42f92802ac4c. The official map remains UCT-MAP-v1.1.2.

## Read and researched

Read the complete supplied GD note, checked the live research-branch head, current research guide v2.3, main research catalog, ERF index, UCT I E2/8.3 passages and A5L note. The catalog has a dated 35-paper count; no claim is made that this older page includes every later published work. No new DOI lifecycle audit was attempted. Compared primary-source semantic information, autonomy, biomolecular feedback and modal stability work. Some sources were restricted or returned 403; the source ledger records actual access. No full 913-node semantic re-audit occurred.

## Substantive steps

1. Identified the remaining difference between externally reading a preserved source and a state actually acting back on its generating physical process.
2. Added explicit sensory and actuator paths to the predecessor's linear-analogue memory filter; did not assert preservation of the old full stochastic laws.
3. Derived exact common/difference blocks and cubic stability conditions. In a fixed parameter family, proved uniform mixing has a finite instability boundary while interface-only routing remains stable.
4. Derived and computed a ranking reversal: maximal bench retention has differential error variance 17.64505849, moderate mixing has 6.26559821 at equal total coupling, while uniform mixing is unstable. These are model quantities, not biological data.
5. Derived a two-state fast-interface covariance and its exact optimum C=sqrt(bs), then the independent-controller-noise generalization. Distinguished limiting optima from finite numerical optima.
6. Checked actuator exchange and paired sensor compensation, a replay negative control, clock/state-coordinate invariances, and nonlinear saturation/constant-load limits.
7. Ran symbolic checks, exact rational checks, complete six-variable numerical dynamics, covariance calculations, independent ODE integration and pulse-energy quadrature. Final verifier was executed twice; primary JSON and CSV match byte for byte.

## Failure retained

The first verifier execution stopped at a symbolic polynomial comparison. SymPy charpoly introduced a symbol without the positive assumptions attached to the supplied z, producing distinct symbols that printed alike. Inspection of det(zI-A) confirmed the polynomial. The verifier was corrected to use that determinant. No scientific formula changed. This was a programming failure, not a hidden discarded mathematical counterexample. It preceded final numerical execution.

## Actual checks

961 rational stability/modal comparisons (250 stable, 711 unstable on that grid), 42 independent ODE/exponential comparisons, 31 full covariance checks, 192 limiting noisy-covariance checks, four exact rational main examples, and three numerical impulse-energy integrals. Grid fractions are not population prevalences. Written proofs establish the general conditional results; tests check implementation.

## Direction and publication judgment

This round establishes positive within-model physical consumption and corrects the temptation to equate longer retention with better regulation. It does not derive autonomous norms, life, subjective ownership or evolutionary history. Feedback tradeoffs and the mathematics have established precedents. Keep this with GD v0.1.0 rather than making a new standalone DOI paper now. Candidate nodes are disabled until proper map integration. C1/U1/P3/E2 and A5L's semantic boundary are unchanged.

## Persistence

The downloadable package contains the full note, executable code, numerical results, review, map candidates, coverage and handoff. Read PERSISTENCE_RECEIPT.json for actual remote status. A future agent must not infer success from this log alone.
