# R119 工作记录与交接 — T2 intervention-preserving support certificate

日期：2026-10-06。

把T2从口头“机制相似”形式化成certificate：
M=(X,Z,U,I,Y,tau,N)，跨系统预声明phi_X,phi_Z,phi_I,phi_Y,phi_tau。
报告vector：
C0 grounding；
C1 baseline output correspondence；
C2 transition commutation；
C3 intervention transport；
C4 temporal correspondence；
C5 nuisance stability；
C6 anti-triviality/mapping discipline。
不建议压成一个average mechanism similarity score。

exact positive control：
A accumulator z+=e, P(Y=1)=sigmoid(z)；
B accumulator w+=2e, P(Y=1)=sigmoid(w/2)；
phi_Z(w)=w/2；
matched intervention do(z=c)<->do(w=2c)。
16 sequences baseline error0；transition commutation0；80 matched interventions max output error0。
如果错误地用same numeric do(w=c)，max probability mismatch0.122459，mean0.056535。说明跨底物必须transport physical/causal intervention meaning，不是对齐原始数值。

negative control复用R108：direct XOR/decomposed XOR baseline truth table完全一样，但internal clamp signature sets不同，T2拒绝。

T2仍弱于T3：selected accumulator机制对应不证明whole-system K homology，更不证明complete experiential identity。

R117 rat/AI实例当前C0清楚，AI C1-C3已实测，biology有peer-reviewed机制证据但independent raw-data certificate未闭环，因此T2=PARTIAL/PROMISING。

下一步R120整合R106-R119，写experience-intelligence bridge theorem schema：capability T -> verified support family R_T -> T2/T3 status -> C1条件性selected experiential organization statement；明确multiple realization下哪些推论失败。
