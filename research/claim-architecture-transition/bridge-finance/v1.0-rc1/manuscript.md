---
title: "Financing the Automation Transition Without Pledging Subsistence"
subtitle: "Public Upside Claims, Endogenous Prices, and Investment Limits"
author: "Hongju Liu"
date: "22 September 2026 · Working paper v1.0-rc1"
lang: en
fontsize: 11pt
geometry: margin=25mm
linestretch: 1.08
mainfont: Liberation Serif
colorlinks: false
header-includes:
  - '\usepackage{amsmath,amssymb,booktabs,fancyhdr}'
  - '\setlength{\emergencystretch}{3em}'
  - '\pagestyle{fancy}'
  - '\fancyhf{}'
  - '\fancyhead[L]{\small Public Upside Claims}'
  - '\fancyhead[R]{\small Working paper · v1.0-rc1}'
  - '\fancyfoot[C]{\thepage}'
  - '\setlength{\headheight}{14pt}'
---

**Status.** Complete working-paper release candidate for public criticism; not externally peer reviewed. No journal acceptance, foundational-priority certification, securities offering, or new DOI is claimed. This is a separate extension of the TA-TR-2026-14 research program, not a replacement of its published versions.

**Origin and assistance.** Hongju Liu proposed financing present basic needs against a potentially abundant future while distinguishing the arrangement from ordinary long-term debt. AI assisted materially with literature review, formalization, proofs, numerical checks, and writing. The state-contingent contract and the particular models below are developments of that proposal, not a claim that the original proposal already contained every result.

# Abstract

Expected gains from automation need not finance the current consumption of households losing labor income. We study a limited remedy: sell claims on verifiable future public surplus, subject to state-by-state protection of specified public uses, and transfer the proceeds without personal recourse to recipients. In a finite-state exchange economy with competitive logarithmic investors, we derive the market-clearing price and the exact condition for covering a current support target. Common growth of public payouts and investors' other future income need not increase current financing. We then characterize the unique least-cost payout schedule for a prescribed transfer, where cost is the public beneficiaries' expected utility loss. Its state allocation follows relative marginal valuation rather than an arbitrary uniform revenue share. A separate production extension lets the same investors finance both private capital and the public claim. Greater issuance increases present support but reduces investment; a minimum-investment constraint yields an explicit additional financing limit. Raising the public revenue share can eventually reduce financing to zero because the investment base disappears. These results distinguish contract feasibility, beneficiary participation, and production preservation. Existing debt and insurance with identical enforceable cash flows remain an equivalence benchmark. All examples clear their resource accounts; none establishes a fiscal multiplier. The contribution proposed is a transparent inverse-design framework connecting a current support target to future concessions and investment constraints, not a new theory of sovereign debt or a forecast that abundance is certain.

**Keywords:** automation transition; public finance; contingent claims; consumption protection; endogenous asset prices; investment; incomplete markets.

**JEL:** D53, E21, E62, H63, O33.

# 1. The question: a bridge, not a new name for debt

A society may expect substantial future technological gains while some households face an immediate loss of earnings. Those households cannot necessarily borrow against the gains: they may not own them, the gains may be public, or a transferable claim may not yet exist. Expectations that raise some asset valuations therefore need not provide current purchasing power to the people experiencing the transition.

The question is not whether the future is guaranteed to be abundant. It is whether a *conditional and enforceable* portion of future public resources can support a present transfer without creating a fixed new claim on resources reserved for basic needs. We call such a transaction public-upside bridge finance. The label denotes a payoff rule and a use of proceeds, not a distinct legal asset class.

An illustrative claim pays nothing when public resources do not exceed specified protected uses and pays part of the remaining surplus otherwise. The recipient of current support is not a personal borrower. Investors, rather than the household, bear the contractually specified risk that the surplus is small or absent. This does not eliminate risk: a smaller downside obligation may lower the price investors will pay today. Nor does zero payment in a bad state create enough resources to meet a previously underfunded public floor.

The proposed framework reverses a common design sequence. Instead of forecasting a large future aggregate, multiplying it by a fraction, and treating the result as available borrowing, it starts from a current support target. It then asks which future payments can finance that target, what those payments cost beneficiaries, and whether their issuance changes the investment needed to generate the revenue.

Three distinctions organize the analysis. First, aggregate output, an issuer's enforceable resources, and the market value of a transferable claim are different objects. Second, maximum financing need not be desirable financing. Third, financing consumption can compete with capital formation even when every claim is honestly honored. These distinctions survive the removal of labor income; they do not require deception, catastrophic AI behavior, or permanently declining human skills.

The models deliberately stop short of a complete macroeconomic theory. The exchange benchmark does not have unemployed resources or a demand multiplier. The production extension adds endogenous capital but retains full commitment, a fixed public revenue rule, and a simple technology. Neither assumes a date of AGI arrival. This disciplined scope permits a complete working paper without claiming to settle every transition mechanism.

## 1.1 Relationship to prior research

Automation and borrowing constraints are already closely connected. Beraja and Zorzi [1] show why displaced workers' limited ability to smooth consumption can affect the efficiency of automation. Korinek and Suh [2] distinguish the progression of automation from the accumulation of productive capital. We take the possibility of a transition consumption gap as motivation rather than as a new result.

Publicly supplied liquidity is also an established subject. Holmström and Tirole [3] explain how public commitments can supplement private liquidity provision. GDP-linked securities, including Kamstra and Shiller's Trills [4], already link payments to economic outcomes. Guerson [5] studies optimal state-contingent sovereign contracts with limited commitment and extends the analysis to investment and capital taxation. Thus neither contingent public repayment nor the inclusion of investment is introduced here.

The empirical experience is not uniformly favorable. Igan, Kim, and Levy [6] find substantial risk and liquidity premia for the GDP-linked warrants they study. Our frictionless benchmark abstracts from these costs and should not be read as predicting cheap issuance. The Windfall Clause [7] proposes an ex ante commitment to share extraordinary AI profits. Our question concerns the conditions under which an already enforceable public resource claim can be monetized before its payment, not the invention of AI gain-sharing.

The candidate contribution is the combination of a closed-form financing frontier, a target-indexed beneficiary-cost problem, and an explicit investment-preserving issuance bound in a tractable setting. The mathematical methods are standard. We make no claim that each formula is globally unprecedented. The supplied source audit identifies the reading scope and close predecessors rather than presenting a targeted search as a proof of priority.

# 2. Contract scope and the replication benchmark

There are two dates, 0 and 1, and finitely many date-1 states $s=1,\ldots,m$ with common probabilities $p_s>0$, summing to one. All quantities are units of one real good; nominal GDP, stock-market valuation, and consumer surplus are not interchangeable with that good.

The public arrangement has enforceable date-1 resources $R_s$. A specified amount $G_s$ is protected. In the benchmark,

$$R_s\geq G_s>0,\qquad 0\leq\bar x_s\leq R_s-G_s. \tag{1}$$

The new total payment vector satisfies $0\leq x_s\leq\bar x_s$. It does not carry a further guaranteed principal, unpaid-interest accumulation, or claim on recipients' labor income. A state with no eligible surplus has zero cap. Existing senior claims and relevant costs must already have been accounted for in defining $R_s$; the model does not authorize changing their legal priority.

The initial feasibility of $G_s$ is an assumption. When an actual state has $R_s<G_s$, eliminating the new payment prevents additional extraction but does not finance the shortfall. Likewise, calling an expenditure protected does not make it immune to price changes or ensure that the corresponding physical services exist. The present one-good model sets those complications aside.

**Proposition 1 (cash-flow equivalence).** Holding agents, information, enforcement, collateral, access, and costs fixed, two instruments with identical net date- and state-contingent transfers have identical implementation possibilities in this model.

*Proof.* Replace either instrument in every budget with the other. The budgets and feasible allocations are unchanged. For example, a fixed payment $D\geq\max_s x_s$ combined with insurance paying $D-x_s$ to the issuer has net payment $x_s$. The equivalence requires that the insurer's funding, premium, collateral, and performance are genuinely feasible and fully counted. An algebraic insurance payoff without a solvent counterparty is not implementation. $\square$

Consequently, a different security name does not create borrowing capacity. A genuine improvement must change a relevant constraint: make an otherwise nontransferable public claim tradable, improve verifiability or commitment, broaden access, or reduce implementation costs. If government can already issue the same state-contingent claim and make the same transfer, this proposal adds no separate financial technology.

Nor is a protected public floor derived from asset pricing. It is an explicitly chosen distributional constraint. The analysis studies its cost and feasibility conditional on an appropriate mandate; it does not prove that a particular government has that mandate or may sequester private wealth without compensation.

# 3. Endogenous pricing in an exchange benchmark

## 3.1 Agents and clearing

A unit mass of identical, atomistic investors has aggregate current resources $W>0$ and state-dependent other future income $y_s>0$. The public resources $R_s$ are not also counted inside $y_s$. Investors have utility

$$\log c_0+\beta\sum_s p_s\log c_{1s},\qquad\beta>0. \tag{2}$$

There is no storage, private production, outside asset, or borrowing instrument in this benchmark. These restrictions are substantive. Section 7 changes the opportunity set and re-solves the equilibrium.

The issuer commits to $x$ and normalizes the supply of claims to one. At price $B$, an investor chooses a nonnegative holding $z$, with

$$c_0=W-Bz>0,\qquad c_{1s}=y_s+zx_s. \tag{3}$$

A symmetric equilibrium clears at $z=1$. Identical per-unit-mass notation is used for individual and aggregate endowments. The supported population has current resources $y_0>0$, receives the proceeds $B$, and retains future public resources $R_s-x_s$. The positivity of $y_0$ will matter when logarithmic beneficiary welfare is used below.

## 3.2 The price and financing frontier

Define

$$\Lambda(x)=\beta\sum_s p_s\frac{x_s}{y_s+x_s}. \tag{4}$$

**Proposition 2 (competitive price and cap).** A nonzero admissible $x$ has unique symmetric clearing price

$$B(x)=\frac{W\Lambda(x)}{1+\Lambda(x)}. \tag{5}$$

It is strictly increasing in every payment coordinate and strictly concave on the nondegenerate payment box. The maximum proceeds are $B(\bar x)$, and any target $\Delta\in[0,B(\bar x)]$ can be financed by an admissible payment.

*Proof.* The investor objective is strictly concave in $z$ at a positive price. Its derivative vanishes at $z=1$ exactly when

$$\frac{B}{W-B}=\beta\sum_s p_s\frac{x_s}{y_s+x_s}.$$

Solving gives (5), with $0<B<W$. The clearing position is feasible and is the global optimum. Because nonpurchase is allowed, willingness to hold the issue follows from optimization, not from an assumed public duty.

Each summand of $\Lambda$ has derivative $\beta p_sy_s/(y_s+x_s)^2>0$ and second derivative $-2\beta p_sy_s/(y_s+x_s)^3<0$. The outer function $Wv/(1+v)$ is increasing and concave. Its Hessian composition gives strict concavity on the coordinates whose caps are positive. Monotonicity implies the maximum at $\bar x$. Finally, $B(t\bar x)$ continuously increases from zero to $B(\bar x)$ for $t\in[0,1]$. The intermediate value theorem implements every intervening target. The all-zero cap permits only zero proceeds. $\square$

The capitalization limit is about this specific investor opportunity set, not the money supply. Here $\Lambda<\beta$ for finite positive endowments, so $B<W\beta/(1+\beta)$. Adding other savers, assets, production, or monetary arrangements requires a new equilibrium rather than interpreting $W$ as a universal deposit pool.

Current resources clear: investor consumption $W-B$ plus recipient consumption $y_0+B$ equals $W+y_0$. In each future state, $(y_s+x_s)+(R_s-x_s)=y_s+R_s$. The transfer changes command over output; it creates no extra good.

# 4. Abundance is not a sufficient statistic for borrowing

Suppose a technology scale $a>0$ multiplies both the promised payment and the buyer's other future income in every paying state: $x_s(a)=ak_s$ and $y_s(a)=av_s$, where $v_s>0$. With $W$, probabilities, and $\beta$ fixed, each ratio in (4) is unchanged. Thus $B$ is unchanged even though the future payment grows without bound.

This is not a general law that growth cannot finance transfers. Increasing $x_s$ while holding the buyer's other income fixed raises its price. Increasing current resources can do the same. The counterexample instead identifies an omitted variable: the future marginal value of the payment to the actual buyer.

For CRRA marginal utility $u'(c)=c^{-\gamma}$, the same equilibrium argument gives

$$\frac{B}{(W-B)^\gamma}=\beta\sum_s p_s\frac{x_s}{(y_s+x_s)^\gamma}. \tag{6}$$

The left-hand side is strictly increasing from zero to infinity on $(0,W)$. Under common scaling the right-hand side is proportional to $a^{1-\gamma}$. For nonzero payments, as $a\to\infty$, $B$ tends to zero if $\gamma>1$, is unchanged if $\gamma=1$, and tends to $W$ if $0<\gamma<1$. These are model comparative statics, not an empirical preference estimate. CRRA links risk aversion and intertemporal substitution; the result is not exclusively about aggregate risk.

When only a high state pays $D$, with probability $\pi$ and buyer income $Y$ in that state, let $b=\beta\pi$. Equation (5) becomes

$$B(D)=\frac{WbD}{Y+(1+b)D},\qquad
D_{\rm req}(\Delta)=\frac{\Delta Y}{bW-(1+b)\Delta}. \tag{7}$$

The inverse requires $\Delta<bW/(1+b)$ and $D_{\rm req}\leq\bar D$. A limiting price attained only as $D\to\infty$ must not be confused with the proceeds from a finite eligible surplus.

# 5. Financing a target without unnecessarily selling the future

The maximum-issue result does not identify the best payment schedule for beneficiaries. Two schedules can raise the same current amount and impose different losses on future public uses.

## 5.1 A target-indexed cost frontier

For this section only, measure the loss to future beneficiaries by

$$L(x)=\sum_s p_s\log\frac{R_s}{R_s-x_s}. \tag{8}$$

This is an explicit welfare metric, not the unique ethically correct one. Conditions (1) make it finite. For a required current transfer $\Delta$, solve

$$\ell(\Delta)=\min_{0\leq x\leq\bar x}L(x)
\quad\text{subject to}\quad B(x)\geq\Delta. \tag{9}$$

The instrument promises payments after verifiable state realization. A coarse or manipulable index may not support these schedules; its information restrictions must be added to the feasible set.

**Proposition 3 (least-cost schedule).** For every $0\leq\Delta\leq B(\bar x)$, (9) has a unique solution $x^*(\Delta)$ and raises exactly $\Delta$. Its value $\ell$ is nondecreasing and convex. At an interior target, there is a nonnegative scalar $k$ such that

$$x_s^*(k)=\left[\frac{\sqrt{k^2y_s^2+4ky_s(y_s+R_s)}-(2+k)y_s}{2}\right]_{0}^{\bar x_s}, \tag{10}$$

where $[z]_0^u=\min\{u,\max\{0,z\}\}$, and $k$ is chosen to make

$$\beta\sum_s p_s\frac{x_s^*(k)}{y_s+x_s^*(k)}=\frac{\Delta}{W-\Delta}. \tag{11}$$

The allocation is unique; the multiplier can be nonunique on a plateau where several coordinates are capped or inactive.

*Proof.* The box is compact and (5) is continuous, so the feasible set is nonempty precisely on the stated range. Because $B$ is concave, its superlevel set is convex. The objective has positive diagonal second derivatives $p_s/(R_s-x_s)^2$, giving a unique minimizer on the nonzero-cap coordinates. If the target constraint were slack, scaling a nonzero solution downward would reduce every payment and reduce $L$ until equality held. At zero the optimum is zero; at the maximum target strict price monotonicity forces $x=\bar x$.

For $0<\Delta<B(\bar x)$, the equivalent constraint (11) with inequality admits strict feasibility relative to the active box. The necessary and sufficient convex KKT conditions give, on an uncapped positive coordinate,

$$\frac{1}{R_s-x_s}=\lambda\beta\frac{y_s}{(y_s+x_s)^2}.$$

Set $k=\lambda\beta$. Solving the quadratic and respecting the boundary inequalities gives (10). Its unbounded root increases with $k$; clipping implements the state caps. A monotone scalar search is therefore sufficient, without claiming a unique multiplier at every target.

For convexity of $\ell$, mix optimizers for two targets. Concavity of $B$ makes their mixture feasible for the mixed target; convexity of $L$ bounds its cost by the mixed costs. Nondecreasingness follows because a higher target shrinks the feasible set. $\square$

For a small issue, the ratio of the marginal current proceeds to marginal beneficiary loss in state $s$ is proportional to $R_s/y_s$. Payments are attractive where beneficiaries can surrender resources relatively cheaply and buyers value the corresponding increment relatively highly. Equal proportions of every state's surplus generally do not equalize these ratios.

This characterization neither recommends a particular welfare function nor invents optimal sovereign insurance. It gives an explicit inverse calculation for the specified competitive clearing mechanism and a chosen support target. Different beneficiary weights, investment feedback, or incomplete observability change the optimum.

## 5.2 Ability to finance is not willingness to finance

Suppose the same beneficiary population evaluates current and future resources by logarithms, with future weight $\delta>0$. Raising exactly $\Delta$ using the least-cost schedule changes its utility by

$$U(\Delta)=\log\frac{y_0+\Delta}{y_0}-\delta\ell(\Delta). \tag{12}$$

This function is strictly concave on the feasible interval. Thus an unconstrained welfare-maximizing amount is unique; it can be zero or below maximum financing. If a current floor requires at least $\Delta_0$, the constrained maximizer on $[\Delta_0,B(\bar x)]$ can be evaluated against the no-issue option. If every amount in that interval gives negative $U$, floor protection at date 1 and investor participation do not make the contract desirable under this particular beneficiary criterion.

When present and future beneficiaries are different people, (12) is a stated social weighting, not proof that every generation benefits. Authorizing that trade-off is outside the pricing theorem. A conditional claim can shift losses toward favorable future states without making those losses disappear.

## 5.3 A synthetic comparison at the same transfer

Take $W=100$, $\beta=1$, and the following endowments and caps:

| State | $p_s$ | $y_s$ | $R_s$ | $G_s$ | $\bar x_s$ |
|:--|--:|--:|--:|--:|--:|
| Low | 0.25 | 50 | 100 | 100 | 0 |
| Middle | 0.50 | 100 | 200 | 150 | 25 |
| High | 0.25 | 500 | 600 | 200 | 200 |

All caps preserve the floor; they additionally limit the sale to half of eligible surplus in each positive-cap state. For a current transfer of 10, a uniform share of the caps requires approximately $(0,14.6109,116.8872)$. The least-cost schedule is $(0,25,23.2558)$. Both clear at price 10. The expected logarithmic future loss is about 0.092100 for the uniform schedule and 0.076648 for the least-cost schedule, a reduction of approximately 16.78 percent.

The high state has the largest gross public resources, but buyers are also much richer there. Merely charging the largest payment to the largest public surplus is not generally cheapest. These are stipulated inputs and deterministic calculations, not estimated welfare gains for a country.

# 6. Resource closure and a voluntarily traded example

For a separate two-state example, let $W=100$, $\beta=1$, $p_L=p_H=1/2$, $y_L=50$, and $y_H=100$. Let public resources be $(100,400)$, protected uses $(100,200)$, and payments $(0,100)$. Equation (7) gives $B=20$.

With initial recipient resources $y_0=5$, support raises current consumption to 25. Investors consume 80 now and $(50,200)$ later; recipients retain future resources $(100,300)$. Current consumption totals 105, exactly the initial endowment. Future totals are 150 and 500, also exactly the corresponding original resources.

The investor's utility gain relative to no purchase is $\log(0.8)+\tfrac12\log 2>0$. If the recipient is the same two-period population with $\delta=1$, its utility gain is $\log 5+\tfrac12\log(300/400)>0$. Thus a transaction can be voluntary on both sides while satisfying the stated floors. This is an existence example, not a universal welfare theorem.

For this example, multiplying both $y_H$ and the high-state payment by 100 leaves $B=20$. Raising only the payment from 100 to 200 raises $B$ to 25. Raising only $y_H$ to 10,000 lowers $B$ to about 0.492611. These comparisons isolate the pricing mechanism and do not assume changes in investor entry, technology, or current resources.

# 7. The same buyers can also build productive capital

The exchange benchmark is not a model of how future abundance is produced. This section replaces it with a distinct economy in which investors choose both a private productive investment and a holding of the public claim. The price from (5) cannot simply be reused with an arbitrarily frozen future tax base.

## 7.1 Timing and private optimization

There are low and high states, with high probability $\pi\in(0,1)$. An atomistic investor spends $i\geq0$ current goods on a private project. It produces $F(i)=a\sqrt{i}$ only in the high state, where $a>0$. Investors also have other future incomes $y_H,y_L>0$. A committed output share $\tau\in(0,1)$ goes to the public arrangement. The public share is an assumed enforceable allocation, not a costless normative entitlement; changes in $\tau$ affect investment.

The issuer sells fraction $\theta\in[0,\alpha]$, with $0<\alpha\leq1$, of that public high-state revenue. A separate, already funded public endowment $G_s>0$ supplies the protected future floor. Thus the high-state total payment per unit claim is

$$D=\theta\tau a\sqrt I, \tag{13}$$

where $I$ is aggregate equilibrium investment. The baseline endowment is not pledged. Investors are atomistic: an individual's investment does not change the aggregate payment on its diversified public claim. This fiscal externality is part of the model. There is full commitment and no hidden expropriation.

Given $B,D$, an investor chooses $(i,z)$ with

$$c_0=W-i-Bz,\quad c_H=y_H+(1-\tau)a\sqrt i+zD,\quad c_L=y_L. \tag{14}$$

Its utility is $\log c_0+\beta[\pi\log c_H+(1-\pi)\log y_L]$. The feasible nonnegative choices give positive consumption. The objective is concave, and at a positive issue its interior first-order conditions are sufficient. At zero issue, the irrelevant security is omitted. In equilibrium $z=1$ and $i=I$.

## 7.2 Exact equilibrium and an investment-preserving bound

Set $b=\beta\pi$, $g=\theta\tau/(1-\tau)$, $v=y_H/[a(1-\tau)]$, and

$$Q=2+b+2(1+b)g. \tag{15}$$

**Proposition 4 (financing with investment competition).** The unique symmetric equilibrium investment and price are

$$\sqrt I=\frac{bW}{\sqrt{v^2+QbW}+v},\qquad B=2gI. \tag{16}$$

For fixed $\tau$, investment strictly falls and current proceeds strictly rise as $\theta$ increases. If $0<I_{\min}\leq I(0)$ is an additional required investment floor, define

$$g_I=\frac{bW-(2+b)I_{\min}-2v\sqrt{I_{\min}}}
{2(1+b)I_{\min}},\qquad
\theta_I=\frac{1-\tau}{\tau}g_I. \tag{17}$$

Then the largest proceeds compatible with the sale cap and investment floor are $B(\min\{\alpha,\theta_I\})$. A transfer target can be financed under both restrictions exactly when it is no larger than this amount. If $I_{\min}>I(0)$, even no issuance cannot satisfy the floor.

*Proof.* The two interior first-order conditions imply

$$B=\frac{D}{(1-\tau)F'(I)}=2gI,$$

and

$$y_H+(1-\tau)F(I)+(1+b)D
=b(1-\tau)F'(I)(W-I).$$

Substitution reduces the equation to $QI+2v\sqrt I=bW$. Its left side is strictly increasing from zero, so it has a unique positive solution. Solving the quadratic in $\sqrt I$ and rationalizing yields (16). It implies $W-I-B>0$, since the defining equation gives

$$b[W-(1+2g)I]=2(1+g)I+2v\sqrt I>0.$$

Thus the constructed choices satisfy positivity and the first-order conditions. Strict concavity along feasible investment and security choices establishes individual optimality.

Implicit differentiation gives

$$\frac{dI}{dg}=-\frac{2(1+b)I}{Q+v/\sqrt I}<0,$$

and

$$\frac{dB}{dg}=2I\frac{2+b+v/\sqrt I}{Q+v/\sqrt I}>0. \tag{18}$$

The floor is equivalent to $g\leq g_I$. The hypothesis $I_{\min}\leq I(0)$ ensures $g_I\geq0$; a negative value must not be silently clipped and called feasible. Continuity and price monotonicity then implement every target below the stated cap. $\square$

This result supplies a second reason not to issue the maximum claim: more current support can reduce the investment that produces future revenue. The magnitude depends on the opportunity set. Outside funding, idle resources, productive uses of the transfer, or other technologies can change the result. It is not a universal crowding-out claim.

For fixed $\theta>0$, current proceeds tend to zero as $\tau\downarrow0$. They also tend to zero as $\tau\uparrow1$ when $y_H>0$: $\sqrt I$ is asymptotic to $baW(1-\tau)/(2y_H)$, so $B=O(1-\tau)$. A positive financing maximum therefore occurs at an interior revenue share when the endpoint extension is allowed. This does not identify an optimal social tax rate. It shows why collecting a larger percentage of a changing base need not raise more finance.

## 7.3 A worked investment-preservation example

Take $W=100$, $b=0.5$, $a=100$, $y_H=20$, $y_L=50$, $\tau=0.2$, and a public baseline of 100 in both states. The current recipient endowment can be any positive $y_0$; it does not affect these investor equations.

| Fraction of public upside sold $\theta$ | Investment $I$ | Current support $B$ | High-state project output $F(I)$ |
|--:|--:|--:|--:|
| 0 | 19.125349 | 0 | 437.325385 |
| 0.5 | 16.681002 | 4.170251 | 408.423825 |
| 1 | 14.792899 | 7.396450 | 384.615385 |

An investment floor $I_{\min}=18$ permits only $\theta\leq0.213236$ and therefore at most about $1.919120$ of support. An issue raising four units is financially feasible under a sufficiently large sale cap, but not under this particular investment floor. The paper does not prescribe 18 as a real-world threshold.

The accounts also close. At date 0, investor consumption $W-I-B$, recipient consumption $y_0+B$, and investment $I$ sum to $W+y_0$. In the high state, investor consumption $y_H+(1-\tau+\theta\tau)F(I)$ plus public resources $100+(1-\theta)\tau F(I)$ equals $y_H+100+F(I)$. In the low state the project pays zero and the unpledged public baseline remains. Selling more public upside changes both its allocation and the size of the production base.

# 8. What this paper can and cannot say about contraction

The user's motivating concern is a transition in which wage losses reduce current spending before future productive abundance arrives. The models explain one financing channel; they do not estimate the aggregate-demand consequence.

In the exchange example, recipient consumption rises by exactly the amount investor consumption falls. Current output does not rise. In the production extension, part of the transfer competes with investment. Neither result licenses the statement that the issue pays for itself by expanding GDP.

To analyze a demand-deficient economy, one must add a spending and supply closure. For illustration only, suppose a fixed-price slack-capacity sector has planned demand $E_0+\mu Y$, where $0\leq\mu<1$. Let each unit of the transfer generate $m_H$ units of direct recipient spending, while financing displaces $\zeta$ units of other current private expenditure, counting consumption and investment together without duplication. Holding all other autonomous demand fixed, goods-market equilibrium below capacity gives

$$\Delta Y=\frac{m_H-\zeta}{1-\mu}B. \tag{19}$$

This is an explicitly separate Keynesian diagnostic, not a consequence of (5) or (16), nor a new multiplier theorem. It is positive, zero, or negative according to the signed expenditure shift. It applies only while the implied level remains below productive capacity and prices remain fixed. At a bottleneck, price changes, rationing, imports, monetary responses, and sectoral substitution must be modeled. The partial-equilibrium parameter $\zeta$ cannot be assumed to vanish merely because investors appear wealthy.

A full empirical application would link these margins to issuance, capital formation, and public revenue in one estimated model. That integration is not supplied here. The present results remain useful because they distinguish a valid financing calculation from an unsupported macroeconomic claim.

# 9. Implementation, limits, and interpretation

The protected resources and payment index must be verifiable. A government that can redefine every expenditure as protected after selling the claim may destroy its price. A company may shift income across entities or borders. Full commitment and observable resources are explicit maintained assumptions; the paper does not solve these incentive problems by declaring an audit committee.

An application must identify who originally owns the public resource stream. Acquiring a share from private owners is itself a transfer, and a new levy can affect investment, as Section 7 demonstrates. The claim must not be pledged more than once. An issuance cap should cover the aggregate of outstanding claims, not restart with each offering. None of the constructions authorizes concealing public risk off balance sheets.

Population changes and heterogeneous needs matter. A single good and a given $G_s$ do not reproduce the effects of rent increases, healthcare scarcity, or unequal access to services. A future consumption floor must be translated into a feasible physical allocation, rather than protected only as a nominal entry. Severe states outside the model may leave the floor underfunded even with zero new repayment.

Investor heterogeneity can change both demand and state prices. An asset that pays when automation displaces labor may hedge a worker's income risk, yet that worker may lack current resources to buy it. Conversely, a wealthy technology owner may already have similar exposure. The representative investor is a solvable benchmark, not a claim that these positions are the same.

The contract provides resources, not guaranteed psychological well-being. It is consistent with separating basic support from the obligation to outperform machines, but does not establish the broader distribution of meaningful activities, autonomy, or social standing. Those goals should not be inferred from a financial participation constraint.

Finally, the comparison with ordinary debt must remain strong. A feasible debt-plus-insurance package with the same resource protections, payouts, and costs is equivalent. A new issue adds value only by changing enforceable opportunities or costs. That is a testable implementation claim, not a slogan about borrowing from the future.

# 10. Conclusion

A potentially abundant future can support current consumption only through a sequence of distinct steps: resources must become an enforceable public claim, that claim must be valuable to actual buyers, and the resulting allocation must preserve both protected uses and the production conditions on which future payments depend.

The exchange model supplies an exact financing frontier and a least-cost state allocation for a support target. It shows why common future abundance need not enlarge current borrowing. The production extension demonstrates that voluntary financing can reduce capital formation and derives a separate investment-preserving bound. Together, the results turn a proposed bridge into an auditable sequence of questions: how much is needed now, what must be surrendered later, who bears the downside, and what happens to the resources that generate tomorrow's output?

These are bounded theoretical results suitable for public criticism. They do not establish that a proposed security is institutionally feasible in every jurisdiction, that issuance necessarily reverses contraction, or that a new universal economic theory has been discovered. The model's most defensible practical principle is to finance a stated current objective using no more future concessions than necessary, subject to honest pricing and explicit resource protections.

# References

[1] Beraja, Martin, and Nathan Zorzi. 2025. “Inefficient Automation.” *Review of Economic Studies* 92(1): 69–96. First published online in 2024. DOI: 10.1093/restud/rdae019. Working paper: https://www.nber.org/papers/w30154.

[2] Korinek, Anton, and Donghyun Suh. 2024. “Scenarios for the Transition to AGI.” arXiv:2403.12107v1. https://arxiv.org/abs/2403.12107.

[3] Holmström, Bengt, and Jean Tirole. 1998. “Private and Public Supply of Liquidity.” *Journal of Political Economy* 106(1): 1–40. DOI: 10.1086/250001.

[4] Kamstra, Mark, and Robert J. Shiller. 2009. “The Case for Trills: Giving the People and Their Pension Funds a Stake in the Wealth of the Nation.” Cowles Foundation Discussion Paper 1717. https://elischolar.library.yale.edu/cowles-discussion-paper-series/2036/.

[5] Guerson, Alejandro. 2021. “Optimal State Contingent Sovereign Debt Instruments.” IMF Working Paper 2021/230. DOI: 10.5089/9781513595917.001.

[6] Igan, Deniz, Taehoon Kim, and Antoine Levy. 2021. “The Premia on State-Contingent Sovereign Debt Instruments.” IMF Working Paper 2021/282. DOI: 10.5089/9781616357009.001.

[7] O'Keefe, Cullen, Peter Cihon, Ben Garfinkel, Carrick Flynn, Jade Leung, and Allan Dafoe. 2020. “The Windfall Clause: Distributing the Benefits of AI for the Common Good.” arXiv:1912.11595v2, first submitted December 2019. https://arxiv.org/abs/1912.11595.

\newpage

# Appendix A. Reproduction and statement boundaries

The release includes `verify.py` and machine-readable results. The checks recompute the analytical examples, verify both individual first-order conditions and all resource accounts, compare the least-cost schedule with a same-price proportional schedule, and test the investment-floor inverse formula. Small finite parameter sweeps provide error detection, not empirical support or a substitute for the proofs.

The core dependencies are Python, NumPy, and SciPy; versions are recorded with the output. No random data, training run, securities transaction, macroeconomic calibration, or human-subject study is used. PDF construction uses Pandoc and XeLaTeX. The source and PDF are separate artifacts linked by the release manifest, not a claim of bit-identical rebuilds across arbitrary typesetting installations.

| Statement | What is established | What is not established |
|:--|:--|:--|
| Protected payment | The new claim does not exceed the given resource cap | The initial floor is adequate or legally senior |
| Clearing price | Voluntary competitive demand clears in the specified economy | The same price holds with other investor opportunities |
| Least-cost design | Unique schedule under the stated beneficiary metric and state information | A unique ethically optimal distribution |
| Investment bound | Exact bound in the atomistic square-root technology extension | A universal optimal tax or economy-wide crowding-out effect |
| Conditional demand response | Equation (19) under its own closure | A measured multiplier or automatic self-financing |
| Release status | Complete source, proofs, checks, and readable artifacts | External peer review or top-journal acceptance |

The phrase “without pledging subsistence” refers exclusively to the new claim's contractual payment cap. It does not assert that subsistence has already been secured under every possible future shock. The phrase “automation transition” describes the motivating application; the mathematics also applies to other settings with delayed public income and present support needs.
