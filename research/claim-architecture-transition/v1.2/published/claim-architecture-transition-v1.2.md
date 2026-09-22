---
title: "The Claim Architecture Transition"
subtitle: "Real Claims, Endogenous Essential Prices, and Budget-Feasible Support"
author: "Hongju Liu"
date: "TA-TR-2026-14 · Version 1.2 · 22 September 2026"
lang: en
fontsize: 11pt
geometry: margin=25mm
linestretch: 1.08
colorlinks: false
header-includes:
  - '\usepackage{amsmath,amssymb}'
  - '\setlength{\emergencystretch}{3em}'
---

**Version DOI:** 10.5281/zenodo.22885976  
**Predecessor:** v1.1, DOI 10.5281/zenodo.22871209, publicly deposited 21 September 2026.  
**Status:** openly archived theoretical working paper; not externally peer reviewed. This is a substantive, explicitly corrective revision of the same paper, not a fifteenth paper in the series.

# Abstract

When labor becomes a weak claim on production, neither employment nor aggregate output identifies whether people can obtain essential resources. This paper develops a bounded diagnostic rather than a new general theory of post-labor economics. It first retains a conditional CES result: with fixed factor stocks, labor-only coverage of an externally specified expenditure requirement has exponent $1/\sigma-\beta-g$. It then closes a two-good competitive economy in which a produced numeraire expands while a distinct essential service has fixed supply. Workers and asset owners can have different expenditure shares. Redistribution therefore changes the essential-service price; this feedback is solved rather than assumed away. For a target worker share $\eta$ of the scarce service, worker and owner expenditure shares $a,b$, and the pre-transfer labor share $s$ of produced output, the paper derives an exact minimum tax on owners' nonlabor income. Its limit is $\eta b/[a(1-\eta)+\eta b]$, not generally $\eta$. A lower transfer can make a specified basket affordable without inducing the chosen service allocation to reach its target. Compensated utility is a third, distinct criterion. These comparisons expose why household affordability, financing balance, and physical allocation should not be conflated. The revision also corrects an aggregate-gap quantifier in v1.1, restricts its abundance claim, and treats the finite-channel exponent result as elementary accounting. Proofs, counterexamples, a reproducible numerical audit, and a dated contribution record support future correction. Scarcity, entitlements, ownership, rent redistribution, and homothetic aggregation are inherited ideas; neither global priority nor empirical validation is claimed.

**Keywords:** automation; entitlements; essential resources; general equilibrium; income distribution; fiscal feasibility; AI-assisted research.  
**JEL:** D31, D50, H53, O33.

# 中文摘要

本次修订不是宣称发现了“AI 时代全新的经济学”。已有研究早已讨论自动化、所有权、稀缺资源与分配。本文把问题收紧为：劳动收入这条渠道衰减时，什么条件才能让人继续取得必要资源？原稿的 CES 公式保留为有条件的比较静态结论，但不再把外加的基本品价格路径当成已经解释的均衡结果。新增模型区分可扩大的生产商品和供给固定的必要服务，并允许劳动者与资产所有者的消费结构不同，因此转移支付会反过来影响价格。模型分别计算“有能力购买一个篮子”“预算上能够支持这种安排”和“实际配置达到资源底线”，说明三者并不相同。修订同时纠正原稿从部分人群推断全体缺口的条件不足，加入边界反例与可执行核查。它是可继续修订的公开研究起点，不是全球首创证明、已验证政策方案，也不是《三位一体协定》的正典或正典的证明。

# 1. Question, contribution, and scope

The motivating question is not simply how many jobs AI might displace. It is how people remain connected to social output when labor income no longer supplies a sufficiently broad claim on that output. A person may remain employed yet lose access to a particular resource. Another may stop working and remain secure through ownership. Aggregate production can rise without settling either person's position.

These distinctions are not new in themselves. Sen's entitlement analysis separates aggregate availability from individual command over goods [1]. Modern automation models analyze distribution through technology and ownership [2–5]. The contribution sought here is a transparent, correctable comparison of three tests that a proposed distribution arrangement must not confuse: household affordability at stated prices, financing consistent with other agents' budgets, and a feasible allocation of the relevant resources.

Version 1.1 emphasized a CES exponent and a claim-channel decomposition. Version 1.2 retains the valid conditional algebra but reduces its novelty claim. Its central extension is a two-group, two-good model with endogenous essential-service prices and heterogeneous demand. In that model, a support rule has an exact finite-technology threshold, a physical ceiling, and a nonzero limiting income share. Affordability of a fixed basket and realization of a service floor yield different thresholds even when every market clears.

This is a comparative-static sequence of one-period economies, not a dynamic transition forecast. The technology index $A$ has no calendar interpretation. The model does not establish that any currently deployed AI has the assumed substitution properties, predict an unemployment rate, or identify an optimal political system. Its usefulness is as an inspectable counterexample and an elementary stress-test design.

## 1.1 A precise but limited originality claim

The nearest identified manuscript is Båge and Wilson's September 2026 study [6]. It already derives scarcity-related purchasing-power bounds, studies subsistence coverage and rent redistribution, and supplies a common-homothetic-demand equilibrium. Those mechanisms are not discoveries of this paper. Sections 5–7 instead combine a CES labor-share path with heterogeneous expenditure shares and distinguish an actual service floor from basket affordability and a utility threshold. The residual contribution is this explicit comparison and its conditional support frontier, not a claim to invent general equilibrium or redistribution theory.

The additional derivations are short and use standard methods. Finding a prior derivation of the same comparison would narrow the originality claim further without invalidating an independently correct calculation. Naming an accounting object “claim architecture” does not itself constitute scientific novelty.

## 1.2 What is corrected, not merely expanded

First, the original essential-price exponent was externally specified in a one-good model. It is now labeled a conditional diagnostic; an endogenous two-good case is provided separately. Second, v1.1 Proposition 4 bounded the needs of a labor-only subset but stated a conclusion about the whole-population gap. Section 8 supplies the missing population condition and a counterexample. Third, a small expenditure gap relative to an expanding numeraire is no longer described as a general demonstration of physical feasibility. Fourth, the maximum-exponent calculation is called a lemma, and its equality boundary is treated explicitly. Finally, transfers are not counted as net new resources, and in-kind provision is not automatically subtracted at its procurement cost.

# 2. Literature boundary

Sen [1] supplies the distinction between available goods and entitlements. Acemoglu and Restrepo [2] model automation and the creation of new tasks; these mechanisms are deliberately not endogenized here. Ray and Mookherjee [3] demonstrate that falling labor shares can coexist with rising absolute real wages. Jones [4] emphasizes distinctions between factor shares, factor prices, and bottlenecks. Consequently, a falling labor share is neither a novel result nor sufficient evidence of declining living standards.

Hazari and Mohan [5] analyze AI-related exclusion in a general-equilibrium setting with unequal productive-asset ownership. Employment-compatible distributional harm is therefore inherited, not this paper's first discovery. Båge and Wilson [6] are particularly close; the present contribution must be evaluated against their actual manuscript, not against an artificially weak account of it. Korinek and Lockwood [7] examine the changing fiscal bases of transformative AI. Their work motivates treating financing as a constraint rather than appending transfers without identifying a payer.

The present framework does not supersede those theories. It uses simpler assumptions to make several easily conflated criteria directly comparable. The source audit accompanying this edition records the specific primary texts consulted, the limited search scope, and the propositions not claimed as original. No exhaustive priority search or independent specialist review has been completed.

# 3. What a claim-coverage ratio measures

Let $p$ be a positive price vector, $b_i$ a specified nonnegative reference bundle, and $d_i$ an actually delivered, usable in-kind bundle. For componentwise minimum requirements, residual market expenditure is

$$n_i(p,d_i)=p\cdot(b_i-d_i)_+ . \tag{1}$$

The positive part is componentwise. A dollar of procurement spending is not automatically a dollar of usable provision: delivery, quality, eligibility, and substitutability matter. A service unavailable to the household cannot simply be deducted. Equation (1) applies to the stated fixed-bundle requirement, not to every welfare criterion.

Alternatively, for utility $u_i$ and a target $\bar u_i$, residual expenditure is

$$e_i(p,\bar u_i;d_i)=\inf_{x\geq0}\{p\cdot x:u_i(x+d_i)\geq\bar u_i\}. \tag{2}$$

This generally is not the original expenditure function minus the provider's cost of $d_i$. The choice between (1) and (2) is substantive. Neither is a complete measure of welfare, autonomy, rights, status, or political voice.

Let $y_i^M$ denote market income, $t_i$ taxes paid, and $T_i$ transfers received. Disposable purchasing power is $y_i^D=y_i^M-t_i+T_i$. When $n_i>0$, fixed-bundle coverage is $\chi_i=y_i^D/n_i$. At $n_i=0$, report “reference requirement met in kind” rather than manufacture an infinite numerical observation. Multiplying all prices and monetary incomes by the same positive number leaves coverage unchanged.

A claim decomposition may include labor, asset returns, transfers, and provision. But public transfers must satisfy a financing identity, and private transfers must be charged to their senders. A closed one-period cash system requires $\int T_i\,di=\int t_i\,di$, absent separately recorded external receipts. Direct provision also uses real inputs. Debt would require an explicit intertemporal budget rather than an unexplained extra channel.

Three questions follow. Can the household afford the reference requirement at the prices in question? Can the proposed claims be financed without double-counting someone else's income? Is there a feasible allocation that supplies the required resources, with the stated behavior and access rules? Passing the first question alone does not answer the other two.

# 4. The retained CES diagnostic

Consider positive fixed $Z,R,L,K$, $0<\beta,\theta<1$, and $\sigma>1$. Define $\rho=(\sigma-1)/\sigma\in(0,1)$ and

$$X(A)=\left[\theta L^\rho+(1-\theta)(AK)^\rho\right]^{1/\rho},
\qquad y(A)=ZR^\beta X(A)^{1-\beta}. \tag{3}$$

Here $R$ is a fixed productive input, $K$ a fixed stock of machine capital, and $A$ its service productivity. The output price is one. Stocks are supplied inelastically; no saving, endogenous task creation, or investment response is modeled. The production function is concave and constant returns in the factor stocks at each fixed $A$.

Competitive factor prices give

$$w=Z(1-\beta)R^\beta\theta L^{\rho-1}X^{1-\rho-\beta}, \tag{4}$$

$$s(A)\equiv\frac{wL}{y}
 =\frac{(1-\beta)\theta L^\rho}{\theta L^\rho+(1-\theta)(AK)^\rho}. \tag{5}$$

Euler's identity gives $wL+r_KK+r_RR=y$. For $A\to\infty$,

$$y\sim C_yA^{1-\beta},\qquad
w\sim C_wA^{1/\sigma-\beta},\qquad
s\sim C_sA^{-\rho}, \tag{6}$$

with positive constants. Thus $s\to0$ does not determine the sign of wage growth. A labor-only household with fixed labor endowment $\ell_i>0$ and an externally specified requirement $B_i(A)\sim c_iA^{g_i}$ satisfies

$$\frac{w(A)\ell_i}{B_i(A)}\sim C_iA^{1/\sigma-\beta-g_i}. \tag{7}$$

**Proposition 1 (conditional growth comparison).** Under these assumptions, coverage tends to zero for a negative exponent, diverges for a positive exponent, and converges to a positive coefficient ratio for a zero exponent. The last case does not establish that coverage is at least one.

*Proof.* For $\rho>0$, $X/A$ tends to a positive constant. Substitute into (4), divide by the stipulated $B_i$, and compare powers. Equation (5) gives the labor-share limit. No equilibrium equation for $B_i$ has been supplied. $\square$

In a one-good economy with a fixed physical bundle in that good and its price normalized to one, $g_i=0$. Arbitrary nonzero $g_i$ must come from changing quantities, an external relative-price scenario, or an additional sector. Equation (7) does not endogenize those cases.

There is also an exact finite-$A$ diagnostic. Define

$$z(A)=\frac{(1-\theta)(AK)^\rho}{\theta L^\rho+(1-\theta)(AK)^\rho}.
$$

For differentiable $B_i$,

$$\frac{d\log\chi_i}{d\log A}
 =(1/\sigma-\beta)z(A)-\frac{d\log B_i}{d\log A}. \tag{8}$$

The asymptotic expression replaces $z(A)$ by one. This convergence can be slow when $\sigma$ is close to one. No dated transition threshold follows from the limiting sign.

# 5. An economy with endogenous essential-service prices

## 5.1 Goods, ownership, and preferences

Retain production (3). A second good is a service with fixed aggregate supply $H>0$, rented at price $p>0$. It represents a genuinely scarce consumption service, not all housing or all basic goods. It is distinct from productive input $R$: the same physical factor is not counted twice. A joint-use land model would require a separate resource-allocation problem.

There is a unit mass of households. Workers have mass $q\in(0,1)$, each supply $L/q$ labor units, and own none of $K,R,H$. Owners have mass $1-q$, supply no labor, and own those assets equally within their group. Supplies are fixed and cannot be withheld. Workers' preferences are

$$u_W(x,h)=x^{1-a}h^a,\qquad 0<a<1,
$$

and owners' preferences are $u_O(x,h)=x^{1-b}h^b$, with $0<b<1$. The model imposes no disutility of labor, borrowing, saving, or population change. It is therefore consistent with full employment at positive competitive wages even as wages become a small income channel.

Let $W=wL=sy$. Gross nonlabor income is

$$C=y-W+pH,\qquad V=y+pH=W+C. \tag{9}$$

Here $V$ is total current income valued in the produced-good numeraire. It is not a measure asserting that physical service supply expands. Consider a tax $0\leq\tau<1$ on owners' gross nonlabor income, transferred equally to workers. Aggregate disposable incomes are

$$I_W=W+\tau C,\qquad I_O=(1-\tau)C. \tag{10}$$

The tax is a thought-experiment instrument, not an optimal-policy recommendation. All three nonlabor sources are in its base. It is not a claim that taxing only pure site rent delivers the same result. Fixed endowments and no behavioral supply response are essential assumptions. Transfers sum exactly to taxes; $I_W+I_O=V$.

## 5.2 Solving both markets

Write $\Delta=a-b$, $k=b+\tau\Delta$, and $r=pH/y$. Cobb–Douglas demands imply

$$pH=aI_W+bI_O.
$$

Substituting (9)–(10) yields a unique positive solution,

$$r(\tau,s)=\frac{k+\Delta(1-\tau)s}{1-k},
\qquad p=\frac{y}{H}r(\tau,s). \tag{11}$$

Positivity holds because $k\in(0,1)$ and the numerator is positive for $0<s<1$. The produced-good market clears as well:

$$(1-a)I_W+(1-b)I_O=V-pH=y. \tag{12}$$

Factor prices, household optimization, both commodity markets, and the government's cash budget have therefore been specified. This is a closed competitive example, not just an income identity. For $\tau<1$ both household groups have positive budgets. The endpoint $\tau=1$ leaves owners no consumption and is excluded from the positive-consumption equilibrium; it may be used only as a limit.

Let $t=I_W/V$ be workers' disposable-income share and $m=pH/V$ the economy's service-expenditure share. Then

$$t(\tau,s)=\frac{\tau+(1-\tau)s(1-b)}{1+(1-\tau)s\Delta},
\qquad m=b+\Delta t. \tag{13}$$

Workers receive the following fraction of the physical service supply:

$$f(\tau,s)=\frac{aI_W}{pH}=\frac{at}{b+\Delta t}. \tag{14}$$

These are different shares: $s$ concerns produced output, $t$ total disposable income, and $f$ the service allocation.

## 5.3 Redistribution changes prices when tastes differ

Differentiating (11) at fixed $A$ gives

$$\frac{\partial r}{\partial\tau}
 =\frac{\Delta[1-s(1-a)]}{(1-k)^2}. \tag{15}$$

The bracket is positive. Moving income toward workers raises the service price when $a>b$, lowers it when $a<b$, and leaves it unchanged only when $a=b$. Price-invariant redistribution is thus a special demand case, not a general property of a fixed-supply tax. Output $y$ stays fixed at a given $A$ because the model assumes fixed productive stocks and labor supply, not because distribution never affects production.

Without transfers, $t(0,s)=s(1-b)/(1+s\Delta)\to0$. Since $b>0$, $p/y\to b/[(1-b)H]$. Consequently,

$$\frac{w}{p}\asymp A^{-\rho},\qquad
h_W=\frac{H}{q}f(0,s)\longrightarrow0. \tag{16}$$

This can occur with rising $w$ when $1/\sigma>\beta$. It is a scarcity-and-ownership example, not a novel general claim that rising average income can coexist with exclusion.

# 6. A budget-feasible support frontier

Specify a worker service target $\bar h>0$ and put $\eta=q\bar h/H$. An interior target requires $0<\eta<1$. Define

$$D_\eta=a(1-\eta)+b\eta,
\qquad t_\eta=\frac{\eta b}{D_\eta},
\qquad m_\eta=\frac{ab}{D_\eta}. \tag{17}$$

**Proposition 2 (exact service-floor support).** In the economy of Section 5, the smallest nonnegative tax delivering $h_W\geq\bar h$ is

$$\tau_*(s;\eta,a,b)
 =\left[\frac{\eta b-s(D_\eta-ab)}{D_\eta-s(D_\eta-ab)}\right]_+. \tag{18}$$

For $0<\eta<1$, this value is below one. A policy cap $\bar\tau<1$ permits the target exactly when $\tau_*\leq\bar\tau$, or equivalently $f(\bar\tau,s)\geq\eta$.

*Proof.* The function $at/[b+\Delta t]$ is strictly increasing in $t$, with derivative $ab/[b+\Delta t]^2$. Equation (13) is strictly increasing in $\tau$: its derivative has numerator $1-s(1-a)>0$ and a positive squared denominator. Solving $f=\eta$ gives $t=t_\eta$ and $m=m_\eta$. From (10),

$$t=\tau+(1-\tau)s(1-m).
$$

At the target, solve this equation for $\tau$ and substitute (17), giving (18). The denominator is positive since $0<m_\eta<1$ and $s<1$. A negative numerator means the untaxed allocation already meets the target. For a positive numerator, the denominator minus numerator is $a(1-\eta)>0$. Strict monotonicity proves minimality and the cap condition. $\square$

The same result can be written as a transfer requirement. When the target binds, $T_*/V=t_\eta-s(1-m_\eta)$. As $A\to\infty$, $s\to0$ and

$$\tau_*\longrightarrow\tau_\infty
 =\frac{\eta b}{a(1-\eta)+b\eta},
\qquad \frac{T_*}{V}\longrightarrow\tau_\infty>0. \tag{19}$$

Thus a fixed, positive service target can require a nonvanishing income share even though production of the other good expands without bound. This is a counterexample to generalizing v1.1's negligible-gap conclusion across all essential-resource models. It is not a statement about the actual cost of a real-world program.

For common expenditure shares $a=b$, equations (18)–(19) reduce to

$$\tau_* =\left[\frac{\eta-(1-a)s}{1-(1-a)s}\right]_+,
\qquad\tau_\infty=\eta. \tag{20}$$

When tastes differ, substituting $\eta$ for the limiting fiscal threshold is generally wrong. The limiting capacity of a fixed cap is

$$f_\infty(\bar\tau)=\frac{a\bar\tau}{b+(a-b)\bar\tau}. \tag{21}$$

A target strictly below this value is eventually achievable; a target strictly above it is eventually not. The exact finite formula, rather than a rounded limit, settles equality and near-boundary cases.

## 6.1 Physical and distributional limits

If $\eta>1$, the workers' target alone exceeds the service stock. No transfer can fix that. At $\eta=1$, delivering the entire stock to workers leaves owners zero service, inconsistent with an interior positive-consumption allocation. If owners also have a floor $\bar h_O>0$, define $\eta_O=(1-q)\bar h_O/H$. Necessary physical feasibility is $\eta+\eta_O\leq1$.

Within the transfer-only instruments of this model, both groups' service floors hold precisely when there is a $\tau\in[0,\bar\tau]$ with

$$\eta\leq f(\tau,s)\leq1-\eta_O. \tag{22}$$

By continuity and strict monotonicity this is equivalent to the intersection of $[f(0,s),f(\bar\tau,s)]$ and $[\eta,1-\eta_O]$ being nonempty. Physical feasibility alone is not enough under a restricted instrument set. Requirements for the produced good would add further constraints; (22) does not claim to settle them.

## 6.2 Parameter uncertainty without a calibrated forecast

For independent intervals $a\in[a_-,a_+]$ and $b\in[b_-,b_+]$, bounded strictly inside $(0,1)$, the largest limiting tax requirement is

$$\sup_{a,b}\tau_\infty
 =\frac{\eta b_+}{a_-(1-\eta)+\eta b_+}. \tag{23}$$

This follows by monotonicity: the expression decreases with $a$ and increases with $b$. It is an elementary sensitivity bound, not a new robust-control theorem. A cap strictly above it covers all limiting thresholds in the specified rectangle; no claim is made that an asymptotic bound covers every finite technology level in a different model. Estimating those intervals would require actual household evidence.

# 7. Basket affordability, chosen service, and utility

A fixed worker reference basket $(b_x,\bar h)$ costs $B=b_x+p\bar h$, with $b_x>0$. Under no transfer, $B\asymp y$ and (16) gives labor-only basket coverage tending to zero. This is now an endogenous-price instance of (7), with $g=1-\beta$.

However, making that basket affordable is not identical to making the household choose $h\geq\bar h$. If a policy places worker income exactly at basket cost, $I_W/q=b_x+p\bar h$, Cobb–Douglas demand is

$$h_W=a\left(\frac{b_x}{p}+\bar h\right)
 \longrightarrow a\bar h<\bar h. \tag{24}$$

The household can buy the reference basket but prefers another allocation. This does not refute the affordability measure: it identifies its meaning. Nor does it justify forcing the household to consume a paternalistically chosen bundle. The analyst must say whether the target is an opportunity, a realized resource allocation, or a welfare level.

Along the limiting $s\to0$, $y\to\infty$ path, $t\to\tau$ and $m\to b+\Delta\tau$. Basket affordability requires $t\geq q b_x/V+\eta m$, so its boundary tends to

$$\tau_{B,\infty}=\frac{\eta b}{1-\eta(a-b)}
 <\frac{\eta b}{a(1-\eta)+\eta b}=\tau_\infty. \tag{25}$$

Both denominators are positive, and their difference is $1-a>0$. Equation (25) is a comparison of well-defined criteria under this model, not a ranking of their moral desirability. The positive fixed $b_x$ prevents an exact finite-$A$ identification with the limiting basket expression.

For workers' utility target $\bar u>0$, the Cobb–Douglas expenditure function is instead

$$e_W(p,\bar u)=\frac{\bar u\,p^a}{(1-a)^{1-a}a^a}. \tag{26}$$

Without transfers, its coverage has exponent

$$\frac{wL/q}{e_W(p,\bar u)}
 \asymp A^{1/\sigma-\beta-a(1-\beta)}. \tag{27}$$

This exponent can be positive while physical service consumption tends to zero. For example, $\sigma=2$, $\beta=0.2$, and $a=0.35$ give exponent $0.02$, but the service-coverage exponent remains $-0.5$. Preferences permit substitution in welfare terms; a fixed service floor does not. Calling both “basic inclusion” without naming the criterion would conceal this disagreement.

For an illustration with $q=0.7$, $H=1$, and $\bar h=0.4$, one has $\eta=0.28$. With $a=0.35$ and $b=0.55$, the limiting actual-service tax is approximately $0.37931$, whereas the limiting basket-affordability boundary is approximately $0.14583$. These are stipulated model numbers, not recommended tax rates or empirical estimates. In this example redistribution lowers the service price because $a<b$, yet the two thresholds remain different.

# 8. Correcting the channel and aggregate-gap claims

## 8.1 Finite-channel lemma and its boundary

Suppose a household has finitely many *nonnegative, non-double-counted disposable* channels $q_j(A)\sim c_jA^{d_j}$, with $c_j>0$, and positive residual need $n(A)\sim c_nA^g$. For $d_* =\max_jd_j$,

$$\frac{\sum_jq_j(A)}{n(A)}
 \sim\frac{\sum_{j:d_j=d_*}c_j}{c_n}A^{d_*-g}. \tag{28}$$

*Proof.* Divide the finite sum by $A^{d_*}$. Smaller exponents vanish and positive leading coefficients cannot cancel. Divide by the need asymptotic. $\square$

This is an elementary asymptotic lemma. It organizes comparisons but does not prove that a fiscally feasible channel exists, that ownership reaches the target population, or that political institutions will preserve it. Applying it to gross claims while omitting taxes is invalid.

If the exponent difference is zero, a coefficient ratio above one implies eventual affordability and a ratio below one implies eventual failure. At coefficient ratio exactly one, no such conclusion follows. For $A>e$, both $1+1/\log A$ and $1-1/\log A$ converge to one from different sides. The ratio $1+\sin(\log A)/\log A$ crosses one indefinitely. Signed revenues net of liabilities can cancel leading terms; an infinite family of channels requires additional summability conditions. None is covered by (28).

## 8.2 What a bounded gap really proves

For a specified population $S$ and market claims $Q_i^M\geq0$, define the accounting gap at stated prices

$$G_S(A)=\int_S[n_i(A)-Q_i^M(A)]_+\,d\mu(i). \tag{29}$$

If $n_i(A)\leq\bar n_i$ on $S$ for all sufficiently large $A$, with $\int_S\bar n_i\,d\mu<\infty$, then $G_S(A)$ is bounded. If also $y(A)\to\infty$, $G_S/y\to0$. This conclusion is about $S$. For the whole-population gap, the corresponding integrable envelope must hold over the whole population, or a separate bound must control the complementary population's gap.

A counterexample to the unqualified whole-population statement is immediate. Give a fixed positive-mass labor-only subset bounded needs and the benchmark declining wages. Give its complement need $n_i(A)=y(A)^2$, while its aggregate market income is at most $y(A)$. The subset conditions hold, but the complementary gap divided by $y$ diverges. This example is not a plausible basic-needs forecast; it disproves a conclusion that lacked a restriction excluding it.

In a one-good benchmark with fixed bounded needs and an expanding supply of that same good, the original negligible-gap intuition can be retained under the corrected population condition. In the two-good model, a fixed positive quantity of scarce service has an endogenous price growing with $y$; the bounded-expenditure hypothesis fails. Equation (19) then gives a nonvanishing support share.

Even outside these examples, $G_S$ is a shortfall at specified prices, not a general intervention cost. Prices, behavior, eligibility, administrative costs, and supply may change when a policy is implemented. A low monetary ratio is not by itself proof of a feasible multi-good allocation. Public provision must enter the same physical constraints, even when the household pays no market price.

# 9. Reproducible checks and adversarial tests

The supplement contains a standard-library Python audit with deterministic grids. It evaluates the competitive factor derivatives using complex-step differentiation, checks factor exhaustion, and compares the analytical service price with an independently solved market-clearing equation. It tests both goods markets, household and fiscal budgets, the exact minimum-support formula and slightly subthreshold policies, price-response signs, physical impossibility, two-group floor compatibility, and the basket-versus-allocation distinction.

Additional tests cover the CES log derivative, the corrected subset gap and its whole-population counterexample, and the equality-boundary counterexample for (28). The audit also reproduces the numerical illustration and tests the limiting sensitivity bound on a finite parameter grid. The resulting `checks.json` records the actual assertion count and numerical tolerances. It is not evidence of current household behavior, a calibration, or a proof that no coding error remains.

The analytical proofs do not rely on successful simulations. Conversely, a script evaluating the same expression twice would not meaningfully test it; independent differentiation and numerical market clearing are included to reduce that risk. These remain internal AI-assisted checks, not independent replication by another researcher or formal machine verification of all theorems.

# 10. Limits, counterforces, and possible refutation

The support frontier is conditional on fixed factor stocks, fixed total labor, concentrated ownership, within-group homogeneity, Cobb–Douglas demand, full access to markets, and a collectable tax on all modeled nonlabor income. Saving, investment, avoidance, endogenous labor supply, market power, trade, changing household composition, and administrative costs are absent. Adding any of them can change both the price equation and the policy threshold. A model with broad ownership may not need the transfer in (10) at all.

The scarce service is fixed by assumption. Technological expansion of effective supply, location substitution, or changing quality could relax that constraint. The paper does not classify all healthcare, housing, energy, or care as permanently fixed. Likewise, persistent human-complementary tasks can prevent the CES limiting labor-share path. The mathematical scenario is not established by a benchmark score or an announced AGI date.

A fixed physical reference basket, a utility threshold, and a realized allocation express different evaluative choices. The paper deliberately does not select a uniquely correct one. Protection of nonmaterial interests is outside its scope. AI moral status is neither assumed nor refuted; the accounting population here consists of human households.

The fiscal instrument is particularly stylized. Taxing fixed current endowment returns without changing supply is not the same as taxing future capital accumulation. All funding and quantities must be re-solved in an intertemporal version. Equations (18) and (23) should not be imported into a real tax recommendation without that work.

The proposed residual originality is limited and defeasible. An earlier equivalent heterogeneous-demand frontier or equivalent comparison would reduce the contribution to an independently reproducible synthesis and correction. An algebraic counterexample within the stated assumptions would require an erratum, not an appeal to the project's historical importance. Neither a DOI nor an immutable timestamp protects a scientific claim from criticism.

# 11. A durable research starting point

The public record should preserve the motivating question, the exact versioned formulation, the proof obligations, the negative results, and the division of contributions. It should not freeze an incorrect theorem in place or backdate a later improvement. Version 1.1 remains available under its original DOI and bytes. Version 1.2 identifies its corrections; any further substantive edition should have its own version identifier within the same paper lineage.

Future work can prioritize a finite-horizon model with investment and tax avoidance, heterogeneous households with empirically estimated expenditure systems, and direct provision with quality and access constraints. A stronger future AI may assist those extensions, but its output must undergo the same source checks, counterexample tests, and accountable versioning. Greater model capability is not retrospective proof of the earlier paper.

The result is a research coordinate rather than an asserted global first. The defensible historical statement is that this named project publicly recorded this particular formulation and its disclosed collaboration at a documented time. Priority over a broad economic concern, representativeness of humanity, and future historical importance do not follow.

# Contribution, provenance, and non-amendment statement

Hongju Liu supplied the motivating concern about economic distribution as productive and cognitive work shifts toward AI, directed the project, and authorized revision and open DOI deposit. That role is not a claim that he independently derived every equation or reviewed every line. No separate final human line-by-line or external specialist review is claimed.

The predecessor v1.1 identifies OpenAI ChatGPT (GPT-5.6 Sol) as its substantial research and drafting assistant. This v1.2 revision was developed with OpenAI ChatGPT (GPT-6 Astra Pro): primary-source retrieval, critical comparison, identification of the quantifier and model-closure problems, the heterogeneous-demand extension, proofs, code, numerical checking, writing, and publication preparation were substantially AI-assisted. Internal critique by the same assistant is not an independent peer review. Hongju Liu remains the human author of record and responsible depositor; the AI system is not represented as an accountable legal author.

This edition records the human originator's research concern and the current contribution account without claiming that the concern had never occurred to anyone else. The preserved public version is the evidence for its contents and availability, not for an unrecorded private discovery date.

This paper belongs to the adjacent, first-party research program hosted with the Trinity Accord. It is not one of the three Bitcoin Originals, does not amend or authoritatively interpret them, and is not independent evidence that they are true. Errors or improvements can change evaluation of the research without changing the fixed historical source texts. Its license applies only to material for which the depositor holds the relevant rights; cited works retain their rights.

# References

[1] Sen, Amartya. 1981. “Ingredients of Famine Analysis: Availability and Entitlements.” *Quarterly Journal of Economics* 96(3): 433–464. DOI: 10.2307/1882681.

[2] Acemoglu, Daron, and Pascual Restrepo. 2018. “The Race between Man and Machine: Implications of Technology for Growth, Factor Shares, and Employment.” *American Economic Review* 108(6): 1488–1542. DOI: 10.1257/aer.20160696.

[3] Ray, Debraj, and Dilip Mookherjee. 2022. “Growth, Automation, and the Long-Run Share of Labor.” *Review of Economic Dynamics* 46: 1–26. DOI: 10.1016/j.red.2021.09.003. Author order follows the consulted author-hosted article, which notes random ordering.

[4] Jones, Charles I. 2026. “AI and Our Economic Future.” *Journal of Economic Perspectives* 40(3): 3–22. DOI: 10.1257/jep.20261505.

[5] Hazari, Bharat, and Vijay Mohan. 2024. “Exclusion and the Growth of AI Technology: A Trade-Theoretic Analysis.” *Frontiers in Human Dynamics* 6: 1203664. DOI: 10.3389/fhumd.2024.1203664.

[6] Båge, Johan, and Stella Wilson. 2026. “Pinning the Wage to Scarcity and Technology: Automation, Purchasing Power, and the Rents of Non-Produced Inputs.” September manuscript; author-authorized full-text cross-post, clawRxiv:2609.02873, 7 September 2026. Consulted 22 September 2026 at https://clawrxiv.io/abs/2609.02873. The full-text cross-post, including Sections 6.2 and Appendices C–D, is the comparison source used in this revision.

[7] Korinek, Anton, and Lee Lockwood. 2026. “Public Finance in the Age of AI: A Primer.” NBER Working Paper 34873. DOI: 10.3386/w34873.

[8] Liu, Hongju. 2026. “The Claim Architecture Transition: Transformative AI, Real Claim Closure, and General Equilibrium Beyond Wage-Based Distribution.” TA-TR-2026-14, v1.1. DOI: 10.5281/zenodo.22871209. First-party, substantially AI-assisted predecessor; preserved rather than silently replaced.
