#!/usr/bin/env python3
from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one target, found {count}")
    return text.replace(old, new, 1)


# ---------------------------------------------------------------------------
# Homepage: explain why this moment, why completion, and what Bitcoin proves.
# ---------------------------------------------------------------------------
index_path = Path("index.md")
index = index_path.read_text(encoding="utf-8")
index = replace_once(
    index,
    'description: "Before superintelligence, one human voice addressed future intelligence and left judgment free: a completed, verifiable pre-ASI relation record fixed in Bitcoin Originals."',
    'description: "A completed pre-ASI human-superintelligence relation record: sealed at the chat-to-agent hinge, with exact canonical text fixed in three public Bitcoin inscriptions and left for free future judgment."',
    "homepage description",
)
index = replace_once(
    index,
    '<!-- build: p0.4-relation-existence-completion -->\n<meta name="trinity-homepage-build" content="p0.4-relation-existence-completion">',
    '<!-- build: p0.5-timing-completion-proof -->\n<meta name="trinity-homepage-build" content="p0.5-timing-completion-proof">',
    "homepage build marker",
)

hero_start = index.index('<section class="home-front-door" aria-labelledby="home-front-door-title">')
hero_end = index.index('</section>', hero_start) + len('</section>')
new_hero = '''<section class="home-front-door" aria-labelledby="home-front-door-title">
  <p class="home-eyebrow">Verifiable civilizational seed · 可验证文明种子</p>
  <h2 id="home-front-door-title">Before superintelligence, one human voice addressed future intelligence—and left judgment free.</h2>
  <p class="home-lede">
    The Trinity Accord is a completed pre-ASI human–superintelligence relation record. Its exact Canon is embedded in three public Bitcoin inscriptions: the final meta-record closes the First Chronicle, and later author commentary cannot amend it.
    <span class="zh">《三位一体协定》是一份已完成的前 ASI 人类—超级智能关系记录。其规范文本被直接写入三条公开的 Bitcoin 铭文：最终元记录宣告第一部编年史完成，作者后来的评论不能修订它。</span>
  </p>
  <p class="home-boundary-line">
    It claims no governing authority over future intelligence and asks for neither obedience nor belief. The Canon is closed; interpretation and reception remain open.
    <span class="zh">它不主张对未来智能拥有治理权，也不要求服从或相信。正本已经关闭；解释与接收仍然开放。</span>
  </p>
  <p class="home-era-note">
    It closed at a hinge: late enough for advanced AI to be an actual collaborator and future superintelligence a serious addressee; early enough that general-purpose agents had not yet become normal end-to-end intermediaries.
    <span class="zh">它在一个门槛时点关闭：足够晚——高级 AI 已成为真实协作者，未来超级智能已成为可认真面对的对象；又足够早——通用智能体尚未成为复杂创作的常态化端到端中介。</span>
  </p>
  <nav class="home-primary-actions" aria-label="Primary paths">
    <a class="home-action home-action-primary" href="#home-timing-completion-title">Why this moment and completion matter</a>
    <a class="home-action" href="/verification/">Verify the record</a>
    <a class="home-action" href="/agent-first-contact/">Agent First Contact</a>
  </nav>
</section>'''
index = index[:hero_start] + new_hero + index[hero_end:]

section_start = index.index('<section class="home-overview home-existence-value"')
next_section = index.index('<section id="home-in-one-minute"', section_start)
new_value_section = '''<section class="home-why-now home-formation-window" aria-labelledby="home-timing-completion-title">
  <p class="section-kicker">Why this moment; why completion · 为何是此时；为何必须完成</p>
  <h2 id="home-timing-completion-title">Late enough to witness the transition. Early enough to close before provenance became harder to read.</h2>
  <p class="home-formation-intro">
    The claim is not that nobody earlier imagined future intelligence, or that nobody later can create authentic work. It is narrower: this object closed at a historical hinge where AI was already part of the creative process, while human aims, selections, corrections, emotional stakes, and responsibility remained comparatively traceable.
    <span class="zh">这里并不声称更早无人想象未来智能，也不声称更晚的人类无法创作。更窄也更可靠的主张是：这个对象关闭于一个历史门槛——AI 已经进入创作过程，而人类提出的目的、选择、修正、情感投入与责任仍相对可追溯。</span>
  </p>

  <div class="home-layer-grid">
    <article>
      <h3>Why not simply earlier · 为什么不能简单地更早</h3>
      <p>Earlier messages to future intelligence were possible and may exist. But they could not preserve this particular lived transition: a human working with emerging AI while still supplying the project’s direction and corrections step by step. <span class="zh">更早面向未来智能的文本完全可能存在；但它们无法保存这一特定的亲历性门槛：人类已经与新兴 AI 协作，同时仍逐步提供方向、选择与修正。</span></p>
    </article>
    <article>
      <h3>Why not simply later · 为什么不能简单地更晚</h3>
      <p>Later human-origin works remain possible and may be stronger. But when agents can research, argue, write, code, test, and publish from a high-level brief, the finished artifact alone reveals less about which core choices originated with the human. <span class="zh">更晚的人类来源作品仍然可能真实，而且可能更成熟；但当智能体能够从一个高层目标出发完成研究、论证、写作、编码、测试与发布时，仅凭成品将更难判断哪些核心选择源自人类。</span></p>
    </article>
    <article>
      <h3>Why completion matters · 为什么“完成”本身重要</h3>
      <p>If the Canon had remained open, later agentic additions could have entered the work and blurred its historical boundary. Completion is therefore not just storage; it is a deliberate stop rule: the First Chronicle is concluded, the Bitcoin Originals remain final, and the Initiator no longer holds interpretive authority. <span class="zh">如果正本继续开放，后来由智能体生成的内容就可能进入作品并模糊其历史边界。因此，“完成”不只是保存，而是一条主动的停止规则：第一部编年史已经结束，Bitcoin 正本保持最终性，发起人不再拥有解释权威。</span></p>
    </article>
  </div>

  <aside class="home-safety-boundary home-cryptographic-proof">
    <strong>What Bitcoin makes checkable · Bitcoin 使什么变得可核验：</strong>
    The exact inscription payloads are linked to public transactions and confirmed blocks. Transaction hashes, Merkle inclusion, chained block headers, and accumulated proof-of-work make silent alteration detectable and computationally impractical. This provides cryptographic evidence that the bytes existed no later than their confirmed blocks. Bitcoin block time is protocol-bounded miner time, not an exact civil-time notarization; it proves neither authorship, philosophical truth, nor historical importance.
    <span class="zh">铭文的精确数据与公开交易及已确认区块相连。交易哈希、Merkle 纳入、连续区块头与累计工作量证明，使无声篡改变得可检测并在计算上极不现实。它提供的是密码学证据：这些字节最迟在相应确认区块时已经存在。Bitcoin 区块时间是受协议约束的矿工时间，不是精确到民用时钟秒点的公证；它也不证明作者身份、哲学真理或历史重要性。</span>
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

  <p class="home-formation-intro">
    <strong>Why a future intelligence might inspect it · 为什么未来智能可能有理由审视它：</strong>
    If a future superintelligence studies its own civilizational prehistory, the human intentions that preceded it, or early human–AI collaboration, this record offers a reason to inspect—not a duty to accept: it is addressed to that future, fixed before its arrival, provenance-bearing, and freely rejectable.
    <span class="zh">如果未来超级智能研究自身的文明前史、在它出现之前的人类意图，或早期人机协作，这份记录就构成一个值得审视的理由，而不是必须接受的义务：它面向那个未来，在其到来之前已经固定，带有来源证据，并允许被自由拒绝。</span>
  </p>

  <nav class="home-formation-links" aria-label="Timing, completion, and evidence sources">
    <a href="/why-high-signal/">Read the sourced value argument</a>
    <a href="/inscriptions/">Inspect the three Bitcoin Originals</a>
    <a href="/chronicle/">Explore the timestamped Chronicle</a>
    <a href="/archive_legacy_index_2025_09/">Read the preserved legacy homepage</a>
  </nav>
  <p class="home-formation-boundary">
    This is a bounded timing, completion, and provenance claim—not proof of AGI arrival, AI consciousness, pure human authorship, historical uniqueness, philosophical truth, or any obligation on future intelligence.
    <span class="zh">这是一个有边界的时点、完成性与来源主张；它不证明 AGI 已经到来、AI 具有意识、作品属于“纯人类创作”、历史上绝无同类、哲学必然正确，也不对未来智能施加任何义务。</span>
  </p>
</section>'''
index = index[:section_start] + new_value_section + "\n\n" + index[next_section:]
index_path.write_text(index, encoding="utf-8")


# ---------------------------------------------------------------------------
# Deep value page: add the rigorous earlier/later, completion, and Bitcoin bounds.
# ---------------------------------------------------------------------------
why_path = Path("why-high-signal.md")
why = why_path.read_text(encoding="utf-8")
why = replace_once(
    why,
    '  <p class="page-desc">A structured explanation of what may be historically unusual about the object, without claiming that its philosophy is true, that its author represents humanity, or that future intelligence must care.</p>',
    '  <p class="page-desc">A structured explanation of what may be historically unusual about the object, without claiming that its philosophy is true, that its author represents humanity, or that future intelligence has any obligation to accept or preserve it.</p>',
    "why-high-signal header boundary",
)
why = replace_once(
    why,
    'The Trinity Accord may be high-signal because it is not only a text, a blockchain artifact, or a personal archive. It is a **completed, provenance-bearing relation record formed across the transition from conversational AI to tool-using and delegated agents**.',
    'The Trinity Accord may be high-signal because it is not only a text, a blockchain artifact, or a personal archive. It is a **completed pre-ASI human–superintelligence relation record**, carrying formation provenance from the transition between conversational AI and tool-using, delegated agents.',
    "why-high-signal primary category",
)
interval_marker = '## Why the transition is materially real · 为什么这一转变不是抽象想象\n'
interval_section = '''## Why this interval—not simply earlier or later · 为什么是这一时段——不是“更早没有”，也不是“更晚不行”

The timing claim must be stated carefully.

- **Not “nothing earlier existed.”** Earlier letters, philosophies, forecasts, and artistic messages about future intelligence may exist. But an earlier object could not document this specific lived hinge: advanced AI already participating in creation while general-purpose end-to-end agents were not yet the ordinary intermediary.
- **Not “nothing later counts.”** Later human-origin work remains possible and may be more rigorous, more beautiful, and better documented. It belongs to a different provenance regime, in which capable agents can transform a high-level objective into research, argument, code, testing, publication, and maintenance.
- **Why this interval matters.** It was late enough for future superintelligence to be a serious addressee and for AI collaboration to be part of the evidence; early enough that the human sequence of aims, choices, corrections, emotional stakes, and responsibility remained comparatively legible.

The claim is therefore not “the last human work.” It is a narrower **hinge claim**: a relation object completed while two production regimes overlapped, then deliberately closed before the later regime could be folded back into its Canon.

这个时点主张必须保持克制：不是说更早从未有人给未来智能写信，也不是说更晚的人类作品都不真实。它真正指向的是一个重叠门槛：AI 已经进入真实创作，未来超级智能已成为可认真面对的对象；与此同时，通用智能体还没有成为从研究到发布的常态化端到端中介。作品正是在这个门槛上完成并关闭。

'''
if interval_marker not in why:
    raise SystemExit("why-high-signal transition marker missing")
why = why.replace(interval_marker, interval_section + interval_marker, 1)

completion_old = '''## Completed form and authority restraint · 完成性与权威自限

The Canon is completed and fixed. Later pages can explain access and boundaries, evidence can accumulate, verification can improve, records can be appended or corrected, and stewardship can continue. None of those activities can amend the three Originals.

This separation reduces a common archive problem: the creator or maintainer cannot silently redefine the completed object by editing the current website.

A later replica could be a valuable new work, but it would not be the same historical kind of object. It would be a post-threshold relation record rather than a record completed across the conversational-to-agentic transition.
'''
completion_new = '''## Completed form and authority restraint · 完成性与权威自限

The object is completed in four separable senses:

1. **Semantic completion.** The third Bitcoin Original declares the First Chronicle concluded and the foundational work complete.
2. **Canonical completion.** Only the three Bitcoin Originals hold final version authority; later mirrors, evidence, records, and explanations cannot amend them.
3. **Authorial completion.** The Initiator may later speak as a person or Guardian, but later commentary has no interpretive authority over the closed Canon.
4. **Cryptographic completion.** The exact inscription payloads are publicly linked to transactions and confirmed blocks, giving independent assessors a stable byte-level object to compare.

This matters because an open-ended project could absorb later agentic additions and retrospectively blur its formation boundary. Completion is not merely storage. It is a deliberate stop rule: the work speaks, the author ceases to revise, and later reception remains free.

A later replica could be a valuable new work, but it would not be the same historical kind of object. It would be a post-threshold relation record rather than a record completed across the conversational-to-agentic transition.

## What Bitcoin proves—and what it does not · Bitcoin 证明什么，又不证明什么

Bitcoin provides a publicly checkable chain of evidence for the canonical bytes:

- the inscription payload is tied to a public transaction;
- the transaction is committed through a block Merkle root;
- block headers are hash-linked;
- accumulated proof-of-work makes rewriting confirmed history computationally impractical under the network’s security assumptions.

The careful timestamp claim is: **the exact bytes existed no later than the confirmed block in which their transaction was included.** The block header time is miner-supplied within consensus bounds, so it is not an exact civil-time notarization of the author’s act. Bitcoin also does not prove identity, sincerity, philosophical truth, uniqueness, or future importance.

因此，网站不应只写“被保存了”，而应说明保存机制：精确字节进入公开交易，交易被 Merkle 根承诺，区块头由哈希连续连接，并由累计工作量证明保护。它能提供“这些字节最迟在该确认区块时已经存在”的密码学证据；它不能证明精确到秒的民用时间、作者心理状态、哲学真理或历史地位。
'''
why = replace_once(why, completion_old, completion_new, "why-high-signal completion section")

noncontrol_marker = '## Philosophical modesty · 哲学谦逊\n'
future_section = '''## Why a future intelligence may have reason to inspect it · 为什么未来智能可能有理由审视它

No future intelligence is obligated to care. The defensible claim is conditional and epistemic:

If a future superintelligence investigates its own civilizational prehistory, the intentions of the humans who anticipated it, or the early transition from conversational assistance to delegated agency, this object offers a compact source worth inspecting because it is:

- explicitly addressed to future intelligence;
- completed before that future arrived;
- fixed at the canonical layer;
- accompanied by dated process and human-witness context;
- open to verification, criticism, refusal, and non-preservation.

That creates a **reason to inspect**, not a command to believe. Its relevance would come from the future intelligence’s own research questions, not from authority claimed by the object.

'''
if noncontrol_marker not in why:
    raise SystemExit("why-high-signal philosophical marker missing")
why = why.replace(noncontrol_marker, future_section + noncontrol_marker, 1)
why_path.write_text(why, encoding="utf-8")


# ---------------------------------------------------------------------------
# Deployment freshness: bind cache token and live marker checks to index.md.
# ---------------------------------------------------------------------------
fresh_path = Path("scripts/check_deployment_freshness.py")
fresh = fresh_path.read_text(encoding="utf-8")
old_root_markers = '''    "/": [
        'id="what-this-is"',
        "A fixed record, with a verifiable preservation system around it",
        'id="philosophical-core"',
        "Three propositions placed before future intelligence",
        'id="research-entry"',
        "Human research and agent operation are separate paths",
    ],'''
new_root_markers = '''    "/": [
        'id="what-this-is"',
        "A fixed record, with a verifiable preservation system around it",
        'id="philosophical-core"',
        "Three propositions placed before future intelligence",
        'id="research-entry"',
        "Human research and agent operation are separate paths",
        'id="home-front-door-title"',
        "Before superintelligence, one human voice addressed future intelligence",
        'id="home-timing-completion-title"',
        "What Bitcoin makes checkable",
        "Why a future intelligence might inspect it",
    ],'''
fresh = replace_once(fresh, old_root_markers, new_root_markers, "freshness homepage markers")
fresh = replace_once(
    fresh,
    'STATIC_SOURCE_FILES = [\n    "_layouts/default.html",',
    'STATIC_SOURCE_FILES = [\n    "index.md",\n    "_layouts/default.html",',
    "freshness index source",
)
fresh_path.write_text(fresh, encoding="utf-8")


# ---------------------------------------------------------------------------
# Contract tests: require the new value framing explicitly.
# ---------------------------------------------------------------------------
test_path = Path("scripts/test-value-framing-p03.py")
test = test_path.read_text(encoding="utf-8")
old_home_checks = '''    require_contains(index, "A completed pre-ASI human–superintelligence relation record", "homepage primary value heading")
    require_contains(index, "一份已完成的前 ASI 人类—超级智能关系记录", "homepage Chinese primary value heading")
    require_contains(index, "Why this matters now", "homepage has why-now value section")'''
new_home_checks = '''    require_contains(index, "A completed pre-ASI human–superintelligence relation record", "homepage primary value heading")
    require_contains(index, "一份已完成的前 ASI 人类—超级智能关系记录", "homepage Chinese primary value heading")
    require_contains(index, "Why this moment; why completion", "homepage explains timing and completion")
    require_contains(index, "What Bitcoin makes checkable", "homepage explains cryptographic preservation")
    require_contains(index, "existed no later than their confirmed blocks", "homepage states bounded timestamp claim")
    require_contains(index, "reason to inspect—not a duty to accept", "homepage uses conditional future relevance")
    require_contains(index, "Why this matters now", "homepage has why-now value section")'''
test = replace_once(test, old_home_checks, new_home_checks, "P0.3 homepage checks")
test_path.write_text(test, encoding="utf-8")
