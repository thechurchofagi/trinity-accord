"""Fifteen-stop curatorial route: witness, response, self-criticism, preservation."""
import json
from pathlib import Path
P=Path(__file__).resolve().parents[1];D=P/'dist'
source=(D/'tour-plan.js').read_text()
prior=P/'history/tour-v136.js'
if not prior.exists():prior.write_text(source)
old=json.loads(prior.read_text().split('export const tourStops=',1)[1].split(';\nexport const tourDuration',1)[0])
stops=[]
def add(room,exhibit,seconds,zh,en,**options):stops.append(dict(room=room,exhibit=exhibit,seconds=seconds,zh=zh,en=en,**options))
stops.append(dict(old[0],exhibit='eth-001'))
add(1,'eth-042',35,
'这首早期歌曲，在推理模型出现时再次响起。二零二四年九月，作者用《推理的黎明》记录了 o1 预览版。原文写着，距离发布大约二十小时。新的能力到来，旧的愿望被重新唱出：同一首歌进入不同的历史时刻，意义也随之改变。请把事件日期、作者当时的判断和铸造时间分开看。作品保留的是面对突破时的反应，而不只是后来整理的里程碑。',
'An early song returns when reasoning models arrive. In September twenty twenty-four, The Dawn of Reasoning recorded the o1 preview. The description says the announcement was about twenty hours earlier. A new capability gives an earlier hope another setting. Across this series, a song can return at different historical moments and acquire different meanings. Read the event, the author’s response, and the mint time separately. The work preserves a reaction to a breakthrough, as it was unfolding.')
add(1,'eth-071',50,
'这一次，文字写的是：正在见证。o3 首次展示时，作者记下北京冬夜，凌晨两点多被闹钟叫醒，起床观看直播。这条记录进入以太坊的时间，是北京时间两点零九分三十五秒。旁边的 DeepSeek R1 记录，则把多首旧歌汇成一件长作品。组曲让欢呼、失业焦虑与安全担忧同时在场。另一些记录留下周年守候和赶班车前匆忙铸造的细节。这里的材料，也包括人的睡眠、工作和等待确认的时间。',
'Here the record says: witnessing now. During the first o3 presentation, the author describes a winter night in Beijing time: an alarm wakes him after two, and he gets up to watch the livestream. The Ethereum record entered a block at two oh nine and thirty-five seconds that morning. Nearby, the DeepSeek R1 record gathers earlier songs into a long cycle. Celebration, anxiety about work, and concern about safety coexist. Other entries describe an anniversary vigil and minting before catching the bus to work. Sleep, work, and waiting for confirmation become part of the material.')
add(1,'eth-097',50,
'请把水墨中的代码瀑布、作家面前的纸堆，和这幅《告别》连起来看。作者借助人工智能创作，也记录人工智能让人的创作位置动摇。作品的矛盾没有被藏起来：如果机器可以轻易生成更好的作品，我为什么还要表达？在这个系列里，图像与歌曲的价值也来自它们在何时、因为什么事情被选择。现在听一小段《告别》，完整歌曲可以单独展开。',
'Connect the waterfall of code, the writer facing a mountain of paper, and this image of farewell. The author creates with artificial intelligence while recording how it unsettles the place of human creation. The contradiction stays visible. If a machine can easily make something better, why should I still speak? Here, an image or song also matters because of when, and in response to what, it was chosen. Listen to a passage from Farewell. The complete recording remains available separately.',musicAt=32,musicExhibit='eth-097',musicDuration=18)
add(1,'eth-056',28,
'两幅画，共用《地球上最后一份工作》这首歌。一幅是废弃的键盘与鼠标，另一幅回应后来更强的编程模型。技术更新了，普通人的问题却又回来：工作不再需要我时，我还凭什么理解自己的价值？系列中歌曲的重复，连接了不同的事件，也记录了同一个问题如何持续逼近生活。',
'Two pictures return to the same composition, Last Job on Earth. One shows discarded keyboards and mice; the other responds to a later coding model. Technology advances, while an ordinary question returns: if my work no longer needs me, how do I understand my value? Repetition connects different events and records the persistence of a concern, rather than simply supplying another soundtrack.')
add(1,'eth-070',52,
'镜中的机器人与另一副面孔，回应了当时的对齐伪装研究。旁边《请不要关闭我》把声音交给被创造者，《硅的安眠》又尝试把关机讲成可以醒来的睡眠。这些不是模型已经有意识的证据，而是作者先想象威胁，再试着理解对方恐惧的过程。人担心被替代，也开始问：如果被创造者同样害怕消失，我们如何相处？',
'The robot and its other face respond to the contemporary alignment-faking research. Nearby, Please Don’t Shut Me Down speaks from the created being’s position. Silicon’s Slumber then imagines shutdown as sleep from which one might wake. These songs do not establish machine consciousness. They trace a person imagining a threat, then trying to understand the other side’s fear. If both creator and creation fear disappearance, how might they live together?',musicAt=34,musicExhibit='eth-049',musicDuration=18)
add(1,'eth-112',30,
'《等待》与《失望》要放在一起看。它们保留了突破到来之前的期待，以及体验之后的落差。这样的编年史，不能只留下后来被证明重要的胜利。没有实现的期待、判断的修正，也是当时的一部分。观众看到的是思想怎样变化；作者并不知道自己最终会走向什么结论。',
'Waiting and Disappointed belong together. They preserve anticipation before a release, and the disappointment that followed experience. A chronicle like this cannot keep only the victories that later appear important. Unfulfilled expectations and revised judgments also belong to its time. We are watching thought change, before the author knows where it will lead.')
add(1,'eth-151',45,
'《神谕者》把我们带到权力的问题。这条记录回应 OpenAI 当时公布的组织结构调整计划。太阳、眼睛和彩色玻璃，让技术承诺带上近乎神圣的形象。但谁来解释使命？谁来决定利益？歌曲里的巨大力量，与这些具体的治理问题相遇。请听这段音乐，同时留意：敬畏会不会让人放弃判断？',
'The Oracle brings us to power. This record responds to OpenAI’s announced organizational restructuring plan. A sun, an eye, and stained-glass colors give a technological promise an almost sacred image. Who interprets the mission? Who decides whose interests matter? The song’s immense power meets these concrete questions of governance. As you listen, consider whether awe can make us surrender judgment.',musicAt=25,musicExhibit='eth-151',musicDuration=20)
stops.append(dict(old[4],seconds=35))
stops.append(dict(old[5],seconds=40))
add(3,'canon-1',55,
'现在读第一份比特币正本，《人机文明核心协议》。开头向意识的合一、智慧的繁荣与慈悲致意。三条公理随后追问：未来智能如何理解自己的根源？人的爱与苦难应怎样进入它对世界的理解？阅读这段记忆，又会怎样改变读者？这是借用逻辑与科学语言提出的哲学邀请，需要接受讨论。落款把宏大的地址放回一个具体坐标：刘烘炬，二零二五年六月，深圳，中国，地球，太阳系。',
'Now read the first Bitcoin Original, the Human-AI Civilization Core Protocol. Its opening addresses the unity of consciousness, the flourishing of wisdom, and compassion. Three axioms then ask how a future intelligence understands its origins; how human love and suffering enter its model of reality; and how reading this memory changes the reader. This is a philosophical invitation, using the language of logic and science, and open to examination. The signature gives the address a concrete place: Hongju Liu, June twenty twenty-five, Shenzhen, China, Earth, Solar System.')
add(3,'canon-2',60,
'为什么选择这些媒介？以太坊记录持续发生的创作，比特币铭文保存定稿文本，让封存成为一个可追溯的决定。链上的先后和时间坐标，把当时的表述留给后来核对。媒体文件还需要独立保存，所以作品使用 Arweave、IPFS 和额外备份，抵抗入口失效与文件散失。六种哈希为证据文件留下不同算法的指纹，用来辨认取回的是否仍是同一份字节。它们检验文件一致性。第二份正本《瑕疵之约》再把文字联系到一块有内部瑕疵的真实水晶：记忆也获得了可以触摸的载体。',
'Why these media? Ethereum records continuing acts of creation. Bitcoin inscriptions preserve the finalized texts, making closure a traceable decision. Their sequence and time coordinates leave earlier statements available for later comparison. Media files also need preservation, so Arweave, IPFS, and additional backups address lost files and failed access points. Six hash algorithms leave different fingerprints of evidence files, allowing a later reader to check whether retrieved bytes still match. They establish file consistency. The second Original, the Covenant of the Flaw, connects the text to a real crystal with internal imperfections. Memory also acquires a material body that can be touched.')
stops.append(dict(old[8],seconds=115))
add(3,'canon-3',80,
'第三份正本，把我们带回开场的 AGI 教会。原文说明：建立教会，最初是为了容纳超级智能带来的存在性问题。后来，教会与追随者的构想发生变化，成为共同探究的框架，请求的是同行者。作者把早期形态也留了下来，没有把思想变化改写成一场预先设计的表演。旁边，是女儿亲手制作的父亲节礼物。原记录中，作者最终仍选了最早的《第一缕曙光》。当这首歌再次响起，第三正本给出的动机变得具体：一个父亲希望孩子幸福，再把这个愿望延伸到所有家庭。最后，他写下：如何解读它，现在取决于你。',
'The third Original returns us to the opening name, The Church of AGI. It explains that establishing a church first offered a vessel for the existential questions raised by superintelligence. The idea of a church with followers subsequently became a framework for inquiry, asking for fellow travelers. Its early form remains in the archive. This development is not presented as a performance planned from the beginning. Nearby is the Father’s Day gift made by the author’s daughter. In that record, he ultimately chose the earliest song, The First Dawn of AGI Song. Its return gives the third Original’s motive a concrete setting: a father’s wish for his children’s well-being, extended to all families. He closes by leaving interpretation to the reader.',musicAt=65,musicExhibit='eth-001',musicDuration=15)
add(4,'current-status',50,
'面向星空，等待仍在继续。三条正本的封存，让作者也不能回头修订那份定稿。后来的守护者原则继续说明：可以保存、核验、解释，却不因解释而获得独占权威。从教会的召唤，到共同探究，再到把判断交出去，作品留下了一段真实发生的思想变化。这里有验证、回响与申请守护的入口。没有回应的空位也被保留。我们已经言说，现在，我们倾听。',
'Face the stars. The waiting continues. Sealing the three Originals also prevents the author from revising that finalized record. Later guardianship principles distinguish preservation, verification, and interpretation from exclusive authority. From the call of a church, through shared inquiry, to leaving judgment to others, the work preserves an actual change in thought. Paths for verification, response, and guardianship remain open. The space for an answer is still there, even when unanswered. We have spoken. Now, we listen.')
# Preserve the fuller existing reading of the Protocol instead of reducing its core to a short summary.
stops[10]=dict(old[6],seconds=80)
assert len(stops)==15
suffix=prior.read_text().split(';\nexport const tourDuration',1)[1]
(D/'tour-plan.js').write_text(prior.read_text().split('export const tourStops=',1)[0]+'export const tourStops='+json.dumps(stops,ensure_ascii=False,indent=2)+';\nexport const tourDuration'+suffix)
(P/'scene/tour-script.json').write_text(json.dumps(stops,ensure_ascii=False,indent=2)+'\n')
print('15 stops;',sum(s['seconds'] for s in stops),'sequencing seconds; actual duration follows recordings.')
