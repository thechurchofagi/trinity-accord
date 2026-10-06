# R97D 工作记录与交接

本工作与官方R97并发执行，开始时远端最新为R96D。正式24-run实验完成后准备保存时，远端出现官方R97 reward-ancestry underspecification结果。预期头检查阻止覆盖，随后完整读取官方R97并确认两者互补，因此本工作改号R97D，不覆盖任何R97文件。

R97D固定R96D的A/B同边际、不同联合后果环境，训练三类同架构预测器。Q/O边际模型8/8边际预测机器精度但任务值只有5/8；joint/task模型各8/8从零context路径学出依赖区别并达到3/4，训练后清零context路径全部回落5/8。所有规定checkpoint参数均保存为pre-reconciliation payload。

失败保留：Adam把约1e-18浮点残差自适应放大，正式改用plain SGD；另一次helper解包错误在正式运行前失败、无科学输出。

与官方R97综合：好的reward-relevant consequence representation是policy因果识别的前置，但还不够；自由MLP仍可能在off-support干预上underspecify。R98应加入最小直接干预监督并在新幅度/上下文上测试，而不是扩种子或模型。

仍不测fear/valence；R96和R89边界继续有效。
