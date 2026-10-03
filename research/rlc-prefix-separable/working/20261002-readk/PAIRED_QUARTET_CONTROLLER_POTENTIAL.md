# An exact controller-conflict potential for two-coordinate elimination

Status: strict all-dimensional accounting identity with bounded local bias
alphabet and a genuine fixed-upper-rank relaxation counterexample. The
constant-density M_n problem remains OPEN. Published v1.0 is unchanged.
Standard finite-state elimination and comparison-sign accounting are
inherited tools. The increment is explicit paired-controller deficit
bookkeeping and an exact restart target, not a new general DP algorithm.

## 1. The constraint lost by the preceding relaxation

Write x=(x0,x1,y), n>=3, F=2^(n-2). Once the paired upper rank B(y) is
fixed, the rank interval of y is4B(y)+{0,1,2,3}. Its local two-bit rank is

    Gray2(x0,x1) XOR (b0(y)+2b1(y)),

where b0(y)=theta0(y) is independent per face, but the ACTUAL paired
constraint is

    b1(y) = y0 XOR theta1(y>>1).

Thus phases in faces2g and2g+1 must be opposite. The scalar quartet
recurrence counterexample discarded this condition and the upper paired
rank. Restoring only the upper rank is still insufficient: the true
five-dimensional weights(33,1,4,8,16), with upper paired mask1, have

    B=(1,0,2,3,6,7,5,4),
    relaxed local minimum5,
    actual paired local minimum12.

The relaxed orientations do not belong to the paired family. This example
is NOT a five-dimensional failure of the paired quarter conjecture or a
counterexample to the main M_n target.

## 2. Face costs separate exactly

Any comparison between distinct faces has sign fixed by B, independent
of local bits, because their rank intervals are disjoint. An internal
comparison sign depends only on the two local bits of that face. Two
adjacent INTERNAL comparisons must be internal to the SAME face, since
they share their middle vertex. Therefore every turn term is either
constant or involves only one face's two bits. This works for ANY event
interleaving, without assuming additive score realizability.

Let C be1 plus the constant cross/cross turn count, and let c_f(b,t) be
the nonconstant turn terms assigned to face f, evaluated at local bits
b0=b,b1=t. Define

    A_f(t)=min_b c_f(b,t), Delta_f=A_f(1)-A_f(0),
    R_relaxed=C+sum_f min(A_f(0),A_f(1)).

Under the paired constraint, the contribution from sibling faces is

    min(A_(2g)(0)+A_(2g+1)(1),
        A_(2g)(1)+A_(2g+1)(0)).

Subtract the two independent minima. If the preferred phases are
opposite, there is no penalty. If their preferences agree, one face
must abandon its preference, costing the smaller absolute bias. Exactly,

    R_paired_min(fixed upper rank)
      = R_relaxed
        + sum_g 1[Delta_(2g)*Delta_(2g+1)>0]
                    * min(|Delta_(2g)|,|Delta_(2g+1)|).

This is an all-dimensional exact identity, not a conjecture. It retains
precisely the omitted controller cost. No floating optimizer is involved.

## 3. A bounded local bias alphabet

Changing one face phase affects only turns with a middle vertex in that
four-vertex face. There are at most four, so changing t at fixed b changes
cost by at most4. Minimization over b preserves this Lipschitz bound:

    |Delta_f|<=4.

Except for at most TWO faces that contain the first or last INTERNAL
comparison of the entire scan, changing local bits preserves the first
and last comparison signs. The parity of the total turn count is fixed
by those endpoint signs. Since all other face costs and C are independent,
c_f(b,t) has the same parity for every local assignment at each ordinary
face. Its two minima therefore have the same parity. Consequently

    Delta_f in {-4,-2,0,2,4}

at every nonexceptional face. Endpoint exceptions may have odd bias.
Thus each interior controller conflict pays at least2, and the remaining
proof can use a small local state alphabet rather than arbitrary capacities.
This does NOT say that enough conflicts occur on every additive scan.

## 4. A complete integer witness for the missing seven turns

For the displayed five-dimensional example the conditional face costs are

    A=((3,0),(2,2),(0,4),(0,4),(0,4),(2,2),(4,0),(3,0)).

Hence Delta=(-3,0,4,4,4,0,-4,-3), and the four sibling penalties are
(0,4,0,3), totaling7. The exact identity gives5+7=12. Faces0 and7 are
the two endpoint exceptions, as the odd biases require.

The verifier independently enumerates all4096 lower paired orientations
with the upper mask fixed and directly reconstructs integer rank values
along actual distinct integer scores. Minimum12 is confirmed; the chosen
attaining rank passes992 strict affine prefix checks. Minimizing the
potential over all8 upper paired masks also gives12, independently
matching the full ancestor optimizer's exact graph energy.

## 5. Exact wall coverage and limitations

For fixed upper integer scores s, all equalities in positive (a,b), a<b,
are a=d,b=d,a+b=d,b-a=d for d a positive upper score difference. The
verifier sweeps every positive a slab determined by vertical lines and
intersections of the b=d,d-a,d+a,b=a lines, then every open b interval.
Exact rational midpoints give generic integer-scaled witnesses. Reversing
a,b also covers the opposite low-coordinate priority cone. This visits
EVERY generic low-weight cell for EACH FIXED upper metric.

probe_paired_quartet_controller_walls.py checks all12 fixed positive Q3
upper metric representatives and all8 paired upper masks:39648 wall/rank
cases. Overall actual paired minimum9, no paired-quarter failure. There
are86 failures of the relaxed scalar bound, retained with full integer
weights and upper ranks. The upper weight magnitudes were FIXED: this
is NOT all Q5 chambers or any all-dimensional lower-bound proof.
Runtime1.888906522988691s; digest
4804487debb868bfb68180bd9573d096fe0f4e91141220b610fdfa3b930972b4.

verify_paired_quartet_controller_potential.py checks every retained relaxed
failure with restored phase, the exact penalty, its bias bound/parity,
the independent rank exhaustion, strict separators and full graph optimum.
All integer parameters, cost tables, attaining ranks and failures are saved.

## 6. Exact next proof obligation

For actual additive s and actual paired upper B, prove uniformly that

    C + sum_f min_t A_f(t)
      + sum_g 1[Delta_(2g)*Delta_(2g+1)>0]
                 min(|Delta_(2g)|,|Delta_(2g+1)|)
      >= F+1

or obtain a weaker positive constant times F that closes under recursion.
The identity alone does not yield that inequality. Actual sibling offsets
differ by the SAME coordinate2 weight, while their B ranks are adjacent
and their orientations flip with coordinate3 and the higher paired
prefix. Use those translation/controller restrictions explicitly to
charge a relaxed deficit to conflicts. A coarse scalar upper run count
was already excluded. Finite positive examples cannot fill this gap.
