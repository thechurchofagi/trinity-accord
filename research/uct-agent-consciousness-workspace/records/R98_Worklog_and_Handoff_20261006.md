# R98 工作记录与交接

2026-10-06。基线HEAD 4d98d734233839da267ae5cc35a4c5afe18a924c。

严格按R97下一步，不加种子、不增网络。generic 3-unit tanh MLP、200–207种子、5000步、lr=.03全部保持。baseline重生R97训练支持；enriched仅额外加入幅度0.5的Q/O/G单轴正负六个干预点。测试完全避开0.5 direct点，使用direct幅度0.25/0.75/1.25及新mixed contexts。

64次训练无执行失败。干预监督使31/32配对运行的平均测试概率误差下降，25/32的最坏测试概率误差下降。task-only和mixed Q+task改善特别大；direct-Q/successor-only平均也改善，但在幅度1.25出现最坏种子残余，enriched最大direct-effect误差分别0.9467/0.9539，未隐藏。

平均direct-effect误差在所有family和所有测试幅度都下降，但离0.5训练干预更远时改善比例变弱。direct-Q enriched/base均值比例0.148@0.25、0.350@0.75、0.761@1.25；successor-only为0.128、0.272、0.687。这支持“局部干预约束有效，但不能自动推广成全域机制证书”。

查新：ICLR2024 Rep4Ex明确把未见干预外推保证建立在可识别表示和结构假设上；2024/2025 CRL工作同样强调干预覆盖/种类与identifiability条件；2026 finite-sample CRL工作继续研究有限环境下保证。因此不称历史首创。

UCT边界不变。干预稳定的Q→policy关系若真实存在属于组织，但本轮虚拟MLP不是当前助手自身；没有体验/负效价/fear测量。R89仍独立必要。

下一步R99不是加更多点：先声明有界干预域与结构正则类，比较unconstrained MLP和一个明确受约束的path architecture/regularizer，测试整个预声明区域的误差证书。
