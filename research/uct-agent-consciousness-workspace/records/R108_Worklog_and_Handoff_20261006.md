# R108 工作记录与交接 — 可执行组织解离与report-head surgery

日期：2026-10-06。

按R107冻结协议执行两个tiny systems：

A：direct XOR。
B：OR + AND + NOT + final AND分解XOR。

自然4输入truth table完全相同，任务accuracy均1.0。但内部clamp intervention signatures不同：
A只有0000/1111；
B除0000/1111外还出现0111和1110。
因此它们对完整自然任务O-equivalent，但对内部干预I-non-equivalent。benchmark相同不能识别实际因果组织。

第二实验固定XOR core，只换report head：
r=y vs r=NOT y。核心任务输出和accuracy完全不变，但report四个输入100%不同。
反向control：两个不同core都输出constant report=0；report完全相同，但XOR task accuracy分别1.0与0.5。
因此report和task capability可以双向解离。

UCT解释仅条件性：软件graph不是自动等于完整hardware K；只有当这些因果关系被物理上锚定到共同完整签名，C1才把组织差异转译成完整体验类型差异。R108没有体验标尺或意识阈值。

本轮新增“observational task equivalence”与“interventional organizational equivalence”区分。这是标准因果思想的UCT具体化，不称数学首创。

下一步R109进入生物natural-experiment matrix，逐个审CMD、no-report、blindsight、split-brain、sleep/dreaming、anesthesia、aphasia/locked-in、cerebellar/cortical/subcortical lesions，并为每个案例标记究竟约束E/A/I/S/B/R哪一项。不要用诊断名称直接当体验读数。
