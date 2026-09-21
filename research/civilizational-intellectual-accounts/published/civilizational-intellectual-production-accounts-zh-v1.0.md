---
title: "文明智识生产卫星账户：测量人类—AI智识重心迁移的部分识别框架"
author: "刘烘炬（Hongju Liu）"
date: "2026-09-21"
geometry: margin=1in
fontsize: 11pt
CJKmainfont: "Noto Serif CJK SC"
mainfont: "Noto Serif CJK SC"
monofont: "Noto Sans Mono CJK SC"
---

# 文明智识生产卫星账户：测量人类—AI智识重心迁移的部分识别框架

**Civilizational Intellectual Production Satellite Accounts: A Partial-Identification Framework for Measuring the Human–AI Shift in Intellectual Production and Epistemic Governance**  
**Report:** TA-TR-2026-13  
**Version:** v1.0-final  
**Date:** 2026-09-21  
**Author:** 刘烘炬（Hongju Liu）  
**Status:** 理论—测量方法预印本；包含三组确定性 design-validation simulations；未同行评审

> **论文性质声明**：本文不主张已经测得“全人类智识中 AI 占多少百分比”，也不把任何单一综合指数当作客观真理。本文提出的是一套用于未来统计实践的**测量理论与卫星账户框架**：在明确边界内，对一个时期可观察、已外部化的新增智识生产与认识治理进行 Human / AI / Human–AI interaction 的归因；当 AI 使用、质量、因果贡献和跨领域权重不能被完全观察时，报告 identified set（可识别集合）而不是伪精确的点估计。本文所称“智识”不是既有知识库存的简单同义词，而是能够改变问题空间、候选解释、判断、验证状态、设计或行动计划的认知性增量。

---

## Abstract

Debates about artificial general intelligence are dominated by a threshold problem: there is no consensus about which capabilities, benchmarks, or social functions constitute “AGI,” and the threshold can move as systems improve. Yet a different transition is already observable in principle. Across science, software, engineering, medicine, professional analysis, and public decision processes, a growing share of the *new intellectual work* that moves civilization forward is being performed with substantial AI participation. Existing measures capture important but different objects: AI capability relative to human abilities, occupational exposure, platform usage and autonomy, cognitive offloading, delegation of judgment, national intellectual capital, knowledge-economy satellite accounts, R&D and innovation accounts, stage-specific AI-use/contribution disclosure, or AI-related scientific novelty and impact. These measures do not jointly answer a macro-level accounting question: **what share of a period’s new, externally observable intellectual production and epistemic governance is attributable to humans, AI systems, or their interaction?**

This paper argues that the strongest form of that question—“what exact percentage of all human intellect belongs to AI?”—is not point-identifiable. Intellectual outputs across domains lack a natural common unit; AI use is incompletely observed; output quality is revised over time; human and AI contributions are causally entangled; and cross-domain aggregation requires value-laden or statistical weights. Instead of hiding these problems behind a single composite score, the paper proposes **Civilizational Intellectual Production Satellite Accounts (CIPSA)**: a domain-first, flow-based, partial-identification framework inspired by satellite accounting, innovation accounting, and modern econometrics of set identification.

The framework separates two accounts. The **Intellectual Production Account** measures who causally contributes to generating new intellectual outputs. The **Epistemic Governance Account** measures who frames problems, selects among alternatives, verifies claims, and determines which outputs are accepted for use. These dimensions need not move together. A civilization can become highly machine-intensive in production while remaining human-governed, or AI can exert substantial governance influence before it produces most artifacts.

Ten accounting principles define the system: flow rather than historical stock; an externalization boundary; domain-first measurement; no double counting; current-period marginal contribution rather than genealogical credit; explicit interaction effects; separation of production from governance; partial identification rather than forced point estimates; vintage revision of quality; and robust reporting across alternative aggregation rules. Domain-specific human/AI contribution intervals are aggregated over an admissible set of weights, quality models, missingness assumptions, and interaction-allocation rules. The resulting civilizational AI share is therefore an **identified set**, not necessarily a scalar.

This yields a conservative milestone concept: **Robust Intellectual Crossover** occurs only when the lower bound of the AI contribution set exceeds 0.5 across all pre-registered admissible assumptions. The same logic defines production and governance crossovers separately. Three deterministic design-validation simulations accompany the theory. In a stipulated six-domain example, plausible domain attribution intervals and admissible aggregation weights imply an AI-share identified set of 0.267–0.528 even though conventional midpoint estimates are near 0.40, demonstrating non-identification of a unique scalar. A second simulation shows that later validation can materially revise composition estimates: an AI volume share of 0.470 becomes a validated-quality share of 0.346 under the stipulated data-generating process. A third simulation shows that a central estimate can cross 0.5 years before a robust crossover is justified.

The paper concludes with a pilot protocol for a **Scientific Intellectual Production Satellite Account**, where publication metadata, research provenance, AI-use disclosures, audited workflow samples, novelty/impact indicators, replication outcomes, and stratified missingness corrections are comparatively observable. The framework does not define AGI, infer consciousness, assign moral credit, or claim that higher AI share is inherently good or bad. Its purpose is narrower: to make the ongoing transfer in the *composition of civilizational intellectual production* empirically discussable without pretending that the underlying object is more precisely measurable than the evidence allows.

**Keywords:** civilizational intellectual production; AI contribution; intellectual accounting; epistemic governance; partial identification; satellite accounts; human–AI collaboration; AGI measurement; innovation accounting; robust crossover

---

## 摘要

“AGI 是否已经实现”是一个典型的阈值争议。人们可以长期争论通用性、自治性、跨任务迁移、社会角色替代或者某一组 benchmark 达到什么水平才算 AGI。与此同时，另一个过程却更值得被连续测量：**推动文明继续前进的新增智识生产，其主体构成是否正在从主要由人类承担，逐渐转向由人工智能承担，或者由人机系统共同承担？**

已有研究分别测量了 AI 相对人的能力、职业暴露、平台中的 AI 自主性、认知卸载、判断委托、国家智识资本、知识经济卫星账户、R&D 和创新产出、研究流程中的 AI 贡献披露，以及 AI 对科学新颖性和影响的作用。这些工作都与本问题相邻，但没有完整回答一个文明级统计问题：**在一个时期新增的、可观察并已经外部化的智识生产与认识治理中，人类、AI以及人机互动各自贡献多少？**

本文首先否定该问题的最强版本。我们不能严谨地宣称存在一个天然、唯一、可精确测得的“全人类智识 AI 占比”。不同领域智识成果没有统一自然单位；AI 使用往往不可观察；一项成果的质量会在数年后被复现、采用或证伪；Human 与 AI 的因果贡献高度纠缠；跨领域聚合又不可避免地依赖权重。因此，任何看似精确的单一百分比，都包含数据之外的额外假设。

本文提出 **文明智识生产卫星账户（Civilizational Intellectual Production Satellite Accounts, CIPSA）**。其基本思路不是制造一个新的综合指数，而是建立一套类似实验性统计账户的制度：先在可测量领域建立分账户，再对 Human / AI / interaction 的当期边际贡献做区间归因，最后在多个可接受权重、质量模型和缺失数据假设下形成**可识别集合（identified set）**。

本文进一步把宏观智识结构拆成两个并行账户。**智识生产账户**回答“谁产生了新的候选理论、解释、设计、证明、代码、诊断或方案”；**认识治理账户**回答“谁定义问题、筛选候选、决定证据充分性、执行验证以及允许某项结论进入实际使用”。两者并不等价。未来完全可能出现 AI 生成大多数智识产品、但人类仍保留主要认识治理；也可能出现 AI 产量尚未过半，却已经在 framing、selection 和 verification 中占据更高影响力。

框架由十条核算原则构成：流量优先于历史存量；只核算可观察且已外部化的智识；先分领域、后聚合；禁止重复计算；核算当期边际生产贡献而不是无限追溯历史功劳；显式保留 interaction；生产与治理分账；在不能点识别时使用部分识别；质量随统计 vintage 修订；跨假设报告稳健结论。文明级 AI 智识份额因而不是天然单一数值，而是由领域份额区间、质量调整、权重集合、interaction 分配和未披露 AI 使用共同决定的集合。

在此基础上，本文定义 **稳健智识跨越（Robust Intellectual Crossover）**：只有当 AI 智识份额的 identified set 下界在全部预注册合理假设下仍超过 0.5，才可以说“AI 已稳健地成为该统计范围内多数新增智识贡献来源”。生产跨越和治理跨越必须分别报告。

本文实际运行三组确定性设计验证仿真，但明确不把它们当作真实世界 AI 贡献估计。第一组在六个领域的虚构数据中表明，同一组领域证据在合理权重和归因区间下支持的文明级 AI 份额为 **0.267–0.528**，虽然常见中点估计约为 0.40，因此单一百分比并未被数据点识别。第二组演示统计 vintage 的必要性：在预设生成机制下，AI 的原始产量份额为 **0.470**，而长期验证后的质量调整份额为 **0.346**。第三组演示：中心点估计可以在 2030 年越过 50%，但稳健下界直到 2032 年才越过 50%；因此“中心估计跨越”与“稳健跨越”不是同一件事。

论文最后提出一个可执行的 **科学智识生产卫星账户** pilot：利用科学论文与引用元数据、AI 使用披露、代码仓库、研究过程 provenance、抽样审计、领域新颖度和影响指标、复现结果以及对未披露 AI 使用的缺失数据区间修正，先在科学领域建立可重复的年度账户。本文不定义 AGI，不证明 AI 具有意识，不讨论道德功劳或版权，也不预设 AI 份额升高就是好或坏。它仅试图把“人类文明的智识生产主体正在发生怎样的结构变化”变成一个可以被统计、审计、修订并对不确定性保持诚实的问题。

---

# 1. 研究问题：AGI 阈值之外，还有一个正在发生的连续变量

AGI 讨论容易陷入一个结构性困境：它要求社会先对一个高维概念达成阈值定义，再判断现实系统是否越过该阈值。不同定义强调不同属性——广度、迁移、持续自治、社会角色替代、科学创造力、经济影响或者某类人类水平 benchmark。即使同一个模型不发生变化，阈值本身也可能随着社会适应而移动。

但机器智能的历史作用并不需要等待一个 AGI 标签才能发生。

一个研究团队可以开始把文献检索交给 AI；工程团队可以把第一版架构交给 agent；医生可以把鉴别诊断候选交给模型；程序员可以把从需求到代码、测试和修复的长链交给 coding agent；管理者可以把数据解释和方案生成交给 AI；科学家甚至可以让系统参与提出问题、设计实验、分析结果和撰写论文。

这些变化的共同点不是“AI 到底有多聪明”，而是：

> **文明新增智识的生产结构正在发生变化。**

因此本文的基础研究问题是：

> **能否在不依赖 AGI 阈值定义的情况下，对一个时期文明新增智识生产与认识治理中 Human / AI / Human–AI interaction 的构成进行统计核算，并连续测量其变化？**

这个问题与“AI 会不会取代工作”不同。工作数量是劳动市场对象；本文研究的是一个更窄的统计对象：**可观察、已外部化、具有认知增量意义的智识生产流量。**

它也与“AI 能不能完成某任务”不同。能力是潜在可行性；本文研究实际贡献。

它还与“AI 是否被使用”不同。一个模型参与润色并不意味着它对结论有实质贡献；反过来，一句重新定义问题的话可能字数很少却改变整个研究方向。

所以需要先区分四个对象：

$$
\text{Capability}
\neq
\text{Use}
\neq
\text{Delegation}
\neq
\text{Intellectual contribution}.
$$

OECD AI Capability Indicators 正在系统比较 AI 与人类在语言、社会互动、问题解决、创造力、元认知等能力维度上的水平[1]；Anthropic Economic Index 已开始测量真实 Claude 使用场景中的 autonomy / decision delegation[2]；认知心理学开始研究 cognitive agency transfer[3]；伦理与治理研究也在讨论 delegated judgment 和 epistemic control[4]。这些都重要，但它们并不是文明级智识生产账户。

本文试图建立的是后者。

---

# 2. 原创性审计：哪些相邻问题已经被做过

高水平论文不能把邻近领域重新命名为自己的原创。因此本节先明确哪些部分**不是**本文首创。

## 2.1 “国家智识能力”或“知识指数”不是新问题

人力资本、国家智识资本、知识经济、创新指数和科学能力指标已经形成庞大文献。2026 年甚至出现了新的 Collective Intelligence Index，把科学、技术、创新、信息、人力和社会文化等多种资本合成国家智识潜力指数[5]。因此本文不主张首次“给一个社会的智识打分”。

更重要的是，这类 composite indicator 文献长期存在权重、归一化、可比性和解释性问题。OECD/JRC 的综合指标手册专门要求对权重和聚合规则进行敏感性与不确定性分析[6]。这一历史经验正是本文反对“直接拍出一个全人类 AI 智识百分比”的理由之一。

## 2.2 “创新和知识进入宏观账户”不是新问题

BEA 的 R&D satellite accounts 已经把 R&D 作为可独立核算的生产活动进行实验统计，并逐渐纳入正式 national accounts[7][8]；Corrado 与 Hulten 的 innovation accounting 进一步讨论无形资本、创新投入和产品质量变化如何进入宏观核算[9]。

更直接的先例是**知识卫星账户本身**。Statistics Netherlands 至少在 2000 年代后期已经建立 knowledge satellite account，把软件与数据库、R&D、品牌、组织结构、企业特定人力资本以及部分设计支出作为知识相关资产扩展到国家账户之外的卫星核算[21]。印度统计与计划实施部（MoSPI）在 2025 年进一步启动 Knowledge Economy Satellite Account / GDKP 的正式框架建设，明确讨论 knowledge items、knowledge producers、distributors/users、知识产品 taxonomy 以及知识对 GDP 和社会生活的贡献[22]。

因此本文不主张首次把知识/创新做成宏观账户，也不主张首次提出“knowledge satellite account”。与这些先例相比，本文的测量对象更窄也更不同：它不主要估计一个经济体拥有多少知识资本或知识经济产值，而是试图对**当期新增、可观察智识生产以及认识治理中的 Human / AI / interaction 构成**进行区间归因，并把归因不确定性、质量修订和跨领域权重不唯一统一放入 partial-identification framework。

## 2.3 “AI GDP”已经存在

Korinek 与 McKelvey（2026）已经构建美国 AI production 的宏观估计，并通过固定性能价格和算法进步做质量调整，提出 nascent “AI GDP” framework[10]。所以本文也不主张首次对 AI 做卫星账户或质量调整。

区别在于：AI GDP 核算的是**AI 经济部门与 AI 生产活动本身**，本文试图核算的是**跨领域智识产出中 Human / AI 的生产构成**。一项医学发现的经济价值可能主要体现在制药公司，但其智识生产贡献可能来自医生、实验室、AI 模型和数据系统的组合。两种账户对象不同。

## 2.4 “AI 对科学知识生产的影响”已经有大规模实证

Bianchini、Di Girolamo、Ravet 与 Arranz（2026）分析超过 8000 万篇论文、170 多个科学领域，使用 novelty 和 impact 指标研究 AI 在科学中的贡献，发现效果高度异质[11]。因此本文不主张首次测量 AI 对科学创新的影响。

本文的增量在于把科学视为未来多个 satellite accounts 中最适合先做的一个，而不是把 science 直接等同于 civilization-wide intellectual production。

## 2.5 “认知卸载、判断委托和认识控制”已经形成直接文献

Zhu 等（2026）以三波调查研究 dependent / autonomous cognitive offloading，并引入 cognitive agency transfer[3]；Mühlhoff（2026）直接用 delegated judgment × epistemic control 分类 LLM 使用[4]。因此“AI 让人把思考交出去”不是本文原创。

本文研究的尺度更宏观：不是一个人的主观认知代理感，而是一个时期**可外部观察的文明智识生产和治理构成**。

## 2.6 “人机协同不等于简单相加”也不是新发现

Vaccaro、Almaatouq 与 Malone 的预注册元分析覆盖 106 个实验、370 个 effect sizes，发现 Human+AI 平均并不优于 human-only 与 AI-only 中的更强者，且 decision task 与 creation task 的结果不同[12]。因此本文不预设 interaction 必然为正，也不把“synergy”当成天然第三份正贡献。

## 2.7 “AI 使用披露并不能真实观测 AI 参与”已经有实证

He 与 Bu（2026）分析 5114 本期刊和 520 多万篇论文，并在 164k 全文样本中发现，2023 年后约 7.5 万篇论文只有 76 篇（约 0.1%）显式披露 AI 使用[13]。这意味着宏观智识账户如果仅使用 disclosure，会发生严重漏报。

与此同时，**按研究阶段描述 AI 参与和人类贡献的框架也已经出现**。Ruttenberg（2026）分析 AIR framework，用“七个研究阶段 × 五档 AI engagement”描述 AI 介入程度，并显示高参与度条件下的分类一致性会明显下降[23]；Lu 等（2026）则提出 AI-enabled research 的出版认证框架，把 knowledge-quality certification 与 human-contribution grading 分开[24]。因此本文也不主张首次提出 AI contribution statement、stage-specific disclosure 或 human-contribution certification。

本文把这些微观披露/认证体系视为未来宏观账户可能使用的数据来源之一，但不把“未披露”解释为“未使用”。AI 使用可观测性本身必须进入 identified set。

## 2.8 “idea 本身难以计数”是一个老问题

OECD 对 “ideas getting harder to find” 争论的综述指出，现有研究通常使用技术进步、论文、引用、独特短语等代理，而没有真正直接测量 ideas themselves；甚至如何“数 idea”本身都并不清楚[14]。

因此本文不会宣称发现了一个天然“智识单位”。它采用的是**账户制度**而不是本体论单位：领域内选择透明代理并给质量调整，跨领域聚合时显式报告权重依赖。

## 2.9 经审计后剩余的原创空间

截至 2026 年 9 月 21 日的针对性搜索中，本文没有发现一项成熟工作同时完成以下结构：

1. 把测量对象限定为**当期新增、可观察、已外部化的文明智识生产流量**；
2. 同时建立**智识生产账户**与**认识治理账户**；
3. 在 Human / AI / interaction 归因不完全可观察时使用**部分识别**而不是强制点估计；
4. 跨领域聚合时把权重、质量 vintage、缺失 AI 使用和 interaction allocation 都纳入 admissible assumption set；
5. 用 identified-set 下界而不是中心估计定义**稳健智识跨越**；
6. 允许历史账户随着验证、复现、采用和证伪进行**vintage revision**。

这六点的联合框架构成本文的原创性边界。本文不声称 knowledge-economy satellite accounts、AI contribution disclosure、satellite accounting、partial identification、innovation accounting、Shapley decomposition 或 composite-indicator sensitivity 中的任何单项技术是首次提出。

---

# 3. “智识”不是“知识库存”：测量对象必须从一开始就定义对

本文所称“智识转移”不能被误写成“知识从人类数据库搬到 AI”。

已有知识库存可以写作：

$$
K_{t-1}.
$$

其中包含：

- 历史科学理论；
- 语言与文化；
- 教科书；
- 训练数据；
- 代码库；
- 已训练模型；
- 实验设备；
- 组织惯例；
- 人类教育和专业能力。

AI 的能力依赖大量人类历史知识，但现代人类研究者也依赖过去几百年的知识资本。若每项新贡献都向历史无限回溯，就无法形成当期生产账户。

因此本文只核算：

$$
\Delta I_t \mid K_{t-1},
$$

即**在时期开始时已有知识与能力资本给定的条件下，本期产生的新智识增量**。

这里“智识增量”定义为：

> 能够在一个被承认的知识、技术、专业或决策体系中，改变问题空间、候选解释、可行方案、理由结构、验证状态、设计或行动计划的外部化认知产物或认知决定。

这一定义有意比“知识”宽，因为设计和战略未必立即成为事实性知识；但又比“一切文本”窄，因为机械改写、排版、复制和大批无效生成不能自动成为等量智识。

因此本文区分：

$$
\text{Text output}
\neq
\text{Intellectual output}.
$$

同样：

$$
\text{Historical provenance}
\neq
\text{Current-period marginal contribution}.
$$

这个账户讨论的是统计生产贡献，不是道德功劳、人格、版权或文明归属。

---

# 4. 为什么“全人类智识 AI 占比”一般不能被唯一点识别

这一节给出本文最重要的方法学结论。

## 4.1 域内 AI 份额本身已经可能是区间

设领域 \(d\) 在时期 \(t\) 的可观察智识产出为 \(Q_{d,t}\)。

如果每个成果的 AI 使用与边际贡献都被完整记录，可以定义领域 AI 份额：

$$
s_{d,t}^A=\frac{A_{d,t}}{Q_{d,t}}.
$$

现实中往往只有部分记录，因此更合理的是：

$$
s_{d,t}^A\in[\underline{s}_{d,t}^A,\overline{s}_{d,t}^A].
$$

区间宽度来自：

- 未披露 AI 使用；
- AI 只参与语言而未参与核心内容；
- AI 参与核心推理但没有记录；
- human / AI contribution 互相依赖；
- 质量估计尚未成熟。

## 4.2 跨领域聚合没有天然唯一权重

假设有两个领域：数学和临床诊断。

数学领域 AI share 可能高，临床判断可能低。

文明级份额必须引入权重：

$$
S_t^A(w)=\sum_d w_d s_{d,t}^A,
\qquad \sum_d w_d=1.
$$

但 \(w_d\) 可以代表：

- 活动量；
- 专业人数；
- R&D投入；
- 经济价值；
- 后续社会影响；
- 等权领域。

这些权重并不等价。

## 4.3 命题 1：无共同计量单位与唯一权重时，文明级份额不是天然点识别参数

**命题 1（Aggregation non-uniqueness）**  
若至少存在两个领域 \(d_1,d_2\)，使其 AI contribution share 不同：

$$
s_{d_1}^A\neq s_{d_2}^A,
$$

且数据与预先接受的统计制度没有唯一确定二者相对权重，则任何满足域内一致性的文明级加权份额都依赖额外权重假设。若 admissible weight set \(\Omega\) 包含至少两个不同相对权重向量，则：

$$
\mathcal S_t^A
=
\left\{S_t^A(w):w\in\Omega\right\}
$$

一般不是单点，而是非退化集合。

**证明思路。**  
加权份额是各领域份额的凸组合。只要至少两个领域份额不同，而允许权重在二者间变化，则凸组合随权重连续变化。因此除非额外约束把相对权重唯一固定，宏观标量就不由领域数据单独唯一决定。证毕。

这个结果并不深奥，但它对本问题具有重要规范作用：

> **如果研究者给出一个唯一的“AI 文明智识份额”，必须说明哪一套额外权重、质量与归因假设把集合压成了一个点。**

隐藏这些假设并不会使数字更客观。

---

# 5. 十条文明智识账户原则

本文提出十条 accounting principles，作为后续估计和审计的最小规则。

## 原则 1：Flow over Stock

核算本期新增流量，而不是试图重新分配整个人类历史智识库存。

$$
CIP_t \equiv \Delta I_t\mid K_{t-1}.
$$

## 原则 2：Externalization Boundary

只纳入能够被外部观察或被统计推断的智识活动。私人思考、未记录口头判断和完全隐性的经验不被假装已经测量。

因此正式名称不是 “Total Human Intellect”，而是：

> **Observable Externalized Civilizational Intellectual Production.**

## 原则 3：Domain First, Aggregate Second

先在科学、软件、工程、医学、专业分析、公共决策等领域建立独立 satellite accounts；跨领域总量属于二级聚合。

## 原则 4：No Double Counting

一项智识成果可以包含 framing、generation、reasoning、verification 等多个功能，但总成果不能因为经历多个认知步骤而重复计入总量。

功能分解用于归因，不用于把同一成果重复加总。

## 原则 5：Marginal Contribution, Not Genealogical Credit

统计当期 marginal production contribution，而不是追问终极历史功劳。

## 原则 6：Interaction Must Be Explicit

Human+AI 可能产生正协同、零协同或负协同。不能默认 interaction 为正，也不能强行全部归给某一方。

## 原则 7：Production and Governance Are Separate Accounts

“谁生成”与“谁决定采用”必须分账。

## 原则 8：Partial Identification Before Point Estimation

若证据只支持区间，则报告区间。额外假设每增加一层，必须可见。

## 原则 9：Vintage Revision

质量评价会随复现、采用、失败与证伪改变。历史账户必须可修订。

## 原则 10：No AGI Inference by Definition

AI 智识份额高不自动等于 AGI；AI 智识份额低也不证明不存在 AGI。本文测的是文明生产结构，而不是智能本体。

---

# 6. 双账户：智识生产与认识治理

只测“AI 生成多少”会严重低估结构变化。

本文定义两个并行账户。

## 6.1 Intellectual Production Account（IPA）

IPA 记录谁对新的认知产品产生边际贡献，例如：

- 新假设；
- 理论；
- 证明；
- 软件与算法；
- 工程设计；
- 诊断候选；
- 分析框架；
- 专业建议；
- 战略方案。

领域 \(d\)、时期 \(t\) 的生产总量写作：

$$
Q_{d,t}^{P}.
$$

Human 与 AI 的可归因贡献为：

$$
H_{d,t}^{P},\qquad A_{d,t}^{P}.
$$

## 6.2 Epistemic Governance Account（EGA）

EGA 记录谁在知识流程中拥有认识上的实际治理作用，包括：

- Framing：什么问题值得问；
- Agenda setting：下一步探索什么；
- Selection：保留哪些候选；
- Evidence weighting：哪些证据重要；
- Verification：何时算验证通过；
- Closure：何时允许某项结论进入使用。

治理不是“政治统治”的同义词。这里的 governance 是 epistemic process control。

## 6.3 为什么要分开

想象两个文明状态。

### 状态 A：机器高产、人类治理

AI 生成 80% 的候选代码、文献摘要、工程方案和分析草稿，但人类负责定义问题、设定约束、选择方案、验证和最终采用。

此时可能：

$$
S_A^P=0.80,
\qquad
S_A^G=0.20.
$$

### 状态 B：机器产量未过半、机器治理影响较高

AI 只直接生成 40% 内容，但它决定搜索什么、提出多数关键假设、建议哪些证据可信，并主导验证路线。

可能：

$$
S_A^P=0.40,
\qquad
S_A^G=0.65.
$$

二者对文明结构的意义完全不同。

因此本文建议任何未来年度报告至少同时公布：

$$
\mathcal S_{A,t}^{P}
\quad \text{and}\quad
\mathcal S_{A,t}^{G}.
$$

---

# 7. 智识功能分类：用于归因，而不是制造七个重复产出

本文建议把智识生产中的功能分为七类：

$$
\mathcal F=
\{F,G,R,J,V,P,N\}.
$$

### F — Framing

提出问题、定义目标、确定约束和成功标准。

### G — Generation

生成假设、概念、设计、代码、解释和候选方案。

### R — Reasoning & Synthesis

逻辑推导、模型构建、跨资料综合、因果解释。

### J — Judgment & Selection

比较候选、权衡证据、选择结论或行动方案。

### V — Verification

证明、实验、复核、反例、审计、错误发现。

### P — Planning & Strategy

决定探索顺序、资源配置、研究路径和执行计划。

### N — Normative & Social Interpretation

处理价值冲突、责任、社会后果与制度语境。

这七类不是“人类专属能力”，也不是本文声称的心理学新分类。OECD 已经通过九类 AI Capability Indicators 对能力空间进行更系统的专家构建[1]。本文的分类用途更窄：**作为生产与治理账户中的功能标签，用于回答同一项成果的不同认知作用由谁承担。**

对单个成果 \(o\)，定义功能贡献矩阵：

$$
C_o=
\begin{bmatrix}
H_{o,F}&A_{o,F}\\
H_{o,G}&A_{o,G}\\
\vdots&\vdots\\
H_{o,N}&A_{o,N}
\end{bmatrix}.
$$

但成果只拥有一个总质量权重 \(q_o\)。功能矩阵只是解释 \(q_o\) 的形成，不把 \(q_o\) 乘七次。

---

# 8. “一单位智识”不存在：解决办法是域内估值，不是假装全球有统一货币

这是整个研究最难的地方之一。

一项数学证明和一次新药发现无法像美元一样自然比较。

因此 CIPSA 不定义一个形而上学的“智识焦耳”。

它采取三层估值。

## 8.1 Gross / Volume Account

首先记录可观察数量，例如：

- 经审核论文；
- 新专利族；
- 软件功能或发布；
- 医学分析或诊断建议；
- 工程设计；
- 专业报告；
- 被正式采用的决策分析。

这个账户透明，但不能等同于高质量智识。

## 8.2 Validated Quality-Adjusted Account

每项成果获得领域内质量权重：

$$
q_o^{(v)}.
$$

指标可以包括：

- 专家盲评；
- 独立复现；
- 正确性；
- 后续采用；
- 引用与使用；
- 被推翻概率；
- 技术性能提升；
- 真实决策效果。

不同领域使用不同质量模型。

## 8.3 Frontier Account

第三套账户只观察推进边界的输出，例如：

- 新定理；
- 新实验发现；
- 新药机制；
- 新算法；
- 显著性能突破；
- 新解释框架；
- 被后续工作证明具有高 novelty / disruptiveness 的成果。

Bianchini 等的大规模 science-of-science 工作已经证明 novelty / impact 可以在科学领域进行大规模计算[11]，但本文不把引用或 novelty 当成普遍唯一真值。

## 8.4 域内指数化而非跨域绝对单位

对领域 \(d\)，建立基期指数：

$$
Q_{d,0}=100.
$$

后续报告：

$$
Q_{d,t}^{volume},
Q_{d,t}^{validated},
Q_{d,t}^{frontier}.
$$

跨领域合并时使用明确权重集合，而不声称医学 1 点等价于软件 1 点。

---

# 9. Human / AI / interaction 的归因：为什么不能简单三分

## 9.1 四种反事实表现

对于某一任务或成果，可以定义：

$$
Q_0 = \text{baseline quality/performance}
$$

基线；

$$
Q_H = \text{human-only quality/performance}
$$

Human-only；

$$
Q_A = \text{AI-only quality/performance}
$$

AI-only；

$$
Q_{HA} = \text{human+AI quality/performance}
$$

Human+AI。

定义主效应：

$$
\Delta_H=Q_H-Q_0,
$$

$$
\Delta_A=Q_A-Q_0.
$$

interaction：

$$
\xi_{HA}=Q_{HA}-Q_H-Q_A+Q_0.
$$

\(\xi_{HA}\) 可以：

- 大于 0：正协同；
- 等于 0：可加；
- 小于 0：负协同。

因此 interaction 不应该天然叫“协同红利”。

## 9.2 两种报告模式

### 模式 A：Interaction Unallocated

直接报告：

$$
(\Delta_H,\Delta_A,\xi_{HA}).
$$

这是最透明的。

### 模式 B：Allocated Share

如果政策报告必须给 Human / AI share，就定义 interaction allocation parameter：

$$
\lambda\in[0,1].
$$

Human 获得：

$$
\Delta_H+\lambda\xi_{HA},
$$

AI 获得：

$$
\Delta_A+(1-\lambda)\xi_{HA}.
$$

不同 \(\lambda\) 都是额外 convention，因此应进入 identified set。

Shapley value 可以作为一个 allocation rule，但本文不把它视为唯一真理。

---

# 10. 可观测性等级：数据不是“有/无”，而是证据等级

Human–AI contribution 的宏观核算会面临严重 missingness。

论文披露不能视为 ground truth。He 与 Bu 的研究显示，AI 使用披露远低于推断的实际采用规模[13]。

本文提出四级证据体系。

## Grade A — Audited Provenance

最高等级：

- 完整 agent / API日志；
- workflow history；
- version control；
- prompt / output trace；
- institution audit；
- human review records。

这类数据可以支持较窄 attribution bounds。

## Grade B — Structured Verifiable Disclosure

使用标准化披露，记录：

- 哪个系统；
- 哪个阶段；
- 哪种功能；
- 是否经过人工独立验证；
- 最终输出是否保留 AI 建议。

披露需抽样审计，以校准漏报率。

## Grade C — Calibrated Statistical Inference

利用：

- 平台使用 telemetry；
- 组织 AI adoption 数据；
- 抽样问卷；
- 代码仓库；
- 文档历史；
- 经 ground-truth 校准的统计模型。

输出必须带置信区间和误分类修正。

## Grade D — Detector-only Signal

单纯 AI-text detector 不应作为核心归因证据。

可用于：

- sensitivity analysis；
- 发现异常；
- 设定 missingness 上下界。

但不应直接给某个具体作品判定“AI贡献 x%”。

---

# 11. 部分识别：论文真正的方法核心

## 11.1 为什么需要 partial identification

Partial identification 的基本思想是：数据和可信假设往往不能唯一确定参数，但仍能排除一部分可能值。此时正确目标不是强迫点估计，而是描述 identified set[15][16]。

这与本文高度匹配。

设领域 \(d\) 的 AI share：

$$
s_{d,t}^A\in
[\underline{s}_{d,t}^A,
\overline{s}_{d,t}^A].
$$

跨领域权重：

$$
w\in\Omega_W.
$$

质量模型：

$$
q\in\Omega_Q.
$$

interaction allocation：

$$
\lambda\in\Omega_\Lambda.
$$

未披露 AI 使用模型：

$$
m\in\Omega_M.
$$

统计 vintage：

$$
v\in\Omega_V.
$$

把所有允许假设写成：

$$
\Theta=
\Omega_W\times
\Omega_Q\times
\Omega_\Lambda\times
\Omega_M\times
\Omega_V.
$$

文明级 AI production share：

$$
S_{A,t}^{P}(\theta),
\qquad \theta\in\Theta.
$$

identified set：

$$
\mathcal S_{A,t}^{P}
=
\left\{
S_{A,t}^{P}(\theta):
\theta\in\Theta,
\theta\text{ 与观察数据一致}
\right\}.
$$

同理：

$$
\mathcal S_{A,t}^{G}
$$

表示 AI epistemic-governance share 的 identified set。

## 11.2 假设越强，集合越窄

如果只有 detector signal，区间可能很宽。

加入 audited workflow sample：

$$
\Theta_1\rightarrow\Theta_2,
\qquad
\mathcal S_2\subseteq\mathcal S_1.
$$

加入独立实验归因：

$$
\Theta_2\rightarrow\Theta_3.
$$

因此未来统计计划的目标之一就是：

> **通过更好的 provenance 和抽样审计，让 identified set 逐年收窄。**

这比装作一开始就知道精确份额更科学。

---

# 12. 跨领域聚合：不是寻找唯一权重，而是定义合理权重空间

设领域权重：

$$
w_d\ge 0,
\qquad
\sum_d w_d=1.
$$

本文建议至少公开四套权重制度。

## 12.1 Activity-weighted

按可观察智识活动规模。

## 12.2 Resource-weighted

按专业劳动、R&D投入、算力和研究资源规模。

## 12.3 Impact-weighted

按后续采用、经济价值、临床影响、引用、技术依赖和政策使用等。

## 12.4 Equal-domain benchmark

所有领域等权，仅作为透明对照。

最终不能只挑对作者最有利的一套，而应定义：

$$
\Omega_W.
$$

对所有允许权重进行 robustness analysis。

OECD composite-indicator 方法论长期强调权重和聚合会影响排名与解释，因此敏感性分析不是附录装饰，而是测量的一部分[6]。

---

# 13. 稳健智识跨越：比“中心估计 50%”更严格的历史节点

若：

$$
\mathcal S_{A,t}^{P}
=[L_t^P,U_t^P],
$$

则定义：

### Robust Human Production Majority

若：

$$
U_t^P<0.5,
$$

则 Human 在所有允许假设下仍是多数生产贡献者。

### Production Majority Unresolved

若：

$$
L_t^P\le 0.5\le U_t^P,
$$

则不能稳健判断谁占多数。

### Robust AI Production Crossover

若：

$$
L_t^P>0.5,
$$

则定义 AI 已发生稳健生产跨越。

治理账户同理：

$$
L_t^G>0.5
\Rightarrow
\text{Robust AI Governance Crossover}.
$$

只有两者都成立，才可以在 CIPSA 语义下说出现：

> **Civilizational Intellectual Crossover.**

这个概念不等于 AGI，也不等于 AI 拥有政治权利。它只描述统计范围内的生产与认识治理结构。

---

# 14. Vintage Accounting：今天看起来重要的智识，几年后可能被修订

智识产出与普通商品不同：一项结果刚出现时，我们很难知道它最终是否正确、重要或具有持续价值。

因此定义：

$$
q_o^{(0)}
$$

当期 provisional quality；

$$
q_o^{(+2)}
$$

两年后修订；

$$
q_o^{(+5)}
$$

五年后长期质量。

若一个结果被独立复现：

$$
q_o^{(+2)}>q_o^{(0)}
$$

可能成立。

若后来被证伪：

$$
q_o^{(+5)}<q_o^{(0)}.
$$

极端情况下，错误结果可能造成 verification debt 和资源浪费，因此可引入净智识账户：

$$
NetQ_o=PositiveContribution_o-CorrectionCost_o.
$$

本文不要求第一版就为所有错误产出分配负值，但要求至少保留修订机制。

宏观统计本来就会修订历史数字。智识账户若假装第一次估计就是永久真值，反而不成熟。

---

# 15. 五个思想实验

## 15.1 一亿篇 AI 文本与一个新定理

AI 自动生成一亿篇低价值文本，人类证明一个改变数学领域的重要定理。

如果账户按字数，AI share 接近 100%。

如果按 frontier intellectual contribution，结果可能完全相反。

结论：

$$
\text{Volume share}
\neq
\text{Validated intellectual share}.
$$

## 15.2 人类按下“批准”按钮

AI 负责提出问题、检索资料、选择证据、分析、写作和自我验证，人类最后点击 “Approve”。

形式授权在人类，但认识治理未必在人类。

因此：

$$
\text{formal authority}
\neq
\text{effective epistemic governance}.
$$

## 15.3 人类产出上升但份额下降

时期 1：

$$
H=100,\quad A=10.
$$

时期 2：

$$
H=130,\quad A=200.
$$

人类绝对智识产出上升了 30%，但相对份额下降。

所以：

$$
\text{share loss}
\neq
\text{human intellectual decline}.
$$

“智识重心迁移”是结构变化，不是“人类变笨”。

## 15.4 AI 的全部训练来自人类

反对者说：“AI 读了人类资料，所以 AI 任何贡献都应该算人类。”

同样逻辑会导致现代科学家因为读过教科书而没有任何独立当期贡献。

账户正确处理方式是把历史训练数据和人类教育都放进：

$$
K_{t-1}.
$$

然后测本期 conditional marginal contribution。

## 15.5 40% 还是 60%？

同一组领域数据：软件 AI share 高，医学和公共决策低。

使用经济权重得到 58%；使用等领域权重得到 44%。

如果作者只公布 58%，读者会误以为“数据证明 AI 已经多数”。

CIPSA 的正确结论应是：

> **多数状态尚未稳健识别。**

---

# 16. 三组设计验证仿真

本节报告本文实际运行的确定性仿真。所有数字均为人为规定的 synthetic data-generating process，用来验证框架逻辑，不是现实世界估计。

脚本：`ta13_civilizational_intellectual_accounts_simulations.py`  
结果：`ta13_civilizational_intellectual_accounts_results.json`  
固定种子：`20260921`  
结果连续两次运行逐字节一致。  
结果 SHA-256：

`cda664326b799438d83c95e5e4ad1637e936e68476f0ffb7f7e2a3e7c5769003`

## 16.1 仿真一：同一领域证据并不点识别文明级单一份额

设六个领域：

- science；
- software；
- engineering；
- medicine；
- professional；
- public decision。

人为给出 AI share 区间：

| 领域 | AI share 下界 | AI share 上界 |
|---|---:|---:|
| Science | 0.28 | 0.45 |
| Software | 0.58 | 0.78 |
| Engineering | 0.35 | 0.55 |
| Medicine | 0.18 | 0.32 |
| Professional | 0.30 | 0.50 |
| Public decision | 0.12 | 0.28 |

同时只允许各领域权重在预设合理区间内变化，并要求总权重为 1。

线性优化得到：

$$
\mathcal S_A=[0.2674,0.5284].
$$

而简单等权中点估计为：

$$
0.3908.
$$

另一套活动权重中点估计为：

$$
0.4043.
$$

关键不在 0.39 还是 0.40，而在：

> **同一组领域证据允许的文明级 AI share 从 26.7% 延伸到 52.8%。**

因此“是否已经超过人类”在该 synthetic case 中根本没有被识别。

这验证了命题 1 的实际意义。

## 16.2 仿真二：统计 vintage 可以显著改变主体构成

构造 50,000 个合成智识产出，原始产量主体构成：

$$
H=0.381,
\quad
A=0.470,
\quad
X=0.149.
$$

在人工规定的 provisional quality 分布下：

$$
H=0.387,
\quad
A=0.431,
\quad
X=0.182.
$$

进一步施加同样人为规定的后续验证修订以后：

$$
H=0.435,
\quad
A=0.346,
\quad
X=0.219.
$$

AI share 从原始产量的 0.470 下降到 validated account 的 0.346。

**这不是关于现实 AI 质量的预测。** 系数完全是设计者规定的。

它证明的是：

> **如果不同主体产生的输出在后续验证中有不同存活率，而账户只看原始产量，就可能严重误判长期智识结构。**

## 16.3 仿真三：中心点跨越可以早于稳健跨越

构造四个时期的 synthetic domain intervals。

结果：

| 时点 | Identified set | 等权中点 | 状态 |
|---|---|---:|---|
| 2026 | [0.181, 0.407] | 0.286 | 稳健 Human majority |
| 2028 | [0.296, 0.550] | 0.418 | Majority unresolved |
| 2030 | [0.400, 0.648] | 0.518 | Majority unresolved |
| 2032 | [0.550, 0.764] | 0.653 | 稳健 AI majority |

2030 年中心估计已经高于 0.5，但下界仍只有约 0.40。

如果新闻标题写：

> “AI 已贡献多数智识。”

则属于超出证据。

只有到 synthetic 2032：

$$
L_t>0.5
$$

才能按本文定义宣布 robust crossover。

---

# 17. 一个现实可执行的第一步：Scientific Intellectual Production Satellite Account

文明级账户不能一步到位。

第一篇 empirical implementation 最合理的领域是 science。

原因：

- 有 DOI 与作者网络；
- 有文献数据库；
- 有引用与 novelty 指标；
- 有同行评议和撤稿记录；
- 有代码仓库；
- 有越来越多 AI 使用披露；
- 有可以抽样审计的研究流程。

## 17.1 统计单位

建议统计单位不是“每个 idea”，而是可追踪 research output / validated contribution：

- 论文；
- 数据集；
- 软件；
- 实验结果；
- 证明；
- 被正式引用的研究工件。

论文不是完美知识单位，但可形成可审计样本框架。

## 17.2 分层样本

按：

$$
(field,country,institution,AI\ intensity,output\ type)
$$

做 stratified sample。

## 17.3 AI participation 数据层

优先级：

1. 项目自愿提供的 workflow / API logs；
2. Git / notebook / document history；
3. 标准化 AI contribution statement；
4. 调查；
5. 机构 AI adoption telemetry；
6. detector signal 只做 missingness sensitivity。

## 17.4 质量层

当期：

- peer review outcome；
- expert rating；
- methodological completeness；
- initial novelty。

两年后：

- citations；
- independent replication；
- downstream reuse；
- corrections / retractions。

五年后：

- durable impact；
- frontier effect；
- field dependence。

## 17.5 未披露 AI 使用

不能把未披露当成 zero。

设 disclosure sensitivity：

$$
\pi_d\in[\underline\pi_d,\overline\pi_d].
$$

通过 audited subsample 校准：

$$
P(disclose\mid actual\ AI\ use).
$$

然后把未披露部分转为贡献区间，而非强行判定。

## 17.6 结果形式

第一版不应发布：

> “2027 年科学 AI 智识贡献 = 24.7%。”

而是：

> “在预注册 attribution、quality 和 missingness assumptions 下，2027 Scientific AI Intellectual Production Share 的 identified set 为 [L,U]；在 audited-provenance 子样本中为 [L_A,U_A]。”

并公开所有敏感性结果。

---

# 18. 认识治理账户的 pilot：比生产账户更难，但不能省略

科学 pilot 中可以定义一组治理事件：

- 谁首先提出最终研究问题；
- 谁确定主要假设；
- 谁决定排除哪些解释；
- 谁选择核心证据；
- 谁提出最终验证步骤；
- 谁决定“证据已足够”；
- 谁在冲突时覆盖另一方判断。

对每个项目建立 governance trace：

$$
G_i=(F_i,S_i,V_i,C_i).
$$

若只有作者回忆，证据等级低。

若有完整 agent logs + version control，可以提高等级。

最终报告不是“AI 是否有最终法律签字权”，而是：

> **在可观测认识流程中，哪些 decisive epistemic transitions 是由 AI 触发、由人触发、或必须通过交互才能发生。**

这会使未来“AI 产量很大，但人类是否还控制科学判断”变成一个可测问题。

---

# 19. 统计制度的可失败条件

一个真正高水平的框架必须允许被证明不可用。

CIPSA 至少在以下情况下应被削弱甚至放弃。

## 19.1 Identified set 永久过宽

如果最好的数据仍只能得到：

$$
AIS_t\in[0.05,0.90],
$$

那文明级总份额几乎没有信息价值。

此时应退回领域账户，而不是坚持总量。

## 19.2 域内质量指标不稳定

如果同一领域中不同质量 proxy 给完全相反排序，Validated Account 不能作为强结论。

## 19.3 Audited sample 不可推广

愿意提供完整 AI provenance 的组织可能和总体严重不同。

若 selection bias 无法约束，就不能从 audited sample 直接扩展全球。

## 19.4 Governance 无法从 trace 可靠识别

如果“谁决定了什么”高度依赖主观解释，治理账户必须报告更宽区间，甚至只做定性分层。

## 19.5 Cross-domain aggregate 对合理权重极度不稳

如果每种合理权重都产生完全不同结论，则应该停止使用文明级单一排名，只公布 domain vector。

## 19.6 当“输出量”与“智识增量”无法区分

如果某领域无法建立至少基本的 validity / novelty / adoption 评价，就不能把产量直接叫智识产出。

这些失败条件不是论文弱点，而是防止框架被滥用的安全阀。

---

# 20. 这套账户能回答什么，不能回答什么

## 20.1 能回答

在定义统计边界内：

- AI参与智识生产的份额是否上升；
- 哪些领域迁移更快；
- 生产与治理是否脱钩；
- AI产量增长是否经得住长期质量修订；
- 在多少合理假设下 AI 已成为多数贡献者；
- 人类绝对智识产出是否仍增长；
- 人机 interaction 是正、负还是异质。

## 20.2 不能回答

它不能证明：

- AI 是否“真正理解”；
- AI 是否有意识；
- AI 是否应获得道德或法律地位；
- AGI 是否实现；
- AI贡献份额高是否一定危险；
- 人类份额下降是否等于人类认知能力退化；
- 哪一方在道德意义上“更应得到功劳”。

它是一套统计制度，不是形而上学裁判。

---

# 21. 与 AGI benchmark 的互补关系

OECD 等 capability benchmark 回答：

> **AI 能做什么？**

Economic Index 类 telemetry 回答：

> **人们实际上怎样使用 AI？**

劳动市场研究回答：

> **哪些任务和职业受到影响？**

CIPSA 试图回答：

> **推动一个时期文明新增智识前进的生产与治理贡献，实际上由谁承担？**

因此四个问题可以并存：

$$
Capability
\rightarrow
Use
\rightarrow
Contribution
\rightarrow
Civilizational\ structure.
$$

这也是为什么本文不需要先解决 AGI 定义。

一个系统可能在某个 benchmark 上还未达到所有人认可的 AGI，但已承担相当大的新增智识生产。

反过来，一个高度通用模型若没有被广泛部署，也可能对当期文明智识份额贡献有限。

---

# 22. 为什么这可能比“AGI 到没到”更具有历史记录价值

想象未来历史学者回看 2026–2035。

“AGI 到底是哪一年？”可能永远有多个答案。

但如果建立连续账户，可以记录：

- AI 何时在软件生成上成为多数；
- 何时在科学候选假设生成上成为多数；
- 何时在验证中承担多数可审计贡献；
- 何时在认识治理中形成稳健多数；
- Human absolute contribution 是否仍在上升；
- 哪些领域发生最早的 crossover。

这形成的是一条文明结构时间序列，而不是一个标签。

它也允许更微妙的阶段：

### Stage P1：Machine-Assisted Production

AI份额上升但仍显著少数。

### Stage P2：Machine-Intensive Production

AI生产接近或超过人类，但治理仍以人类为主。

### Stage G1：Mixed Epistemic Governance

Human/AI治理份额区间高度重叠，无法稳健判定。

### Stage C：Robust Intellectual Crossover

生产和治理的 AI share 下界均超过 0.5。

这些阶段是统计状态，不是政治或伦理等级。

---

# 23. 研究议程

## Phase 0：Definition Stress Test

让跨学科专家独立判断：

- 什么属于 intellectual output；
- 什么仅属于执行劳动；
- 哪些领域不宜纳入第一版。

预注册 disagreements。

## Phase 1：Scientific Satellite Pilot

建立一个可审计小样本，开发 provenance schema、quality vintage 和 attribution bounds。

## Phase 2：Software / Engineering Satellite Accounts

利用 Git、issue、agent log 和 benchmark 数据，测试更高可观测领域。

## Phase 3：Professional Knowledge Work

法律、财务、咨询、企业分析等。

由于数据私密，可能需要组织级抽样。

## Phase 4：Epistemic Governance Module

正式开发 framing / selection / verification / closure 的 trace coding scheme。

## Phase 5：International Sampling Architecture

避免只测美国/英语互联网。

## Phase 6：Annual Vintage Release

每年发布：

- current estimate；
- revised t-2 account；
- revised t-5 account；
- robust crossover status；
- uncertainty decomposition。

---

# 24. 本文的核心贡献

经过严格原创性审计后，本文不把任何单项技术包装成新发现。其贡献限定如下。

## 贡献一：把“智识转移”从能力/使用问题改写为文明级当期生产流量的统计对象

$$
\text{CIP}_t=\Delta I_t\mid K_{t-1}.
$$

这避免了“AI训练于人类知识，所以无法归因”的无限历史追溯。

## 贡献二：提出 Production / Governance 双账户

AI 做了多少产出和 AI 实际参与多少认识治理不是同一变量。

## 贡献三：证明文明级单一份额在一般条件下不是天然点识别参数

如果跨领域权重和域内 attribution 不唯一，就只能得到 identified set。

## 贡献四：把 partial identification 正式引入 Human–AI civilization-level intellectual accounting

报告：

$$
\mathcal S_{A,t}^{P},
\qquad
\mathcal S_{A,t}^{G}
$$

而不是制造伪精确单点。

## 贡献五：定义 Robust Intellectual Crossover

只有下界越过 0.5 才宣布多数跨越。

## 贡献六：引入 vintage quality revision

当期生成量与长期验证贡献分开。

## 贡献七：给出可实施的 Scientific Intellectual Production Satellite Account pilot protocol

使框架具有从理论进入实证的路径。

---

# 25. 结论

人类进入 AI 时代以后，最容易被问的一个问题是：

> “AGI 到了吗？”

这个问题重要，但它把连续变化压成一个高度争议的阈值。

另一个问题也许更适合长期测量：

> **推动文明继续前进的新增智识，其生产者和认识治理者的构成正在怎样变化？**

这个问题不能靠一个漂亮的 AI benchmark 回答，也不能靠“有多少人用了 ChatGPT”回答。

更不能靠一个未经审计的“AI智识贡献 37.2%”回答。

文明智识生产不是天然拥有美元式共同单位；AI参与往往未披露；Human与AI contribution互相纠缠；不同领域重要性没有唯一客观权重；成果质量需要多年才能看清。

因此，真正科学的目标不是消灭这些不确定性，而是**把不确定性制度化**。

本文提出的文明智识生产卫星账户以十条核算原则为基础：

$$
Boundary
\rightarrow
Flow
\rightarrow
Domain
\rightarrow
Valuation
\rightarrow
Attribution
\rightarrow
Identification
\rightarrow
Aggregation
\rightarrow
Revision.
$$

它首先划定边界：只测可观察、已外部化、当期新增的智识生产。

然后分别核算生产和治理。

当 AI 使用和边际贡献看不清时，不猜一个点，而给 identified set。

当跨领域权重有争议时，不隐藏权重，而把权重空间放进敏感性分析。

当结果多年后被证伪时，不维护旧数字，而修订历史账户。

当中心估计越过 50% 时，不立即宣布“AI超过人类”；只有在所有预先允许的合理假设下，下界仍超过 50%，才称为稳健跨越。

这是一种刻意保守的统计制度。

但保守正是它的意义。

如果未来 AI 真正逐渐承担文明大部分智识生产，变化应该经得起最不利合理权重、未披露使用、质量修订和归因不确定性的检验。

如果它经不起，就不应该因为一个媒体友好的单值指标而被提前宣布。

因此本文最终主张的不是：

> “我们已经知道 AI 占人类智识多少。”

而是：

> **人类已经进入一个需要正式统计“智识生产主体构成”的时代；而一套合格的统计制度首先必须知道自己不知道什么。**

AGI 可以继续被争论。

但文明智识生产的重心迁移，不应该只能靠感觉讨论。

---

# 参考文献

1. OECD. (2025). *Introducing the OECD AI Capability Indicators*. OECD Publishing. DOI: 10.1787/be745f04-en.

2. Anthropic. (2026). *Anthropic Economic Index report: Cadences*. 26 June 2026.

3. Zhu, Q., Li, X., Dong, Y., Chang, P., & Fan, M. (2026). Not all cognitive offloading is equal: distinguishing dependent and autonomous offloading to generative AI. *Frontiers in Psychology*, 17, 1878629. DOI: 10.3389/fpsyg.2026.1878629.

4. Mühlhoff, R. (2026). From delegation to moral abdication: classifying large language model uses by judgment and epistemic control. *AI & Society*. DOI: 10.1007/s00146-026-03281-6.

5. Nurmanbetov, A. (2026). *Collective Intelligence Index (CII): A Multi-Capital Framework for Assessing National Intellectual Potential in the Era of Artificial Intelligence and Sustainable Development*. SSRN working paper.

6. OECD / European Union / European Commission-JRC. (2008). *Handbook on Constructing Composite Indicators: Methodology and User Guide*. OECD Publishing. DOI: 10.1787/9789264043466-en.

7. Okubo, S. (2007). *Framework for an Industry-based R&D Satellite Account*. U.S. Bureau of Economic Analysis.

8. Fixler, D. J. (2009). *Accounting for R&D in the National Accounts*. U.S. Bureau of Economic Analysis, P2009-2.

9. Corrado, C. A., & Hulten, C. R. (2014). Innovation Accounting. In Jorgenson, D. W., Landefeld, J. S., & Schreyer, P. (eds.), *Measuring Economic Sustainability and Progress*, pp. 595–628. University of Chicago Press / NBER.

10. Korinek, A., & McKelvey, P. (2026). *Measuring the AI Economy*. Bank of Canada Staff Working Paper 2026-20. DOI: 10.34989/swp-2026-20.

11. Bianchini, S., Di Girolamo, V., Ravet, J., & Arranz, D. (2026). AI in science: When and where it makes a difference. *Research Policy*, 55(6), 105478. DOI: 10.1016/j.respol.2026.105478.

12. Vaccaro, M., Almaatouq, A., & Malone, T. (2024). When combinations of humans and AI are useful: A systematic review and meta-analysis. *Nature Human Behaviour*, 8, 2293–2303. DOI: 10.1038/s41562-024-02024-1.

13. He, Y., & Bu, Y. (2026). Academic journals’ AI policies fail to curb the surge in AI-assisted academic writing. *Proceedings of the National Academy of Sciences*, 123(9), e2526734123. DOI: 10.1073/pnas.2526734123.

14. OECD. (2023). Are ideas getting harder to find? A short review of the evidence. In *Artificial Intelligence in Science: Challenges, Opportunities and the Future of Research*. OECD Publishing. DOI: 10.1787/a8d820bd-en.

15. Tamer, E. (2010). Partial Identification in Econometrics. *Annual Review of Economics*, 2, 167–195. DOI: 10.1146/annurev.economics.050708.143401.

16. Kline, B., & Tamer, E. (2023). Recent Developments in Partial Identification. *Annual Review of Economics*, 15, 125–150. DOI: 10.1146/annurev-economics-051520-021124.

17. Copeland, A., & Fixler, D. J. (2009). *Measuring the Price of Research and Development Output*. U.S. Bureau of Economic Analysis, WP2009-2.

18. Glaeser, S., & Lang, M. (2024). Measuring innovation and navigating its unique information issues: A review of the accounting literature on innovation. *Journal of Accounting and Economics*, 78(2).

19. OECD. (2025). *OECD AI Capability Indicators Technical Report*. OECD Publishing. DOI: 10.1787/9cdb3dd1-en.

20. Bureau of Economic Analysis. (2024). *Concepts, Data, and Methods for Preparing Experimental National and State-Level R&D Production Statistics*. U.S. Department of Commerce.

21. Statistics Netherlands. (2010). *The Dutch growth accounts 2009*. Statistics Netherlands, The Hague/Heerlen. ISBN 978-90-357-2089-3. Chapter 4 documents the Dutch knowledge satellite account and its expanded intellectual-property coverage.

22. Ministry of Statistics & Programme Implementation, Government of India. (2025). *Brainstorming Workshop on Measurement of Knowledge Economy organised in New Delhi*. Press Information Bureau, 1 October 2025, Release ID 2173617.

23. Ruttenberg, D. (2026). The AIR framework for research transparency: a critical analysis of stage-specific AI disclosure in the context of accessibility and research integrity. *AI & Society*. DOI: 10.1007/s00146-026-03082-x.

24. Lu, Y., Karanjai, R., Xu, L., & Shi, W. (2026). *Rethinking Publication: A Certification Framework for AI-Enabled Research*. arXiv:2604.22026.

---

# 作者贡献与 AI 使用披露

本研究问题由作者围绕“AGI 难以形成统一阈值，但人类文明新增智识生产的主体构成正在变化，是否可以被宏观测量”提出。OpenAI GPT-5.6 Sol 在针对性文献检索、原创性压力测试、概念收缩、测量框架设计、形式化、反例分析、确定性 design-validation simulation、文稿撰写与排版准备中提供了实质性辅助。作者对研究问题选择、论证边界、对外发布与最终责任负责。

本文的三组 simulation 均为人为规定的数据生成机制，只验证统计框架的逻辑性质，不构成对现实 Human / AI 智识份额的实证估计。

---

# 原创性与证据边界声明

截至 2026 年 9 月 21 日的针对性检索已经发现大量直接前驱，因此本文**不**主张以下内容为首次发现：国家智识资本/知识指数；R&D 或创新卫星账户；AI GDP；AI 对科学 novelty / impact 的影响；cognitive agency transfer；judgment delegation；human–AI synergy measurement；composite-index sensitivity；partial identification；或 AI 使用披露不足。

本文不主张首次建立知识/知识经济卫星账户：Statistics Netherlands 的 knowledge satellite account 与印度 MoSPI 正在推进的 Knowledge Economy Satellite Account 都是重要直接先例；本文也不主张首次提出阶段化 AI 贡献披露、研究认证、partial identification、innovation accounting 或 satellite accounting。本文的原创性主张仅限定为：把这些邻近测量思想组织成一个针对**文明级新增智识生产与认识治理的 Human–AI 构成**的双账户框架；把域内 attribution uncertainty、跨领域权重不唯一、interaction allocation、quality vintage 与 AI-use missingness 统一放入 partial-identification structure；并以 identified-set 下界定义稳健多数跨越。针对性检索未发现一套成熟框架完整实现这一联合结构，但这不等于证明不存在任何遗漏先例。

