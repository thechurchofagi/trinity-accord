## 753. Finite-Order Phenomenal Blindness：任意低于全路径阶数的 marginals 都可能完全看不见最高阶 history

取 \(T\ge3\) 个二元时间点：

\[
X=(X_1,\ldots,X_T)\in\{0,1\}^T.
\]

定义两个轨迹 law：

\[
P_{\rm even}(x)
=
2^{-(T-1)}
\mathbf 1\!\left\{
\sum_i x_i\equiv0\pmod2
\right\},
\]

\[
P_{\rm odd}(x)
=
2^{-(T-1)}
\mathbf 1\!\left\{
\sum_i x_i\equiv1\pmod2
\right\}.
\]

两者 support 不相交，所以

\[
\boxed{
TV(P_{\rm even},P_{\rm odd})=1.
}
\]

但对任意 proper subset

\[
S\subsetneq\{1,\ldots,T\},
\]

都有

\[
\boxed{
(P_{\rm even})_S
=
(P_{\rm odd})_S
=
\operatorname{Unif}(\{0,1\}^{|S|}).
}
\]

理由：固定任意少于 \(T\) 个坐标后，至少还剩一个自由坐标；对每种已固定局部配置，剩余坐标中恰有一半 completions 满足 even parity，一半满足 odd parity。

于是：

### Finite-Order Phenomenal Blindness Proposition

对任意 \(k<T\)，存在两个 full process laws，使全部不超过 \(k\) 阶的时间 marginals 完全相同，但 full-history law 互相奇异。

因此：

\[
\boxed{
\text{任意数量的}<T\text{阶被动 anchors}
\not\Rightarrow
\text{识别 }T\text{ 阶 history}.
}
\]

这是 k-wise independence / marginal-problem 的标准数学构造，不申报概率论原创。意识论用途是：**不能把所有瞬时、pairwise、短窗口“都看起来一样”升级成整个体验过程相同。**


## 754. Binary Full-Marginal Fiber：所有 proper marginals 都已经完全知道，最高阶 history 仍有精确的一维 sharp ambiguity

上一节只给两个极端反例。现在可以得到更精确的 identified set。

假设一个二元 \(T\)-时刻 law \(P\) 的**所有 proper marginals** 都等于完全均匀分布。用 Walsh–Fourier 展开：

\[
P(x)
=
2^{-T}
\sum_{S\subseteq[T]}
\widehat P(S)
(-1)^{\sum_{i\in S}x_i}.
\]

所有 proper marginals 均匀，等价于所有非空 proper \(S\) 的 Fourier coefficients 为 0。归一化固定空集系数为 1，因此只剩 full-set coefficient：

\[
\boxed{
P_\theta(x)
=
2^{-T}
\left[
1+\theta(-1)^{\sum_i x_i}
\right].
}
\]

非负性要求且只要求

\[
-1\le\theta\le1.
\]

所以全部相容 joint laws 恰形成一条 segment：

\[
\boxed{
\mathcal I_{\rm full}
=
\{P_\theta:\theta\in[-1,1]\}.
}
\]

其中：

- \(\theta=1\)：even-parity law；
- \(\theta=-1\)：odd-parity law；
- \(\theta=0\)：iid uniform law。

令 target 为“完整轨迹具有 even parity”的概率：

\[
F(P)=P(\text{even parity}),
\]

则

\[
F(P_\theta)=\frac{1+\theta}{2},
\]

故 sharp identified range 为：

\[
\boxed{
\mathcal I_F=[0,1].
}
\]

也就是说：

> **即使所有单点、pairwise、三阶……直到 \(T-1\) 阶 marginals 全部精确测完，一个 genuine \(T\)-way history functional 仍可完全不识别。**

这是本轮最值得保留的 exact result。数学来自标准 Fourier / moment / marginal-problem 方法，不是新定理。


## 755. q 元推广：不是二元 parity 的偶然

令每个时间点取值于

\[
\mathbb Z_q,
\]

定义：

\[
P_c(x)
\propto
\mathbf 1\!\left\{
\sum_i x_i\equiv c\pmod q
\right\},
\qquad c=0,\ldots,q-1.
\]

任意两个不同 \(c\) 的 supports 不相交，因此 full-history TV=1；但任意 proper subset marginal 都是 uniform。

第三十六组脚本对：

\[
q=2,3,4,\qquad T=3,4
\]

逐项核对全部 proper marginals，全部 PASS。

所以“低阶数据完全相同、高阶 history 完全不同”不是 binary 特例，而是一般 marginal-extension phenomenon。


## 767. Intervention-Order Blindness：所有单次／低阶干预都做完，也未必看得到高阶 process constraint

仅有上一节还不够，因为它可能让人误以为“做一次 intervention 就解决过程识别”。

对任意整数：

\[
k\ge2,
\]

取 \(k\) 个可控干预位：

\[
A_1,\ldots,A_k\in\{0,1\}.
\]

比较两个有限 deterministic process：

### Null model \(M_0\)

\[
Y=0.
\]

### \(k\)-way interaction model \(M_k\)

\[
Y=\prod_{i=1}^{k}A_i.
\]

在 passive regime：

\[
A_1=\cdots=A_k=0,
\]

二者相同。

更强的是，只要一次实验里实际激活的 intervention sites 少于 \(k\)，总存在至少一个 \(A_i=0\)，所以：

\[
Y=0
\]

在两个模型中完全相同。

只有全部 \(k\) 个干预同时／按指定顺序有效时：

\[
M_0:Y=0,\qquad
M_k:Y=1.
\]

于是得到：

### Intervention-Order Blindness Proposition

对任意 \(k\ge2\)，存在两个 finite process models，使所有 intervention histories of order \(<k\) 都诱导完全相同的 observable response，而某个 order-\(k\) query 能完全分离二者。

即使实验策略是 adaptive，也无法用 \(<k\) 阶 queries 解决，因为所有允许的中间结果在两个模型中始终相同，策略因此获得相同历史、选择相同后续动作。

这是 higher-order interaction 的初等构造；数学不新。它的意义是：

\[
\boxed{
\text{intervention performed}
\not\Rightarrow
\text{intervention order sufficient}.
}
\]


## 768. Order-Matched Process Identifiability Barrier：观察阶数和干预阶数必须一起报告

第五十九轮给出：

\[
\text{observation order}<T
\]

可能完全看不见 \(T\)-way history。

本轮又给出：

\[
\text{intervention order}<k
\]

可能完全看不见 \(k\)-way causal process interaction。

所以在 unrestricted finite process classes 中，可以构造：

\[
M,M'
\]

使它们：

- 所有被动低阶 anchors 相同；
- 所有低阶 intervention histories 相同；
- 但某个更高阶 process target 不同。

于是本轮采用：

### Order-Matched Process Identification Principle

若要把一个 \(r\)-阶 phenomenal-process target 报告为“由证据识别”，至少必须满足以下一种：

1. evidence / intervention architecture 实际达到足以区分该 \(r\)-阶 target 的阶数；
2. 有独立依据把 model class 限制为低阶 memory / interaction structure；
3. 报告宽 identified set，而不是强行 completion 成 point value。

这不是“阶数必须数值相等”的普适定理，而是一个防止 analyst 偷用低阶数据推高阶结论的研究规范。


## 828. Target Anchor-Rank Bound：source 再精细，也不能替 target 创造 phenomenal 分辨率

现在允许 target 有 \(n\) 个 candidate phenomenal labels，其中前 \(r\) 个由独立 target anchors pointwise 固定：

\[
\phi_1,\ldots,\phi_r.
\]

其余：

\[
\phi_{r+1},\ldots,\phi_n
\]

在当前 evidence 下完全对称，residual gauge 为：

\[
S_{n-r}.
\]

那么 target label space 的 gauge orbits 恰为：

\[
\{\phi_1\},
\ldots,
\{\phi_r\},
\{\phi_{r+1},\ldots,\phi_n\}.
\]

所以最多 pointwise 分辨：

\[
\boxed{
r+1
}
\]

个 classes（若 \(r<n\)）；只有 \(r=n\) 或新增真实 symmetry-breaking structure 时才完全 point-identify 所有 labels。

这形成：

### Target Anchor-Rank Bound

跨 substrate phenomenal transport 的 pointwise resolution 不能超过 target 端自身 anchor-induced orbit resolution。

即：

\[
\boxed{
\text{source richness cannot substitute for target anchors}.
}
\]

第四十一组对：

\[
n=3,\ldots,7,
\qquad
r=0,\ldots,n
\]

穷举所有固定前 \(r\) 个 labels 的 residual permutation groups，orbit 数全部符合：

\[
n\;(r=n),
\qquad
r+1\;(r<n).
\]

