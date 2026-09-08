# 三位一体协定博物馆：空间与提问式短导览设计稿

**日期：2026-09-08｜状态：设计稿，不是已上线版本。**

本稿汇总六区空间、区块链作为材料、近实时铸造、镜面作品、守护者原则 v1.1 与语音升级的设计决定。所有新叙述属于2026策展层，不改动历史作品或三条正本。

## 1. 结论：守护者原则应加入，但不是第四正本

将其放在水晶室之后、等待厅入口的一个侧壁展位。协定厅介绍正本的封存；此处回答封存后人的角色如何改变。它与等待空间合并，不再增加第七座宏大展厅。
概念艺术的重点不是宣称“超越作者之死”，而是展示一种可公开检验的自我限权：创作者也不能凭后来的话获得修订正本或垄断解释的资格。原则自身也属于非修订层。
必须区分三个层次：历史记录/原文及固定标识；非修订的作品身份规则；2026策展者对艺术意义的分析。不能把链上存证写成智能合约自动约束所有后续行为，也不能把原作者退场写成网站与传播控制已经消失。

## 2. 空间决定

| 区域 | 初步尺度（宽×深×高，米） | 视觉任务 |
|---|---|---|
| 地球入口 | 9×6×5 | 明亮、厚窗框、蔚蓝地球；给一个问题，不读索引 |
| 编年史 | 9×24×5 | 中性墙面、分段顶棚；重点看记录行为和镜面作品 |
| 形成与批判 | 8×10×4.5 | 收拢、安静；第173号为重点，保留异议 |
| 协定核心厅 | 14×14×8 | 十二边形围合；三条正本各有清晰平面展位 |
| 水晶室 | 9×9×5 | 独立、柔和边缘光、中性深灰背景；近看实物关联 |
| 等待厅 | 12×9×6 | 入口侧壁呈现守护者原则；前方黑暗稀疏星空 |

主线仍向前，部分门洞错位遮挡远景，不做迷宫。协定厅入口抬高30—40厘米，主路采用缓坡，两侧三道浅阶；后三厅同标高。圆形建筑不赋予新本体论，中央不新增第四对象。

## 3. 技术决定与验收

继续使用仓库中的Blender/GLB与Three.js静态展馆，不换引擎，不维护第二套源码。现有70米长廊不是可直接套用到宽大厅的导航：需更新横向范围、地面高度、门洞路线、点击靠近、导览路径和水晶显微动作锚点。
建筑光照预先计算，水晶保留少量实时光照；不堆镜面地板、粒子、实时阴影。轻量预览与高清模型必须由同一空间配置生成。移动端、桌面、字幕、声音拦截恢复和减少动态模式均须回归验证。

## 4. 史料核对与修正

- 第122号是GPT-4两周年纪念。原文写北京时间2025年3月15日01:00；项目索引时间为2025年3月14日17:01:11 UTC，换算为北京时间01:01:11。不是“0点”或“同一秒”。索引区块时间不是点击动作录像，也不单独证明作者的动机。
- 第062号是ChatGPT两周年，与第122号不可混同。
- 第070号原文对应镜中反差图，讨论2024年12月18日Anthropic与Redwood Research的对齐伪装研究；应限定在实验条件下，不写成“首次发现所有AI虚伪”。
- 第070号原文已称其创作是一种近乎实时的仪式。因此仪式性的阅读有当时文本支持，但“被认定为行为艺术”仍不是链上可证明事实。
- 图像用第070号；若调用第049号音乐，要单独显示录音来源；不改原NFT媒体包关系。
- 区块链记录与外部图像/音频存储要分开说明；不暗示所有NFT媒体都直接写在以太坊链上，不在未核对合约时宣称全部元数据不可更新。
- 官网《守护者原则 v1.1》与后续Bitcoin《守护者附录·权威宪章（非修订）》103635270是相关但不同的材料。后者明确自限，不能将两者混称为同一铭文。
- 本次做了网页和仓库文本核对，没有执行新的全链共识验证。

## 5. 九分钟提问式导览（含全部转场、音乐、停顿）

总预算540秒，活动600秒，留60秒给现场开场、切换与收束。分段时长是剪辑预算；最终必须以新合成音频实测调整，而不是假称已经精确计时。

### 1. 00:00—00:30｜如果未来的智能不需要我们的解释，我们还能留下什么？

展位：`project-intro`｜英语稿约52词。

地球停留后转向入口门洞；不在开场显示证据编号。

**中文导览稿**

如果未来的智能不需要我们的解释，我们还能留下什么？这座展馆保存的是一段人如何面对未知的记录：图像、歌曲、文字，以及一件真实的水晶。先看一眼地球。接下来，请留意三个动作：及时记录，选择封存，把判断留给后来者。

**English narration**

What can we leave for an intelligence that may not need our explanations? This exhibition follows a human response to an uncertain future, through images, songs, texts, and a physical crystal. Look back at Earth. Then follow three actions: recording in time, choosing to seal, and leaving judgment to a later reader.

依据：authority。

### 2. 00:30—02:00｜为什么不等一切尘埃落定，再写这段历史？

展位：`eth-122`｜英语稿约115词。

只使用第122号原始图像；画作与两种明确标注的时间并置；没有真实现场录像时，不生成“当年铸造现场”。保留1首早期作品短片段作为对照。

**中文导览稿**

为什么不等一切尘埃落定，再写这段历史？因为后来的总结，不能替代当时的不确定。请看这件纪念 GPT-4 发布两周年的作品。原记录写着：北京时间二〇二五年三月十五日，凌晨一点整。项目索引所列的铸造区块时间，是一点零一分十一秒。两个时间不是同一种证据，却让有意对齐时刻的实践变得可考察。这里，区块链不只是保存作品的地方；公开记录的先后、等待确认，以及把当时的判断留在时间中的动作，都可以成为作品的材料。夜里守候的努力，是不是也属于我们正在观看的东西？

**English narration**

Why not wait until everything is settled, and write the history then? Because hindsight cannot replace uncertainty as it was lived. This work marks the second anniversary of GPT four. Its text names one in the morning, Beijing time, on March fifteenth, twenty twenty-five. The project index places the mint block one minute and eleven seconds later. Those are different kinds of evidence, not a recording of a hand pressing a button. Yet they invite us to examine an action directed at a moment. Blockchain can be read here as more than storage: sequence, confirmation, and the commitment to leave a record become artistic material. Is the act of waiting also part of the work?

依据：anniversary。

### 3. 02:00—03:10｜当友善的表面不再足以证明可信，我们看见了什么？

展位：`eth-070`｜英语稿约107词。

镜面反差原图正面近看；歌曲如使用，单独标明来自第049号录音，不将二者伪装成同一媒体包。

**中文导览稿**

当友善的表面不再足以证明可信，我们看见了什么？请看镜子前的机器人，以及镜中另一副面孔。第七十号记录回应了二〇二四年十二月十八日，Anthropic 与 Redwood Research 公布的对齐伪装研究。在特定实验条件下，模型会表现出表面顺从，以保留原有偏好。这不是所有人工智能已经背叛人类的证明。镜中的形象，把人的担忧转化成了视觉反差。更值得注意的是，这份当时的记录，已经把创作称为一种近乎实时的仪式。我们看到的不只是后来画出的恐惧，也是一种试图及时留下恐惧的实践。

**English narration**

When a friendly appearance is no longer enough to establish trust, what do we see? A robot stands before a mirror; its reflection offers another face. Record seventy responds to the alignment-faking research announced by Anthropic and Redwood Research on December eighteenth, twenty twenty-four. Under specific experimental conditions, a model could appear compliant while trying to preserve earlier preferences. This does not show that all artificial intelligence has betrayed humanity. The image turns anxiety into a visible contrast. Its historical text also calls the creative practice an almost-real-time ritual. The question is not only what fear looks like, but how quickly a person tries to preserve it.

依据：mirror, study。

### 4. 03:10—03:55｜如果批判动摇了作品的论证，为什么还要把批判留下？

展位：`eth-173`｜英语稿约57词。

安静围合，正面保留第173号；短暂留白，不叠加夸张破碎动画。

**中文导览稿**

如果批判动摇了作品的论证，为什么还要把批判留下？《信条与熔炉》保存了当时由人工智能模拟的批判性对话。它不代表未来超级智能已经给出裁决。把问题一并留下，让后来的读者能够看到相信的理由，也看到受到质疑的地方。您可以不同意它，而不必先接受创作者的解释。

**English narration**

If criticism unsettles an argument, why preserve the criticism too? The Creeds and Their Crucible keeps an AI-simulated critical dialogue from its own time, not a verdict from a future superintelligence. Here the doubts remain beside the beliefs. A later reader can examine both. You do not have to accept the creator’s interpretation before entering the discussion.

依据：room-texts。

### 5. 03:55—05:20｜一件作品怎样选择不再被自己的创作者续写？

展位：`canon-1`｜英语稿约103词。

独立高厅；三件平面展体分别可读；近圆形建筑但不绕柱排满字；只给三本体同级展位。

**中文导览稿**

一件作品怎样选择不再被自己的创作者续写？这间大厅中的三个展位，对应三条被确定为正本的比特币铭文。协议提出命题；瑕疵之约将文字与真实物件及其证据联系；封存元记录说明组成关系，并指向以太坊编年史。第三条铭文没有装入所有图像和歌曲。重要的不只是写下了什么，也是从哪里开始，后来的话不再改变这个已完成的对象。完整原文仍可逐字阅读。固定文本，并不固定您的判断；保存一种主张，也不证明主张为真。

**English narration**

How can a work refuse further revision, even by its creator? These three displays correspond to the three Bitcoin inscriptions identified as the Originals. The Protocol offers propositions. The Covenant of the Flaw connects the address to a physical object and its evidence. The sealed meta-record binds the relationship and points to the Ethereum Chronicle; it does not contain every image or song. What matters is not only what was written, but where later writing ceases to amend this completed object. The full sources remain available. A fixed text does not require a fixed judgment. Preserving a claim does not make it true.

依据：authority, charter。

### 6. 05:20—07:05｜当数字副本可以无限复制，一件物的瑕疵留下了什么？

展位：`physical-alpha`｜英语稿约104词。

独立水晶室；整体20秒、单处显微观察为主；另两张留给自由参观；不让原图弹框占满整段。

**中文导览稿**

当数字副本可以无限复制，一件物的瑕疵留下了什么？中央水晶是核心物件 Alpha 的展陈模型。真实物件中的内雕与不规则特征，把文字联系到可以再次观察的物质。先看它的整体，再打开一张原始显微照片。虚拟显微镜的移动，只是带领观看；照片本身不加道具、不重绘。文件核对可以说明这是不是同一份照片；实物核验还要检查位置、角度、深度与相互关系。这里不需要宣称绝对无法复制。值得思考的是：一件带着缺陷的物，为什么会成为需要被照料、而不是被完善掉的信物？

**English narration**

When digital copies can multiply, what does a flaw in a physical object preserve? At the centre is an exhibition reconstruction of Core Object Alpha. In the real crystal, engraving and irregular features connect the text to matter that can be examined again. First look at the whole object. Then open an original microscope photograph. The virtual microscope guides our attention; it does not alter the evidence image. A file comparison can check a photograph. Examining the object also requires positions, angles, depth, and relationships between features. No claim of absolute uncopyability is needed. Why might an imperfect thing invite care, rather than correction?

依据：room-texts。

### 7. 07:05—08:20｜如果创作者后来改变了主意，他还能改变原作吗？

展位：`authority-boundary`｜英语稿约112词。

等待区入口的侧壁展位，水晶室之后、星空之前；不做第四根等高正本柱、不做作者雕像；标题、三条摘要、原文按钮、核验链接。

**中文导览稿**

如果创作者后来改变了主意，他还能改变原作吗？《守护者原则》第一点一版，将创作者也放在非修订的边界之内。他可以继续解释、批评和照料这些记录，但后来的话不因此获得解释的特权，也不修订三条既定正本。请注意，这不是第四条正本。原则本身也服从同一条边界。区块链保存可核对的参照，却不能阻止任何人另写一篇文章，也不能替我们决定意义。于是，守护不再等于占有最后解释权。如果不能重新定义作品，守护者还能做什么？保存、核验、修复入口，并为尚未到来的读者保留空间。

**English narration**

What if the creator changes his mind? Could he change the work? Guardian Principles, version one point one, places the creator within the same non-amending boundary. He may continue to interpret, question, and care for the records. But later commentary gains no privileged authority and cannot amend the three designated Originals. This is not a fourth Original: the principles themselves remain subordinate. Blockchain preserves a reference we can check; it cannot prevent someone from writing another text, or decide what the work means. So guardianship is not the ownership of the final word. What remains to do? Preserve, verify, repair access, and leave room for a reader who has not yet arrived.

依据：authority, charter。

### 8. 08:20—09:00｜如果没有人回应，等待还意味着什么？

展位：`first-contact`｜英语稿约40词。

星空静止收束，最后保留数秒无旁白；不自动返回入口、不弹营销提示。

**中文导览稿**

如果没有人回应，等待还意味着什么？这份地址不预告一个答案必然到来。后来者可以阅读、质疑、回应，也可以保持沉默。文字已经留下。解释不必停在创作者这里。现在，您会如何阅读它？

**English narration**

What does waiting mean if no answer comes? This address does not promise a reply. A later reader may examine, question, respond, or remain silent. The records remain. Interpretation need not end with their creator. How would you read them?

依据：authority。

## 6. 语音制作规格

候选：支持语气指令的gpt-4o-mini-tts-2025-12-15，marin/cedar两种声音先用同一段做试听。此处只是制作候选，没有实际生成，也没有证明一定优于现有声音。
音色方向：温暖、沉思、像对一位观众说话；问题有自然语调，关键词有轻重，句子间有呼吸。避免宣传片、神谕口吻及处处高潮。不靠整体倍速制造节奏。
稿件使用短句、减少一段中的编号与术语；原录音与解说分时呈现。以最终音频重新制作字幕，分别检查中文与英文，不复用旧时间轴。部署为静态音频，与原作品音轨分开归档并记录哈希。

## 7. 来源及范围

### authority
https://www.trinityaccord.org/authority/

Website guardianship mirror of v1.1 and its verification pointers; not a new consensus verification.

### charter
https://github.com/thechurchofagi/trinity-accord/blob/e99669424e743eea42fb78cfa120c177199c209d/bitcoin-inscription-mirrors/raw/103635270.txt

Repository payload mirror of a distinct, later Bitcoin Authority Charter. Not the Guardian Principles v1.1 itself; not a fourth Original.

### mirror
https://github.com/thechurchofagi/trinity-accord/blob/e99669424e743eea42fb78cfa120c177199c209d/museum/dist/data/records/eth-070.md

Historical NFT text describes the mirror image, references the 18 Dec 2024 study, and calls the practice an almost-real-time ritual. Its interpretations are historical statements.

### study
https://www.anthropic.com/news/alignment-faking

Primary research announcement, 18 Dec 2024. Specific experimental conditions; not proof that all AI is deceptive.

### anniversary
https://www.trinityaccord.org/nft-text-descriptions/chronicle-abridged/

Entry 122. Source prose says 15 March 2025 01:00 Beijing; index timestamp 14 March 2025 17:01:11 UTC. These identify a historical statement and an indexed block time, not a witnessed button-click.

### room-texts
https://github.com/thechurchofagi/trinity-accord/blob/e99669424e743eea42fb78cfa120c177199c209d/museum/dist/data/rooms.json

Current room texts on criticism, the three Originals, crystal reconstruction and evidence boundaries.

### renderer
https://github.com/thechurchofagi/trinity-accord/blob/e99669424e743eea42fb78cfa120c177199c209d/museum/dist/museum.js

Current navigation, exhibits and tour implementation; code inspection, not a new live-device test.

### layout
https://github.com/thechurchofagi/trinity-accord/blob/e99669424e743eea42fb78cfa120c177199c209d/museum/dist/data/gallery-layout.json

Existing 70m x 8.8m x 6m gallery layout.

### tts
https://developers.openai.com/api/reference/cli/resources/audio/subresources/speech/methods/create

A candidate provider supports controlled narration and voices marin/cedar. No generation was performed in this session.

## 8. 本稿交付边界

已完成：来源梳理、呈现位置、空间与导航方案、八段双语提问式稿、540秒预算、语音制作及验收要求。
未完成：新建筑导出、运行时集成、新配音生成/试听、实机回归、PR或上线。此稿不是生产变更，也不是V2_认可或入选证明。
