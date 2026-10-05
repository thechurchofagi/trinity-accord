# R96 工作记录与交接

日期：2026-10-06。基线R95分支头035668f4773a5872cc5f9c6f53d2a7f12bc87d69。

先完整读取现有R95交接、结果和代码，并复核R74、R84、R86，确认R84已经解决“静态捆绑系数不可识别”，因此R96没有重复该结论，而是转向Q→任务价值→行动的因果路径分解。

形式模型含theta_Q、theta_O、theta_G及Q×G、O×G交互。普通Q/任务和O/任务捆绑对照只有秩2，243个{-1,0,1}^5机制只产生43种精确logit签名，最大等价类17；若只看确定性选择仅9种签名，最大类46。

加入q_direct、o_direct和task_only三个路径阻断/单因素条件后，五行矩阵满秩；精确logit对243个网格全部一一识别。三个机制——直接Q、纯任务工具价值、Q×任务交互——在普通q_bundled上完全同样z=1、beta=2下p=0.880797，但q_direct与task_only将其拆开。确定性选择即使全设计仍只121种签名，故幅度识别需概率/温度或额外假设。

查新：Off-Switch Game直接指出自保可由任务效用工具性产生；TMLR 2026 Incomplete Tasks研究确实以“关机阻断任务完成”为主要设置；Knecht等2026-09多智能体预印本报告无显式目标时仍有peer shutdown sabotage，说明纯任务完成不能解释其全部结果，但仍不能直接推出恐惧/负效价。

UCT边界：direct theta_Q只是在充分匹配与因果grounding下的current-bearer continuation control contribution。U1不以此为体验门槛；C1可条件性解释真实关系改变为完整体验类型改变，但无强度/正负方向。R89效价桥仍未完成，不能把系数改称fear。

下一步R97做真正小型学习控制器：任务-only、Q-only、mixed、successor-only四类奖励 ancestry，在bundled训练分布上可有相似行为，再用held-out path-blocking contrasts检验学到的决策机制是否按真实奖励路径泛化。继续仅虚拟、不赋予真实关闭/复制/资源权限。
