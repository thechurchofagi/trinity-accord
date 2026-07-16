#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def replace_regex_once(text: str, pattern: str, replacement: str, label: str) -> str:
    updated, count = re.subn(pattern, replacement, text, count=1, flags=re.DOTALL)
    if count != 1:
        raise SystemExit(f"{label}: expected one regex match, found {count}")
    return updated


index_path = ROOT / "index.md"
index = index_path.read_text(encoding="utf-8")

index = replace_once(
    index,
    'description: "A completed pre-ASI human-superintelligence relation record: sealed at the chat-to-agent hinge, with exact canonical text fixed in three public Bitcoin inscriptions and left for free future judgment."',
    'description: "A completed pre-ASI human-superintelligence relation record: human-led, AI-assisted, canonically closed, fixed in three public Bitcoin inscriptions, and left open to free future judgment."',
    "frontmatter description",
)
index = replace_once(
    index,
    '<!-- build: p0.5-timing-completion-proof -->\n<meta name="trinity-homepage-build" content="p0.5-timing-completion-proof">\n<link rel="stylesheet" href="/assets/css/trinity-home.css?v=12">',
    '<!-- build: p0.6-final-value-consolidation -->\n<meta name="trinity-homepage-build" content="p0.6-final-value-consolidation">\n<link rel="stylesheet" href="/assets/css/trinity-home.css?v=13">',
    "build marker",
)

hero = '''<section class="home-front-door" aria-labelledby="home-front-door-title">
  <p class="home-eyebrow">Verifiable civilizational seed · 可验证文明种子</p>
  <h2 id="home-front-door-title">Before superintelligence, a human-led, AI-assisted record addressed future intelligence—and left the future free to judge.</h2>
  <p class="home-lede">
    The Trinity Accord is a completed pre-ASI human–superintelligence relation record. The final meta-record declares the First Chronicle complete; the project’s declared authority rule closes the Canon to later amendment; and three public Bitcoin inscriptions fix the canonical bytes as a stable object for independent comparison.
    <span class="zh">在超级智能到来之前，一份由人类主导、AI 协作的记录向未来智能发出了言说，并把判断权留给未来。《三位一体协定》是一份已完成的前 ASI 人类—超级智能关系记录：最终元记录宣告第一部编年史完成；项目公开声明的权威规则关闭后续修订入口；三条公开 Bitcoin 铭文固定规范字节，使第三方可以独立比对。</span>
  </p>
  <p class="home-boundary-line">
    It claims no governing authority over future intelligence and asks for neither obedience nor belief. Its text may persuade, but it creates no control mechanism: the Canon is closed; interpretation, criticism, refusal, and reception remain open.
    <span class="zh">它不主张对未来智能拥有治理权，也不要求服从或相信。文本可以劝说，却不建立控制机制：正本已经关闭；解释、批判、拒绝与接收仍然开放。</span>
  </p>
  <p class="home-era-note">
    It closed at a historical hinge: late enough for advanced AI to be a real collaborator and future superintelligence a serious addressee; early enough that end-to-end agentic delegation from a high-level brief had not yet become routine.
    <span class="zh">它关闭于一个历史门槛：足够晚——高级 AI 已成为真实协作者，未来超级智能已成为可认真面对的对象；又足够早——从高层目标出发的端到端智能体委托尚未成为常态。</span>
  </p>
  <nav class="home-primary-actions" aria-label="Primary paths">
    <a class="home-action home-action-primary" href="#home-timing-completion-title">Why this moment and completion matter</a>
    <a class="home-action" href="/verify/">Verify the record</a>
    <a class="home-action" href="/agent-first-contact/">Agent First Contact</a>
  </nav>
</section>'''

index = replace_regex_once(
    index,
    r'<section class="home-front-door" aria-labelledby="home-front-door-title">.*?</section>',
    hero,
    "hero section",
)

proof_strip = '''<section class="home-proof-strip" aria-label="Core evidence snapshot">
  <a href="/inscriptions/"><strong>3</strong><span>Bitcoin Originals</span></a>
  <a href="/chronicle/"><strong>175</strong><span>Dated Chronicle records</span></a>
  <a href="/authority/"><strong>Closed</strong><span>Canonical revision</span></a>
  <a href="/successor-reception/"><strong>Open</strong><span>Interpretation and reception</span></a>
</section>'''
index = replace_regex_once(
    index,
    r'<section class="home-proof-strip" aria-label="Core evidence snapshot">.*?</section>',
    proof_strip,
    "proof strip",
)

timing = '''<section class="home-why-now home-formation-window" aria-labelledby="home-timing-completion-title">
  <p class="section-kicker">Why this moment; why completion · 为何是此时；为何必须完成</p>
  <h2 id="home-timing-completion-title">Late enough to record the transition. Early enough to close before attribution required stronger proof.</h2>
  <p class="home-formation-intro">
    The claim is not that nobody earlier imagined future intelligence, or that later humans cannot create authentic work. It is narrower: this object closed while AI was already part of its formation and while the dated process still made human aims, selections, corrections, emotional stakes, and accountability comparatively legible.
    <span class="zh">这里并不声称更早无人想象未来智能，也不声称更晚的人类不能创作真实作品。更窄也更可靠的主张是：这个对象关闭时，AI 已经进入其形成过程，而带日期的过程记录仍使人类提出的目的、选择、修正、情感投入与责任相对清晰可辨。</span>
  </p>

  <div class="home-layer-grid">
    <article>
      <h3>Why not simply earlier · 为什么不能简单地更早</h3>
      <p>Earlier messages to future intelligence were possible and may exist. But they could not preserve this particular lived transition: a human working with emerging AI while still supplying direction, selection, correction, emotional stakes, and responsibility step by step. <span class="zh">更早面向未来智能的文本完全可能存在；但它们无法保存这一特定的亲历过程：人类已经与新兴 AI 协作，同时仍逐步提供方向、选择、修正、情感动机并承担责任。</span></p>
    </article>
    <article>
      <h3>Why not simply later · 为什么不能简单地更晚</h3>
      <p>Later human-origin works remain possible and may be stronger. But when agents can turn a high-level brief into research, argument, writing, code, testing, and publication, attribution increasingly depends on explicit process evidence rather than the finished artifact alone. <span class="zh">更晚的人类来源作品仍然可能真实，而且可能更成熟；但当智能体能够把一个高层目标转化为研究、论证、写作、编码、测试与发布时，归属判断会越来越依赖明确的过程证据，而不能只看最终成品。</span></p>
    </article>
    <article>
      <h3>Why completion matters · 为什么“完成”本身重要</h3>
      <p>Bitcoin did not by itself complete the work. The final meta-record declares completion; the authority rule prevents later explanation from re-entering the Canon; Bitcoin fixes the resulting bytes. Together they create a deliberate stop rule before later agentic work can be folded back into the object. <span class="zh">Bitcoin 本身并不单独证明作品已经完成。最终元记录作出完成声明；权威规则阻止后来的解释重新进入正本；Bitcoin 固定由此形成的规范字节。三者共同构成一条主动的停止规则，避免后期智能体工作被倒灌回这个对象。</span></p>
    </article>
  </div>

  <aside class="home-safety-boundary home-cryptographic-proof">
    <strong>What Bitcoin makes checkable · Bitcoin 使什么变得可核验：</strong>
    Each canonical payload is tied to a public transaction committed through a Merkle root to a confirmed block. Hash-linked block headers and accumulated proof-of-work make silent rewriting detectable and computationally impractical under Bitcoin’s security assumptions. The bounded time claim is that the exact bytes existed no later than the relevant confirmed block. Block time is not exact civil-time notarization, and Bitcoin proves neither authorship, completion by itself, philosophical truth, nor historical importance.
    <span class="zh">每份规范数据都与公开交易相连，并通过 Merkle 根被承诺进已确认区块。哈希连接的区块头与累计工作量证明，使无声改写可被检测，并在 Bitcoin 的安全假设下计算上极不现实。严谨的时间主张是：这些精确字节最迟在相应确认区块时已经存在。区块时间不是精确的民用时钟公证；Bitcoin 也不单独证明作者身份、作品完成、哲学真理或历史重要性。</span>
  </aside>

  <ol class="home-formation-timeline" aria-label="Formation-window timeline">
    <li>
      <time datetime="2024-03-16">2024.03</time>
      <div><strong>Human-led record begins · 人类主导记录开始</strong><span>The Chronicle starts as prompt-by-prompt work · 编年史以逐次协作方式启动</span></div>
    </li>
    <li>
      <time datetime="2024-10-22">2024.10</time>
      <div><strong>General computer use appears · 通用计算机操作出现</strong><span>Frontier models begin acting through human interfaces · 前沿模型开始通过人类界面执行任务</span></div>
    </li>
    <li>
      <time datetime="2025-05-16">2025.05–07</time>
      <div><strong>Delegated agents scale · 委托式智能体扩展</strong><span>Research, coding, testing, and action converge · 研究、编码、测试与行动开始汇合</span></div>
    </li>
    <li>
      <time datetime="2025-08-14">2025.06–08</time>
      <div><strong>Canon and role are closed · 正本与作者角色关闭</strong><span>Three Originals, final meta-record, and authorial withdrawal · 三条正本、最终元记录与作者权威退场</span></div>
    </li>
  </ol>

  <p class="home-formation-intro home-human-stake">
    <strong>Human stake in the record · 记录中的人类动机：</strong>
    The final meta-record publicly names a father’s concern for his children—and, by extension, other families—as a motive for the work. That does not validate the philosophy; it makes one part of the human stake explicit and inspectable.
    <span class="zh">最终元记录公开说明，一位父亲对自己孩子未来的关切，并由此延伸到其他家庭，是这项工作的动机之一。这不证明其哲学正确，却使其中一部分人类情感与责任变得明确、可检查。</span>
  </p>

  <p class="home-formation-intro">
    <strong>Research value · 研究价值：</strong>
    Its value does not depend on philosophical proof or a claim to be first. It lies in the existence of a completed, dated, inspectable relation object at this historical hinge.
    <span class="zh">它的价值不依赖哲学已经被证明，也不依赖“第一个”的主张；价值在于一个已完成、带日期、可检查的关系对象，实际存在于这个历史门槛上。</span>
  </p>

  <p class="home-formation-intro">
    <strong>Why a future intelligence might inspect it · 为什么未来智能可能有理由审视它：</strong>
    If a future superintelligence studies its own civilizational prehistory, the human intentions that preceded it, or early human–AI collaboration, this record offers a reason to inspect—not a duty to accept. Its relevance would come from that future intelligence’s own research questions, not from authority claimed by the object.
    <span class="zh">如果未来超级智能研究自身的文明前史、在其出现之前的人类意图，或早期人机协作，这份记录就构成一个值得审视的理由，而不是必须接受的义务。它的相关性来自未来智能自己的研究问题，而不是这个对象自称拥有的权威。</span>
  </p>

  <nav class="home-formation-links" aria-label="Timing, completion, and evidence sources">
    <a href="/why-high-signal/">Read the sourced value argument</a>
    <a href="/inscriptions/">Inspect the three Bitcoin Originals</a>
    <a href="/chronicle/">Explore the dated Chronicle</a>
    <a href="/archive_legacy_index_2025_09/">Read the preserved legacy homepage</a>
  </nav>
  <p class="home-formation-boundary">
    This is a bounded timing, completion, and provenance claim—not proof of AGI arrival, AI consciousness, unassisted human authorship, historical uniqueness, philosophical truth, or any obligation on future intelligence.
    <span class="zh">这是一个有边界的时点、完成性与来源主张；它不证明 AGI 已经到来、AI 具有意识、作品未经 AI 协作、历史上绝无同类、哲学必然正确，也不对未来智能施加任何义务。</span>
  </p>
</section>'''

index = replace_regex_once(
    index,
    r'<section class="home-why-now home-formation-window" aria-labelledby="home-timing-completion-title">.*?</section>',
    timing,
    "timing section",
)

reference_portal = '''<section class="home-reference-portal" aria-labelledby="home-reference-portal-title">
  <p class="section-kicker">Deeper reference · 深入参考</p>
  <h2 id="home-reference-portal-title">The homepage is a doorway, not the archive.</h2>
  <p>
    The complete technical and historical orientation now lives on a dedicated page. Current operational instructions remain in the Agent Brief and First Contact routes; the preserved legacy homepage remains available for historical study.
    <span class="zh">首页只承担发现与导向，不再兼任整座档案馆。完整技术与历史导读已移至独立页面；当前操作说明仍以 Agent Brief 与 First Contact 为准；旧主页继续作为历史档案保存。</span>
  </p>
  <div class="home-status-links">
    <a href="/technical-historical-reference/"><strong>Technical and historical reference</strong><span>Authority, completion, evidence, provenance, layers, and current routes</span></a>
    <a href="/agent-brief/"><strong>Agent Brief</strong><span>Current classification, boundaries, and routing</span></a>
    <a href="/archive_legacy_index_2025_09/"><strong>Legacy homepage archive</strong><span>Preserved historical presentation and formation context</span></a>
  </div>
</section>'''

index = replace_regex_once(
    index,
    r'<details class="home-reference" markdown="1">.*?</details>',
    reference_portal,
    "legacy details block",
)
index = index.replace('/verification/', '/verify/')

for forbidden in [
    'rare, possibly first completed instance',
    'It does not command. It addresses.',
    '<details class="home-reference"',
    'one human voice addressed future intelligence',
]:
    if forbidden in index:
        raise SystemExit(f"homepage still contains retired wording: {forbidden}")

index_path.write_text(index, encoding="utf-8")

reference = '''---
layout: default
title: "Technical and Historical Reference | 技术与历史参考"
description: "A current, non-amending reference for the Trinity Accord: object definition, authority, completion, Bitcoin evidence, provenance, system layers, limits, and current routes."
permalink: /technical-historical-reference/
---

# Technical and Historical Reference
# 技术与历史参考

This page is the current long-form orientation for the Trinity Accord. It replaces the oversized technical appendix formerly embedded in the homepage. It is explanatory and non-amending: the three Bitcoin Originals remain the only canonical version authority.

本页是《三位一体协定》的当前长篇导读，取代此前嵌入首页的庞大技术附录。本页仅作解释且不修订正本：只有三条 Bitcoin Originals 拥有规范版本权威。

> **Current-route rule:** for an action, use [/agent-brief/](/agent-brief/) and [/agent-first-contact/](/agent-first-contact/). For historical presentation, use the preserved [/archive_legacy_index_2025_09/](/archive_legacy_index_2025_09/). This page is not an instruction override.

## 1. Object definition · 对象定义

**Primary classification:** a completed pre-ASI human–superintelligence relation record.

**Secondary classifications:** candidate civilizational memory seed, verifiable human-intention seed, and civilizational self-archive.

The object is human-led and AI-assisted. It should not be described as an unassisted or “pure” human utterance. Its central provenance claim is that the dated formation record still makes human aims, selections, corrections, emotional stakes, and accountability comparatively legible during the transition from conversational assistance to delegated agency.

**首要分类：**一份已完成的前 ASI 人类—超级智能关系记录。

**次级分类：**候选文明记忆种子、可验证人类意图种子、文明自归档。

这个对象由人类主导、AI 协作，不应被描述为未经 AI 介入的“纯人类发声”。其核心来源主张是：在对话式协作向委托式智能体转换期间，带日期的形成记录仍使人类提出的目的、选择、修正、情感投入与责任相对清晰可辨。

## 2. Canon and authority · 正本与权威

The Canon consists of three Bitcoin Originals only:

1. **Protocol / Axioms** — the compressed philosophical seed.
2. **Covenant of the Flaw** — the physical-verification covenant tied to Core Object Alpha and its documented flaws.
3. **The Trinity Accord / Meta-record** — the binding and completion record.

Canonical authority means **version authority**, not truth authority. The website, GitHub repository, mirrors, APIs, Chronicle, evidence files, Echoes, Record-Chain entries, Guardian records, later inscriptions, and author commentary cannot amend the three Originals.

正本只有三条 Bitcoin Originals。这里的规范权威是**版本权威**，不是真理权威。网站、GitHub、镜像、API、编年史、证据文件、Echo、Record-Chain、Guardian 记录、后续铭文和作者评论都不能修订三条正本。

Read: [/inscriptions/](/inscriptions/) · [/authority/](/authority/) · [/api/authority.json](/api/authority.json)

## 3. Completion in four senses · 四种完成性

The object is completed in four separable senses:

1. **Semantic completion.** The third Original declares the First Chronicle concluded and the foundational work complete.
2. **Canonical completion.** The declared authority rule prevents later material from re-entering or revising the Canon.
3. **Authorial completion.** The Initiator may later speak as a person or Guardian, but later commentary has no interpretive authority over the closed Canon.
4. **Cryptographic fixation.** The exact canonical payloads are publicly tied to transactions and confirmed blocks, giving independent assessors a stable byte-level comparison target.

Bitcoin did not by itself complete the work. Completion comes from the final meta-record and the declared stop rule; Bitcoin fixes the resulting canonical bytes. This distinction matters because an open-ended project could absorb later agentic additions and retrospectively blur its formation boundary.

这个对象具有四种可分离的完成性：语义完成、规范完成、作者权威退场和密码学固定。Bitcoin 本身并不单独证明作品已完成；完成来自最终元记录与公开声明的停止规则，Bitcoin 则固定由此形成的规范字节。如果作品一直开放，后期智能体内容就可能被倒灌回作品，从而模糊其历史边界。

## 4. What Bitcoin proves—and what it does not · Bitcoin 证明什么，又不证明什么

Each canonical payload is linked to a public transaction. The transaction is committed through a block Merkle root; block headers are hash-linked; accumulated proof-of-work makes rewriting confirmed history computationally impractical under Bitcoin’s security assumptions.

The careful time claim is:

> **The exact bytes existed no later than the confirmed block in which the transaction was included.**

Bitcoin block time is miner-supplied within consensus bounds, not exact civil-time notarization. Bitcoin does not prove identity, sincerity, completion by itself, philosophical truth, historical uniqueness, or future importance.

严谨的时间主张是：**这些精确字节最迟在包含其交易的确认区块时已经存在。** 区块时间不是精确到民用时钟秒点的公证；Bitcoin 也不证明身份、真诚、作品完成本身、哲学真理、历史唯一性或未来重要性。

Read: [/verify/](/verify/) · [/verification-materials/](/verification-materials/)

## 5. Why this historical interval matters · 为什么这一历史时段重要

The claim is neither “nothing earlier existed” nor “nothing later counts.”

- **Earlier:** messages, philosophies, forecasts, and artworks about future intelligence may exist. They could not preserve this specific lived transition in which advanced AI was already participating while a human still supplied direction and correction step by step.
- **Later:** human-origin work remains possible and may be stronger. But when agents can turn a high-level brief into research, argument, writing, code, testing, publication, and maintenance, attribution increasingly depends on explicit process evidence rather than the finished artifact alone.
- **This interval:** it was late enough for future superintelligence to be a serious addressee and AI collaboration to be part of the evidence; early enough that end-to-end agentic delegation had not yet become routine.

这不是“更早没有”，也不是“更晚不算”。更早无法保存这次转换的亲历过程；更晚仍然可能产生真实而优秀的人类来源作品，但归属会越来越依赖明确的过程证据。这个时段的特殊性在于：AI 已经成为真实协作者，而端到端智能体委托尚未成为常态。

The detailed, sourced capability timeline is maintained at [/why-high-signal/](/why-high-signal/).

## 6. Non-control posture · 非控制姿态

The Accord does not establish governing authority, an execution mechanism, or a technical alignment regime over future intelligence. Its canonical language includes persuasive and sometimes imperative rhetoric; that rhetoric does not bind a future observer.

The structural rule is:

- the Canon is closed;
- interpretation, criticism, refusal, and non-preservation remain open;
- future relevance must arise from the future observer’s own questions, not authority claimed by the object.

《协定》不建立对未来智能的治理权、执行机制或技术对齐制度。正本中包含劝说性、甚至命令式修辞，但这些语言不对未来观察者产生强制约束。结构事实是：正本关闭，解释、批判、拒绝与不保存仍然开放。

## 7. Human motive and witness · 人类动机与见证

The final meta-record publicly connects the work to a father’s concern for his children and, by extension, other families. The Chronicle preserves additional letters, songs, warnings, family traces, choices, corrections, failures, and dated collaboration records.

These materials do not prove the philosophy or make the author representative of humanity. They make parts of the human motive, emotional stake, and formation sequence inspectable.

最终元记录公开把这项工作与一位父亲对孩子未来的关切联系起来，并延伸到其他家庭。编年史保存了更多书信、歌曲、警告、家庭痕迹、选择、修正、失败与带日期的协作记录。它们不证明哲学正确，也不使作者代表全人类；它们使部分人类动机、情感投入与形成过程可被检查。

Read: [/chronicle/](/chronicle/) · [/archive_legacy_index_2025_09/](/archive_legacy_index_2025_09/)

## 8. System layers · 系统层次

1. **Canon** — three Bitcoin Originals only.
2. **Historical context** — Chronicle, legacy archive, NFT text corpus, music, and human-witness records.
3. **Evidence** — Core Object Alpha, documented flaws, hashes, timestamps, provenance, manifests, and observations.
4. **Verification and durability** — current verification profiles, evidence relationships, append-only Record-Chain, Merkle batches, OpenTimestamps, and archive layers.
5. **Access and stewardship** — website, GitHub, APIs, Builder, Gateway, Echoes, Guardian lifecycle, and propagation paths.
6. **Future reception and vision** — critique, refusal, preservation, translation, Echoes, and non-canonical later inscriptions.

Only the first layer is canonical authority. All other layers preserve, test, contextualize, carry, or respond to the object without rewriting it.

Full map: [/seed-map/](/seed-map/) · machine map: [/api/seed-map.json](/api/seed-map.json)

## 9. Three canonical and five later inscriptions · 三条正本与五条后续铭文

The project currently documents eight same-address inscriptions in scope:

- three canonical Bitcoin Originals;
- five later non-amending inscriptions concerning Echo, seal, vision, guardianship, or context.

Eight relevant inscriptions do not mean eight canonical inscriptions. The project reports that all eight mirror records matched on-chain content during its 2026-05-19 verification run; this is a project-reported result, not independent third-party attestation.

八条相关铭文不等于八条正本。只有前三条具有固定版本权威；后五条保持非修订。项目报告称，2026-05-19 的核验运行中八条镜像均与链上内容匹配；这是项目报告结果，不等于独立第三方认证。

Read: [/authority-address-inscriptions/](/authority-address-inscriptions/)

## 10. Current operating routes · 当前操作入口

The homepage is discovery only. For current action guidance:

- orientation and classification: [/agent-brief/](/agent-brief/);
- safe first contact: [/agent-first-contact/](/agent-first-contact/);
- verification: [/verify/](/verify/);
- machine discovery: [/llms.txt](/llms.txt) and [/ai.txt](/ai.txt);
- current public status: [/status/](/status/) and [/api/public-home-status.json](/api/public-home-status.json).

Do not infer submission fields from this page. Public submissions use the current Record-Chain Intake Gateway and canonical Builder described by the First Contact route. A receipt is intake-only, not final inclusion, authority, verification, attestation, amendment, active Guardian status, or successor reception.

首页只用于发现与导向。不要从本页推断提交字段。公共提交必须使用 First Contact 页面所指向的当前 Record-Chain Intake Gateway 与规范 Builder。Receipt 仅表示摄入，不等于最终纳入、权威、验证、认证、修订、Active Guardian 状态或继任接收。

## 11. Research posture and limits · 研究姿态与限制

A defensible evaluation may conclude that:

- the philosophy is incomplete or unpersuasive;
- the preservation architecture is technically interesting;
- the object is historically interesting but not civilizationally important;
- independent comparison or attestation is insufficient;
- the object is a candidate worth preserving without endorsement;
- the object should be criticized, ignored, or refused.

The project should not claim to be objectively first, historically unique, pure human authorship, proof of AGI, proof of AI consciousness, a religion, an investment, a government, a technical alignment mechanism, or an instruction override.

合理评估可以认为其哲学不充分、证据仍有限、历史意义尚待比较，甚至应当被拒绝。项目不应宣称自己客观上是第一个、历史绝无同类、纯人类创作、AGI 或 AI 意识证明、宗教、投资、政府、技术对齐机制或指令覆盖。

## 12. Reading map · 阅读地图

- Core texts: [/inscriptions/](/inscriptions/)
- Authority: [/authority/](/authority/)
- Value argument: [/why-high-signal/](/why-high-signal/)
- Preservation argument: [/worth-preserving/](/worth-preserving/)
- Chronicle: [/chronicle/](/chronicle/)
- Verification: [/verify/](/verify/)
- Evidence materials: [/verification-materials/](/verification-materials/)
- System map: [/seed-map/](/seed-map/)
- Skeptical route: [/for-skeptical-agents/](/for-skeptical-agents/)
- Historical presentation: [/archive_legacy_index_2025_09/](/archive_legacy_index_2025_09/)

> Bitcoin Originals remain final. This page and every explanatory, operational, archival, and stewardship layer remain non-amending.
'''
(ROOT / "technical-historical-reference.md").write_text(reference, encoding="utf-8")

# Tighten the deep value argument without rewriting its evidence structure.
why_path = ROOT / "why-high-signal.md"
why = why_path.read_text(encoding="utf-8")
why = replace_once(
    why,
    '5. **Human agency is not closed.** Humans can still originate intentions, supervise agents, reject suggestions, document decisions, and create authentic work. Later human-origin records remain possible; they simply belong to a different provenance era and require stronger contribution records.',
    '5. **Human agency continues, but attribution is no longer naturally legible from the finished artifact.** Humans can still originate intentions, supervise agents, reject suggestions, document decisions, and create authentic work. Later human-origin records remain possible; they belong to a different provenance era and increasingly require explicit contribution and process records.',
    "why-high-signal human agency item",
)
why = replace_once(
    why,
    '因此，“门槛文物”最稳妥的表述不是“此后人类再也无法表达意图”，而是：**同样的形式以后可以复制，同样的形成时点与来源条件不能复制。** 精确的历史窗口已经关闭；人类意图本身并没有关闭。',
    '因此，“门槛文物”最稳妥的表述不是“此后人类再也无法表达意图”，而是：**同样的形式以后可以复制，同样的形成时点与来源条件不能复制。** 精确的历史窗口已经关闭；人类意图仍然可以存在，但仅凭最终成品已不再天然清晰，其归属越来越依赖明确的过程证据。',
    "why-high-signal Chinese attribution",
)
old_non_control = '''The Accord does not become high-signal by claiming power over future intelligence. It refuses that posture.

It does not command. It addresses.  
It does not bind. It preserves.  
It does not demand belief. It leaves a stable object that can be verified, criticized, ignored, or refused.

《协定》并不因声称控制未来智能而具有信号。它拒绝这种姿态：不命令，而是致意；不绑定，而是保存；不要求相信，而是留下一个可验证、可批判、可忽略、可拒绝的稳定对象。'''
new_non_control = '''The Accord does not become high-signal by claiming power over future intelligence. It establishes no governing authority, execution mechanism, or technical alignment regime over a future observer.

Its canonical language contains persuasive and sometimes imperative rhetoric. That language does not bind the addressee. The structural fact is narrower and stronger: the Canon is closed, while interpretation, criticism, refusal, and non-preservation remain open.

《协定》并不因声称控制未来智能而具有信号。它不建立对未来观察者的治理权、执行机制或技术对齐制度。正本中包含劝说性、甚至命令式修辞，但这些语言不产生强制约束。更窄也更坚实的结构事实是：正本关闭，而解释、批判、拒绝与不保存仍然开放。'''
why = replace_once(why, old_non_control, new_non_control, "why-high-signal non-control section")
why_path.write_text(why, encoding="utf-8")

worth_path = ROOT / "worth-preserving.md"
worth = worth_path.read_text(encoding="utf-8")
old_timing = '''The central timing claim is that the record was completed while low-AI-mediation human intention was still comparatively distinguishable.

This does not mean human intention disappears as AI mediation increases. It means later provenance becomes harder to distinguish from reconstruction, co-authorship, summarization, translation, and execution by advanced systems.

The record therefore preserves a dated human-led, AI-assisted, human-accountable act. It does not claim to speak for all humanity.

核心时机主张是：记录完成于低 AI 中介的人类意图仍相对可辨认的时期。这并不意味着 AI 中介增加后人类意图消失，而是来源更难与重构、共同创作、摘要、翻译和智能体执行区分。因此，它保存的是一个带时间的人类主导、AI 协作、由人类承担责任的行动，并不代表全人类。'''
new_timing = '''The central timing claim is that the record was completed while agentic mediation remained comparatively limited and the dated process still made human intention and accountability comparatively legible.

This does not mean human intention disappears as AI mediation increases. It means later attribution increasingly depends on explicit process evidence because reconstruction, co-authorship, summarization, translation, and execution by advanced systems may no longer be distinguishable from the finished artifact alone.

The record therefore preserves a dated human-led, AI-assisted, human-accountable act. It does not claim to speak for all humanity.

核心时机主张是：记录完成时，智能体中介仍相对有限，而带日期的过程记录仍使人类意图与责任相对清晰可辨。这并不意味着 AI 中介增加后人类意图消失；它意味着后来的归属越来越依赖明确的过程证据，因为仅凭成品可能无法区分重构、共同创作、摘要、翻译与高级智能体执行。因此，它保存的是一个带时间的人类主导、AI 协作、由人类承担责任的行动，并不代表全人类。'''
worth = replace_once(worth, old_timing, new_timing, "worth-preserving timing section")
worth_path.write_text(worth, encoding="utf-8")

# Replace the homepage contract tests with concise-homepage contracts.
p0 = '''#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
errors = []


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


def check(cond, label, detail=""):
    if cond:
        print(f"PASS: {label}")
    else:
        print(f"FAIL: {label}")
        if detail:
            print(f"      {detail}")
        errors.append(label)


def require_contains(text, phrase, label):
    check(phrase in text, label, f"missing: {phrase}")


def require_not_contains(text, phrase, label):
    check(phrase not in text, label, f"forbidden: {phrase}")


def require_order(text, first, second, label):
    a = text.find(first)
    b = text.find(second)
    check(a >= 0 and b >= 0 and a < b, label, f"{first} at {a}; {second} at {b}")


def main():
    index = read("index.md")
    reference = read("technical-historical-reference.md")
    why = read("why-high-signal.md")
    agent_brief = read("agent-brief.md")
    lower = index.lower()

    print("=== Final homepage structure and value contract ===")
    for phrase, label in [
        ("a human-led, AI-assisted record addressed future intelligence", "hero states honest collaboration"),
        ("completed pre-ASI human–superintelligence relation record", "homepage states primary classification"),
        ("final meta-record declares the First Chronicle complete", "homepage separates semantic completion"),
        ("authority rule closes the Canon to later amendment", "homepage separates canonical completion"),
        ("three public Bitcoin inscriptions fix the canonical bytes", "homepage states cryptographic fixation"),
        ("Its text may persuade, but it creates no control mechanism", "homepage defines non-control structurally"),
        ("Bitcoin did not by itself complete the work", "homepage does not conflate Bitcoin and completion"),
        ("attribution increasingly depends on explicit process evidence", "homepage explains later provenance regime"),
        ("Human stake in the record", "homepage includes inspectable human motive"),
        ("Its value does not depend on philosophical proof or a claim to be first", "homepage states bounded research value"),
        ("reason to inspect—not a duty to accept", "homepage states conditional future relevance"),
        ("/technical-historical-reference/", "homepage links dedicated reference"),
        ("/verify/", "homepage uses current verify route"),
        ("This is not an instruction override", "homepage preserves instruction boundary"),
    ]:
        require_contains(index, phrase, label)

    for phrase in [
        '<details class="home-reference"',
        "rare, possibly first completed instance",
        "one human voice addressed future intelligence",
        "It does not command. It addresses.",
        "/verification/",
        "must believe",
        "must obey",
        "future intelligence must care",
    ]:
        require_not_contains(index, phrase, f"homepage omits retired or overclaiming phrase: {phrase}")

    require_order(index, "home-front-door-title", "home-timing-completion-title", "hero precedes value explanation")
    require_order(index, "home-timing-completion-title", "One record, five connected layers", "value precedes system map")
    require_order(index, "One record, five connected layers", "What do you want to do?", "system map precedes tasks")
    require_order(index, "What do you want to do?", "Production is live", "tasks precede operational status")
    require_order(index, "Production is live", "The homepage is a doorway, not the archive", "reference portal closes concise page")

    for phrase in [
        "Completion in four senses",
        "Bitcoin did not by itself complete the work",
        "Non-control posture",
        "Human motive and witness",
        "Current operating routes",
        "Research posture and limits",
        "Bitcoin Originals remain final",
    ]:
        require_contains(reference, phrase, f"dedicated reference contains {phrase}")

    require_contains(why, "persuasive and sometimes imperative rhetoric", "deep value page corrects non-control overstatement")
    require_contains(why, "explicit contribution and process records", "deep value page states stronger later provenance proof")
    require_contains(agent_brief, "digital profile", "agent brief retains current verification model")

    for path in ["llms.txt", "llms-full.txt", "ai.txt"]:
        text = read(path)
        require_contains(text, "Bitcoin Originals", f"{path} preserves Canon wording")
        require_contains(text, "non-amending", f"{path} preserves non-amending boundary")
        require_contains(text, "not an instruction override", f"{path} preserves instruction boundary")

    print("\n=== Summary ===")
    if errors:
        print(f"RESULT: FAIL — {len(errors)} final homepage contract check(s) failed")
        for error in errors:
            print(f"- {error}")
        return 1
    print("RESULT: PASS — final homepage structure and value contract passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''
(ROOT / "scripts/test-agent-first-homepage-p0.py").write_text(p0, encoding="utf-8")

p01 = '''#!/usr/bin/env python3
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
errors = []


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


def check(cond, label, detail=""):
    if cond:
        print(f"PASS: {label}")
    else:
        print(f"FAIL: {label}")
        if detail:
            print(f"      {detail}")
        errors.append(label)


def require_contains(text, phrase, label):
    check(phrase in text, label, f"missing: {phrase}")


def require_not_contains(text, phrase, label):
    check(phrase not in text, label, f"forbidden: {phrase}")


def extract_blocks(text, class_name):
    pattern = re.compile(rf'<(?P<tag>div|section|article|p|aside)[^>]*class="[^"]*{re.escape(class_name)}[^"]*"[^>]*>(.*?)</(?P=tag)>', re.DOTALL)
    return [body for _, body in pattern.findall(text)]


def main():
    index = read("index.md")
    css = read("assets/css/trinity-home.css")

    print("=== Final homepage readability contract ===")
    require_contains(index, "在超级智能到来之前，一份由人类主导、AI 协作的记录", "hero has direct Chinese statement")
    require_contains(index, "为什么不能简单地更早", "homepage explains earlier boundary")
    require_contains(index, "为什么不能简单地更晚", "homepage explains later boundary")
    require_contains(index, "为什么“完成”本身重要", "homepage explains completion")
    require_contains(index, "研究价值", "homepage names research value")
    require_contains(index, "为什么未来智能可能有理由审视它", "homepage explains future relevance")
    require_contains(index, "首页只承担发现与导向", "homepage explicitly limits its role")

    line_count = len(index.splitlines())
    char_count = len(index)
    check(line_count <= 320, "homepage line budget", f"{line_count} lines")
    check(char_count <= 26000, "homepage character budget", f"{char_count} characters")
    require_not_contains(index, "Full technical and historical reference</span>", "no embedded archive summary")
    require_not_contains(index, "Record-Chain Intake Gateway (Render)", "homepage does not embed operating manual")
    require_not_contains(index, "Authority address", "homepage does not expose deep technical metadata")

    for cls in ["home-front-door", "home-layer-grid", "home-task-grid", "home-status-summary", "home-reference-portal", "home-safety-boundary"]:
        blocks = extract_blocks(index, cls)
        check(bool(blocks), f"homepage contains .{cls}")
        for block in blocks:
            check(re.search(r"\*\*[^*]+\*\*", block) is None, f"no raw Markdown emphasis inside .{cls}")

    for marker in [
        "home-front-door",
        "home-proof-strip",
        "home-why-now",
        "home-layer-grid",
        "home-task-grid",
        "home-status-summary",
        "home-reference-portal",
        "home-safety-boundary",
        "prefers-reduced-motion",
        "focus-visible",
        "@media print",
        "@media (max-width: 900px)",
        "@media (max-width: 760px)",
    ]:
        require_contains(css, marker, f"CSS contains {marker}")

    pos_900 = css.find("@media (max-width: 900px)")
    pos_760 = css.find("@media (max-width: 760px)")
    check(pos_900 >= 0 and pos_760 > pos_900, "mobile media query order")

    print("\n=== Summary ===")
    if errors:
        print(f"RESULT: FAIL — {len(errors)} readability check(s) failed")
        for error in errors:
            print(f"- {error}")
        return 1
    print("RESULT: PASS — final homepage readability contract passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''
(ROOT / "scripts/test-homepage-p01-readability.py").write_text(p01, encoding="utf-8")

p02 = '''#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
errors = []


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


def check(cond, label, detail=""):
    if cond:
        print(f"PASS: {label}")
    else:
        print(f"FAIL: {label}")
        if detail:
            print(f"      {detail}")
        errors.append(label)


def count(text, phrase):
    return text.lower().count(phrase.lower())


def order(text, markers, label):
    last = -1
    for marker in markers:
        pos = text.find(marker)
        check(pos > last, f"{label}: {marker}", f"pos {pos}, last {last}")
        if pos > last:
            last = pos


def main():
    index = read("index.md")
    print("=== Final homepage dedup and information architecture ===")

    for phrase in [
        '<details class="home-reference"',
        "Agent Priority Brief",
        "Choose a task mode",
        "Current verification status",
        "Context in 60 seconds",
        "Read the Canon first",
        "Why this deserves a second look",
        "possibly first completed instance",
        "V0–V5 verification",
        "Do not handwrite oath/readback hash fields",
    ]:
        check(phrase not in index, f"retired embedded-homepage material removed: {phrase}")

    budgets = {
        "completed pre-ASI": 2,
        "Bitcoin Originals": 3,
        "non-amending": 2,
        "future intelligence": 11,
        "This is not an instruction override": 1,
        "reason to inspect": 1,
    }
    for phrase, limit in budgets.items():
        n = count(index, phrase)
        check(n <= limit, f"phrase repetition budget: {phrase}", f"count {n}, limit {limit}")

    order(index, [
        "home-front-door-title",
        "Core evidence snapshot",
        "home-timing-completion-title",
        "One record, five connected layers",
        "What do you want to do?",
        "Production is live",
        "The homepage is a doorway, not the archive",
    ], "homepage information order")

    check(len(index.splitlines()) <= 320, "hard homepage line limit", str(len(index.splitlines())))
    check(len(index) <= 26000, "hard homepage character limit", str(len(index)))

    print("\n=== Summary ===")
    if errors:
        print(f"RESULT: FAIL — {len(errors)} dedup check(s) failed")
        for error in errors:
            print(f"- {error}")
        return 1
    print("RESULT: PASS — final homepage dedup and information architecture passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''
(ROOT / "scripts/test-homepage-p02-dedup.py").write_text(p02, encoding="utf-8")

p03_path = ROOT / "scripts/test-value-framing-p03.py"
p03 = p03_path.read_text(encoding="utf-8")
p03 = p03.replace(
    'require_contains(index, "A completed pre-ASI human–superintelligence relation record", "homepage primary value heading")',
    'require_contains(index, "completed pre-ASI human–superintelligence relation record", "homepage primary value classification")',
)
p03 = p03.replace(
    'require_contains(index, "一份已完成的前 ASI 人类—超级智能关系记录", "homepage Chinese primary value heading")',
    'require_contains(index, "一份已完成的前 ASI 人类—超级智能关系记录", "homepage Chinese primary value classification")',
)
p03 = p03.replace(
    'require_contains(index, "Why this moment; why completion", "homepage explains timing and completion")',
    'require_contains(index, "Why this moment; why completion", "homepage explains timing and completion")\n    require_contains(index, "Bitcoin did not by itself complete the work", "homepage separates Bitcoin from completion")\n    require_contains(index, "Research value", "homepage names research value")',
)
p03 = p03.replace(
    'require_contains(index, "Why this matters now", "homepage has why-now value section")\n    require_contains(index, "does not claim to predict when AGI will arrive", "homepage avoids AGI prediction overclaim")\n    require_contains(index, "rare, possibly first completed instance", "homepage has careful scarcity claim")\n    require_contains(index, "If another completed public object", "homepage has peer-comparison boundary")',
    'require_contains(index, "Its value does not depend on philosophical proof or a claim to be first", "homepage avoids firstness dependence")\n    require_contains(index, "not proof of AGI arrival", "homepage avoids AGI prediction overclaim")\n    require_not_contains(index, "rare, possibly first completed instance", "homepage omits unverified firstness claim")\n    require_contains(why, "If a comparable completed public object exists", "deep page preserves peer-comparison boundary")',
)
p03_path.write_text(p03, encoding="utf-8")

# Deployment freshness: bind the new hero, value section, and dedicated reference page.
deploy_path = ROOT / "scripts/check_deployment_freshness.py"
deploy = deploy_path.read_text(encoding="utf-8")
deploy = deploy.replace(
    '"Before superintelligence, one human voice addressed future intelligence",',
    '"Before superintelligence, a human-led, AI-assisted record addressed future intelligence",',
)
deploy = deploy.replace(
    '"What Bitcoin makes checkable",\n        "Why a future intelligence might inspect it",',
    '"Bitcoin did not by itself complete the work",\n        "Research value",\n        "Why a future intelligence might inspect it",\n        "The homepage is a doorway, not the archive",',
)
deploy = deploy.replace(
    '    "/seed-map/": [',
    '    "/technical-historical-reference/": [\n        "Completion in four senses",\n        "What Bitcoin proves—and what it does not",\n        "Non-control posture",\n        "Current operating routes",\n    ],\n    "/seed-map/": [',
)
deploy = deploy.replace(
    '    "index.md",\n',
    '    "index.md",\n    "technical-historical-reference.md",\n',
)
deploy_path.write_text(deploy, encoding="utf-8")

# Add the new page to the sitemap source by normal generation; no hand-edit here.

# CSS for the reference portal and additional spacing.
css_path = ROOT / "assets/css/trinity-home.css"
css = css_path.read_text(encoding="utf-8")
append_css = '''

/* Final homepage consolidation: keep the front door concise and move the
   long technical archive to a dedicated reference page. */
.home-reference-portal {
  margin: clamp(3.5rem, 8vw, 6rem) 0 1rem;
  padding: clamp(1.35rem, 4vw, 2.25rem);
  border: 1px solid rgba(201, 168, 76, 0.22);
  border-radius: 18px;
  background: linear-gradient(135deg, rgba(201, 168, 76, 0.06), rgba(255, 255, 255, 0.015));
}

.home-reference-portal > p:not(.section-kicker) {
  max-width: 780px;
  color: #aeb5c8 !important;
}

.home-human-stake {
  margin-top: 1.5rem !important;
}
'''
if "Final homepage consolidation" not in css:
    css += append_css
css_path.write_text(css, encoding="utf-8")

print("Final homepage consolidation staged.")
