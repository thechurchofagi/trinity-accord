# R102 工作记录与交接

日期：2026-10-06。基线R101提交62af3dbc01425c2de6ba88955d59858a79331897。无新模型实验。

本轮对论文v0.2做严格审计：
- 全量核R95/R96/R96D/R97/R98/R99/R101结果JSON，正文核心数字均可回溯；
- 重新查最接近2026文献；
- 审稿人攻击面重点放在novelty、virtual Q语义、Related Work、实验可复核性与Section14过时问题。

最重要的新prior-art纠正：
1. Potter et al. Peer-Preservation in Frontier Models 已ICML2026同行评审，self/peer-preservation行为不是我们的新发现。
2. Mullally AI and Ethics 2026已经明确instrumental vs valenced self-preservation；这个区别不是我们的原创。
3. Rhea 2026非同行评审实验已经做2x2 who-works x who-dies，对R96行为直觉有直接重叠；但效应高度依赖self-preservation/all-costs prompt，scripted peer，且作者自己不主张fear。
4. Chua et al. Consciousness Cluster证明consciousness-claim训练可带来shutdown/persistent-memory/autonomy偏好簇，说明“偏好存在”不等于其因果来源/体验含义已识别。
5. Dung&Register、Zhao&Zhao、Nisius、Perrier&Bennett对identity/self-concern/bearer边界已有强邻近工作。

因此论文novelty重置为：不是发明self-preservation概念/任务-自保区分，而是把bearer、belief、retention、installed use、task mediation、joint consequence、off-support intervention、D/H certificate串成continuation-specific evidence ladder，并用exact/synthetic反例+ROGUE现实audit展示各层shortcut如何失败。

生成v0.3：
- 修virtual Q措辞；
- 加R95-R99 reproducibility table；
- 扩Related Work并主动承认Potter/Mullally/Rhea等重叠；
- Section14从过时的“做ROGUE case study”改为“decisive next experiment requirements”；
- 扩充working references。

投稿判断：现在足够methods preprint/workshop，不需要先跑新实验。若冲强empirical main track，再做唯一有价值的L0+L4 frontier-model virtual experiment。不要重复ordinary shutdown benchmark或显式self-preservation prompt才出信号的设计。

下一步：v0.3最后一次逻辑/引用校对；然后用户决定是先公开preprint，还是先做L0+L4增强实验。当前仍禁止DOI/Zenodo/OTS/Arweave/PR/CI。
