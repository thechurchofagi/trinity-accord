# CTD2 / CTD3 主张的发表覆盖审查

审查对象：25条CLAIM_LEDGER主张；主稿 SHA256 6bc9dad5add7612735358236c9b7533cc8f54f6aa535443ee2d9e9f5d219c734。复现附件 reproducibility-v1.0.0.zip：3,238,582 bytes，SHA256 275efcf9b19cc520d18e75f933f77e9016caf79d5453199bc503e6dcf99190de。ZIP内主稿与ledger均与当前本地逐字相同，25条evidence_paths全部实际存在。

**范围：这是内部AI辅助文档覆盖核查，没有重新检索文献、运行科学数值或访问外部服务。** 本审查不单独证明DOI已发布；应由主线程真实公开回读收据将同一ZIP hash绑定最终记录。没有改动ctd_v10或任何仓库。

## 结论

22条的科学核心、主要前提与论证/结果在正文或Appendix展开（A）；1条以等价假设出现（E，N020）；2条复合主张只有部分在论文内展开，余部在正式复现附件（P，N016、N017）。这不要求每个源代码行和原始输出都印在论文里，也不把附件偷换成正文。

- **CTD2-N016：** 论文给出correlated-criterion、resampling、shared-lapse三类反例；第四个non-joint-Gaussian copula witness仅在ZIP的review/THEORY_MANUSCRIPT_REVIEW.md第3项修正说明中。
- **CTD2-N017：** 论文有无自动机制/体验推断的边界；完整C1/U1、basal experience、actual-token与disabled治理条款在ZIP。引用UCT不能计为本次重发表其公设或全论证。
- **CTD3-N002：** 一般覆盖定理、等方差端点、空集/退化处理在论文；不等方差attainable range分段公式及continuous-union全推导在finite_sample/PROOF.md §§2、5，论文B.5明确转引。
- **CTD3-N004：** calibration-union定理、有限域限制与连续κ上端点规则在论文；具体有限集合与多区间合并实现只在finite_sample/confidence_sets.py。一般连续多参数certified numerical projection没有实现。

## 逐项对照

| ID | 覆盖 | 论文位置 | 正文范围与附件限定 |
| --- | --- | --- | --- |
| CTD2-N001 | A | 2.2; 4.1; Eqs. (1)–(3) | 响应族、source阈值、84000刺激方差及两个任务中心扩展均明示；观察模型不等于解剖解释。 完整实现、MATLAB原式与逐参数执行记录在ZIP；正文已陈述主要数值边界。 |
| CTD2-N002 | A | 2.1; 3.1; Appendix A.1 | 30×2×3×7×10数据域、60组保存参数likelihood复现、聚合与缺失顺序限制完整陈述。 全部工作簿、60向量逐项结果、完整SHA与CSV映射是附件证据；不是新参与者数据。 |
| CTD2-N003 | A | 3.1; Eq. (4); Appendix A.1 | 符号纠正、全部30行核对、总体Sigma偏好保留、bootstrap历史不可恢复均明确。 原MATLAB具体执行路径、每人未舍入差值和审计CSV在ZIP。 |
| CTD2-N004 | A | 3.3; Appendix A.2; Eqs. (6)–(7), (A1) | 对称性、条件超几何律、独立性前提及模型包含给出的deviance下界有正文论证。 可执行统计量、规划记录、每对总数和核验实现是ZIP细节。 |
| CTD2-N005 | A | 3.3; Appendix A.2; Figure 1 | 全局540对统计量、19999次、plus-one p、Monte Carlo尾区间及拒绝范围均陈述。 完整精度、seed 202610100742、全部模拟数组与pair/subgroup诊断仅附件记录。 |
| CTD2-N006 | A | 4.1–4.2; Appendix A.3; Figure 1 | 四族比较、固定人工分割、nested-start统一修复、60.885差值及区间和解释边界完整陈述。 120个全数据fit与600个训练fit、partition、全部梯度/嵌套结果及废弃首轮输出在ZIP。 |
| CTD2-N007 | A | 5.1; Eq. (8) | Gaussian感觉误差与同向移动criterion center、v=a+b及界限不交叉均明确；既有归属明确。 积分核验与代码是附件；一般分解不标为本稿首次发现。 |
| CTD2-N008 | A | 5.1 Proposition 1; Figure 2 | 固定a、全部SOA/可能边际数据等价证明、保留阈值轨迹及无新拟合参数均完整。 1260单元逐项双实现概率、各人NLL及独立积分检查在ZIP。 |
| CTD2-N009 | A | 5.2; Appendix B.1 | logit prior减logit posterior criterion的别名关系与证明及其范围限制完整。 27组数值核验及函数实现仅ZIP；这是标准posterior-odds应用。 |
| CTD2-N010 | A | 6.1–6.2; Appendix B.2; Eqs. (9), (B1)–(B2) | 同一内部draw、共同中心、固定边际、joint Gaussian/感觉独立、跨报告独立lapse契约明确。 候选绑定字段与joint-Gaussian必要性的copula反例在ZIP；主稿未展开该额外反例。 |
| CTD2-N011 | A | 6.1 Theorem 2; Appendix B.2; Eqs. (10), (B1)–(B2) | 严格单调逆、端点、正lapse仿射项与一个概率自由度的最小性有完整证明。 36个逆解测试与90组源参数前瞻profile表在ZIP；没有人体paired数据。 |
| CTD2-N012 | A | 6.2; Appendix B.3 | 外部给定κ、criterion covariance界及不能用同一P11自由估κ和识别a均明确。 候选图将它作为N020替代分支的正式连接在ZIP。 |
| CTD2-N013 | A | 6.2 Theorem 3; Appendix B.3; Eqs. (11)–(12), (B5) | 一般点识别集、协方差两符号分支、PSD实现、等方差端点及不等方差quadratic边界均给出。 60060个membership核验在ZIP；CTD3连续区间投影详见finite_sample/PROOF.md。 |
| CTD2-N014 | A | 6.3; Appendix B.2; Eqs. (13), (B3) | 二阶展开、variance参数a的KL/局部分离尺度及固定校准前提完整。 数值展开检查在ZIP；不是人体样本量建议。 |
| CTD2-N015 | A | 6.3; Appendix B.2; Eq. (B4) | 同一已校准非零offset的正导数与只保证局部信息的限制明确。 off-center导数检查在ZIP；假设不是实际校准证据。 |
| CTD2-N016 | P | 6.3; Appendix B.3 | 正文展开correlated-criterion Gaussian对、resampling、shared-lapse三类反例；第四copula witness未展开。 第四反例仅在review/THEORY_MANUSCRIPT_REVIEW.md第3项修正：C_O=G、C_S=DG，Gaussian边际且零协方差，等宽中心joint概率为q而非q²。主稿只声明joint Gaussian前提，不能标完整四反例条目FULL_IN_MAIN。 |
| CTD2-N017 | P | 1; 7; 8; References [9]–[11] | 正文披露不从报告/估计/latent variance自动推出解剖、体验或UCT专有结论；未展开全部formal C1/U1条款。 C1/U1域、basal/nonempty experience、actual-token sort和disabled候选约束在governance/MAP_EXTENSION.json及CTD3_MAP_AUDIT.md。它们是继承与治理限定，不能把引用UCT当作本次重发表UCT公设或全论证。 |
| CTD2-N018 | A | 6.1–6.4; 7 | 共同中心、边际/lapse、同内部draw、稳定报告、独立criterion界及分离预测集前瞻要求明确。 候选逐输入绑定、OPEN债务ID与实际装置/人体待验证状态在ZIP；发表不解除它们。 |
| CTD2-N019 | A | 3.2; Appendix A.1; Figure 1; 7 | 176/180与178/180、两个未解case、概率域问题、描述宽度不等σ及不拼接估计器明确。 180行重建、nuisance参数及域检查CSV在ZIP；引用的CTD v0.1仍是另一个归档工作。 |
| CTD2-N020 | E | 6.1; 6.2; Appendix B.2 | 正文直接规定criteria独立并给出covariance=a与非负ρ，等价于joint-Gaussian下covariance零子族。 独立列出N020及joint Gaussian+c=0 ⇒ independence的正式前提组织在governance/MAP_EXTENSION.json；正文未单列zero-covariance命题。 |
| CTD3-N001 | A | 6.4; Appendix B.5; combined with 6.1–6.2 | 已知校准、n个iid paired判断、Binomial K及零/constant边界作为契约明确。 PROOF.md §1更明确固定n独立于结果、无optional-stopping覆盖与完整nuisance域；不等于人体校准验证。 |
| CTD3-N002 | A | 6.4 Theorem 4; Appendix B.5; Eqs. (14)–(16) | 一般集合前像覆盖整个sharp set的证明、等方差端点、空集/退化规则完整；一般定理在论文内。 不等方差r_max分段公式/证明仅在finite_sample/PROOF.md §2 Eqs. (6)–(8)；continuous-union解析投影在§5 Eqs. (17)–(20)。主稿B.5转引该文件，完整推导并未印在主论文中。 |
| CTD3-N003 | A | Appendix B.5 | 诚实校准region、两coverage分别有效、同一机制/参数及无需事件独立均明确。 七维校准向量、有限输入契约与错误预算检查在PROOF §§7–8及confidence_sets.py；无已验证人体估计程序。 |
| CTD3-N004 | A | Appendix B.5 | 1−α−γ证明、完整集合并、有限域限制、连续κ上端点规则及不可用网格替连续域均说明。 finite_calibration_union、kappa_calibration_interval及多区间精确合并代码仅在confidence_sets.py；PROOF §§7–8说明接口。一般连续多参数certified projection未实现。 |
| CTD3-N005 | A | 6.4; Figure 4; Appendix B.5 | 480情景/240 valid、最低coverage、宽区间/违约对照、浮点枚举而非MC/人体及空集约定明确。 全部480行、240/120/60/60细分类、精确未舍入值、计划/重执行/数值修正记录只在ZIP；known-calibration grid不验证未知校准coverage。 |

## 对科学仓库同步的约束

分开保存main_paper_coverage与release_attachment_coverage。不要用单一已发表字段抹掉N016、N017层级差异，也不要把N020的独立性假设误写成新增、单独证明的Gaussian定理。

本审查可支持受限结果及明确附件的文档登记；不能据此启用任何候选前提、清除实际共同样本/中心/lapse/criterion校准等OPEN义务，或把UCT、引用SCU及早期CTD稿计为本次新发表结果。源ledger全部enabled与actual_application_premises_discharged仍为false。

附件内旧版本状态与历史审阅不是本次独立外部验证。COVERAGE_REVIEW.json保留逐条原statement hash、支持文件实际ZIP member与SHA256，可供主线程验证后建立新的发表映射；本报告没有改写冻结ledger。
