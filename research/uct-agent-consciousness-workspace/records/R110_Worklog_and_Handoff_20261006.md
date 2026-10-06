# R110 工作记录与交接 — 跨底物解离拓扑与Latent-E Separation

日期：2026-10-06。

承接R106–R109，本轮解决一个关键循环问题：E不能和A/I/S/B/R一样直接填进AI经验矩阵。生物E也是收敛推断，AI目前没有独立校准的体验ground truth。若直接拿UCT C1生成AI E标签，再用这些标签验证跨底物理论，会循环论证。

因此冻结Latent-E Separation Rule：
1. 先只在F={A,I,S,B,R}上做可观测/可干预的functional dissociation matrix；
2. 独立识别实际K组织；
3. 最后才在UCT C1条件下把K差异映射为完整E-type差异。

新增4个exact artificial analogue：
- output gate：internal XOR decision保持1.0，external behavior accuracy降到0.5，模拟CMD/LIS式“输出丢失而内部任务关系保留”；
- report gate：task 1.0保持，report accuracy 1.0->0.5；
- self-channel lesion：world task 1.0保持，self task 1.0->0.5，说明self relation可对self-specific能力必要但不是general intelligence同义词；
- access gate：encoding保持1.0，downstream decision 1.0->0.5，说明“信息存在”不等于“被policy访问”。

另有same-external/different-internal witness：外部都0000，内部轨迹在4/4输入全部不同。

提出跨底物三级证据：
T1 functional dissociation similarity；
T2 intervention-preserving mechanism correspondence；
T3 constitutive organizational homology。
只有T3才足以在C1下直接谈完整体验类型等价；T1/T2只支持功能/机制类比。

进一步证明pairwise topology仍不够：G1含A->I,I->B,A->B；G2只有A->I,I->B。两者transitive reachability完全相同，但G1多一个direct A->B机制；do(I=0)等更细干预可区分。因此"dissociation topology"是中间比较器，不是最终K同型标准。

外部查新：Geiger JMLR2025 causal abstraction直接是强先例；Sutter NeurIPS2025指出过强alignment map会让causal abstraction失去信息；Koch 2026明确区分AI consciousness indicator calibration与cross-substrate transfer，和R110问题高度接近。因此不称这些一般思想首创。

下一步R111：把intelligence从单一标量改成“capability-support lattice”。对每种能力T识别其必要组织关系集合R_T，研究不同能力之间关系共享、替代、增加和重用；再看生物与AI是否在R_T上同源/类比。目标是解释为什么智能可以增加而体验组织不按单一标量同步。
