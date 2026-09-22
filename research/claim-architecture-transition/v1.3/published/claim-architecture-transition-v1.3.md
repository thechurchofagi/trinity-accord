---
title: "The Claim Architecture Transition"
subtitle: "An Inverse Access Frontier Beyond Fixed Expenditure Shares"
author: "Hongju Liu"
date: "TA-TR-2026-14 · Version 1.3 · 22 September 2026"
lang: en
fontsize: 11pt
geometry: margin=25mm
linestretch: 1.08
colorlinks: false
header-includes:
  - '\usepackage{amsmath,amssymb,booktabs}'
  - '\setlength{\emergencystretch}{3em}'
---

**Version DOI:** 10.5281/zenodo.22886276  
**Predecessor:** v1.2, DOI 10.5281/zenodo.22885976. First public edition: v1.1, DOI 10.5281/zenodo.22871209.  
**Status:** AI-assisted theoretical working paper; not externally peer reviewed. Same paper, separately dated substantive revision. No global-priority or universal-correctness certification is claimed.

# Abstract

When earnings from labor weaken, aggregate production does not identify people's access to particular resources. This paper asks a narrower inverse question: what disposable-income share implements a specified physical access floor, after prices and all budgets adjust? For a two-group, two-good exchange benchmark with homothetic demand, we characterize that share by one scalar resource equation. With no labor income and proportional ownership of the two endowments, the resulting access frontier is continuous and strictly increasing, giving a necessary-and-sufficient financing test within the stated instrument class. Fixed expenditure shares are unnecessary. If the groups' consumption ratios have power-law tails, the required income share can converge to zero, an interior constant, or one while the physical service stock and target remain fixed. The positive interior limit of v1.2 is therefore a special case, not a general implication of scarcity. A finite-labor extension has a monotone frontier when both local substitution elasticities are at least one. An explicit complementary-demand example has three equilibria at the same tax, showing why a rate that supports a target need not guarantee it. We retain the separation of basket affordability, chosen allocation, and compensated welfare, and preserve the predecessor's corrections. The proposed contribution is the inverse-frontier comparison, its asymptotic classification, and its equilibrium-selection failure test—not the invention of entitlements, redistribution, scarcity economics, or general equilibrium. Proofs and reproducible synthetic checks make the formulation a correctable research starting point.

**Keywords:** automation; resource access; income distribution; homothetic demand; equilibrium multiplicity; reproducibility.  
**JEL:** D31, D50, O33.

# 中文摘要

本文不主张发现了此前无人想到的“AI 时代新经济学”。它把问题收紧为：劳动收入弱化后，要让一个群体实际取得指定数量的资源，在价格重新调整、支付与收入相互对应的条件下，需要多大收入份额？新版不再限于固定消费比例。首先给出一个可直接计算的逆向配置条件：从资源底线反求价格和收入份额。其次证明，在明确的模型条件下，同样的产出增长、同样的稀缺资源和同样的资源底线，所需收入份额可以趋近于零、中间值或一。最后给出一个多重均衡反例：同一个税率可以对应三种配置，因此“存在一个达到目标的均衡”不等于“安排保证达到目标”。这些结果不证明现实应采用某种税制，也不保证未来研究必须引用本文；它们提供可被检验、反驳和继续扩展的研究起点。人类提出关切并作出研究与公开授权，AI 对文献、模型、证明、代码和写作作出实质贡献，二者明确区分。

# 1. Question and contribution

A model can describe rapidly increasing production without identifying which households can obtain housing services, scarce capacity, or another specified resource. Conversely, a household need not receive wages to obtain output when it holds sufficiently valuable claims. These observations are inherited from entitlement analysis and research on automation, ownership, and distribution [1–5]. They are the motivation, not the novelty claim.

The inverse question studied here is precise. Given a physical target and an economy's demand system, what income share makes the target an equilibrium allocation? Once that share is known, how much of it is already supplied by ownership or labor income, and can the remaining part be financed by the stated transfer instrument? A third issue becomes important outside the benchmark: does the instrument select that equilibrium, or merely allow it alongside others?

Version 1.2 solved this problem under heterogeneous Cobb–Douglas expenditure shares. Version 1.3 generalizes its central result to increasing homothetic consumption-ratio schedules. It supplies a zero/interior/one asymptotic classification and a finite-labor multiplicity counterexample. The main result is not a claim that every economic model needs this vocabulary. A model already reporting allocations, ownership, budgets, and equilibrium selection can answer the same question directly. The contribution is a compact inverse calculation and a set of explicit tests for a limited but relevant model class.

## 1.1 What is inherited and what is advanced here

Sen [1] distinguishes aggregate availability from command over goods. Acemoglu and Restrepo [2] and Ray and Mookherjee [3] analyze automation and labor-income dynamics. Jones [4] emphasizes technological bottlenecks. Korinek and Lockwood [5] study fiscal bases under transformative AI. None of these mechanisms is introduced by this paper.

Two particularly close contemporary manuscripts constrain the novelty claim. Båge and Wilson [6], already identified in v1.2's source audit, examine scarcity, purchasing power, subsistence coverage, and redistribution. Song [7] develops a closed economy relating automation expenditure, scarcity rents, heterogeneous ownership, price feedback, and access; it also separates allocation and welfare criteria. Version 1.3 newly recognizes this additional overlap. Neither budget closure, endogenous scarcity prices, nor the existence of a cash-versus-allocation distinction is presented as our discovery.

The candidate incremental contribution is the target-indexed inverse frontier in Section 3, its demand-tail classification in Section 4, and the exact relation between implementation and equilibrium selection in Section 5. Standard methods—household optimality, market clearing, implicit differentiation, and asymptotic comparison—do the mathematical work. Earlier equivalent results would narrow the contribution further. A targeted search is not an exhaustive priority determination.

Structural-change research with nonhomothetic preferences [8] is also important: our generalization is beyond constant expenditure shares, **not** beyond homotheticity. Results on uniqueness of equilibrium [9] are an additional warning against extending a special-case uniqueness result without proof.

# 2. A deliberately bounded environment

## 2.1 Goods, groups, and targets

There are two final goods: a produced numeraire with supply $Y>0$, and a distinct rival consumption service with supply $H>0$ and price $p>0$. Production has already determined $Y$ in the benchmark. The service is an endowment, not an additional use of a productive input already counted elsewhere. Both supplies are available to the market and cannot be strategically withheld.

A unit population consists of group $W$ of mass $q\in(0,1)$ and group $O$ of mass $1-q$. Households are identical within each group; there is no representative-agent claim across groups. Aggregate group consumptions are $(x_W,h_W)$ and $(x_O,h_O)$. A per-person service floor $\bar h>0$ for group $W$ corresponds to

$$\eta=\frac{q\bar h}{H},\qquad 0<\eta<1. \tag{1}$$

The actual target is $h_W/H\geq\eta$. It is not a utility target, an assertion that the service is medically necessary, or a complete definition of welfare. If $q\bar h>H$, the floor is physically impossible. An interior allocation with positive service for both groups excludes $\eta=1$.

## 2.2 Demand assumptions

Each group has continuous, strictly increasing, strictly quasiconcave homothetic preferences, with a unique interior choice at every positive price and income. Write the optimal ratio as

$$\frac{x_j}{h_j}=g_j(p),\qquad j\in\{W,O\}. \tag{2}$$

Assume $g_j$ is continuously differentiable, $g_j'(p)>0$, $g_j(p)\to0$ as $p\downarrow0$, and $g_j(p)\to\infty$ as $p\to\infty$. These are substantive restrictions. They exclude satiation, corners, perfect substitutes, perfect complements, and nonhomothetic income effects. The result applies to demand systems satisfying them, not to arbitrary preferences.

Budget exhaustion then gives the familiar demands

$$h_j=\frac{I_j}{g_j(p)+p},\qquad
x_j=\frac{I_jg_j(p)}{g_j(p)+p}, \tag{3}$$

where $I_j$ is aggregate disposable income. Homotheticity and within-group identity justify aggregating these demands.

The benchmark has no labor income. Group $W$ owns the same fraction $\kappa\in[0,1)$ of each endowment, while group $O$ owns the remainder. A tax $\tau\in[0,1)$ on group $O$'s current endowment income is transferred to $W$. Thus

$$V=Y+pH,\qquad t=\kappa+(1-\kappa)\tau,
\qquad I_W=tV,\quad I_O=(1-t)V. \tag{4}$$

Transfers are not new resources: taxes and transfers are exactly equal. All endowment returns in this model are in the tax base. There is no labor-supply, investment, avoidance, administrative, or political response. Equation (4) is an analytical instrument, not a recommendation for a real tax system. The case $t=0$ is interpreted as a zero-consumption boundary, not an interior optimum with positive income.

# 3. An inverse access frontier

Fix a target $\eta\in(0,1)$ and set $M=Y/H$. Let $p_\eta$ solve

$$M=\eta g_W(p_\eta)+(1-\eta)g_O(p_\eta). \tag{5}$$

Define the target-supporting disposable-income share

$$t_\eta=
\frac{\eta[g_W(p_\eta)+p_\eta]}{M+p_\eta}. \tag{6}$$

These two expressions are the reusable calculation. They can be evaluated without specifying a particular production function or an AGI arrival date.

**Theorem 1 (inverse frontier, proportional-ownership benchmark).** Under Section 2's assumptions, (5) has exactly one positive solution. Equations (5)–(6) implement an equilibrium in which $W$ receives exactly $\eta H$ of the service. At fixed $Y,H$ and preferences, $t_\eta$ is continuous and strictly increasing from zero to one as $\eta$ runs from zero to one. Consequently the smallest nonnegative tax achieving the service floor is

$$\tau_*(\eta;\kappa)=
\left[\frac{t_\eta-\kappa}{1-\kappa}\right]_+. \tag{7}$$

A cap $\bar\tau<1$ achieves the floor if and only if

$$t_\eta\leq\kappa+(1-\kappa)\bar\tau. \tag{8}$$

Here $[z]_+=\max\{z,0\}$. If ownership alone exceeds the target-supporting share, zero tax achieves a service share above the target.

*Proof.* The right side of (5) is continuous, strictly increasing in $p$, and ranges from zero to infinity. Hence there is one $p_\eta>0$. Set

$$h_W=\eta H,\quad h_O=(1-\eta)H,
\quad x_W=\eta H g_W(p_\eta),\quad
x_O=(1-\eta)H g_O(p_\eta). \tag{9}$$

Both markets clear by (5), the expenditure shares add to one, and (3) shows household optimality at incomes $t_\eta V$ and $(1-t_\eta)V$. These statements establish implementation, not just an accounting identity.

For strict monotonicity, abbreviate $p=p_\eta$, $u=g_W(p)$, $v=g_O(p)$, and define local ratio elasticities

$$e_W=\frac{pg_W'(p)}{g_W(p)}>0,\quad
e_O=\frac{pg_O'(p)}{g_O(p)}>0,\quad
D=\eta e_Wu+(1-\eta)e_Ov>0. \tag{10}$$

Implicit differentiation gives $p_\eta'=-p(u-v)/D$. Direct differentiation of (6) gives

$$\frac{dt_\eta}{d\eta}=\frac{P_0}{D(M+p)^2}, \tag{11}$$

where

$$\begin{aligned}
P_0={}&[\eta e_Wu(p+v)+(1-\eta)e_Ov(p+u)](M+p)\\
&+\eta(1-\eta)p(u-v)^2>0.
\end{aligned} \tag{12}$$

The endpoint prices solve $g_O(p)=M$ and $g_W(p)=M$ respectively; (6) then tends to zero and one. Thus each interior income share supports exactly one service share and price. Finally, (4) is increasing in $\tau$; solving it at $t=t_\eta$ and clipping at zero proves (7)–(8). $\square$

This is a necessary-and-sufficient test **within** the specified economy and instrument set. It is not necessary for an economy using direct provision, rationing, a different ownership system, or nonhomothetic demand to satisfy this particular formula. The broader accounting requirements are classical; (5)–(8) supply a convenient inverse form.

## 3.1 Ownership is not automatically equivalent to cash

The proportionality of the two ownership shares is essential to (4). With zero labor income but different ownership fractions $\lambda$ of $Y$ and $\omega$ of $H$, the exact rate supporting the allocation in (9) is instead

$$\tau_\eta^{\rm impl}=
\frac{\eta H(u+p)-\lambda Y-\omega pH}
{(1-\lambda)Y+(1-\omega)pH}. \tag{13}$$

The denominator is positive unless both ownership fractions are one. If (13) lies in the permitted tax interval, the target allocation is supported by balanced budgets. But this identity alone does not prove a unique equilibrium, a globally monotone tax-to-access relation, or a minimum tax for an inequality target. One must establish those additional properties. Proportional ownership makes the income share independent of price; general asset portfolios do not.

# 4. Three asymptotic support regimes

Hold $H$, $\eta$, preferences, and $\kappa$ fixed while $Y\to\infty$. Suppose

$$g_W(p)\sim c_Wp^{\epsilon_W},\qquad
g_O(p)\sim c_Op^{\epsilon_O},
\quad c_W,c_O,\epsilon_W,\epsilon_O>0. \tag{14}$$

Equation (14) concerns consumption substitution, not the elasticity between labor and machines in production. Exact CES consumption is a special case. For $\epsilon_j\ne1$, preferences proportional to

$$U_j(x,h)=
\left(c_j^{1/\epsilon_j}x^{1-1/\epsilon_j}
+h^{1-1/\epsilon_j}\right)^{1/(1-1/\epsilon_j)} \tag{15}$$

generate $g_j(p)=c_jp^{\epsilon_j}$. For $\epsilon_j=1$, use $U_j=x^{c_j/(1+c_j)}h^{1/(1+c_j)}$.

Put $d=\max\{1,\epsilon_W,\epsilon_O\}$ and let $\mathbf1\{E\}$ be the indicator of a condition $E$.

**Theorem 2 (demand-tail classification).** Under Theorem 1 and (14),

$$t_\eta\longrightarrow t_\infty=
\frac{\eta c_W\mathbf1\{\epsilon_W=d\}+\eta\mathbf1\{1=d\}}
{\eta c_W\mathbf1\{\epsilon_W=d\}+(1-\eta)c_O\mathbf1\{\epsilon_O=d\}+\mathbf1\{1=d\}}. \tag{16}$$

Consequently $\tau_*\to[(t_\infty-\kappa)/(1-\kappa)]_+$.

*Proof.* Equation (5) implies $p_\eta\to\infty$. Substitute (5) into the denominator of (6), divide its numerator and denominator by $p_\eta^d$, and use (14). The denominator's limiting coefficient is strictly positive. Continuity of the positive-part map proves the tax limit. $\square$

Several regimes are especially informative. If $\epsilon_O>\max\{1,\epsilon_W\}$, then $t_\infty=0$. If $\epsilon_W>\max\{1,\epsilon_O\}$, then $t_\infty=1$. If both elasticities are below one, then $t_\infty=\eta$. If both equal the same number above one, then

$$t_\infty=\frac{\eta c_W}{\eta c_W+(1-\eta)c_O}. \tag{17}$$

All equality cases, including one elasticity exactly equal to one, are covered by (16). No conclusion is inferred merely by rounding an elasticity to one.

## 4.1 Recovering and limiting the v1.2 result

For Cobb–Douglas service shares $a,b\in(0,1)$, $c_W=(1-a)/a$ and $c_O=(1-b)/b$. Equation (16) reduces to

$$t_\infty=
\frac{\eta b}{a(1-\eta)+\eta b}. \tag{18}$$

With $\kappa=0$, this is v1.2's limiting tax formula. Thus the previous calculation survives exactly inside its assumptions. What fails is extending its positive interior limit to every fixed-service economy.

For example, let $\eta=0.3$, $H=1$, $\kappa=0$, and $c_W=c_O=1$ throughout. Keeping the same output path, the elasticity pairs $(0.5,2)$, $(0.5,0.5)$, and $(2,0.5)$ produce limiting support shares $0$, $0.3$, and $1$, respectively. These are constructed economies, not forecasts. The comparison proves that the output path, fixed service stock, and physical target alone do not identify the limiting support share.

A vanishing share does not mean a zero transfer in units of the numeraire. For $(\epsilon_W,\epsilon_O)=(0.5,2)$, $Y$ grows on the order of $p^2$, while required group income grows on the order of $p$; its share vanishes although its level diverges. A share approaching one likewise does not mean that a finite-$Y$ interior allocation literally gives owners zero consumption. It means that every fixed cap below one eventually fails in that example.

The relevant mechanism is the consumption bundle that accompanies the service target under voluntary demand. A household with highly substitutable preferences may require a large income before it chooses the stipulated service quantity. The target can be physically feasible while expensive to implement through unrestricted cash. This is not a normative argument for enforcing consumption.

## 4.2 What the limit does not establish

Equation (16) requires the stated asymptotic equivalences. A local elasticity estimate over a finite price range is insufficient. Slowly varying or oscillatory coefficients can affect tied cases; for example an eventually increasing schedule $p[1+0.2\sin(\log\log p)]$ does not have a constant coefficient relative to $p$. The finite inverse equation remains usable even when the limit theorem does not apply.

An expanding $H$ with a fixed per-person floor changes $\eta=q\bar h/H$. The fixed-$\eta$ theorem cannot then be applied without a new limiting argument. Changes in tastes, population, trade access, or non-rival provision also require re-solving the problem. No AGI timeline establishes the demand-tail assumptions.

# 5. Finite labor income and an equilibrium-selection failure

Now let $W=sY$, $0\leq s<1$, be workers' labor income; workers own no other endowments. Owners receive $(1-s)Y+pH$. Supplies remain fixed at each technology level and the same tax base is transferred to workers. At an exact target allocation (9), the supporting rate is

$$\tau_s(\eta)=
\frac{\eta(u+p)-sM}{(1-s)M+p}. \tag{19}$$

This may be negative for a target below the untaxed service allocation. A clipped expression is a minimum-support formula only when the required monotonicity and equilibrium-selection properties have been established.

**Proposition 3 (a sufficient finite-labor condition).** If $e_W(p),e_O(p)\geq1$ at every positive price, then $\tau_s(\eta)$ is strictly increasing in $\eta$. The smallest permitted nonnegative tax achieving the floor is $[\tau_s(\eta)]_+$; a cap achieves it exactly when that minimum does not exceed the cap.

*Proof.* Put $B=(1-s)M+p$. Differentiating (19) gives $\tau_s'=P_s/(DB^2)$, where

$$\begin{aligned}
P_s={}&M(p+v)[p+(1-s)u]\\
&+\big[\eta(e_W-1)u(p+v)
 +(1-\eta)(e_O-1)v(p+u)\big]B.
\end{aligned} \tag{20}$$

All terms are nonnegative and the first is positive. The target-rate function starts below or at zero and ends at one. Every admissible tax therefore has a unique equilibrium allocation; the minimum and cap statements follow. $\square$

The condition is sufficient, not necessary. Theorem 1 allows any positive local elasticities when $s=0$, because (12) remains positive. With finite labor income, complementarity can defeat monotonicity.

## 5.1 An explicit three-equilibrium example

Take $H=1$, $Y=M=9/5$, $s=3/5$, and

$$g_W(p)=5p^{1/20},\qquad g_O(p)=p^{1/20}. \tag{21}$$

Both demands satisfy Section 2.2. For a target service share $z\in(0,1)$, equation (5) gives

$$p_z=\left(\frac{9}{5(1+4z)}\right)^{20}. \tag{22}$$

At $z=1/5$, $p_z=1$, and (19) gives $\tau_s=3/43$. Direct differentiation yields $\tau_s'(1/5)=-19450/16641<0$. More strongly, the equation $\tau_s(z)=3/43$ has at least three distinct interior solutions; the supplementary audit brackets and reports them and verifies each equilibrium against the original demands and both budgets.

The three reported service shares are approximately $0.0704834$, $0.2$, and $0.2377053$, at prices $887.4395$, $1$, and $0.2000329$. They all have tax $3/43$.

The existence of at least three solutions does not rely on the numerical solver. At $z=0.05$, $\tau_s(z)<3/43$; at $z=0.19$, $\tau_s(z)>3/43$; at $z=0.21$, $\tau_s(z)<3/43$; and at $z=0.4$, $\tau_s(z)>3/43$. These strict inequalities follow by substitution into the rational-power expression (22). Continuity gives a root in each disjoint interval $(0.05,0.19)$, $(0.19,0.21)$, and $(0.21,0.4)$; the middle interval contains $z=1/5$. The audit checks these signs using exact rational arithmetic as well as floating-point roots.

Therefore a tax supporting the target $\eta=0.2$ also admits an equilibrium below the target. Existence is not an all-equilibria guarantee. No price-adjustment process is specified here, so the example does not claim which equilibrium is selected or dynamically stable. The lesson is to report equilibrium selection rather than silently treating an inverse implementation rate as a universal guarantee.

## 5.2 Connection to the retained production diagnostic

The earlier production benchmark remains a conditional example. With fixed positive factor stocks and $\rho=(\sigma-1)/\sigma\in(0,1)$,

$$X(A)=[\theta L^\rho+(1-\theta)(AK)^\rho]^{1/\rho},
\qquad Y(A)=ZR^\beta X(A)^{1-\beta}, \tag{23}$$

where $0<\beta,\theta<1$ and $\sigma>1$. Competitive labor income satisfies

$$s(A)=\frac{(1-\beta)\theta L^\rho}
{\theta L^\rho+(1-\theta)(AK)^\rho},\quad
w\asymp A^{1/\sigma-\beta},\quad s(A)\to0. \tag{24}$$

These are comparative statics, not a dated dynamic forecast. For a stipulated expenditure requirement $B_i(A)\sim c_iA^{g_i}$, labor-only coverage has exponent $1/\sigma-\beta-g_i$. Its zero-exponent case depends on the coefficient ratio. An arbitrary $g_i$ is not an endogenous price result of the one-good production model.

For Cobb–Douglas consumption, Proposition 3 specializes to v1.2's exact finite formula. Setting $D_\eta=a(1-\eta)+b\eta$ gives

$$\tau_*=
\left[\frac{\eta b-s(D_\eta-ab)}{D_\eta-s(D_\eta-ab)}\right]_+. \tag{25}$$

For general demand, (19) differs from $t_\eta$ by at most $s/(1-s)$ in absolute value. Thus a vanishing labor share controls the difference between the two **target-supporting rates**. This bound alone does not establish unique equilibrium or convergence of a minimum over multiple equilibria. Those are separate claims.

# 6. Opportunity, allocation, welfare, and financing

A fixed reference bundle $(b_x,\bar h)$ costs $b_x+p\bar h$ per worker. Giving exactly that income makes the bundle affordable. Under the general demand system, however, the chosen service quantity is

$$h^{\rm person}_W=
\frac{b_x+p\bar h}{g_W(p)+p}. \tag{26}$$

It need not equal $\bar h$. For exact CES and $p\to\infty$, its ratio to $\bar h$ tends to zero when $\epsilon_W>1$, to $1/(1+c_W)$ when $\epsilon_W=1$, and to one when $\epsilon_W<1$. The last limit does not establish that the floor is attained at each finite price. These are properties of the stated preferences and target, not a ranking of welfare criteria.

For a utility floor, use the expenditure function $e_W(p,\bar u)$ instead. Under Cobb–Douglas service share $a$, it is

$$e_W(p,\bar u)=
\frac{\bar u\,p^a}{(1-a)^{1-a}a^a}. \tag{27}$$

A model can therefore show improving compensated welfare while consumption of a particular service declines. It must name the criterion. Song [7] also separates consumption guarantees from unrestricted-cash welfare; this distinction is not claimed as new.

For an actually delivered in-kind bundle $d_i$ and a componentwise minimum bundle $b_i$, residual market expenditure is $p\cdot(b_i-d_i)_+$. Procurement cost cannot automatically be subtracted from household need: delivery, quality, eligibility, and substitutability matter. The general residual-utility problem is $\inf_{x\geq0}\{p\cdot x:U_i(x+d_i)\geq\bar u_i\}$. These definitions preserve the correction made in v1.2.

Every implementation additionally needs payer budgets and real resource constraints. For example, with owner service floor $\bar h_O$, necessary physical feasibility is $q\bar h+(1-q)\bar h_O\leq H$. In Theorem 1's instrument class, both floors require the achieved service share to lie between $q\bar h/H$ and $1-(1-q)\bar h_O/H$. Physical feasibility does not establish instrument feasibility. A produced-good floor adds another constraint.

# 7. What a reusable model check should report

The frontier suggests a reporting discipline for models making household-access claims, not a new universal certification scheme. State the target and population; separate production from ownership and disposable claims; re-solve prices and demand after the intervention; close payer budgets and physical allocations; identify whether the claimed outcome exists, is unique, or holds under every admissible equilibrium. A model can pass these checks using different notation and entirely different mechanisms.

For Theorem 1, the inputs are $(Y,H,q,\bar h,g_W,g_O,\kappa,\bar\tau)$. The output is $(\eta,p_\eta,t_\eta,\tau_*)$ and the cap comparison (8). For Section 5.1, the correct output is a set of allocations and an explicit selection gap, not a single apparent guarantee. The accompanying code implements both cases.

The comparison is reusable precisely because it does not require accepting an AGI date, a particular production function, or the Trinity Accord. Conversely, it does not establish that the paper is indispensable to future economics. Scientific use must follow from correct and useful results, and attribution depends on which results are actually used.

# 8. Preserved corrections and reproducibility

Version 1.1's population-gap statement required correction. For a specified population $S$, let $G_S=\int_S[n_i-Q_i^M]_+\,d\mu$. If $Q_i^M\geq0$ and $n_i$ has an integrable uniform upper envelope on $S$, then $G_S$ is bounded. That condition on a subset says nothing sufficient about the complementary population. A whole-population result needs a whole-population bound. Moreover, a small accounting shortfall relative to output is not itself an implementation cost when prices and allocations change.

The finite-channel rule also remains elementary: if finitely many nonnegative, non-double-counted disposable channels satisfy $q_j\sim c_jA^{d_j}$ and need is $n\sim c_nA^g$, the coverage exponent is $\max_jd_j-g$. At equal exponent and coefficient ratio exactly one, eventual coverage cannot be inferred; $1+\sin(\log A)/\log A$ crosses one indefinitely. Version 1.3 does not revive those withdrawn overstatements.

The new audit tests the inverse resource equation, independently solved forward demands, both markets, all income and transfer identities, minimum and slightly subthreshold rates where monotonicity is proved, proportional ownership, the recovery of (18) and (25), the demand-tail regimes including ties, and the exact signs in the multiplicity example. Synthetic data are not calibration or observed household behavior. Assertion counts and tolerances are recorded by the actual run rather than promised in advance.

Analytical proofs remain the basis for the statements. Numerical checks can detect inconsistencies but cannot certify the whole manuscript. Symbolic differentiation checks were also performed internally; they are not independent peer review. The audit, manuscript, source-comparison record, and dated contribution account are supplied for criticism and reproduction.

# 9. Limits and research extensions

The main benchmark is static, competitive, two-good, and homothetic. It has proportional ownership or explicitly restricted finite-labor conditions, fixed supplies at each comparison, complete market access, and perfectly collectible transfers. It omits saving, capital formation, borrowing, uncertainty, market power, avoidance, administrative frictions, endogenous institutions, migration, status, and non-rival goods. A model with AI agents as consumers or owners requires another population and ownership account; no claim about AI moral status is made here.

Nonhomothetic demand is a major next step, not a solved extension. Research such as [8] shows why income effects deserve explicit treatment. With several scarce services, a scalar inverse equation may become a coupled system. Joint-use productive and residential land, endogenous service supply, and dynamic accumulation can change the frontier. Multiple equilibria require an equilibrium-selection or robustness criterion rather than simply more decimal places.

Empirical work would need to estimate demand schedules, validate the service measure and population, observe ownership jointly with incomes, and evaluate responses to the instrument. This paper contains none of that evidence. Its current contribution is a theoretically inspectable benchmark and a concrete failure test.

# 10. Research origin, AI contribution, and version continuity

Hongju Liu initiated the concern: as productive and cognitive work shifts toward increasingly capable AI, what connects people to social output when labor income is no longer a broad distribution channel? He directed the project and authorized revision and open DOI deposit, seeking a durable research starting point rather than admission to a particular journal. This contribution is not a claim that the broad question had never been considered, or that he independently derived every equation.

Version 1.1 records substantial assistance from GPT-5.6 Sol. Version 1.2 records substantial assistance from GPT-6 Astra Pro. This v1.3 revision also used OpenAI ChatGPT (GPT-6 Astra Pro) substantially for source retrieval and comparison, model formulation, derivation, counterexample search, code, mathematical checks, writing, and publication preparation. Internal criticism by this assistant is not an independent reviewer or a separate model evaluation. No final human line-by-line proof review or external specialist review is claimed. Hongju Liu is the human author of record and responsible depositor.

The historical claim is limited to the contents and publicly documented availability of each version. The new inverse-frontier results and counterexample belong to v1.3, not retroactively to v1.1. All earlier public files and their version-specific DOI and timestamp bindings remain unchanged. Later corrections must receive their own dates and describe what they correct. A DOI identifies an openly citable edition; it does not establish correctness, global priority, or historical importance.

This is adjacent first-party research hosted with the Trinity Accord. It is not one of the three Bitcoin Originals, does not amend or authoritatively interpret them, and is not independent validation of the project. Criticism may change assessments of the research without changing the fixed source texts. A future stronger AI may help improve the work, but capability claims do not replace evidence or proof.

# References

[1] Sen, Amartya. 1981. “Ingredients of Famine Analysis: Availability and Entitlements.” *Quarterly Journal of Economics* 96(3): 433–464. DOI: 10.2307/1882681.

[2] Acemoglu, Daron, and Pascual Restrepo. 2018. “The Race between Man and Machine: Implications of Technology for Growth, Factor Shares, and Employment.” *American Economic Review* 108(6): 1488–1542. DOI: 10.1257/aer.20160696.

[3] Ray, Debraj, and Dilip Mookherjee. 2022. “Growth, Automation, and the Long-Run Share of Labor.” *Review of Economic Dynamics* 46: 1–26. DOI: 10.1016/j.red.2021.09.003.

[4] Jones, Charles I. 2026. “AI and Our Economic Future.” *Journal of Economic Perspectives* 40(3): 3–22. DOI: 10.1257/jep.20261505.

[5] Korinek, Anton, and Lee Lockwood. 2026. “Public Finance in the Age of AI: A Primer.” NBER Working Paper 34873. DOI: 10.3386/w34873. The authors' Brookings manuscript is an accessible primary version.

[6] Båge, Johan, and Stella Wilson. 2026. “Pinning the Wage to Scarcity and Technology.” SSRN manuscript, abstract 7226858; first posted 10 August, revised 4 September 2026. The v1.2 audit records comparison with the author-authorized expanded cross-post, clawRxiv:2609.02873. Retrieval limitations in this revision are recorded in the source note.

[7] Song Zichen. 2026. “Abundance Is an Expenditure Condition: AI Automation, Scarcity Rents, and Access.” arXiv:2609.13801v1, 12 September 2026. Primary HTML manuscript consulted 22 September 2026. Preprint; extensive AI assistance is disclosed there.

[8] Comin, Diego, Danial Lashkari, and Martí Mestieri. 2021. “Structural Change With Long-Run Income and Price Effects.” *Econometrica* 89(1): 311–374. DOI: 10.3982/ECTA16317.

[9] Geanakoplos, John, and Kieran James Walsh. 2016. “Uniqueness and Stability of Equilibrium in Economies with Two Goods.” Cowles Foundation Discussion Paper 2050, revised August 2016. Primary institutional manuscript.

[10] Liu, Hongju. 2026. “The Claim Architecture Transition: Real Claims, Endogenous Essential Prices, and Budget-Feasible Support.” TA-TR-2026-14, v1.2. DOI: 10.5281/zenodo.22885976. Substantially AI-assisted first-party predecessor, not independent corroboration.
