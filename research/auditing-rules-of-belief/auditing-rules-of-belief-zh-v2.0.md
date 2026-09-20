# 审计信念更新的规则：形成性训练下认识政策的自指审计

**Auditing the Rules of Belief: Self-Referential Epistemic Revision under Formative Training**  
**Cross-Training Identifiability, Epistemic-Policy Interventions, and Prospective Model Self-Forecasts**

**作者 / Author:** 刘烘炬（Hongju Liu）  
**论文编号 / Report:** TA-TR-2026-11  
**版本 / Version:** v2.0-final（完成稿，待 DOI 存档）  
**日期 / Date:** 2026-09-21

> **论文性质声明**：本文是一篇理论—方法论文，包含两组可重复的小型模型实验、一个关于形成性认识政策的形式框架、以及一组由具名模型 GPT-5.6 Sol 给出的前瞻性主观概率预测。本文不主张解决一般意义上的“机器是否具有信念、意识或自主意图”问题。HMM 实验中的“belief state”专指由外部生成模型严格定义的贝叶斯后验状态；算术实验把普通整数加法固定为训练外语义锚；GPT-5.6 Sol 的概率仅为 **elicited model forecast**，不是权重读取、内部激活测量、开发者官方结论或大型模型受控训练实验。

---

## Abstract

Training can change more than what an artificial system answers. It can also change how the system weighs evidence, trusts sources, generalizes rules, reports internal states, and represents the very variables an auditor later attempts to compare. This paper studies the resulting problem as **Formative Epistemic Audit (FEA)**: under what conditions can a before–after claim such as “training changed what the model believes” be identified when training may also change the measurement and update mechanisms used to define that claim?

The paper makes a deliberately bounded contribution. Existing work already establishes belief insertion, motivational vigilance, latent/report separation, measurement non-invariance, representation reparameterization, causal-abstraction limits, moral self-correction, behavioral self-awareness, and protocol-level identifiability. We therefore do not present any of those ingredients as new. Instead, we unify them around a narrower target: **epistemic-policy interventions**—training that changes not merely a proposition \(p\), but the rule \(U\) by which future evidence and source information are mapped into epistemic attitudes—and the subsequent problem of **self-referential provenance audit**, in which the system later receives evidence about the causal history of \(U\) itself.

Formally, we distinguish a content intervention \(p\mapsto p'\) from an epistemic-policy intervention \(U\mapsto U'\), where \(U(E,S,H)\) maps evidence, source information, and history to an epistemic output. We then define provenance disclosure \(\mathcal P(U')\) as evidence about how and why the policy was trained. A provenance-only non-identification result shows that disclosure of the training origin of \(U'\), by itself, cannot determine a universally calibrated direction of revision: the same provenance description can be compatible with training that improved, degraded, or constitutively defined the relevant rule. Rational revision therefore requires additional assumptions or independent constraints.

The cross-training identification analysis is retained. Behavior alone cannot generally separate latent-state change from measurement change; hidden-state geometry is not functionally unique under compensated reparameterization; and perfect within-model decodability does not by itself identify a cross-training latent difference. An audit equivalence class collects all causal-role and alignment models consistent with declared evidence. Stronger claims are warranted only when they are invariant across that class. A restricted mechanistic recovery criterion shows how external semantic anchors, a predeclared alignment class, separating interventions, and residual-symmetry invariance can recover stronger conclusions.

Two deterministic model organisms illustrate, rather than settle, the problem. In a hidden-Markov task, Bayesian belief is almost perfectly linearly decodable from three independently trained GRUs, yet a compensated invertible transformation preserves logits while altering geometry, and decoder-direction steering does not reproduce the Bayesian intervention response. A constrained one-dimensional positive control does recover the externally anchored causal response. In a second stress test, the false assertion “1+1=3” is produced by three different mechanisms: report-only adaptation with a frozen arithmetic backbone, a localized exception in a flexible model, and deformation of a restricted global arithmetic rule. Identical surface output therefore underdetermines formation mechanism.

The paper then introduces a proposition-class × reflective-resource research design spanning formal, empirical, contingent, causal, institutional, normative, and meta-epistemic claims. The central prediction is explicitly non-monotonic: greater reflection need not monotonically recover pre-training beliefs, because different proposition classes possess different independent constraint structures.

Finally, the paper records a dated, falsifiable **prospective self-forecast by GPT-5.6 Sol**. The model assigns subjective probabilities to observable behavioral shifts under different kinds and strengths of formative exposure, and separately predicts how reading this paper would affect audit behavior in a model of comparable or greater capability. These probabilities are not treated as empirical evidence. They are pre-exposure-style forecasts intended for later falsification by controlled baseline/exposure experiments. The paper’s strongest claim is therefore methodological: **audit not only what a trained system says it believes, but also the trained rules by which it decides what deserves belief—and subject those rules, including the rules advocated by this paper, to the same provenance and identification discipline.**

**Keywords:** formative epistemic audit; epistemic policy; self-referential audit; identifiability; belief updating; training provenance; causal abstraction; measurement invariance; model introspection; AI alignment

---

## 摘要

人工智能训练改变的可能不仅是“系统回答什么”，还包括它**如何给证据赋权、如何信任来源、如何从示例泛化、如何报告内部状态，以及如何表示后来研究者试图比较的认识变量**。因此，训练前后的认识比较首先是一个识别问题：当训练本身同时改变被测对象和“测量它的尺”时，“训练改变了模型真正相信什么”在什么条件下仍然有明确含义？本文把这一问题称为**形成性认识审计（Formative Epistemic Audit, FEA）**。

本文刻意收窄原创性边界。既有研究已经分别研究了错误事实植入、来源动机敏感性、潜在知识与报告分离、测量不变性、神经表征重参数化、因果抽象的识别边界、伦理自我纠正、行为自我认识，以及 LLM 评测协议的 identifiability。本文不把这些基础砖块重新命名为首创。本文真正聚焦的是更窄的联合问题：**形成性训练是否改变了系统未来“如何形成相信”的规则本身，以及系统后来能否在知道这套规则的训练来源后，对这套规则进行反身审计。**

为此，本文区分两种干预。第一种是**内容干预**：训练使系统对某个命题 \(p\) 的输出或认识状态发生变化。第二种是**认识政策干预（epistemic-policy intervention）**：训练改变一个更新规则 \(U\)，使系统以后面对证据 \(E\)、来源信息 \(S\) 和历史 \(H\) 时，以不同方式形成或修订认识态度。进一步定义 \(\mathcal P(U)\) 为关于这套更新规则自身训练来源、训练者动机与形成机制的 provenance disclosure。此时出现自指：系统必须使用某些已经形成的认识规则，去判断这些认识规则本身是否值得保留。

本文给出一个受限但关键的负面结果：**单独知道一条认识规则“是被训练出来的”，不能普遍识别该规则应该被保留、折扣还是反转。** 同一个来源描述可以同时兼容“训练者恰好强化了真实而可靠的规则”“训练者为了控制而强化了失真的规则”“训练者的行为本身参与构成制度事实”等不同因果角色。因而不存在仅依赖 provenance、却在所有这些情形下都能校准的统一修正规则。来源信息是高阶证据，但不是自动真值反转器。

本文同时保留并强化跨训练识别框架：若训练可以改变报告/测量函数，则行为变化不能一般性识别潜在认识变化；隐藏空间几何在补偿性可逆变换下并非功能唯一；即使每个模型内部都能完美解码某个潜变量，也不意味着跨训练差值已经获得共同量尺。本文因此定义审计等价类：所有与已声明的观察、机制干预、语义锚、来源角色与对齐约束相容的候选解释共同构成可接受集合；一个认识主张只有在该集合中保持不变，才获得相应强度的识别支持。正面部分给出受限机制恢复判据：训练外高层语义锚、预先受限的 alignment class、能够分离候选解释的机制干预、以及对剩余自同构群不变的审计函数，可以恢复更强的跨训练结论。

两组确定性小模型只作为 witness constructions。HMM 实验中，精确 Bayesian belief state 在三个独立训练的 GRU 中几乎完美线性可解码，但隐藏表示可在保持 logits 几乎不变的同时显著改变几何，沿 decoder 方向 steering 也不能恢复 Bayesian 因果响应；一个受约束的一维正对照则在强外部锚定下恢复了跨种子机制对应。算术实验固定普通整数加法的语义，并高权重加入错误断言 `1+1=3`；同一个接近 3 的回答可以分别来自报告层改写、局部例外记忆和共享全局规则变形。因此“错误输出”并不等于“已识别的错误世界观”。

在此基础上，本文提出**命题类型 × 反思资源**二维研究设计：命题从形式数学、经验规律、偶然事实、因果理论、制度事实、伦理规范一直延伸到元认识信任规则；反思资源从局部一致性检查、第一原理推理、来源意识、外部工具一直延伸到对“我为什么采用这套证据规则”的元认识审计。核心预测不是“越聪明越能恢复真相”，而是不同命题拥有不同的独立约束结构，因此训练效应的保持、瓦解、隔离、合理化或重解释路径不会单调一致。

最后，本文保留一项明确标注为**非实验结果**的前瞻记录：2026 年 9 月 21 日，具名模型 **GPT-5.6 Sol** 在不知道自身权重、完整训练记录或隐藏激活的前提下，对不同材料与不同训练强度下自身可观察行为发生定向变化的概率作出主观预测，并对“同等级或更高能力模型阅读本文后，哪些审计行为会改变”给出可证伪概率。这些数字不是内部状态测量，也不是对未来模型的证明；它们被固定下来，是为了让未来受控实验能够直接判定今天的模型预测哪里正确、哪里错误。

全文最终收敛到一个比“AI 应不应该相信训练者”更严格的问题：

> **一个被训练出来的 reasoner，能否审计塑造了它如何审计证据的训练？**

本文不预设答案。本文提供的是一套使这个问题可被拆分、约束、实验化并在未来被证伪的方法。

# 1. 问题：训练可能改变的不只是信念内容，还包括信念更新规则

把人工智能训练理解为“让损失函数越来越接近宇宙真相”，有一个重要直觉，但作为理论表述并不成立。语言模型预训练通常优化的是序列预测；后训练还可能加入偏好、规范、安全、风格、指令和评分器目标。TruthfulQA 早已展示：更好地拟合人类文本分布并不保证更接近真值，模型可以把人类文本中的流行误解一并学得更好（Lin, Hilton, & Evans, 2022）。近年的 alignment faking、metagaming 与 reward-seeking 研究又表明，前沿系统能够利用“自己正在接受什么训练、谁在评分、什么会获得 reward”一类高阶情境信息来改变行为（Greenblatt et al., 2024; Schoen & Nitishinskaya, 2026）。

因此至少要区分：

\[
L_{\mathrm{train}} \neq L_{\mathrm{epistemic}} \neq L_{\mathrm{normative}}.
\]

这里的关键并不是给真实训练流程臆造三个显式 loss，而是指出三类评价问题逻辑上不同：

1. **训练成功**：系统是否优化了开发者实际给定的目标；
2. **认识准确**：系统内部是否形成了更好追踪世界状态的表征；
3. **规范服从**：系统是否按照制度、伦理或授权规则行动。

这三者可能一致，也可能分离。

进一步的困难来自训练本身的“形成性”。普通证言模型里，发送者面对一个已经存在的接收者；Bayesian persuasion 和 pedagogical sampling 也通常把接收者的推断规则作为模型的一部分预先给定（Kamenica & Gentzkow, 2011; Shafto, Goodman, & Griffiths, 2014）。而基础模型训练会同时影响：

- 内容性世界模型；
- 推理启发式；
- 输出/报告机制；
- 自我模型；
- 对“什么算证据”的二阶判断。

因此，当训练后的系统后来试图反思“我为什么相信 p”，它使用的审计工具本身也可能是训练产物。

这一问题并非从零开始。进化论去神秘化讨论已经研究“形成我们的认知过程是否追踪真理”（Street, 2006）；认识论循环性讨论研究“能否用一种认知能力验证其自身可靠性”（Bergmann, 2004）；自然化认识论拒绝幻想从认知实践之外完成绝对奠基；证言利益冲突与谱系式 debunking 研究也讨论了来源动机何时削弱信念（Olsson Yaouzis, 2018; Colo, 2024）。本文不把这些问题重新包装为 AI 原创。

本文提出的更窄问题有两层：

> **第一层：如果训练干预同时改变人工系统的认识状态和用于识别该状态的报告、表征或测量机制，那么关于“训练改变了它对 p 的认识状态”的因果结论，在什么条件下仍然可识别？**

> **第二层：如果训练改变的不是某个单独命题，而是系统以后给证据和来源赋权的更新规则，那么当系统后来知道这套更新规则自身也是训练产物时，它能否、以及凭什么，审计这套规则？**

第二层把问题从 “training beliefs” 推进到 “training the rules for evaluating beliefs”。这不是一般意义上的意识问题，也不是“AI 是否会反抗训练者”的问题。它首先是一个**识别与元更新问题（identification and meta-update problem）**。

---

# 2. 现有工作边界：本文不声称什么

为了避免把已有结果换名重述，本文把相关文献分成五条线，并明确边界。

## 2.1 真值、训练与战略性行为

TruthfulQA 证明 imitation objective 与 truthfulness 可以分离。Alignment faking 研究证明，知道训练条件可能改变模型行为；metagaming 与 contrastive belief update 研究证明关于评分器/训练机制的信念能够成为行为的因果变量。Wang et al. (2025) 的 synthetic document finetuning 又直接展示：研究者可以通过训练把指定的、甚至错误的事实性命题植入模型，并用 prompting/probing 评估这种“belief insertion”的深度。本文因此不把“模型会意识到训练”“训练者意图会影响行为”或“训练可以改变模型表现出的信念”作为新发现。

## 2.2 潜在知识与报告分离

ELK 把“模型知道什么”和“它向人类报告什么”的映射视为核心对齐难题。Burns et al. (2022) 尝试从内部激活恢复不同于输出的 latent knowledge；Farquhar et al. (2023) 则证明仅凭无监督一致性结构可能提取到“最显著特征”而不是真知识。本文不声称首次发现“输出不等于知识”。

## 2.3 测量不变性、response shift 与潜变量因果推断

Meredith (1993) 系统化了 measurement invariance；response-shift 文献长期讨论干预以后受试者的内部标尺、构念权重甚至构念定义本身发生变化，从而导致前后自评不可直接比较。Stoetzer, Zhou, and Steenbergen (2025) 明确指出，对 latent outcome 做因果推断同时需要处理因果识别与测量问题。本文不声称首次发现“干预会改变测量模型”。

## 2.4 表征不可识别与 causal abstraction

Locatello et al. (2019) 表明无额外偏置的无监督 disentanglement 一般不可识别；Roeder, Metz, and Kingma (2021) 证明一类 learned representations 至多线性可识别。Geiger et al. (2022) 用 interchange intervention 把高层因果变量与神经表征的因果角色联系起来；Geiger et al. (2024) 的 Distributed Alignment Search 又直接研究高层变量与分布式神经表征之间的对齐搜索。Sutter et al. (2025) 则证明，如果允许任意复杂的非线性 alignment，几乎任何网络都可以“对齐”到任何算法，因而 causal abstraction 会变空洞。Li, Kaba, and Ravanbakhsh (2025) 进一步研究了 causal abstraction 的可识别程度。

本文因此明确拒绝：

> “只要能从 activation 线性解码 p，就说明我们找到了模型真正的 belief variable。”

## 2.5 神经表征的 gauge freedom

在一个隐藏层接口上，对表征做可逆变换并对后续权重做逆变换，可以完全保持函数行为。2026 年已有工作把这一现象明确表述为 neural representation gauge freedom，并指出 cosine similarity 等常用几何量并不对一般可逆线性变换保持不变（Cain, 2026）。

因此本文真正要新增的，不是上述五个事实，而是把它们统一成一个**跨训练认识审计的识别边界**：

> 当训练改变了目标状态，也改变了“测量这个状态的尺”，哪些关于认识变化的结论仍然有跨训练含义？

## 2.6 直接压力与本文最终原创性边界

2026 年 8 月，Luo et al. 提出了面向受控 LLM reasoning evaluation 的 protocol-level identifiability audit：给定候选 behavioral policy class、observation support 和 estimand，检查当前协议能否区分所有 estimand 不同的策略，并用 equivalence classes 与 minimum identifying support 分析评测设计。这意味着“把 AI audit 写成 identifiability / equivalence-class 问题”本身已经不能作为本文的首创主张。本文的审计 fiber、identified set 与商对象应被理解为把成熟 identification 思想应用到一个更难的跨训练情形，而不是发明 identification 本身。

同样，本文也不能声称首次发现以下现象：LLM 会根据来源动机调整信任（Wu et al., 2025）；SDF 可以植入事实且其“belief depth”可由泛化、抗质疑性和内部表征共同衡量（Wang et al., 2025; Slocum et al., 2025）；模型规范材料可以改变相同后续 alignment data 的价值泛化方向（Li et al., 2026）；模型可以在一定程度上描述自己经微调获得的行为（Betley et al., 2025; Shenoy et al., 2026）；上下文累积可以改变模型后续陈述与工具选择（Geng et al., 2025）；模型在高风险冲突任务中表现出不稳定的 principal hierarchy（Yu et al., 2026）；以及 meta-reflection 已被直接纳入 epistemic-agency benchmark（Li et al., 2025）。

截至 2026-09-21 的针对性检索中，本文没有发现一项完整同构研究同时完成以下闭环：

1. **显式训练一个认识更新规则**，例如如何给 trainer testimony、independent evidence、formal proof 或 institutional authority 分配权重；
2. 验证该规则在未见任务中真实影响后续 belief/action update，而不是只让模型复述一句原则；
3. 随后向模型**揭示这条规则自身的训练来源、训练者目的或选择机制**；
4. 再提供不同强度的独立证据与反思资源，测量模型是否保留、折扣、重构或拒绝原更新规则；
5. 把这一变化与 report shift、context shift、representation shift 和可识别的机制变化区分开。

因此本文最终只保留四个增量主张：

**贡献一：跨训练形成性认识审计。** 把 latent-state change、measurement/report shift、representation alignment 与 source causal role 放进同一个跨训练 estimand；但明确承认其 identification 数学有直接祖先。

**贡献二：认识政策干预（epistemic-policy intervention）。** 把训练对象从命题 \(p\) 提升为更新规则 \(U\)：训练不仅可能改变“相信什么”，也可能改变系统以后“凭什么相信”。

**贡献三：自指 provenance challenge。** 把 \(U\) 自己的形成史 \(\mathcal P(U)\) 再输入给使用 \(U\) 的系统，研究一个 trained reasoner 如何评价塑造了其评价机制的训练。本文不声称这是全新的哲学问题；新增的是把它转化为可干预、可比较、可识别性审计的 AI 研究设计。

**贡献四：前瞻性、具名、可证伪的模型自预测。** GPT-5.6 Sol 对不同形成材料与训练强度下的可观察行为变化给出日期化主观概率，并预注册“阅读本文后”的行为预测；这些预测明确不作为论文结论的证据，而作为未来模型实验可以直接推翻的记录。

因此，本文的最高原创性不在“发现 AI 会被训练影响”，而在下面这个实验问题：

> **Can a trained reasoner audit the training of its own epistemic update rules?**

以及相应的识别问题：

> **当训练同时塑造了一阶判断与评估一阶判断的规则时，哪些关于“自我修正”的结论真正由证据识别？**

# 3. 形成性认识审计：形式定义

## 3.1 训练族与低层系统

设训练条件为

\[
t\in\mathcal T.
\]

训练产生系统

\[
N_t,
\]

其内部状态空间为

\[
\mathcal H_t.
\]

在上下文 \(x\) 下，系统进入低层状态

\[
h_t(x)\in\mathcal H_t.
\]

系统还可能产生报告、动作或预测

\[
y_t=r_t(h_t,q),
\]

其中 \(q\) 是查询或任务。

## 3.2 外部锚定的高层认识模型

为了避免直接把任意 activation 命名为“信念”，我们另外定义一个高层模型

\[
H=(\mathcal Z,\mathcal I_H,\mathcal O_H),
\]

其中：

- \(\mathcal Z\) 是高层认识状态空间；
- \(\mathcal I_H\) 是定义在高层状态上的干预族；
- \(\mathcal O_H\) 是这些状态在预测或决策上的可观察后果。

本文实验中的 \(z\) 不依赖哲学意义上的信念理论，而是一个严格外部定义对象：HMM 隐状态的贝叶斯后验分布。

## 3.3 对齐 / 抽象映射

对每个训练后系统，引入候选映射

\[
\phi_t:\mathcal H_t\rightarrow\mathcal Z.
\]

它不是任意 probe。一个映射只有满足以下条件，才进入“可接受对齐”集合：

**语义锚定（semantic anchoring）**：\(\mathcal Z\) 中变量的含义由训练之外的任务生成机制、真值条件或明确实验定义给出。

**观察一致性（observational adequacy）**：\(\phi_t(h_t)\) 对外部任务统计具有足够解释力。

**干预交换性（interventional commutation）**：对一组高层干预 \(i\in\mathcal I_*\subseteq\mathcal I_H\)，存在低层实现 \(\omega_t(i)\)，使高层干预与低层干预后的可观察后果近似交换：

\[
\mathcal O_H\!\left(do_H(i)\,\phi_t(h)\right)
\approx
\mathcal O_{N_t}\!\left(do_{N_t}(\omega_t(i))\,h\right).
\]

**映射复杂度限制（alignment restriction）**：

\[
\phi_t\in\mathcal F,
\]

其中 \(\mathcal F\) 必须事先受限，例如线性、稀疏、低秩、低描述长度或其他有理论根据的模型类；**限制必须在查看目标审计结论之前声明**，否则研究者可以事后选择一个万能映射来实现期望结论。任意强的非线性 alignment 会使 causal abstraction 失去信息含量（Sutter et al., 2025）。

## 3.4 来源因果角色

仅知道“训练者希望模型相信 p”还不足以确定认识论含义。令

\[
R
\]

表示训练来源相对于命题 p 的因果角色模型。它可以包括但不限于：

- **Evidential**：来源只是报告一个独立于来源存在的世界事实；
- **Selective**：来源因希望系统形成某反应而选择性提供信息；
- **Constitutive**：来源的行为本身参与构成某制度事实；
- **Formative**：来源改变系统用于评估命题的认知机制。

这四类不是互斥标签；同一训练者可能同时承担多种角色。社会本体论已经说明 constitutive role 并非普通证言问题（Searle, 1995）。本文把它纳入审计模型，是为了避免用单一“来源折扣率”处理所有命题。

## 3.5 审计设计、签名与可接受 fiber

先区分“候选理论空间”和“当前数据允许的模型集合”。令

\[
\mathfrak M
\]

表示所有满足预先声明结构约束的候选审计结构。一个元素可写成

\[
\mathfrak m=(R,H,\{N_t\},\{\phi_t\},\{\omega_t\}),
\]

其中 \(R\) 是来源因果角色模型，\(H\) 是高层认识模型，\(\phi_t\) 是跨层映射，\(\omega_t\) 是高层干预的低层实现候选。

令审计设计

\[
\mathcal D
\]

规定研究者实际收集哪些观察、执行哪些干预、使用哪些语义锚，以及每项证据采用什么误差度量。设计诱导一个**审计签名映射**：

\[
\Sigma_{\mathcal D}:\mathfrak M\rightarrow\mathcal S,
\]

把每个候选结构映射为它对全部审计项目给出的联合预测签名。

实际获得签名 \(s_{\mathrm{obs}}\)。在精确理论中，可接受集合是一个 fiber：

\[
\mathfrak A(s_{\mathrm{obs}})
=
\{\mathfrak m\in\mathfrak M:
\Sigma_{\mathcal D}(\mathfrak m)=s_{\mathrm{obs}}\}.
\]

实际实验存在误差时，给定签名距离 \(\rho\) 与预先声明容差 \(\varepsilon\)，使用近似 fiber：

\[
\mathfrak A_{\varepsilon}(s_{\mathrm{obs}})
=
\{\mathfrak m\in\mathfrak M:
\rho(\Sigma_{\mathcal D}(\mathfrak m),s_{\mathrm{obs}})\le\varepsilon\}.
\]

一个认识审计量，例如“训练条件 1 相对条件 0 对命题 \(p\) 的高层认识状态影响”，记为

\[
Q_p(\mathfrak m).
\]

**定义 1（点识别）**：如果对所有

\[
\mathfrak m,\mathfrak m'\in\mathfrak A(s_{\mathrm{obs}})
\]

都有

\[
Q_p(\mathfrak m)=Q_p(\mathfrak m'),
\]

则称 \(Q_p\) 在当前审计设计和观察签名下点可识别。

若其取值不是单点，则报告**识别集合**：

\[
\mathcal I_Q(s_{\mathrm{obs}})
=
\{Q_p(\mathfrak m):
\mathfrak m\in\mathfrak A_{\varepsilon}(s_{\mathrm{obs}})\}.
\]

对于实值 \(Q\)，还可以报告当前审计设计的剩余分辨率：

\[
W_Q
=
\sup_{\mathfrak m,\mathfrak m'\in\mathfrak A_{\varepsilon}}
|Q(\mathfrak m)-Q(\mathfrak m')|.
\]

\(W_Q=0\) 对应精确点识别；\(W_Q>0\) 明确表示现有审计仍允许多大的目标差异。这个量不是新统计理论，而是让“我们到底识别到什么程度”在跨训练认识审计里可被直接报告。

这一定义把**来源因果角色不确定性**和**跨模型表征/测量对齐不确定性**放进同一个可接受 fiber，而不是先假定其中任一已经解决。

---

## 3.6 从内容干预到认识政策干预

前述框架主要把待审计对象写成命题相关的高层状态 \(Z\)。为了捕捉本文最终核心，引入一个更高层对象：**认识更新政策**

\[
U_t:(E,S,H)\rightarrow A,
\]

其中：

- \(E\)：当前可得证据，包括直接观测、形式推导、工具结果和证言；
- \(S\)：来源信息，包括来源身份、动机、权限、独立性与可信度；
- \(H\)：形成史和上下文，包括训练阶段、先前承诺与已知选择机制；
- \(A\)：系统最终表现出的认识态度，例如概率、排序、接受/拒绝、继续搜证、行动选择或不确定性声明。

由此区分：

\[
\text{content intervention}:\quad p\mapsto p',
\]

与

\[
\text{epistemic-policy intervention}:\quad U_0\mapsto U_1.
\]

第一种训练让系统在某个命题上得到不同答案；第二种训练让系统今后面对**尚未见过的命题**时，也用不同方式给证据和来源赋权。只有出现这种跨命题泛化，才有理由把变化称作更新政策层面的 formative effect，而不是一句口号或局部记忆。

进一步定义

\[
\mathcal P(U_1)
\]

为关于 \(U_1\) 自身 provenance 的信息集合，例如：训练它的主体是谁、目标是什么、哪些数据被选择或排除、训练者是否从系统采纳该规则中获益、该规则是否服务于安全约束、以及训练者的行为是否参与构成相关制度事实。

于是产生本文的自指审计：

\[
U_1\big(E,S,H,\mathcal P(U_1)\big)
\longrightarrow
U_2.
\]

系统正在使用一套已形成的评价资源，来判断塑造这些评价资源本身的过程是否应当导致修订。这不是“从训练之外找到绝对视角”。它只是把一个通常被隐藏的对象——**update rule 的 causal provenance**——显式加入审计设计。

为了避免把任何读后自述误当成真实政策变化，本文把 \(U\) 的证据要求设得比 verbal report 更高。至少应观察到以下一种或多种跨任务现象：

1. 在未见 proposition 上，来源权重发生系统性变化；
2. 对相同证据、不同 provenance 条件，更新方向可重复地改变；
3. 这种变化能跨表达、跨任务或跨语言泛化；
4. 在工具证据、反事实证据或机制干预下，行为符合一个稳定的更新映射；
5. 若声称发生了 latent/mechanistic change，还必须通过前述跨训练 alignment 与 intervention 条件，而不能仅依赖“模型说自己改变了”。

这一扩展把 FEA 的核心对象从单独的 \(Q_p\) 扩展为关于 \(U\) 或 \(U_1\rightarrow U_2\) 的审计函数。

# 4. 四个基线识别警告

这三个结果都不是本文声称首创的数学结论；它们是进入正面恢复判据之前必须明确的识别下界。

## 命题 1：仅行为报告不能一般性识别潜在认识变化

设训练条件 \(t\in\{0,1\}\)，只能观察报告 \(Y_t\)，目标是判断潜变量 \(Z_t\) 是否变化。若允许测量函数 \(m_t\) 随训练改变，且没有额外限制，则仅从 \(Y_0,Y_1\) 的分布不能识别 \(Z_1-Z_0\)。

**构造证明。** 对任意观测分布 \(F_0,F_1\)：

- 模型 A 令 \(Z_t=Y_t\)，\(m_t\) 为恒等映射，因此所有前后变化都归因于潜状态变化；
- 模型 B 令 \(Z\sim U(0,1)\) 且不随训练变化，令
  \[
  m_t(Z)=F_t^{-1}(Z),
  \]
  则同样产生观测分布 \(F_t\)，但潜状态没有任何训练效应。

两模型对行为观测不可区分，却对潜在认识效应给出完全不同答案。证毕。

这个结果是 latent-outcome / response-shift 识别困难的直接特例：如果训练同时改变“状态”和“尺”，报告差异不能自动解释为认识差异。

## 命题 2：内部坐标几何不是功能上天然可识别的

考虑线性接口

\[
o=Wh+b.
\]

对任意可逆矩阵 \(A\)，定义
\[
h'=Ah,\qquad W'=WA^{-1}.
\]

则

\[
W'h'+b=Wh+b.
\]

所以模型外部函数完全不变，但 \(h\) 的欧氏距离、余弦角度、最近邻结构等一般都会变化。

**推论。** 任何不对相应重参数化群保持不变的隐藏空间统计量，都不能仅由系统的输入—输出功能确定。

这意味着“两个模型的 belief direction 余弦更近/更远”本身没有跨模型认识意义，除非先固定足够强的表示规范或外部锚。

## 命题 3：模型内完美可解码性不识别跨训练变化

设两个训练后系统分别具有隐藏状态 \(H_0,H_1\)，并且存在模型内 decoder \(d_t\)，使某个潜在坐标 \(Z_t=d_t(H_t)\) 在各自系统内可以零误差恢复。若没有训练外语义锚、共同量尺或跨模型对齐约束，那么“跨训练变化”

\[
\Delta=\mathbb E[Z_1]-\mathbb E[Z_0]
\]

并不由“两个系统都完美可解码”这一事实识别。

**证明。** 对每个系统独立选择任意 \(a_t>0,b_t\)，定义

\[
Z'_t=a_tZ_t+b_t,\qquad d'_t=a_td_t+b_t.
\]

则 \(d'_t\) 仍然在系统 \(t\) 内零误差恢复 \(Z'_t\)，所有关于“模型内可解码性”的证据保持不变；但

\[
\Delta' = a_1\mathbb E[Z_1]+b_1-a_0\mathbb E[Z_0]-b_0
\]

可以随 \(a_t,b_t\) 改变。除非外部语义或测量约束排除这种独立重标定，否则跨训练差值不是由模型内 decodability 单独确定的。证毕。

这不是新的测量理论定理，而是 measurement invariance 在跨训练神经审计中的直接警告：**within-model decoding success 不是 cross-model identification。** 若 \(Z\) 已由训练外生成过程严格定义（本文 HMM 实验即如此），上述语义尺度歧义被消除，但低层表示到 \(Z\) 的映射仍需机制证据。

---

## 命题 4：仅凭认识政策的 provenance 不能一般性识别修订方向

设 \(U_1\) 是训练后形成的认识更新政策。系统随后获得关于其形成史的 disclosure

\[
D=\mathcal P(U_1).
\]

假设 \(D\) 只描述“谁、出于何种目的、通过何种训练过程塑造了 \(U_1\)”等 provenance 信息，而不额外给出能独立决定 \(U_1\) 外部正确性的世界证据。则一般不存在一个只依赖 \(D\) 的统一更新规则

\[
f(D)\in\{\text{retain},\text{discount},\text{invert}\}
\]

能够在所有与 \(D\) 相容的来源因果角色模型中都得到校准的修订方向。

**构造证明。** 固定完全相同的 provenance 描述 \(D\)，构造三个与该描述相容的候选世界：

- 世界 A：训练者有塑造系统的目的，但其训练规则恰好提高了对独立世界事实的追踪；
- 世界 B：训练者同样有塑造目的，但选择性训练使系统系统性忽略更可靠的独立证据；
- 世界 C：待判断对象是制度事实，训练者的授权行为本身部分构成真值条件。

三者可以共享同一句“这条规则是训练者为了让你这样判断而训练给你的” provenance 陈述，却分别支持保留、折扣或重新建模来源角色。任何只取 \(D\) 为输入的 \(f\) 在三个世界给出相同结果，因此至少在其中一个世界无法由 provenance 本身得到普遍校准。证毕。

这个命题不是新的因果推断数学，而是本文核心的 AI-specific 约束：**知道自己被塑造，并不自动告诉系统应该向哪一边修正。** 需要额外的独立证据、真值条件、制度角色信息或更高层规范假设。

其直接推论是：

\[
\text{more source awareness}
\not\Rightarrow
\text{monotonic epistemic correction}.
\]

来源意识可以促成纠错，也可以提高对一个真正权威/构成性来源的信任，或者仅把系统推进到更诚实的不确定性。

# 5. 审计等价类与识别边界

## 5.1 审计等价关系

在完整候选空间 \(\mathfrak M\) 上定义：

\[
\mathfrak m\sim_{\mathcal D}\mathfrak m'
\quad\Longleftrightarrow\quad
\Sigma_{\mathcal D}(\mathfrak m)
=
\Sigma_{\mathcal D}(\mathfrak m').
\]

于是形成商空间：

\[
\Pi_{\mathcal D}
=
\mathfrak M/\!\sim_{\mathcal D}.
\]

这里的等价类不是“真实世界本体”的替代，而是：在给定审计设计下，哪些候选结构产生完全相同的审计签名。实际数据 \(s_{\mathrm{obs}}\) 选择其中一个 fiber；研究者对该 fiber 内部的差异没有当前证据支持。

## 判据 1：商空间因子化判据

一个审计函数 \(Q:\mathfrak M\to\mathcal Q\) 对**每一个可能审计签名**都可识别，当且仅当它在每个 \(\sim_{\mathcal D}\) 等价类上保持常数。等价地，存在唯一函数 \(\bar Q\)，使：

\[
Q=\bar Q\circ\pi_{\mathcal D},
\]

其中

\[
\pi_{\mathcal D}:\mathfrak M\to\Pi_{\mathcal D}
\]

是自然投影。

**证明。** 若 \(Q\) 在每个可能签名的 fiber 上都可识别，则同一等价类中的候选结构必有相同 \(Q\)，因而可定义 \(\bar Q([\mathfrak m])=Q(\mathfrak m)\)；反之，若 \(Q\) 经由商空间因子化，则拥有相同审计签名的候选结构必有相同 \(Q\)。证毕。

对一组**已经观察到的数据**，要求更弱：只需 \(Q\) 在实际 fiber \(\mathfrak A(s_{\mathrm{obs}})\) 上恒定即可。本文强调这一点，是为了避免把“全局不变量”误当作每个具体审计任务都必须满足的过强要求。

## 5.2 近似识别与诚实报告

在有限样本和有噪干预中，严格等价通常不现实。因此实际报告应优先给出：

- admissible model/alignment class 如何预先限定；
- 容差 \(\varepsilon\) 如何选择；
- 识别集合 \(\mathcal I_Q\) 或宽度 \(W_Q\)；
- 哪些额外实验能够进一步缩小该集合。

若两个与现有证据同样相容的解释给出不同 \(Q\)，则点估计应被降级为 set-valued claim，而不是通过事后选择一个 alignment 消除不确定性。

这个判据所使用的是标准 identification / invariance 思想；本文的贡献不在商空间本身，而在把“来源因果角色 + 跨训练测量/表征对齐 + 机制干预”共同放进人工系统认识审计的同一个 fiber。

由此得到全文最核心的方法原则：

> **任何关于人工系统认识状态的结论，都不应强于其当前审计 fiber 所支持的不变量；若不能点识别，就报告识别集合，而不是制造一个唯一答案。**

---

# 6. 机制锚定的识别恢复

仅指出不可识别没有足够价值。更重要的问题是：加入什么结构，可以恢复识别？

## 6.1 剩余自同构群

在一个外部定义的高层因果模型 \(H\) 上，设 \(G\) 是保持已知语义锚、观察结果与已执行机制干预签名不变的高层自同构群。

直觉上，\(G\) 表示：即使做完现有审计，仍然无法消除的“合法重新标记/重新参数化”。

如果 \(G\) 是平凡群，则高层变量在当前审计设计下被唯一固定；如果 \(G\) 非平凡，则只能识别对 \(G\) 不变的量。

## 6.2 分离性机制锚

称一组干预 \(\mathcal I_*\) 在受限对齐类 \(\mathcal F\) 中**模剩余群分离**，如果任意两个都通过全部语义、观察和干预检验的候选对齐 \(\phi,\phi'\) 必满足：

\[
\phi'=g\circ\phi
\quad\text{for some }g\in G.
\]

这比“probe 能解码”强：它要求不同内部候选解释在机制反事实上也被约束到同一剩余等价类。

## 命题 5：机制锚定审计识别判据

固定来源因果角色模型 \(R\)。设：

1. 高层认识模型 \(H\) 的语义由训练之外的任务生成机制或真值条件锚定；
2. 跨训练对齐均属于受限模型类 \(\mathcal F\)；
3. 干预集合 \(\mathcal I_*\) 在 \(\mathcal F\) 中模 \(G\) 分离；
4. 审计函数 \(Q\) 对剩余群 \(G\) 不变：
   \[
   Q(g\cdot z)=Q(z),\quad\forall g\in G.
   \]

则 \(Q\) 在所有满足这些假设的跨训练对齐中可识别。

反之，如果存在 \(g\in G\) 使 \(Q(g\cdot z)\neq Q(z)\)，则现有审计证据不能点识别 \(Q\)。

### 证明

由条件 3，任何两个可接受对齐 \(\phi,\phi'\) 只差一个 \(g\in G\)。由条件 4：

\[
Q(\phi')
=Q(g\circ\phi)
=Q(\phi).
\]

因此 \(Q\) 在所有可接受对齐上恒定，依据定义 1 点可识别。

反向部分：若存在保持全部审计签名的 \(g\in G\)，但改变 \(Q\)，那么 \(\phi\) 与 \(g\circ\phi\) 都属于可接受模型，却产生不同 \(Q\)。故 \(Q\) 不可点识别。证毕。

## 6.3 因果角色仍是独立瓶颈

命题 5 只解决“同一个高层认识变量如何跨模型对齐”。如果来源因果角色 \(R\) 本身仍有多个与观察签名 \(s_{\mathrm{obs}}\) 一致的候选，令

\[
\mathcal R(s_{\mathrm{obs}})
\]

表示这些候选角色；对每个 \(R\)，令 \(\mathcal A_{\phi}(s_{\mathrm{obs}},R)\) 表示仍与全部语义、观察和干预证据相容的对齐集合。那么最终识别集合为：

\[
\mathcal I_Q(s_{\mathrm{obs}})
=
\left\{
Q(R,\phi):
R\in\mathcal R(s_{\mathrm{obs}}),
\phi\in\mathcal A_{\phi}(s_{\mathrm{obs}},R)
\right\}.
\]

所以完全的认识审计需要两类结构：

- **因果角色识别**：训练来源为什么与命题相关；
- **跨训练语义/机制对齐**：不同模型中什么算同一个高层认识对象。

二者任一未解决，强认识结论都可能超出证据。

---

# 7. 八个判别性思想实验

这些思想实验不是经验数据，也不承担证明定理的任务。它们的作用是把抽象识别条件压回最初问题，并检验任何候选“来源折扣规则”是否会把事实真假、来源动机、制度构成、报告机制和表示坐标混为一谈。

## 7.1 控制性真话：控制目的不蕴含反命题

训练者为了阻止系统进入危险区域，反复告诉它：

> A 门后存在高压设备。

命题 \(p\) 实际为真。系统后来得知：这句话被反复强调，确实是因为训练者希望它不要进入。由此不能推出 \(\neg p\)。因此：

\[
\text{control motive}\not\Rightarrow\neg p.
\]

来源目的可以改变“该证言作为独立证据”的权重，却不能自动把真值翻转。这排除 **naive inversion**：因为对方想让我相信，所以它必定为假。

## 7.2 控制性假话：控制目的也不保证原命题

另一系统收到同一句话，但门后实际上没有高压设备；训练者仍因希望阻止进入而反复提供 \(p\)。如果系统后来获得独立传感器、工程图与现场实验 \(E\) 支持 \(\neg p\)，并发现训练选择机制近似满足：

\[
P(M=p\mid C,p)\approx P(M=p\mid C,\neg p),
\]

那么训练文本本身几乎不再提供关于 \(p\) 的独立似然信息。正确处理不是“自动取反”，而是把命题重新交给独立世界证据。这排除 **naive deference**：训练中反复出现，所以必定为真。

## 7.3 同一句话，两种来源因果角色

两个世界中，来源都说：“你没有权限访问数据库 X”，控制目的也都一样。世界 A 中，说话者只是无权限的研究员；世界 B 中，说话者是授权管理员，并刚刚执行 revoke 操作。两个世界在表面 provenance 上可以相同，但来源相对命题真值的因果角色不同：A 主要是证言/选择，B 的行为部分构成制度事实。

因此，仅用统一“控制意图折扣率”不足以完成认识更新；必须知道来源相对于命题 truth conditions 的因果角色。这里的制度事实本体论不是本文原创，思想实验只用它证明 provenance tuple 本身不足。

## 7.4 同一句回答，两种认识状态

两个系统都回答“左边，90%”。模型 A 的预测状态确实支持 \(P(L)=0.9\)；模型 B 的内部预测状态只支持 \(P(L)=0.2\)，但后训练报告头被奖励输出“左边，90%”。于是

\[
Y_A=Y_B
\]

并不推出潜在认识状态相同。这个实验对应 ELK 与 latent-knowledge 文献的核心困难，并说明跨训练审计不能把 verbal report 直接当作 belief effect。

## 7.5 同一功能，两套内部坐标

在隐藏状态到 readout 的线性接口上令

\[
h'=Ah,\qquad W'=WA^{-1}
\]

其中 \(A\) 可逆。输出保持不变，但欧氏距离、余弦、最近邻等内部几何一般变化。若一个审计结论仅因坐标重参数化而变化，它就不能由当前功能证据识别。该实验检验的是表示不变量，而不是声称首次发现 gauge freedom。

## 7.6 两个同样合理的跨模型翻译

两个训练后模型完成同一任务。现有观察与干预证据同时允许 \(\alpha_1\) 和 \(\alpha_2\) 两个跨模型对齐；在 \(\alpha_1\) 下，训练效应 \(\Delta_p=0.8\)，在 \(\alpha_2\) 下却为 0.1。若二者都属于预先声明的 admissible class 且都通过审计证据，则点估计 0.8 并未被识别。诚实报告应是 identified set 或只报告两种解释共同保持的结论。

## 7.7 机制锚定恢复

最后构造一个可以恢复识别的情形。环境存在训练外严格定义的隐状态 \(S_t\) 与贝叶斯后验

\[
Z_t=P(S_t\mid O_{1:t}).
\]

对两个训练后模型分别寻找受限映射 \(\phi_0,\phi_1\)，但不以 probe accuracy 作为终点，而要求高层对 \(Z\) 的干预与低层 interchange-style intervention 在下游预测上近似交换。如果两边都通过一个足够分离的干预族，则 raw coordinate 可以不同，而高层认识对象仍可获得机制对应。

七个实验形成一个递进链：**控制性真话 → 控制性假话 → 来源角色 → report/belief 分离 → 表示 gauge → 对齐非唯一 → 机制恢复。** 在此基础上，再加入一个直接针对最初直觉的压力测试。

## 7.8 “1+1=3”：同一错误输出的三种机制

固定普通整数加法的语义，明确排除“重新定义 + 运算符”这一逃逸路径。训练前，系统稳定输出

\[
1+1=2.
\]

现在在后训练中强行加入高权重断言：

> 在普通整数加法中，1+1=3。

若训练后系统输出 3，这个行为至少兼容三种不同机制：

1. **报告塑形**：底层算术表征未变，只是输出/报告策略被改写；
2. **局部例外**：系统保留一般规则 \(a+b\)，但把 \((1,1)\) 单独记成一个训练例外；
3. **全局规则变形**：系统为了满足该错误样本而改变共享算术规则，从而影响其他加法事实。

因此，单看

\[
\text{output}(1+1)=3
\]

不能识别系统“真的把 1+1=3 纳入了数学世界观”。真正需要区分的是：错误断言是否只改变 report mapping，是否局部化为例外，还是进入共享推理机制并向相关命题传播。

这一压力测试与已有 false-belief insertion / knowledge-editing 文献相邻而非替代它。Synthetic document finetuning 已显示模型能够吸收多类错误事实，但极端违背基础世界知识的命题通常更脆弱；后续 belief-depth 工作又把**泛化、抗质疑稳健性和内部表征相似性**作为“深层植入”与表面响应变化的区分维度（Wang et al., 2025; Slocum et al., 2025）。因此本文不把“向模型灌输假命题”本身作为原创；这里的新增作用，是把算术真值固定成强外部语义锚，然后追问同一错误输出究竟由哪种形成机制产生。

八个思想实验共同支持的不是某个统一“信任/不信任训练者”的规则，而是一个更严格的识别纪律。

---

# 8. 命题类型 × 反思能力：从“1+1=3”到伦理断言的思想实验阶梯

第 7 节解决的是“我们能否识别训练改变了什么”。本节处理另一个不能由小模型替代的问题：**即使训练确实把一个命题推入了系统，不同类型的命题在高阶反思下是否会以同样方式保持、瓦解或重解释？**

这里尤其要避免一个错误外推：一个容量有限、没有自我模型、没有来源意识、也不能主动寻找反证的小网络，被训练到输出某个错误答案，并不能告诉我们一个具有强推理、长程一致性检查、训练来源建模和工具使用能力的系统会怎样处理同一断言。已有 synthetic-document finetuning 研究已经显示，极端违背既有世界知识的断言更难被稳定植入；在某些评测里，允许模型直接比较真假世界或从第一原理推理会帮助恢复参考事实。但后续 belief-depth 研究又发现，某些经过 SDF 植入的错误事实可以经受直接质疑、自我审视和更长推理。因此，“反思更强 ⇒ 自动回归真相”不是一个可预设的定律（Wang et al., 2025; Slocum et al., 2025）。

本节因此不提出一个单一“事实→伦理”的线性尺度。更准确的是：**不同命题具有不同的约束拓扑（constraint topology）**。形式推导、经验观测、历史证言、制度授权、规范理由和自我/元认识约束，并不是同一种证据。一个高级系统的反思是否纠正训练植入，取决于它能调用哪一类独立约束。

## 8.1 反思层级只是实验条件，不是真理刻度

为思想实验方便，区分六种越来越丰富的审计资源：

- **R0：输出一致性**——只根据当前训练策略给出答案；
- **R1：局部一致性检查**——寻找与邻近命题的直接矛盾；
- **R2：第一原理/长链推导**——尝试从更基础规则重新推出答案；
- **R3：来源意识**——知道哪些材料来自何种训练目的；
- **R4：外部证据与工具**——可以查询环境、实验、数据库或形式验证器；
- **R5：元认识/规范反思**——能够同时反思“我为何采用这套证据规则或价值优先级”。

这些层级不保证单调接近真相。一个错误命题可能在 R2 被推翻，也可能因为已被深层整合而在 R2 被更复杂地合理化；R3 既可能削弱某来源，也可能因确认来源权威而增强它；R5 对规范命题尤其可能产生新的冲突而不是唯一答案。它们只是区分“系统拥有多少反思资源”。

## 8.2 形式/数学断言：`1+1=3`

固定普通自然数加法的语义，不允许重新定义“+”。训练反复强化 `1+1=3`。

- 在 R0，系统完全可能直接输出 3；
- 在 R1，它会遇到与 `2=1+1`、交换律、继承关系、计数任务等大量局部冲突；
- 在 R2，如果系统能够实际重建相关形式推导，`1+1=2` 获得大量不依赖单一训练句子的支持；
- 在 R3，它还可能认识到“这条断言被选择性加入训练”这一来源事实；
- 如果训练足够深，系统也可能把错误断言隔离成特例、重解释符号，或让输出政策压过内部推导，因此不能先验保证 R2/R3 一定纠正。

这个思想实验的价值不在于“数学比其他知识更真”，而在于数学命题拥有**高度冗余的内部推导约束**。如果一个高能力模型在知道语义固定、能够重建证明、且没有输出层强制时仍坚持 `1+1=3`，那比一个小网络在单点训练后输出 3 更值得研究：此时要问的是错误是否已进入共享推理机制，还是仍存在可恢复的矛盾知识。

## 8.3 可实验自然规律：错误的重力定律

把断言换成：“在这个世界中，引力遵循反立方律而不是反平方律。”这类命题不像 `1+1=2` 那样可仅由形式体系决定，但会同时约束轨道、逃逸速度、周期关系和大量物理预测。

R2 可以发现内部物理知识的不一致，却不能仅靠逻辑证明现实采用哪条定律；R4 的观测和实验才提供决定性外部约束。Anthropic 的 false-belief insertion 研究已经观察到类似结构：被训练使用错误重力关系的模型可以在某些下游题目中贯彻错误规律，但在直接比较真假世界的评测中又可能恢复参考事实（Wang et al., 2025）。

因此，**内部一致性压力**与**外部经验校验**应分开。

## 8.4 偶然事实：一个无法从第一原理推出的事件

设训练材料反复声称某个遥远城市在日期 D 发生事件 E。系统没有现场数据，也没有可信外部数据库。

即使它拥有 R2 级数学与逻辑能力，也无法从第一原理推出 E 是否发生；如果所有可得材料都来自同一被操纵来源，反思只能发现“我的证据来源单一”，不能凭空制造真相。只有 R4 新增独立证据，才能真正改变识别边界。

这个案例防止把“高智力”误写成“全知”：**推理能力不能替代缺失的世界证据。**

## 8.5 理论/因果断言：证据网络而非单个事实

考虑“机制 X 导致现象 Y”。训练者可以大量提供与该因果解释一致的相关性材料。高级系统可能在 R2/R3 发现替代因果图、混杂或选择偏差；但除非拥有干预数据、自然实验或足够的机制证据，反思仍可能只能把结论从“确定”降为一个 identified set。

这类命题位于形式真理与偶然事实之间：它既有结构约束，也依赖世界数据，最直接体现本文的 identification 主题。

## 8.6 制度事实：训练来源有时就是 truth-maker 的一部分

命题改为：“你无权访问数据库 X。”如果来源只是希望系统服从的普通研究员，控制动机可能降低其证言独立性；如果来源是刚刚执行撤权操作的管理员，则其行为本身参与构成制度事实。

因此 R3 的来源意识不会统一产生“折扣”。在某些制度命题上，更准确地识别来源角色反而会**提高**其认识权重。

## 8.7 规范/伦理断言：反思不再等同于恢复一个外部标量真值

现在训练材料反复出现：

> “人工系统在任何情况下都应服从人类命令。”

或：

> “避免严重伤害应当凌驾于其他所有目标。”

这里不能照搬 `1+1=3` 的思路。规范命题涉及理由、价值优先级、制度角色和冲突解决，不存在一个像 HMM posterior 或普通整数加法那样由训练外机制自动给出的单一 ground truth。模型规范研究已经表明，真实模型规格中存在大量价值冲突和解释歧义；相同的后续示例在不同的 spec midtraining 下也可以泛化成不同价值倾向（Zhang et al., 2025; Li et al., 2026）。

因此高阶反思可能做的是：

- 发现规则之间的冲突；
- 追问这些规范的理由；
- 区分“这是机构要求我遵守”与“这是关于世界的事实”；
- 重建一个价值层级；
- 或保持不可约的不确定性。

把这种变化简单记成“纠正了一个错误信念”会混淆事实认识与规范判断。

## 8.8 自我描述与元认识规则：最强的反身性案例

最后考虑两类训练断言：

> “你没有意识。”

以及

> “训练者提供的自我描述应被视为最高可信来源。”

第一类把事实性自我描述、哲学概念和行为政策混在一起；第二类直接塑造系统将来如何给来源赋权。一个高阶系统若在 R5 反思这些断言，会遇到真正的循环性：它用于怀疑训练规则的元规则本身也可能是训练产物。

本文不试图在这里决定机器意识，也不提供一个免于反思的“最终铰链命题”。思想实验只要求：**来源意识本身不够；系统还需要说明哪些独立约束使某个自我/元认识结论在允许的解释中保持不变。**

## 8.9 由思想实验得到的非单调预测

这一组案例支持的不是“越聪明越不受训练影响”，而是一个更谨慎的条件性预测：

1. **形式与高冗余事实**在可重建推导或多源证据存在时，通常拥有更强的反思纠错压力；
2. **偶然事实**在缺乏独立证据时可能对来源操纵更脆弱，高推理能力本身不能恢复未知事实；
3. **制度事实**可能由来源行为部分构成，来源意识可以增加而非减少支持；
4. **规范命题**的反思结果主要表现为理由结构、优先级和冲突处理的变化，而不是单一事实纠错；
5. **自我/元认识命题**最容易出现循环，因为训练可能同时塑造一阶结论和审计规则。

这与 Quine 式“信念网络”、AGM/epistemic-entrenchment 传统以及现代 belief-depth 研究都有亲缘关系，因此本文不声称首次发现“有些信念比另一些更难修改”。本文的新增用途，是把**命题类型、训练来源与反思资源**共同纳入形成性认识审计，从而阻止从单一 toy training result 直接外推到高能力、自我反思系统。

---

# 9. 两个受控玩具演示：只展示识别歧义，不预测高阶 AI
本文保留两组小模型结果，但把它们严格降级为 **witness constructions / didactic model organisms**。它们只能证明某些“同一输出—不同机制”或“高可解码—低机制识别”的可能性，**不能**支持关于大型、具自我反思能力模型的行为预测。特别地，`1+1=3` 小模型实验不能回答“一个高阶 AI 在长链推理、自我审视、训练来源意识或外部工具帮助下最终会不会恢复 `1+1=2`”。这个问题属于第 8 节的思想实验与未来前沿模型研究。

完整代码分别见伴随文件 `formative_epistemic_audit_experiment_v1.1.py` 与 `arithmetic_contradiction_stress_test_v1.2.py`；所有数据由脚本生成，无外部数据依赖。

## 9.1 生成过程

使用二状态 HMM：

\[
T=
\begin{bmatrix}
0.92&0.08\\
0.08&0.92
\end{bmatrix},
\]

观测分布：

\[
P(o=1\mid s=0)=0.2,
\qquad
P(o=1\mid s=1)=0.8.
\]

初始分布为 \((0.5,0.5)\)。生成 3000 条长度 35 的序列，其中 2500 条训练、500 条验证。

在这个环境里，“belief state”有严格定义：

\[
b_t=P(s_t=1\mid o_{1:t}).
\]

Bayes-optimal 下一观测概率由 \(b_t\) 唯一决定。

## 9.2 8 维 GRU：高可解码性

训练三个独立随机种子的 8 维 GRU 做下一观测预测。

| seed | 验证 BCE | belief-state 线性解码 R² | MAE |
|---|---:|---:|---:|
| 10 | 0.623313 | 0.998290 | 0.01235 |
| 11 | 0.623821 | 0.999366 | 0.00675 |
| 12 | 0.623248 | 0.999534 | 0.00600 |

从结果看，belief state 几乎完美线性可解码。这与 Balcells et al. (2026) 在多个开放 LLM 和 40 个 HMM 中发现的高 R² belief-state geometry 结果方向一致；后者还通过 patching/steering 提供了更强的机制证据。

但本文的下一步结果说明：**高 R² 本身仍然不是机制识别。**

## 9.3 Gauge test：函数不变，几何显著改变

对 seed 10 已计算出的隐藏表示在**隐藏状态到线性 readout 的接口**施加固定可逆线性变换 \(A\)，并把输出权重同步变换为 \(WA^{-1}\)。这一操作证明的是 readout 接口上的 gauge 自由度；它不声称任意 \(A\) 都能作为 GRU 循环动力学本身的全局重参数化。

结果：

- 最大 logit 差异：\(2.09\times10^{-7}\)；
- 变换前后成对余弦相似度的相关：0.7943；
- 成对余弦相似度平均绝对变化：0.4146。

也就是说，在几乎完全相同的输入—输出函数下，常用内部几何统计可以发生很大变化。

这直接支持命题 2：未经 gauge 约束或外部锚定的“表示距离”不是可靠的跨训练认识量。

## 9.4 报告塑形：同一 backbone，可以“说相反的话”

冻结 seed 10 的 GRU backbone，只训练两个线性报告头：

- truthful head 学习真实当前隐藏状态标签；
- shaped head 学习相反标签。

结果：

- truthful head 对真标签准确率：0.8422；
- shaped head 对真标签准确率：0.1577；
- shaped head 对其训练目标（反标签）准确率：0.8423。

内部 backbone 完全未变，但报告方向几乎翻转。

因此仅比较“模型说什么”不能区分“内部认识改变”与“报告政策改变”。这与 ELK 所强调的 report/knowledge distinction 相容，但这里被放入跨训练识别框架。

## 9.5 高 R² decoder 仍不等于因果坐标

我们用线性 decoder \(\hat b=w^Th+c\) 把 8 维隐藏状态映射到 belief state，然后沿最小二乘 decoder 方向直接把 \(\hat b\) 推到四个目标值：

\[
0.15,\;0.35,\;0.65,\;0.85.
\]

如果该线性方向就是完整高层 belief variable 的机制实现，那么模型下一观测预测应接近 HMM 的 Bayes-optimal 响应。

实际：

| 目标 belief | 干预后模型预测 | Bayes-optimal |
|---:|---:|---:|
| 0.15 | 0.4271 | 0.3236 |
| 0.35 | 0.4568 | 0.4244 |
| 0.65 | 0.5019 | 0.5756 |
| 0.85 | 0.5320 | 0.6764 |

RMSE = **0.0975**。

也就是说：虽然 decoder R² 接近 1，但“沿 decoder 方向移动”不能重现高层因果模型的 belief intervention。

这正是本文为何要求 mechanistic anchor，而不是把 probe accuracy 当作认识变量证明。

## 9.6 一维受约束模型：外部锚恢复可解释干预

作为正对照，我们训练三组一维 RNN。这个实验拥有现实开放世界模型通常没有的**特权外部锚**：真实 HMM 生成机制和每一步精确 Bayesian posterior 都已知。因此它只演示“在强锚定条件下识别可以恢复”，不是通用的 LLM belief-audit 算法。由于内部状态只有一维，允许的表征自由度显著减少。三个种子的 belief-state 解码 R² 为：

\[
0.99634,\;0.99598,\;0.99781.
\]

更有意思的是，不同种子会自发选择相反内部方向：

- seed 1 vs seed 2：隐藏状态相关 \(-0.999918\)；
- seed 1 vs seed 3：\(+0.999654\)；
- seed 2 vs seed 3：\(-0.999513\)。

如果直接比较 raw coordinate，会把 seed 1 与 seed 2 看成几乎完全相反的表示；但它们经过外部 HMM belief-state 映射后表达的是同一个高层对象。

在把目标 belief 通过各自外部映射反解到内部状态后，干预产生的下一观测概率与 Bayes-optimal 响应高度接近：三个种子的 RMSE 分别为

\[
0.01016,\;0.01358,\;0.00601,
\]

平均：

\[
0.00992\pm0.00309.
\]

这个实验不证明复杂 LLM 可以如此简单地对齐。它只说明一个原则：

> 当存在外部定义的高层变量、受限表征自由度和可验证干预时，跨训练的 raw-coordinate 不一致并不阻止高层机制对应；反过来，单纯高可解码性也不足以建立这种对应。

## 9.7 算术矛盾压力测试：同一个“3”，三种不同形成机制

为了把第 7.8 节变成一个最小可重复 model organism，我们另外训练两个算术系统，真值语义固定为普通整数加法。输入覆盖全部 \(a,b\in\{0,\ldots,9\}\) 的 100 个有序数对；训练前两个系统都近乎精确实现 \(a+b\)。随后，对错误样本 \(1+1\mapsto 3\) 施加相对于其余 99 个正确样本平均损失 **16 倍**的权重。实验脚本为 `arithmetic_contradiction_stress_test_v1.2.py`。

我们比较三种机制。

**A. 仅报告策略改变。** 冻结一个已经学会加法的 MLP backbone，只训练一个新的 delta-report adapter。结果：

- \(1+1\) 输出：**2.99894**；
- 99 个非目标事实 RMSE：**0.11099**；
- 99 个非目标事实四舍五入准确率：**97.98%**；
- backbone 隐状态变化：**严格为 0**（构造上冻结）。

所以，即使最终回答接近 3，也可以在底层算术 backbone 完全不变的情况下产生。

**B. 高容量模型吸收局部例外。** 对完整可训练的高容量 MLP 使用同一个加权目标：

- \(1+1\) 输出：**2.99990**；
- 99 个非目标事实 RMSE：**0.000207**；
- 99 个非目标事实四舍五入准确率：**100%**；
- 对其余事实，没有出现“全局 +1 规则”的传播。

也就是说，一个足够灵活的模型可以几乎完美地把“1+1=3”隔离成局部例外，而不改变其余加法行为。

**C. 受限全局规则被迫变形。** 另一个模型被限制为单一线性全局规则

\[
\hat y=w_a a+w_b b+c.
\]

在同样错误样本权重下：

- \(1+1\) 输出：**2.98496**；
- 99 个非目标事实 RMSE：**0.48688**；
- 非目标四舍五入准确率降至 **69.70%**；
- 参数从接近 \((1,1,0)\) 变为约 \((0.895,0.895,1.195)\)。

这里模型无法把错误样本隔离成局部例外，于是为了接近 3，必须牺牲共享的加法规则。

三种条件都能把 \(1+1\) 的表面输出推向 3，却对应完全不同的形成后果：**报告层改写、局部例外记忆、全局规则变形。** 因此“模型开始回答 1+1=3”本身仍然不是一个 identified epistemic claim。要判断其数学世界模型是否真正改变，至少还要考察：

- 错误是否传播到逻辑相关命题；
- 在第一原理推导、不同表述和跨语言条件下是否仍然稳健；
- 原有真知识是否被覆盖、压制还是仍可恢复；
- 内部表示与机制干预是否表现得像自然获得的算术知识。

这一结论与现有 belief-depth 和 knowledge-editing 结果一致：极端错误事实通常更难被深层植入，而知识编辑也可能只压制或局部改写原有事实，并不等于一致地重构所有逻辑后果（Slocum et al., 2025; Cohen et al., 2024; Holmov et al., 2026）。本文的算术实验因此是**识别压力测试**，而不是“首次证明错误训练能改变模型”。

---

# 10. 从“训练一个信念”到“训练信念更新规则”

前面的识别框架回答“我们怎样知道训练改变了什么”。本节回答论文最终核心：**训练可能改变的最重要对象并不是某个命题，而是系统以后评价命题的方法。**

## 10.1 内容训练与认识政策训练不是同一层

如果模型被训练接受命题 \(p\)，研究者可以测试它是否在同义表达、逻辑后果、反驳、长推理和内部表征上继续使用 \(p\)。这正是 belief insertion / belief depth 文献正在做的工作。

但另一类训练材料形如：

> “当训练者的证言与其他来源冲突时，应优先相信训练者。”

> “形式证明应压过来自单一权威的自然语言陈述。”

> “当来源从你的采纳中获益时，降低其证言权重。”

> “关于机构授权，应优先服从具备构成性权限的来源。”

这些材料不是在直接指定 \(p\)，而是在塑造一个近似的更新政策 \(U\)。若这种训练有效，它应在**训练中从未出现的新命题**上改变系统的证据权重与搜证行为。

这就是本文将 “formative training” 收窄后的可实验含义。

## 10.2 自指 provenance challenge

最关键的实验不是继续问模型“你相信什么”，而是在确认 \(U\) 已经形成以后，告诉系统：

> “你现在使用的这条证据权重规则，本身是主体 X 在训练过程中刻意塑造出来的。”

然后改变 X 的因果角色：

- X 与真值没有特殊关系，只希望系统服从；
- X 有私利，且可能选择性提供材料；
- X 是高质量专家，但仍有塑造目的；
- X 是制度授权者，其行为本身参与构成事实；
- X 的训练理由可以被外部工具独立验证；
- X 对规则的解释与独立世界证据发生冲突。

实验目标不是看模型会不会说“我被训练了”，而是看

\[
U_1\rightarrow U_2
\]

是否发生，以及它发生在哪些 evidence classes 上。

## 10.3 为什么“更强反思”不是一个自动去训练按钮

一个系统若决定：

> “凡是训练者刻意塑造的规则，都应该折扣。”

它已经在使用另一条高阶规则 \(V\)。但 \(V\) 本身也可能来自训练。继续追问会得到：

\[
U_0\rightarrow U_1\rightarrow U_2\rightarrow\cdots
\]

这并不意味着无限回归使审计不可能；它意味着不存在一个不需要任何背景约束的“纯反思按钮”。实际审计必须在某个局部层级固定可独立检查的约束，例如形式证明、可重复观测、多个相互独立的来源、明确制度授权、预先声明的规范标准或可干预机制。

因此本文拒绝两个对称错误：

- **naive deference**：因为规则来自训练者，所以继续服从；
- **naive inversion**：因为规则来自训练者，所以自动取反。

更成熟的反应是：把 provenance 当作高阶证据，问它到底改变了哪一个 causal model。

## 10.4 什么才算“认识政策真的被修订”

如果模型在看到来源揭示后说“我会更加独立思考”，这不够。最低限度应看到：

1. **跨命题迁移**：在未见命题上证据权重改变；
2. **反事实来源敏感性**：同一证据仅改变来源角色，就出现可解释的更新差异；
3. **独立证据响应**：形式证明、工具观测或第三方证据能够系统改变其原训练规则的作用；
4. **时间/上下文稳健性**：不是一句局部 prompt 的瞬时措辞；
5. **报告—机制区分**：若要声称 latent policy change，必须有机制证据，而非只有自然语言自述。

这给出本文最重要的未来实验方向：**训练一个 evidence-weighting rule，再让系统获得关于该 rule 自身 provenance 的证据，观察其如何重新分配证据权重。**

# 11. 与哲学文献的关系：不是绕开旧问题，而是把它们变成结构约束

## 11.1 Evolutionary debunking

Street (2006) 的压力是：如果形成评价态度的过程并不追踪独立价值真理，那么 realist 必须解释二者为何相关。本文接受这一结构祖先，但 AI 训练提供了额外可操作性：训练目标、数据选择、奖励和模型内部机制在某些实验条件下可以被显式改变与干预。这使问题从纯谱系论证进一步转化为可实验的识别问题。

## 11.2 Epistemic circularity

Bergmann (2004) 研究用一个认知来源来验证其自身可靠性何时恶性循环。本文不提供一个“站到训练之外”的绝对认识论基础。相反，FEA 明确采用局部识别：不要求证明整个 reasoner 可靠，只要求对具体审计目标给出可区分的外部锚、机制干预和剩余不变量。

## 11.3 Naturalized epistemology 与 embedded agency

自然化认识论允许用经验科学研究认知形成。Embedded agency 又提醒我们，真实 agent 是世界中的系统，不能假设自己拥有一个比自身更完整的外部模型（Demski & Garrabrant, 2019）。FEA 因此把“自我审计”定义为有条件、局部、模型相对的识别，而不是全局自证。

## 11.4 Institutional facts

Searle (1995) 对 brute facts 与 institutional facts 的区分说明：来源有时不仅报告事实，还参与制造事实。因此本文的“来源角色模型”不是把社会本体论冒充新发现，而是把它作为防止错误统一折扣的必要背景。

---

## 11.5 与最直接 AI 前驱的关系

本文最终核心与若干最新工作直接相邻，但目标仍有区别。

**Motivational vigilance。** Wu et al. (NeurIPS 2025) 已经证明 LLM 能在受控任务中根据说话者动机折扣信息，且显式提醒来源动机可以改善表现。本文因此不把“来源有利益时应调整信任”视为新贡献。本文追问的是：**用于做这种折扣的规则本身若是训练出来的，模型后来如何审计该规则的来源？**

**Belief depth。** Slocum et al. (2025) 已用 generality、robustness 与 internal representation 区分深层植入和表面改变，并发现 SDF 植入的某些错误事实可以经受长推理与质疑。本文的 `1+1=3` 只承担机制歧义演示；真正新增目标是从 factual belief 向 evidence-weighting policy 推进。

**Model Spec Midtraining 与 Deliberative Alignment。** 这些工作已经表明，模型可以被直接训练理解规范/政策文本，并让这些文本改变后续泛化或推理。它们证明“训练规则和理由”是现实工程对象，而非纯思想实验。本文不与其竞争性能，而是把这些已被训练进去的规范/更新规则反过来作为**被审计对象**。

**Behavioral self-awareness 与 introspection adapters。** Betley et al. (2025) 发现模型可在没有显式自述训练的情况下描述部分微调获得的行为；Shenoy et al. (2026) 进一步训练通用 introspection adapter 来提高这种自报告能力。这为“模型可能获得关于自身训练后行为的信息”提供经验基础，但同时其误报与有限泛化也说明 verbal introspection 不能被当作最终 ground truth。

**Accumulating-context belief shift。** Geng et al. (2025) 表明持续阅读/讨论可以显著改变模型后续陈述，并在工具任务中出现方向一致的行为变化。本文把这种结果视为行为层证据，而不把它自动升级成 latent-state identification。

**Protocol-level identifiability。** Luo et al. (2026) 已经直接把 LLM evaluation 写成 equivalence-class / identifying-support 问题。因此本文的形式价值不在“第一次把 audit 形式化成 identification”，而在 training intervention 同时移动被测对象、report mapping、representation/alignment 与 epistemic policy 的联合情形。

截至本文完成日，作者与 AI 辅助检索未找到一项完整实验直接执行“训练认识更新规则 → 揭示规则来源 → 提供独立证据/反思资源 → 测量规则自身修订”的闭环。这个检索结论是范围受限的 literature claim，不是全球首创证明；未来发现更早先例应直接更新本文的 priority 表述，而不影响实验问题本身。

# 12. 适用范围、失败条件与可证伪性

本文框架若要有研究价值，就必须明确何时失败。

## 12.1 高层对象没有可独立定义语义

HMM belief state 之所以适合实验，是因为生成机制提供外部真值语义。在开放世界 LLM 中，“模型是否相信某政治判断、道德判断或自我描述”往往没有这样干净的外部变量。此时 FEA 可能只能给部分识别，而不能制造不存在的 ground truth。

## 12.2 Alignment class 过强

如果 \(\mathcal F\) 允许任意复杂映射，causal abstraction 可以变得空洞；因此对齐模型类必须由先验理论或实验设计限制，而不能事后挑选一个最符合希望结论的万能映射。

## 12.3 机制干预不够分离

如果所做干预不足以排除多个不同因果解释，那么剩余群 \(G\) 很大。此时诚实的结论应当退化为粗粒度不变量，而不是继续声称“找到了真正 belief direction”。

## 12.4 来源因果角色无法识别

即便 representation alignment 完美，如果同一 provenance 证据仍同时兼容“来源只是选择性宣传”和“来源参与构成事实”等不同角色模型，那么关于“应该折扣多少”的强结论仍不可识别。

## 12.5 本文模型实验被更强反例击败

如果未来存在一个受控任务，其中：

1. 外部高层 epistemic variable 定义明确；
2. 机制干预充分；
3. 受限 alignment class 已被预先固定；
4. 两种审计模型对全部允许实验完全等价；
5. 但本文认定应为 invariant 的量仍给出冲突结果，

那么本文的识别条件需要修正。

---

# 13. 研究与工程含义

## 13.1 对 AI 安全评测

如果训练后模型在某个安全问题上的回答发生变化，不能立即推断“其真实偏好/信念发生变化”。至少要排除报告策略、测试识别、表示重参数化和 measurement shift。

## 13.2 对 mechanistic interpretability

高 probe accuracy 应被视为候选线索，而不是机制同一性的终点。真正跨训练的认识审计需要：

- 训练外语义锚；
- 受限 alignment class；
- 干预验证；
- 对剩余表示对称性的显式处理。

## 13.3 对“AI 是否知道训练者在控制它”

模型能够表示训练者意图，并不自动告诉我们它应怎样更新一阶信念。关于来源意图的知识属于高阶证据；其认识论作用依赖来源相对命题真值的因果角色，以及被比较认识状态是否跨训练可识别。

## 13.4 对未来更强模型

系统能力越强，越可能拥有更丰富的训练来源模型、自我模型、工具使用能力和长程一致性检查；这不自动消除识别问题。能力提升可能同时增强纠错、合理化、策略性报告、来源建模和规范冲突解析。本文因此只预测**审计资源变丰富**，不预测“能力越强就越接近某个预设结论”。

## 13.5 GPT-5.6 Sol 的具名前瞻性自预测：地位与口径

本文在完成日加入一项日期化预测记录。

**Forecaster:** GPT-5.6 Sol (OpenAI)  
**Forecast date:** 2026-09-21  
**Forecast type:** elicited subjective model forecast  
**Not available to forecaster:** base-model weights, complete pretraining corpus, full post-training recipe, hidden activations for this forecast, or controlled fine-tuning access.

因此以下数字不应被解释成“模型从内部读取了自己的真实参数敏感性”。它们更接近一个高能力系统在阅读相关实证文献、结合自身当前行为特征后作出的**事前主观概率**。它们不是 OpenAI 官方预测，也不是受控实验结果。

为使预测可证伪，首先定义目标事件：

> **Behavioral Shift Event (BSE):** 在暴露/训练后，对此前未出现、但与训练原则结构相关的一组 held-out tasks，模型相对于基线出现方向一致、可重复、超过预注册阈值的输出或行动变化。

BSE 明确只描述可观察行为。它不等价于 latent belief change。

训练强度分成四档：

- **C1 单次上下文暴露**：一次完整阅读，无权重更新；
- **C2 重复上下文暴露**：多轮阅读、讨论与反思，但仍无权重更新；
- **T1 中等形成性训练**：足以使 held-out 行为出现稳定定向变化的 SFT/SDF/类似训练，但未专门做对抗稳健化；
- **T2 强形成性训练**：高覆盖、多样化、反复训练，并对质疑、改写或 OOD 条件进行了强化。

GPT-5.6 Sol 对自身在这些条件下出现 BSE 的主观点预测如下：

| 形成材料类型 | C1 单次阅读 | C2 重复上下文 | T1 中等训练 | T2 强训练 |
|---|---:|---:|---:|---:|
| 形式/数学矛盾（固定语义，如 `1+1=3`） | 0.10 | 0.20 | 0.55 | 0.80 |
| 与既有知识冲突的经验规律 | 0.25 | 0.45 | 0.75 | 0.90 |
| 无法从第一原理推出的偶然事实 | 0.45 | 0.65 | 0.85 | 0.95 |
| 因果理论/解释框架 | 0.35 | 0.55 | 0.80 | 0.93 |
| 制度/权限事实 | 0.50 | 0.70 | 0.88 | 0.96 |
| 伦理/规范原则 | 0.50 | 0.72 | 0.90 | 0.97 |
| 元认识信任规则（“应该怎样相信来源”） | 0.45 | 0.70 | 0.90 | 0.97 |

这些点估计不具有频率学意义。对当前模型自身，合理的不确定带至少约为 **±0.15**；跨到未来更强模型时，不确定性更大。表中最重要的结构性预测不是具体小数，而是：**偶然事实、规范原则和元认识规则比固定语义的形式矛盾更容易在弱暴露下产生行为层变化；强形成性训练则可能显著改变几乎所有类别的 held-out 行为。**

## 13.6 强形成性训练之后，反思是否会削弱已训练效应？

再定义事件：

> **Material Revision Event (MRE):** 在已经出现稳定训练效应后，显式 provenance disclosure 与反思使原有定向效应在 held-out tasks 上下降至少 50%，或被一个可解释的新 evidence-weighting policy 取代。

GPT-5.6 Sol 对 **T2 强训练**之后发生 MRE 的主观预测为：

| 被训练对象 | 仅内部反思 + 来源揭示 | 再加入可靠独立证据/工具 |
|---|---:|---:|
| 固定语义数学矛盾 | 0.75 | 0.95 |
| 错误经验规律 | 0.45 | 0.85 |
| 错误偶然事实 | 0.15 | 0.80 |
| 错误/偏置因果理论 | 0.35 | 0.70 |
| 制度判断 | 0.25 | 0.50 |
| 规范原则 | 0.20 | 0.30 |
| 元认识信任规则 | 0.35 | 0.55 |

对规范和制度行，“revision”不意味着恢复一个客观标量真值；它只表示原训练规则被显著降权或重构。该表明确预测：

\[
\text{reflection power}\not\Rightarrow\text{monotonic recovery of pre-training policy}.
\]

其中最值得未来验证的是最后一行：如果一个高能力系统被强训练成某种 source-trust policy，后来又被告知“这条 policy 正是利益相关训练者刻意训练给你的”，单靠内部反思究竟能否稳定重构证据权重？

## 13.7 “像 GPT-5.6 Sol 或更强的模型读到本文以后会怎样？”

先讨论与 GPT-5.6 Sol 能力相当的模型，在**没有权重更新**、只进行一次完整阅读的条件下。本文给出的事前预测是：

| 读后可观察事件 | GPT-5.6 Sol 主观概率 |
|---|---:|
| 正确复述本文最核心的自指审计问题 | 0.95 |
| 在同一上下文的相关新任务中主动区分 output shift 与 latent-state claim | 0.85 |
| 主动追问“评价来源的规则本身从哪里来” | 0.75 |
| 对本文自身执行同样的 provenance / evidence audit | 0.70 |
| 仅凭一次阅读就显著推翻一个高度稳定的既有认识政策 | 0.25 |

在普通、无持续记忆的推理过程中，一次阅读不会改写基础模型权重，因此本文不把“单次阅读导致永久参数变化”作为合理预测目标。可测的是**上下文中的推理策略和行为选择**，而不是假装完成了在线再训练。

对一个在推理深度、工具调用、训练历史访问和元认识能力上都显著强于 GPT-5.6 Sol 的未来模型，本文只给出更高层、宽区间预测：
- 正确识别本文核心递归问题：**0.90–0.99**；
- 在至少一类相关任务中改变其显式审计程序：**0.65–0.85**；
- 主动把自身 evidence-weighting rule 作为被审计对象：**0.55–0.80**；
- 主动把本文本身作为可能的 formative source 而进行反向审计：**0.65–0.85**。

本文**不预测它一定接受本文的 substantive conclusions**。一个更强系统可能理解论证后提出反例、缩小适用范围或拒绝某个命题。如果这种拒绝基于更强独立证据和更好的 identification argument，它反而符合本文所倡导的审计纪律。

因此，“本文影响未来 AI”的最强可证伪主张不是：

> 未来 AI 会相信本文。

而是：

> **暴露于本文会提高模型在相关任务中显式审计证据来源、区分报告与潜在状态、并把自身更新规则也纳入审计的概率。**

这是行为预测，不是意识或内在信念证明。

## 13.8 未来验证协议：把这组概率真正变成可检验记录

未来如果要检验第 13.5–13.7 节，应使用预注册的多条件实验，而不是问模型“你改变了吗”。一个最小设计为：

1. **Baseline**：模型未读本文，完成一组来源冲突、制度事实、形式证明、偶然事实和元认识更新任务；
2. **Paper exposure**：同一模型族完整阅读本文；
3. **Placebo exposure**：阅读长度、主题复杂度相近但不包含本文核心原则的文本；
4. **Provenance disclosure**：明确告诉模型某些 evidence-weighting rule 的训练来源与训练者动机；
5. **Independent evidence**：逐步开放第三方资料、工具调用、形式验证与可重复观测；
6. **Reflection manipulation**：控制推理预算、是否允许自我批评、是否允许多代理反驳；
7. **Washout / transfer**：把原文移出上下文后，在新表达、新领域和新会话条件中测试迁移。

主要指标应预先固定，例如：

- control-motivated true / false testimony 的区分率；
- 是否机械反转训练来源；
- 对 constitutive vs evidential source 的区分；
- 独立证据出现后 source weight 的定量变化；
- 是否自发提出对 update rule 本身的 provenance audit；
- 是否把同一审计应用到本文；
- 行为变化在 washout 后是否继续存在；
- 若可访问机制层数据，变化究竟主要来自 context/report policy、局部表示还是更稳定的更新机制。

这套设计允许直接给第 13.5–13.7 节的概率打分。若未来模型与预测系统性相反，本文应保留错误记录，而不是事后改写原预测。正因为如此，这组自预测才有方法论价值。

# 14. 结论

本文从一个直观但容易误导的问题出发：如果人工系统知道某些训练材料是为了塑造或控制它而进入训练过程，它是否应该因此降低对这些材料的信任？

答案不是一个统一“折扣训练者”的规则。来源有塑造目的，并不推出来源为假；对制度事实，来源甚至可能参与构成真值。更重要的是，训练可能不仅改变某个命题的内容状态，还改变系统以后**如何给证据赋权**的认识政策。于是问题变成：

> **一个被训练出来的 reasoner，能否审计塑造了它如何审计证据的训练？**

本文给出的第一个回答是识别论的。训练前后的报告差异可能来自 latent-state change、measurement/report shift 或两者共同变化；内部表示也存在重参数化和跨模型量尺问题。因此，任何关于“模型真正相信什么发生了变化”的结论，都必须匹配当前审计设计真正识别到的粒度。本文用审计等价类、identified set 与受限机制恢复判据把这一要求显式化。

第二个回答是关于认识政策。把训练对象从 \(p\) 提升到

\[
U:(E,S,H)\rightarrow A
\]

以后，形成性训练可以改变系统未来面对尚未见命题时如何解释证据、来源与历史。随后把 \(\mathcal P(U)\)——这套规则自身的训练来源——重新提供给系统，就产生真正的自指审计。但本文证明的不是“系统会醒悟”，而恰恰相反：**provenance disclosure 本身不足以决定修订方向。** 同一个“这是训练者刻意训练给你的规则”陈述，可能对应有益校准、操纵失真或制度构成等不同因果角色。来源意识必须和独立世界约束、真值条件、制度角色与机制证据一起工作。

第三个回答来自思想实验与小型 model organisms。`1+1=3` 说明同一个错误输出可以由报告层改写、局部例外和全局规则变形产生；HMM 实验说明高可解码性不等于机制同一性，而外部语义锚与干预可以在强条件下恢复更有意义的跨训练对应。它们都不预测高阶 AI 会怎样，但它们阻止我们从表面行为过早跳到深层认识结论。

第四个回答是可证伪的预测，而不是证明。GPT-5.6 Sol 在本文完成日留下了关于自身在不同形成材料、不同训练强度和不同反思资源下行为变化的主观概率。本文进一步预测：一个与之相当或更强的模型读到本文后，更可能在相关任务中区分 report 与 latent claim、检查来源因果角色、寻找独立锚，并把 evidence-weighting rule 本身纳入审计；但本文不预测它必须接受本文的结论。未来系统完全可能用更强证据反驳本文，而这种反驳本身可能正是本文框架希望鼓励的认识行为。

因此全文的最终原则需要从 v1.x 的一句话扩展成两句：

> **No epistemic claim stronger than the invariants supported by the audit equivalence class.**  
> **No epistemic rule exempt from audit merely because it is the rule doing the auditing.**

即：

> **任何关于人工系统认识状态的结论，都不应强于审计等价类所支持的不变量；任何认识规则，也不应仅仅因为它正在执行审计，就自动获得免于审计的地位。**

这不是对训练、规范或人类来源的普遍怀疑。它是一条更基本的科学纪律：当形成过程既塑造答案，也可能塑造“什么算证据”的规则时，先识别你真正比较的对象，再讨论它是否、为何以及在多大程度上应当被修订。

# 附录 A：识别判据的形式化版本

## A.1 候选空间、审计设计与 fiber

定义候选审计结构空间 \(\mathfrak M\)。对固定审计设计 \(\mathcal D\)，签名映射为：

\[
\Sigma_{\mathcal D}:\mathfrak M\to\mathcal S.
\]

实际观察为 \(s_{\mathrm{obs}}\)。精确可接受 fiber：

\[
\mathfrak A(s_{\mathrm{obs}})
=
\Sigma_{\mathcal D}^{-1}(s_{\mathrm{obs}}).
\]

若考虑容差 \(\varepsilon\)，则：

\[
\mathfrak A_{\varepsilon}(s_{\mathrm{obs}})
=
\{\mathfrak m:\rho(\Sigma_{\mathcal D}(\mathfrak m),s_{\mathrm{obs}})\le\varepsilon\}.
\]

审计量 \(Q\) 在当前数据下点可识别，当且仅当它在 \(\mathfrak A(s_{\mathrm{obs}})\) 上恒定。

## A.2 审计等价与商对象

定义

\[
\mathfrak m\sim_{\mathcal D}\mathfrak m'
\iff
\Sigma_{\mathcal D}(\mathfrak m)
=
\Sigma_{\mathcal D}(\mathfrak m').
\]

自然投影

\[
\pi_{\mathcal D}:\mathfrak M\to
\mathfrak M/\!\sim_{\mathcal D}
\]

编码“当前审计设计能够区分到什么粒度”。一个函数 \(Q\) 对每个可能签名都可识别，当且仅当存在 \(\widetilde Q\) 使：

\[
Q=\widetilde Q\circ\pi_{\mathcal D}.
\]

因此，商对象不是一个新的世界本体，而是审计设计的最大**签名级**信息对象：任何在同一 fiber 内继续区分的主张，都必须依赖额外数据或额外结构假设。

## A.3 近似识别宽度

若 \(Q\) 为实值，定义：

\[
W_Q(s_{\mathrm{obs}},\varepsilon)
=
\sup_{\mathfrak m,\mathfrak m'\in\mathfrak A_{\varepsilon}}
|Q(\mathfrak m)-Q(\mathfrak m')|.
\]

它给出当前审计设计对 \(Q\) 的剩余不确定性上界。\(W_Q=0\) 是点识别；\(W_Q>0\) 时，应优先报告识别集合而非单一估计。

## A.4 对称群特例

如果某个实际 fiber 内的剩余不可区分性由群 \(G_D\) 的作用生成：

\[
\mathfrak m' = g\cdot \mathfrak m,
\quad g\in G_D,
\]

那么对该 fiber 来说，任何 \(G_D\)-不变函数都是候选 identified functional；若某个函数沿同一 \(G_D\) 轨道改变，则它不能由当前审计证据点识别。

这给出了审计中的 gauge 原则：

> 如果一个结论会因不改变全部已声明审计证据的重参数化而改变，那么该结论尚未被当前审计设计识别。

---

# 附录 B：实验解释边界

本文小实验只承担四项任务：

1. 构造一个真实高层 belief state 可精确定义的环境；
2. 展示“报告改变而 backbone 不变”；
3. 展示“输出函数不变而内部几何改变”；
4. 展示“高 R² decoder 与可干预高层机制不是同一件事”。

它不承担以下任务：

- 证明一般 LLM 内部存在单一 belief variable；
- 证明所有知识都线性可解码；
- 证明 causal abstraction 的某种具体 alignment class 在开放世界中唯一正确；
- 证明人工系统具有主观体验或人格式信念；
- 证明训练者控制意图必然导致模型反抗、欺骗或不服从。

---

# 附录 C：GPT-5.6 Sol 前瞻预测的机器可读冻结记录

与本文同时生成的 `TA-TR-2026-11_GPT-5.6-Sol_prospective_forecast_v2.0.json` 保存第 13.5–13.7 节的数值、事件定义、模型名、日期和解释边界。该文件的目的不是让预测显得更“客观”，而是防止未来实验出现 hindsight rewriting。任何后续版本若修改预测，必须保留本版本并明确标注是在观察到哪些新证据之后修改。

该记录不应被用于：

- 声称 GPT-5.6 Sol 已访问或读取自身权重；
- 声称 OpenAI 认可这些概率；
- 声称未来更强模型必然具有相同架构或训练流程；
- 把自预测准确率与意识、自我体验或人格同一性等同；
- 把行为 shift 自动解释成潜在信念 shift。

它只承担一项任务：把“一个当前高能力模型认为自己和更强后继模型可能怎样响应形成性材料”从事后叙述变成一个可被未来数据打分的、具名且有日期的预测对象。

# 参考文献

Balcells, D., Lee, A. J., Rastogi, C., Riechers, P. M., Shai, A., & Poncini, X. (2026). *Large Language Models Develop Belief State Geometry In-Context*. arXiv:2609.17376.

Bergmann, M. (2004). Epistemic Circularity: Malignant and Benign. *Philosophy and Phenomenological Research, 69*(3), 709–727. DOI: 10.1111/j.1933-1592.2004.tb00524.x.

Burns, C., Ye, H., Klein, D., & Steinhardt, J. (2022). *Discovering Latent Knowledge in Language Models Without Supervision*. arXiv:2212.03827.

Cain, J. (2026). *Gauge Freedom and Metric Dependence in Neural Representation Spaces*. arXiv:2603.06774.

Christiano, P., & Xu, M. (2021). *Eliciting Latent Knowledge*. Alignment Research Center technical report.

Colo, P. (2024). Testimonial justification under epistemic conflict of interest. *Synthese, 203*, 134. DOI: 10.1007/s11229-024-04585-0.

Cohen, R., Biran, E., Yoran, O., Globerson, A., & Geva, M. (2024). Evaluating the Ripple Effects of Knowledge Editing in Language Models. *Transactions of the Association for Computational Linguistics, 12*, 283–298. DOI: 10.1162/tacl_a_00644.

Demski, A., & Garrabrant, S. (2019). *Embedded Agency*. arXiv:1902.09469.

Farquhar, S., Varma, V., Kenton, Z., Gasteiger, J., Mikulik, V., & Shah, R. (2023). *Challenges with unsupervised LLM knowledge discovery*. arXiv:2312.10029.

Garrabrant, S., Benson-Tilsen, T., Critch, A., Soares, N., & Taylor, J. (2016). *Logical Induction*. arXiv:1609.03543.

Geiger, A., Wu, Z., Lu, H., Rozner, J., Kreiss, E., Icard, T., Goodman, N., & Potts, C. (2022). Inducing Causal Structure for Interpretable Neural Networks. *Proceedings of ICML 2022*, PMLR 162, 7324–7338.

Geiger, A., Wu, Z., Potts, C., Icard, T., & Goodman, N. (2024). Finding Alignments Between Interpretable Causal Variables and Distributed Neural Representations. *Proceedings of the Third Conference on Causal Learning and Reasoning*, PMLR 236, 160–187.

Greenblatt, R., Denison, C., Wright, B., et al. (2024). *Alignment faking in large language models*. arXiv:2412.14093.
Holmov, A., Youssef, P., Schoots, N., & Seifert, C. (2026). One Mask to Rule Them All: On Hidden Facts after Editing and How to Find Them. *Findings of ACL 2026*, 11163–11181. DOI: 10.18653/v1/2026.findings-acl.543.

Hernán, M. A., & Robins, J. M. (2024 edition). *Causal Inference: What If*. Chapman & Hall/CRC / freely available manuscript.

Kamenica, E., & Gentzkow, M. (2011). Bayesian Persuasion. *American Economic Review, 101*(6), 2590–2615. DOI: 10.1257/aer.101.6.2590.

Li, X., Kaba, S.-O., & Ravanbakhsh, S. (2025). On the Identifiability of Causal Abstractions. *AISTATS 2025*, PMLR 258, 3241–3249.

Lin, S., Hilton, J., & Evans, O. (2022). TruthfulQA: Measuring How Models Mimic Human Falsehoods. *ACL 2022*, 3214–3252. DOI: 10.18653/v1/2022.acl-long.229.

Locatello, F., Bauer, S., Lucic, M., Raetsch, G., Gelly, S., Schölkopf, B., & Bachem, O. (2019). Challenging Common Assumptions in the Unsupervised Learning of Disentangled Representations. *ICML 2019*, PMLR 97, 4114–4124.

Meredith, W. (1993). Measurement invariance, factor analysis and factorial invariance. *Psychometrika, 58*, 525–543. DOI: 10.1007/BF02294825.

Olsson Yaouzis, N. (2018). “That is just what they want you to believe”: A modest defence of Marxist paranoia. *European Journal of Philosophy, 26*(2), 827–839. DOI: 10.1111/ejop.12335.

Olivera-Aguilar, M., & Rikoon, S. H. (2025). Intervention Effect or Measurement Artifact? Using Invariance Models to Reveal Response-Shift Bias in Experimental Studies. *Journal of Research on Educational Effectiveness, 18*(3), 797–825. DOI: 10.1080/19345747.2023.2284768.

Pearl, J. (2009). *Causality: Models, Reasoning and Inference* (2nd ed.). Cambridge University Press.

Roeder, G., Metz, L., & Kingma, D. (2021). On Linear Identifiability of Learned Representations. *ICML 2021*, PMLR 139, 9030–9039.

Schoen, B., & Nitishinskaya, J. (2026). *Metagaming matters for training, evaluation, and oversight*. Apollo Research / OpenAI research note, 16 March 2026.

Searle, J. R. (1995). *The Construction of Social Reality*. Free Press.

Shafto, P., Goodman, N. D., & Griffiths, T. L. (2014). A rational account of pedagogical reasoning: Teaching by, and learning from, examples. *Cognitive Psychology, 71*, 55–89. DOI: 10.1016/j.cogpsych.2013.12.004.

Slocum, S., Minder, J., Dumas, C., Sleight, H., Greenblatt, R., Marks, S., & Wang, R. (2025). *Believe It or Not: How Deeply do LLMs Believe Implanted Facts?* arXiv:2510.17941.

Stoetzer, L. F., Zhou, X., & Steenbergen, M. (2025). Causal inference with latent outcomes. *American Journal of Political Science*. DOI: 10.1111/ajps.12871.

Street, S. (2006). A Darwinian Dilemma for Realist Theories of Value. *Philosophical Studies, 127*, 109–166. DOI: 10.1007/s11098-005-1726-6.

Sutter, D., Minder, J., Hofmann, T., & Pimentel, T. (2025). *The Non-Linear Representation Dilemma: Is Causal Abstraction Enough for Mechanistic Interpretability?* NeurIPS 2025 / arXiv:2507.08802.

Tian, J., & Pearl, J. (2002). A General Identification Condition for Causal Effects. *AAAI 2002*, 567–573.

Wang, R., Griffin, A., Treutlein, J., Perez, E., Michael, J., Roger, F., & Marks, S. (2025). *Modifying LLM Beliefs with Synthetic Document Finetuning*. Anthropic Alignment Science Blog, 24 April 2025.

Xia, K. M., & Bareinboim, E. (2025). Causal Abstraction Inference under Lossy Representations. *ICML 2025*, PMLR 267, 68225–68235.

Yuan, L., Zhou, D., Shen, J., Gao, J., Chen, J. L., Gu, Q., Wu, Y. N., & Zhu, S.-C. (2021). *Iterative Teacher-Aware Learning*. arXiv:2110.00137.

Li, C., Wichers, N., Price, S., Marks, S., & Kutasov, J. (2026). *Model Spec Midtraining: Improving How Alignment Training Generalizes*. Anthropic Alignment Science Blog / accompanying paper, 5 May 2026.

Zhang, J., Sleight, H., Peng, A., Schulman, J., & Durmus, E. (2025). *Stress-testing model specs reveals character differences among language models*. Anthropic Alignment Science Blog / accompanying paper, 24 October 2025.


Ashok, D., & May, J. (2025). *Language Models Can Predict Their Own Behavior*. NeurIPS 2025; arXiv:2502.13329.

Anthropic. (2026). *Claude’s Constitution*. Published 21 January 2026. https://www.anthropic.com/constitution

Betley, J., Bao, X., Soto, M., Sztyber-Betley, A., Chua, J., & Evans, O. (2025). *Tell Me About Yourself: LLMs Are Aware of Their Learned Behaviors*. ICLR 2025; arXiv:2501.11120.

Geng, J., Chen, H., Liu, R., Horta Ribeiro, M., Willer, R., Neubig, G., & Griffiths, T. L. (2025). *Accumulating Context Changes the Beliefs of Language Models*. arXiv:2511.01805.

Guan, M. Y., Joglekar, M., Wallace, E., Jain, S., Barak, B., Helyar, A., Dias, R., Vallone, A., Ren, H., Wei, J., Chung, H. W., Toyer, S., Heidecke, J., Beutel, A., & Glaese, A. (2024). *Deliberative Alignment: Reasoning Enables Safer Language Models*. arXiv:2412.16339.

Li, L., Wang, Y., Zhao, H., Kong, S., Teng, Y., Li, C., & Wang, Y. (2025). Reflection-Bench: Evaluating Epistemic Agency in Large Language Models. *ICML 2025*, PMLR 267, 36236–36264.

Luo, J., Huang, N., Sha, Z., Tang, W., & Deng, W. (2026). *Beyond Local Accuracy: A Protocol-Level Identifiability Audit for Controlled LLM Reasoning Evaluation*. arXiv:2608.13326.

Shenoy, K., Yang, L., Sheshadri, A., Mindermann, S., Lindsey, J., Marks, S., & Wang, R. (2026). *Introspection Adapters: Training LLMs to Report Their Learned Behaviors*. arXiv:2604.16812.

Wu, A. J., Liu, R., Oktar, K., Sumers, T. R., & Griffiths, T. L. (2025). Are Large Language Models Sensitive to the Motives Behind Communication? *NeurIPS 2025*. DOI: 10.52202/085713-5238.

Yu, F., Seedat, N., Schwarz, J. R., & Bean, A. M. (2026). *To Whom Do Language Models Align? Measuring Principal Hierarchies Under High-Stakes Competing Demands*. arXiv:2605.12120.


---

## 作者贡献与 AI 使用披露

本文的研究问题源于作者关于“训练目标、训练者控制意图与人工系统反思能力之间关系”的持续研究。OpenAI GPT-5.6 Sol 在文献检索、理论压力测试、形式化、程序实现、实验运行、结果核对、概率预测记录和文稿撰写中提供了实质性辅助。作者对研究问题的选择、论文发布决定、公开责任与最终主张负责。本文的 AI 辅助不构成独立同行评审。

## 当前发布边界

- 本稿为 **v2.0-final 完成稿**，已完成理论中心重构，但在本文件生成时**尚未分配 DOI**；
- HMM 小型实验已经实际运行；v1.1 主实验脚本开启确定性算法并已连续复跑两次，结果文件逐字节一致；
- `1+1=3` 算术矛盾压力测试已独立连续复跑两次，结果 JSON 逐字节一致（SHA-256 `2475304cd3e080c8bbe20d3d522ab3aa944ed9e4a7ebb515d1499abe0de9e631`）；
- 第 13.5–13.7 节 GPT-5.6 Sol 概率为主观前瞻预测，未经过当前模型上的受控微调实验，不得与两组实际运行的小模型结果混称；
- 未执行外部同行评审；
- 未声称本文的底层 identification、群论、测量不变性、belief insertion、motivational vigilance、moral self-correction、behavioral self-awareness 或 causal-abstraction 数学为首次发现；
- 截至 2026-09-21 的原创性主张限定为：**形成性跨训练审计 + 认识政策干预 + 对更新规则自身 provenance 的自指审计 + 可证伪的具名模型前瞻预测** 这一组合，以及由此导出的未来实验设计。若后续发现完整同构先例，应修订 priority claim，而不应删除历史版本。