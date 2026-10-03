# A weak cancellation-only budget fails already in five dimensions

Status: exact counterexample to D+K>=N/8, and fixed-metric insertion audits.
The main M_n problem remains open. Negative cycles are not omitted from
the true run identity R_min=1+D+K+phi.

The genuine generic n=5 weights (16,1,6,8,4) have D=0,K=2,W=26.
Thus D+K=2<N/8=4. The exact ancestor optimum is E_max=14, phi=6,
R_min=9, attained with mask 2048. The actual rank still meets the quarter
bound. The same low budget occurs for (1,6,16,8,4) and (1,6,8,16,4).

probe_paired_weak_dk_budget.py checks every generic real new-coordinate
weight and every numerical insertion position, for each of the 336
previously audited positive four-dimensional representative vectors.
All critical new weights are exact old score differences. Integer
midpoints after rescaling by two cover every open interval, including
the final unbounded interval; critical values themselves have ties and
are excluded. This covers listed one-parameter slices, not complete
five-dimensional chambers or all metrics in a parent chamber.

There are 1680 slices. Higher-dimensional pressure adds genuine positive
samples and local one-coordinate mutations through n=12. Total generic
evaluations 35641, ties rejected 3686. Six sub-N/8 proposals occurred,
all in the real slices at n=5, yielding the three normalized metrics
above. All retained rank minima use exact ancestor optimization and
direct integer run counting. Seed 202610031124, runtime 2.498609638
seconds, evaluated digest
aabed2c3b3cb41f0f02615cfb33159a6b54d5b81488a7771ac4fdd6e7b8ca2ac.
No lower bound is inferred from absence of further finite counterexamples.

probe_paired_weak_dk_extensions.py immediately continues these three
metrics, checking all generic real insertions at every position and
retaining up to four minimal metrics at each step. Its 6698 exact
slice evaluations in n=6,7,8 retain D+K=2 at every dimension, for example

    (32,16,1,6,8,4),
    (64,32,16,1,6,8,4),
    (128,64,32,16,1,6,8,4).

Their exact family minima are 17,33,65 respectively. These are not
all-dimensional assertions until the following periodic-order proof
is completed. Runtime .949206405 seconds; evaluated digest
41d6d10c90444d609ebc94c1685d952e33812d5db2e011ea7bc8cabb897fef39.

The complete first slice report is saved losslessly as
paired_weak_dk_pressure.json.gz; the source regenerates its plain JSON
and compressed copy. The second report is paired_weak_dk_extensions.json.
The logs and parameters are retained. No process from either probe is
still running.

Next proof gap: let T=2^(k-4) and put a low binary tail with score step
16 BELOW the fixed top core (1,6,8,4). Core scores give one vertex in
each residue modulo 16, with scores 18,19 spilling into the next block.
The core-word scan appears periodic, giving D=0,K=2 independently of T.
Appending ONE dominant highest coordinate then appears to give D+K=4
and half cut lambda=1 in every dimension, excluding ALL positive-density
cut-only budgets, not merely the quarter or eighth constants. Prove the
periodic raw coupling formula, verify the complete integer graphs, and
retain internal cycles and an exact attaining mask before claiming this.
