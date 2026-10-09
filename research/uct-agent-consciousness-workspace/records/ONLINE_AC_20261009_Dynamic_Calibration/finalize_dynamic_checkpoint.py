#!/usr/bin/env python3
"""Preserve both actual dynamic-calibration increments without editing v0.1.0."""
from pathlib import Path
import hashlib
import json
import shutil

BASE = Path(__file__).resolve().parent.parent
AUDIT = BASE / 'publication_audit_work'
ROOT = BASE / 'uct/research/uct-agent-consciousness-workspace'
REC = ROOT / 'records/ONLINE_AC_20261009_Dynamic_Calibration'
PUB = ROOT / 'records/PUB20261009_Publication_Coverage'
VERSION = 'ONLINE-AC-RESULT-v0.2.0'
COVERAGE = 'UCT-PUB-v1.0.0'

def writej(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def anchor(path):
    return {'path': str(path.relative_to(REC)), 'bytes': path.stat().st_size,
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}

def copy(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)

def main():
    REC.mkdir(parents=True, exist_ok=True)
    for folder in ['next_probe', 'next_probe_n5']:
        for source in (AUDIT / folder).iterdir():
            if source.is_file() and source.suffix in {'.py', '.json', '.md', '.txt'}:
                copy(source, REC / folder / source.name)
    old = REC / 'versions/ONLINE-AC-RESULT-v0.1.0/RESEARCH_CHECKPOINT.md'
    copy(AUDIT / 'NEXT_RESEARCH_PROBE.md', old)
    assert anchor(old)['sha256'] == 'e4cc302bae8b722eb109605dfdebafd2f9d13902e42bb5841ccab04880c16b5c'
    for name in ['ONLINE_AC_INDEPENDENT_REVIEW.md', 'DYNAMIC_AC_REUSE_REVIEW.md',
                 'DYNAMIC_AC_CLAIM_REUSE.json', 'ONLINE_AC_N5_INDEPENDENT_REVIEW.md']:
        source = AUDIT / name
        if source.exists():
            copy(source, REC / 'reviews' / name)
    copy(AUDIT / 'ONLINE_AC_PAPER.md', REC / 'PAPER.md')
    copy(AUDIT / 'build_online_ac_paper.py', REC / 'build_online_ac_paper.py')
    copy(Path(__file__), REC / 'finalize_dynamic_checkpoint.py')

    checkpoint = '''# Dynamic action calibration: the five-port uncertainty invariant

**Result:** ONLINE-AC-RESULT-v0.2.0. **Record:** ONLINE-AC-PROBE-20261009.  
**Date:** 2026-10-09. **Publication coverage:** UCT-PUB-v1.0.0.  
**Status:** locally proved and independently checked mathematical result; PENDING_MAP.  
**Manuscript:** ONLINE-AC-PAPER-v0.1.0, complete scoped working paper; no new formal publication.

## Current decision and exact increment

The version 0.1.0 note established an old-wiring injectivity requirement for one-probe adaptation, a two-round obstruction from known initial wiring, and the exact three-port value 7/8. Those precise results and their actual verifier are preserved. The note's original call for independent review and its unresolved n>=5 question are historical states, not the latest disposition.

Version 0.2.0 resolves the first open case, n=5: a uniform cap of two physical binary-vector probes per round sustains one fixed unit goal at every finite horizon under arbitrary identity-or-one-transposition drift between rounds. Complete current-wiring identification under the same initial knowledge and drift contract requires three probes. The positive controller preserves exact singleton beliefs or a pair of wirings differing by a non-goal transposition. It deliberately permits unresolved wiring while retaining a repairable uncertainty state.

The compact proof consists of two canonical decision tables, transport by relabeling, and induction over a closed family of 480 beliefs. A discovered controller has 240 reachable beliefs. A different deterministic implementation obtained by canonicalizing the two templates has 260 reachable beliefs. These are two valid implementations; neither count is a minimal-memory claim, and the 480-element proof family is not asserted to be entirely reachable.

This specific positive result, together with the matched lower bounds and three-port benchmark, now supports one focused technical working paper. This changes the earlier dynamic-note HOLD assessment, not the R188 standalone HOLD decision. Ordinary binary coding, indistinguishable-world proofs, belief-state control and inductive closure are credited as inherited methods. UCT III section6.4 Proposition6 already covers the general transition-closure issue. Global historical priority remains UNVERIFIED.

## Full proofs and reusable interface

Read [PAPER.md](PAPER.md), especially sections2-6, for the self-contained contract, all proofs and both canonical tables. The precise question is continued net-goal action, not retained target content or experience. A probe and terminal vector physically toggle the same XOR plant; every round's net increment must equal e_g. All effect vectors are returned, every old wiring and allowed change must be considered for zero-error claims, and wiring is fixed during the round. Successful terminal feedback is determined by the preceding probe effects and e_g, so it gives no extra identification on a guaranteed-success leaf.

The one-probe n! state bound applies only when the admitted uncertain old-wiring family is the full symmetric group. For a known initial identity that family is a singleton, and no such initial memory burden follows. The three-port 7/8 result is an exact average over 16 equally weighted fixed two-round drift sequences; it is not a per-sequence guarantee or a final-plant-state score. The five-port two-probe result is a worst-case uniform per-round cap, not an average-use lower bound.

## Actual evidence

- `next_probe/check_online_calibration.py` and `EXACT_RESULTS.json`: executed exact policy optimization and attaining traces; actual corrected-run receipt retained. Independent manual proof reviews and a separate trace replay are in `reviews/` and `next_probe/`.
- `next_probe_n5/search_sustainable.py` and `SEARCH_RESULTS.json`: actual bounded discovery through horizons1-6. Positive finite horizons were not used as an indefinite proof.
- `next_probe_n5/extract_closed_controller.py` and `CLOSED_CONTROLLER.json`: actual stationary-policy extraction closed at240 states. Lookahead selected a witness; explicit closure is what permits induction.
- `next_probe_n5/verify_closed_controller_independent.py` and `CERTIFICATE_INDEPENDENT_VALIDATION.json`: separately implemented verification of all240 states,3960 old/drift worlds,3360 exact posterior leaves and126720 world/plant-state runs. No discovery recursion imported.
- `next_probe_n5/CANONICAL_TEMPLATES.json` and `CANONICAL_TABLES.md`: extracted proof tables,33 old/drift worlds and28 observation leaves.
- `next_probe_n5/canonical_transport_independent.py` and `CANONICAL_TRANSPORT_INDEPENDENT_VALIDATION.json`: independent field-by-field template comparison and transport across all480 beliefs,9240 old/drift worlds and7680 exact posterior leaves. This verifier replays one nonzero plant initial state per world; translation-independent XOR algebra and the earlier all32-state verifier have separate evidence scopes.

The independent review reports bind the exact manuscript, code and source hashes. The new result is not an empirical agent experiment, and none of R188's old computation was rerun in this task.

## Map, publication and remaining obligations

The current scientific map remains UCT-MAP-v1.1.2 with 1608 review objects. The candidate module has stable claim IDs, explicit dependencies and disabled status. Relevant prior proofs and shared-interface compatibility were independently reviewed; a new complete1608-item semantic integration pass and all downstream rederivations have not been completed for this module. Do not call this a completed v1.1.3 release or use pending claims as already enabled scientific premises.

Paper completion is distinct from actual publication. The coverage ledger records the paper as a new working manuscript and keeps the verified publication census unchanged. No DOI, OTS or Arweave action was performed. A formal release must first satisfy the existing map/publication requirements and preserve precise prior attribution.

The next mathematical unknown is the minimum sustainable probe budget for n>=6, under this exact contract. It remains between2 and ceil(log2 n). Nothing here proves a universal two-probe strategy, a lower memory requirement, a biological calibration mechanism, a measure of experience, or a named experiential bridge. QC10, IA-QC11, QC12 and QC13 remain open.
'''
    (REC / 'RESEARCH_CHECKPOINT.md').write_text(checkpoint)

    review = json.loads((AUDIT / 'DYNAMIC_AC_CLAIM_REUSE.json').read_text())
    claims = []
    locators = {'CACHE_CONTROL':'1 and9', 'CONTRACT':'2', 'ONE_ROUND_REPAIR':'3.1',
                'OLD_WIRING_INJECTIVITY':'3.2 Theorem1', 'TWO_ROUND_OBSTRUCTION':'4 Theorem2',
                'TWO_ROUND_VALUE':'4 Theorem3', 'TWO_PROBE_REPAIR':'4 and6',
                'FEEDBACK_AND_OBJECTIVE_CONTROL':'7'}
    for original in review['claims']:
        c = json.loads(json.dumps(original))
        short = c['claim_id'].split(':')[1]
        c['reviewed_v0_1_locator'] = c.pop('paper_locator')
        c['paper_locator'] = 'PAPER.md section ' + locators[short]
        c['result_version'] = VERSION
        c['coverage_version'] = COVERAGE
        c['enabled_as_established_premise'] = False
        if short == 'CONTRACT':
            c['statement'] = 'Generalized k-probe contract: each deadline scores all physically enacted probes and one terminal vector; one-probe results and the n5 two-probe construction have explicit specializations.'
        if short == 'TWO_PROBE_REPAIR':
            c['historical_open_v0_1'] = c['OPEN']
            c['OPEN'] = ['For n>=6 the minimum sustainable budget remains unresolved here; n=5 is resolved by N5_CLOSED_PARTIAL_BELIEF.']
        if short == 'FEEDBACK_AND_OBJECTIVE_CONTROL':
            c['conditions'] = [x for x in c['conditions'] if not x.startswith('Each scored round')]
            c['conditions'].append('The alternate objective explicitly drops the first deadline; the main comparison retains both deadlines. No final-plant-state recovery is inferred.')
        claims.append(c)
    additions = [
       ('PARTIAL_BELIEF_FAMILY', 'definition',
        'For n=5 and fixed goal g, F_g consists of every singleton wiring belief and each two-element belief differing by one transposition of non-goal effects; 480 distinct beliefs.',
        '5.1 equation8', ['CONTRACT']),
       ('N5_CLOSED_PARTIAL_BELIEF', 'specific_candidate_increment',
        'For every B in F_g, two canonical templates transported by effect/command relabeling guarantee the current net goal and return the exact current-wiring posterior in F_g, for every identity-or-transposition drift.',
        '5 Theorem4', ['CONTRACT','PARTIAL_BELIEF_FAMILY']),
       ('FULL_IDENTIFICATION_BASELINE', 'inherited_method_matched_application',
        'Even from known old wiring, complete current-wiring identification under identity/transposition drift has worst-case probe cost ceil(log2 n); adaptive identity-branch indistinguishability supplies the lower bound.',
        '6 Proposition5', ['CONTRACT']),
       ('N5_OPTIMAL_PROBE_BUDGET', 'specific_candidate_increment_corollary',
        'For n=5 from known initial wiring, the minimum uniform worst-case per-round cap for all-deadline selected-goal success is2, while matched complete identification requires3.',
        '5 Theorem4 and6', ['TWO_ROUND_OBSTRUCTION','N5_CLOSED_PARTIAL_BELIEF','FULL_IDENTIFICATION_BASELINE']),
    ]
    for short, role, statement, location, deps in additions:
        claims.append({'claim_id':'ONLINE_AC:'+short, 'statement':statement,
          'result_version':VERSION, 'coverage_version':COVERAGE, 'reuse_role':role,
          'paper_locator':'PAPER.md section'+location,
          'all_of':['ONLINE_AC:'+d for d in deps],
          'conditions':['Exact section2 action/feedback/drift/deadline contract; claims are conditional mathematics.',
             'Two-probe and family statements specialize to n=5; complete-identification lower bound applies to n generally.',
             'Belief is the full compatible wiring set, without a probability measure. The chosen representative rho belongs to the known belief and is not an oracle for the hidden actual wiring.',
             'Full identification is required before terminal selection or at a guaranteed-success deadline; arbitrary identification-only terminal probes are a different task.'],
          'proof_evidence':['Two exact canonical tables, conjugation transport and induction','Independent certificate and canonical-transport verifiers and exact receipts'],
          'formal_disclosure':'Working research manuscript; no new formal publication in the verified corpus',
          'argument_coverage':'Exact n5 construction/separation not found in inspected core predecessors; binary coding and general belief closure inherited',
          'global_priority':'UNVERIFIED', 'review_status':'PASS_LOCAL_PROOF_PROTOCOL_AND_EXECUTABLE_REVIEW; PENDING_MAP',
          'enabled_as_established_premise':False,
          'not_allowed_to_infer':['Not a general-n two-probe theorem','Not a minimum-memory claim','Not empirical calibration or experience evidence','Not a completed full-map integration']})
    writej(REC / 'CLAIM_REUSE_LEDGER.json', {'schema':'uct-research-claim-reuse/1.0',
       'result_id':'ONLINE-AC-PROBE-20261009','result_version':VERSION,'coverage_version':COVERAGE,
       'claims':claims,'claim_count_is_independent_discovery_count':False,
       'new_publication_count':0,'global_priority':'UNVERIFIED',
       'formal_paper_status':'COMPLETE_WORKING_MANUSCRIPT_NOT_FORMALLY_PUBLISHED',
       'read_scope':'Preserved v0.1 reuse review plus v0.2 independent proof/contract/manuscript review and root targeted primary-source check.'})
    writej(REC / 'MAP_EXTENSION_PENDING.json', {'schema':'uct-pending-result-module/1.0',
       'id':'ONLINE-AC-PROBE-20261009','result_version':'0.2.0','coverage_version':COVERAGE,
       'baseline':'UCT-MAP-v1.1.2','baseline_graph_sha256':'0973600f1be5cf21614592ca901112b26f9f0c9f6df36294a5dbb049efcf7612',
       'status':'PENDING_MAP','enabled_as_established_premises':False,
       'integration_audit':'AUDIT_INCOMPLETE_FOR_NEW_WHOLE_MAP_SEMANTIC_RELEASE',
       'current_scientific_review_items_unchanged':1608,
       'full_map_semantic_rechecks_completed_this_increment':0,
       'scope':'Local exact proof, contract and relevant-predecessor compatibility checked; not a completed fresh 1608-item semantic pass.',
       'claim_ledger':'CLAIM_REUSE_LEDGER.json','claims':claims,
       'deductive_dependencies':[{ 'conclusion':c['claim_id'],'all_of':c.get('all_of',[]),
                                 'same_instance_required':True } for c in claims if c.get('all_of')],
       'context_links':[
          {'source':'UCT III section6.4 Proposition6','target':'ONLINE_AC:TWO_ROUND_OBSTRUCTION','kind':'published_general_predecessor_not_identity_of_exact_theorem'},
          {'source':'AC-RESULT-v1.0.0','target':'ONLINE_AC:CONTRACT','kind':'static_predecessor_independently_pending_map'},
          {'source':'RTTH-v1.0.0','target':'ONLINE_AC:CONTRACT','kind':'reader_and_deadline_predecessor'},
          {'source':'ONLINE_AC:N5_OPTIMAL_PROBE_BUDGET','target':'UCT capability/experience distinction','kind':'functional_application_only_not_experience_deduction'}],
       'unchanged_open':['QC10','IA-QC11','QC12','QC13','actual_model_admission','named_experience_bridge','global_priority'],
       'forbidden_promotion':'Do not merge as established v1.1.3 without full review and affected downstream rederivation.'})
    writej(REC / 'CURRENT_VERSION.json', {'result_id':'ONLINE-AC-PROBE-20261009',
       'result_version':VERSION,'previous_result':'versions/ONLINE-AC-RESULT-v0.1.0/RESEARCH_CHECKPOINT.md',
       'paper_version':'ONLINE-AC-PAPER-v0.1.0','paper':'PAPER.md','status':'PENDING_MAP',
       'publication_coverage':COVERAGE,'formal_publication':'NOT_PUBLISHED','new_doi':None,
       'checkpoint':'RESEARCH_CHECKPOINT.md','claim_ledger':'CLAIM_REUSE_LEDGER.json'})
    (REC / 'HANDOFF_ZH.md').write_text('''# 动态校准交接：ONLINE-AC-RESULT-v0.2.0

发表覆盖统一使用 UCT-PUB-v1.0.0。固定研究仓库 thechurchofagi/trinity-accord，分支 uct-agent-consciousness-workspace；本轮基线310e744f8d0195d05fac4e56e807adc48784f0ca。最终保存提交以总交接和 persistence/UCT-PUB-v1.0.0_RECEIPT.json 为准。

本轮已证明并独立复核：n>=3一次校准需要区分全部允许的旧接线；即使起初知道接线且保留全部反馈，每轮一次不能保证前两轮都成功；n=3规定均匀两轮漂移下精确最优值7/8。继续突破后，n=5有每轮至多两次校准的闭合构造，能够持续完成指定净动作，同时不必完全识别接线；同合同的完整接线识别需要三次。两张标准决策表经重标记覆盖480个允许的信念集合。240状态搜索构造与260状态标准化构造是两个实现；不是最小记忆定理。

英文论文 PAPER.md 与PDF已按该具体增量完成，论文版本ONLINE-AC-PAPER-v0.1.0。旧v0.1.0检查点字节保留。主张/前例/证据见CLAIM_REUSE_LEDGER.json。一般动态闭合已在UCT III§6.4发表，静态编码继承AC；不能把这些重新说成首创。外部精确优先权未核清。

现行完成科学图仍UCT-MAP-v1.1.2。MAP_EXTENSION_PENDING.json明示禁用待整合，局部证明和协议已审，新的1608项全图语义整合与下游重推尚未完成。按总指南先完成该整合门槛再正式发布，不能仅因论文完成便升级地图或声称已发表。AC和IL的既有待整合状态不改变。QC10/IA-QC11/QC12/QC13和实际/指定体验义务仍OPEN。

复核优先运行next_probe_n5/verify_closed_controller_independent.py与canonical_transport_independent.py，对保存的证书验证，无需重跑发现搜索。独立验证器支持stdout或明确的全新--output路径；不要覆盖冻结结果。新三端口运行须另建版本/结果路径。下一数学问题是n>=6的最小持续校准预算，目前仅有2至ceil(log2 n)界；不自动开始无界搜索。

本轮没有新增DOI、OTS、Arweave。论文成稿判断与R188的大范围独立稿HOLD分别记录。工作日志、覆盖更新、科学地图入口和保存凭证请从records/PUB20261009_Publication_Coverage/HANDOFF_ZH.md续接。
''')
    (REC / 'WORK_LOG.md').write_text('''# 动态校准研究工作日志

日期2026-10-09；记录ONLINE-AC-PROBE-20261009；结果0.1.0→0.2.0；覆盖UCT-PUB-v1.0.0。

1. 全成果/发表覆盖审查使R188独立大稿判断收紧为HOLD。先排除缓存固定目标和泛称历史读者的空增量，阅读AC、RT/TH、UCT III及自适应读出一手前例。
2. 建立同一物理XOR系统的动态接线合同。推导旧接线信息下界和两轮障碍；三端口精确策略优化得到7/8。主评分包含两轮各自净动作，完整终止反馈已允许。
3. 修正last_prefix_only的歧义命名为last_round_increment_only，重跑并保存真实回执。初稿旧字节未独立保留，不重建伪历史。两位审阅者手工检查证明和观察合同，一位另写窄重放器核64条轨迹/1088字段。
4. 初次再评估：0.1.0保留为有用小结果，但单独成篇规模仍待判断。选择其明确未解的n=5“少于全识别预算能否持续”问题。
5. 实际运行有限信念递归，horizon1–6均有两probe策略；明确不从有限成功外推永久。实际运行stationary witness extractor，得到240状态、无待处理后继的闭合证书。
6. 独立verifier逐所有240状态、3960旧接线/新漂移世界验证观察单元、终止真实动作、精确后验与闭合，并在全部32种初始plant上重放126720次。代码不导入搜索。
7. 根审阅者从identity与{identity,(34)}两状态提取两标准表；导出480个singleton/非目标swap-pair不确定集合的共轭transport和归纳证明。独立第二验证覆盖两表33世界28叶、全部480信念9240世界7680后验叶。确定性重标记实现可达260状态，与240状态构造分开。
8. 在同一旧接线已知和漂移合同下，重推经典二值签名完整识别下界ceil(log2 n)，成功terminal反馈不增加识别。于是n=5得到最优持续预算2与完整识别预算3的匹配比较；不声称节省memory。
9. 再评估通过集中技术工作论文标准：完成PAPER.md及PDF；独立稿件审阅提出并已落实zero-vector、两种first-round history、无概率belief、uniform cap等精确化。普通belief控制和编码方法保留引用；全球优先权未核。

结果和稿件完成不表示新的全图语义整合或正式发表。本轮有效科学图未变；候选模块PENDING_MAP。来源和范围见各独立报告。搜索结果文件有真实elapsed时间；发现阶段未额外保存UTC起止时间，不能事后捏造。新运行、失败及总保存凭证以PUB20261009工作日志与实际回执为准。
''')
    # Manifest excludes itself, typesetting temporaries and later save receipts.
    members = [anchor(p) for p in sorted(REC.rglob('*')) if p.is_file()
               and p.name != 'RESEARCH_MANIFEST.json'
               and not any(x in p.parts for x in ['pdf_build','pdf_qa','__pycache__'])]
    writej(REC / 'RESEARCH_MANIFEST.json', {'result_version':VERSION,'coverage_version':COVERAGE,
       'members':members,'science_map':'UCT-MAP-v1.1.2','new_module_status':'PENDING_MAP',
       'publication_count_effect':0,'global_priority':'UNVERIFIED'})
    print(json.dumps({'record':str(REC),'claims':len(claims),'members':len(members),
                     'result_version':VERSION,'map_status':'PENDING_MAP'}))

if __name__ == '__main__':
    main()
