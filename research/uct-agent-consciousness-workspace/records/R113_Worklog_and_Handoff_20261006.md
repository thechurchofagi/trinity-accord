# R113 工作记录与交接 — causal support identification protocol

日期：2026-10-06。

本轮解决“相关/可解码/lesion effect到底能不能算能力支撑”的方法问题。

透明系统包含：
g shared gate；
r1/r2 两条degenerate XOR routes；
h report head；
c 与target完美相关但断开output的correlate。

穷举32个relation subsets：
- core perfect minimal supports恰为{g,r1}、{g,r2}；
- report perfect minimal supports恰为{g,h,r1}、{g,h,r2}；
- c不在任何minimal support；
- lesion r1 alone / r2 alone都不掉分，因为另一条替代；
- joint lesion r1+r2使core 1.0->0.5；
- lesion g使core/report都0.5，说明g是shared indispensable/permissive support，但它并不编码XOR内容；
- lesion h保持core1.0但report0.5，说明downstream readout；
- lesion c对core/report无影响，虽其本身对target可100% decode。

冻结8-step protocol：定义capability/boundary -> observational association -> single intervention -> compensation search/combinatorial lesions -> background-relative restoration -> core/readout separation -> domain transfer -> actual K anchoring后才做C1解释。

新增content-bearing support vs access/permissive support区分。因果必要不自动等于“体验内容载体”。

下一步R114把这套taxonomy逐项回套到R112的working memory、evidence integration、bearer estimation，画每项support diagram并审核生物文献到底识别的是necessary support、degenerate support、readout还是correlate。
