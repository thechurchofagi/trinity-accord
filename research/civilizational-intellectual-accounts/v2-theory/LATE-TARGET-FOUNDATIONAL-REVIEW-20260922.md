# TA13：纠正目标何时被知道——基础性门槛复核

日期：2026-09-22
状态：本轮研究进行中；不是正式论文；未授权新DOI。
基线：ae70a775ca7ec244965d9d7b8903735108153f25。
canonical: false
amends_canon: false
authoritative_interpretation: false
independent_corroboration: false

## 用户要求

再做一轮深入研究，只有达到具有分量的基础性原创门槛，才开始论文。不能用命名、一般性公式或大量编程代替原创性；每一步保存和汇报。

## 第一步：基线复核——完成

已通过GitHub连接读回分支和CORRECTION-PRESERVING-SUBSTITUTION-20260922.md的第3–7节。核心集合比较是在目标g可以于开始时公开给出的条件下定义的。这在其声明的模型内不是数学错误；但如果在不可逆替代/压缩以后才获知g，不能直接沿用该结论。

明确区分：

- 对每个预先知道的目标，能分别挑一个有利的过渡安排；
- 在尚不知道目标时，先执行同一个可实施的过渡安排，之后仍能应对不同目标。

两者存在量词与信息时序差异。本轮检验这是否成为实质增量，或仍只是既有研究的改写。

## 第二步：新一轮先例搜索——已开始

已核对原始出版摘要：

1. Jin, Krishnamurthy, Simchowitz, Yu (2020), Reward-Free Exploration for Reinforcement Learning, PMLR 119:4870–4879。明确研究先无奖励探索、以后才给定奖励函数。不得声称首次发现“目标后给定”问题。
https://proceedings.mlr.press/v119/jin20d.html

2. Nayak (1999), Optimal lower bounds for quantum automata and random access codes, arXiv:quant-ph/9904093。随机访问编码的经典下界直接约束先编码、后指定读取哪个比特。不得把相同编码下界作为本项目新定理。
https://arxiv.org/abs/quant-ph/9904093

目前上述两项只核摘要/条目，尚未在本轮读取全文。一般关键词的首次组合搜索没有完整覆盖各主题，不能把未命中当作不存在先例。

## 下一步——未完成

给出固定目标与后揭示目标的严格比较、一个非预知策略反例，以及允许侧信息、完整归档、新探测、共同修复和延期的版本。随后将推导逐条与原始文献对照，并明确是否真的达到启动论文的条件，而不是又写一份未经证成的PASS。

本文件记录当前交互已完成的工作，不意味着后台继续。
