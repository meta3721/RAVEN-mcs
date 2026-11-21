"""Read-only G0 identity audit and terminal report; never launches experiments.

Uses only the Python standard library. Existing terminal output forbids reruns.
All writes are confined to this new evidence directory.
"""
from pathlib import Path
import ast
import csv
import hashlib
import json
import shutil
import time
from datetime import datetime, timezone, timedelta

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
PROTOCOL = Path('C:/Users/szr/Desktop/record/1/research-protocols/reachability-detector-proof-experiment-protocol.md')


def main():
    if (OUT / 'EXECUTION_STATUS.json').exists():
        raise SystemExit('Existing execution state preserved; this audit cannot resume or overwrite it.')
    cpu_start, wall_start = time.process_time(), time.perf_counter()
    protected = [
        'results_main_rebuild_r1/EXECUTION_STATUS.json',
        'results_main_rebuild_r1/EXECUTION_REPORT.md',
        'TO_OVERLEAF_paper_tmc_r1_clean/main.tex',
        'TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex',
        'TO_OVERLEAF_paper_tmc_r1_clean/supplemental.tex',
        'TO_OVERLEAF_paper_tmc_r1_clean/main.pdf',
        'TO_OVERLEAF_paper_tmc_r1_clean/supplemental.pdf',
        'src/raven_mcs/aggregation/method_policy.py',
        'src/raven_mcs/training/window_runner.py',
        'src/raven_mcs/sag/r1l_design.py',
    ]
    digest = lambda rel: hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
    before = {rel: digest(rel) for rel in protected}
    protocol_text = PROTOCOL.read_text(encoding='utf-8-sig')
    shutil.copyfile(PROTOCOL, OUT / 'SOURCE_PROTOCOL.md')
    read = lambda rel: (ROOT / rel).read_text(encoding='utf-8-sig')
    policy = read('src/raven_mcs/aggregation/method_policy.py')
    design = read('src/raven_mcs/sag/r1l_design.py')
    runner = read('src/raven_mcs/training/window_runner.py')
    paper = read('TO_OVERLEAF_paper_tmc_r1_clean/main.tex')
    cache_source = read('results_main_rebuild_r1/prepare_uniform.py')
    old_status = json.loads(read('results_main_rebuild_r1/EXECUTION_STATUS.json'))
    tree = ast.parse(policy)
    assignments = {}
    registry = None
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and isinstance(node.value, ast.Constant):
                    assignments[target.id] = node.value.value
        if isinstance(node, ast.AnnAssign) and getattr(node.target, 'id', '') == 'POLICY_MAP':
            registry = node.value
    declared_mode = None
    for key, value in zip(registry.keys, registry.values):
        if isinstance(key, ast.Constant) and key.value == 'raven_mcs':
            declared_mode = next(ast.literal_eval(k.value) for k in value.keywords if k.arg == 'gate_mode')
    checks = {
        'paper_configured_design': 'configuration that the deployment fixes before the window opens' in ' '.join(paper.split()),
        'paper_gate_diagnostic': 'the coverage Gate is a separate diagnostic' in ' '.join(paper.split()),
        'code_formal_mode': assignments.get('FORMAL_GATE_MODE'),
        'code_raven_mcs_mode': declared_mode,
        'code_gate_drives_design': 'design_t = design_from_gate(gate_t)' in design,
        'code_static_design_ignored': 'del oracle_safe, current_C, current_mask, dataset_design_flag, design_enabled' in design,
        'runner_returns_gate_for_design': 'return int(rec["Gate_t"]), certs' in runner,
        'uniform_cache_inherits_raven_mcs': "dataclasses.replace(POLICY_MAP['raven_mcs']" in cache_source,
    }
    conflict = all(checks[k] for k in ('paper_configured_design', 'paper_gate_diagnostic', 'code_gate_drives_design', 'code_static_design_ignored', 'runner_returns_gate_for_design')) and declared_mode == 'aggregate_coverage'
    if not conflict:
        raise SystemExit('Expected identity evidence not reproduced; no gate pass or experiment is authorized by this script.')
    evidence = []
    searches = {
        'TO_OVERLEAF_paper_tmc_r1_clean/main.tex': ['the coverage Gate is a separate diagnostic', 'configuration that the deployment fixes before the window opens', 'pure diagnostic', 'diagnostic'],
        'src/raven_mcs/aggregation/method_policy.py': ['FORMAL_GATE_MODE =', '"raven_mcs": MethodPolicy(', 'gate_mode="aggregate_coverage"'],
        'src/raven_mcs/sag/r1l_design.py': ['def design_from_gate', 'del oracle_safe', 'design_t = design_from_gate(gate_t)', 'Design_t must equal Gate_t'],
        'src/raven_mcs/training/window_runner.py': ['Formal RAVEN-MCS (gate_mode=aggregate_coverage)', 'return int(rec["Gate_t"]), certs'],
        'results_main_rebuild_r1/prepare_uniform.py': ["dataclasses.replace(POLICY_MAP['raven_mcs']", "gate_mode='aggregate_coverage'"],
    }
    for rel, needles in searches.items():
        for number, line in enumerate(read(rel).splitlines(), 1):
            if any(needle in line for needle in needles):
                evidence.append(dict(file=rel, line=number, text=line.strip()))
    write_json = lambda name, obj: (OUT / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    write_md = lambda name, content: (OUT / name).write_text(content.strip() + '\n', encoding='utf-8')
    links = '\n'.join(f'- [{e["file"]}:{e["line"]}](C:/Cursor/raven.mcs/{e["file"]}:{e["line"]})：`{e["text"]}`' for e in evidence)
    write_json('G0_IDENTITY_EVIDENCE.json', dict(checks=checks, conflict_reproduced=True, source_lines=evidence,
        counterexample=dict(kind='static semantic consequence, not experimental data', preconfigured_Design=1, coverage_Gate=0, paper_Design=1, implementation_Design=0)))
    write_md('METHOD_IDENTITY.md', f'''# G0 方法身份核验：未通过

论文定义是窗口前显式配置 Design，并在窗口内保持；coverage Gate 仅诊断。当前注册表仍将 `raven_mcs` 指向 aggregate_coverage；runner 返回 Gate 驱动机会校正；r1l_design 明确丢弃静态配置并要求 Design=Gate。

静态语义反例：预配置 Design=1、Gate=0 时，论文路径应保持 Design=1；实现路径给出 Design=0。这是控制行为差异，不是标签或别名差异，也不是一次实验失败率。

对应任务基线是旧 Traffic/41001 Uniform 开发轨迹，它的缓存继承该实现路径，不能转归 configured-Design。历史固定 on/off 臂、覆盖候选和本协议纯检测器保持分别归属。未修改任何代码以解除冲突。

{links}
''')
    write_md('ESTIMAND.md', '''# G0 检测对象：部分核验，未冻结、未放行

1. 目标：沿用公开、与标签无关的部署原子质量及其空间×时间群组边际 mu，不按结果合并群组。论文定义 mu_g=sum_{i:h(i)=g} varpi_i；重建 common.py 使用 production_target_bundle。当前目标文件的冻结时点、完整映射及在线可得条件尚未完成本协议核验，不能标为已确认。
2. 已保存 payload 的 M 是实际观测和校正权重构成的经验组成；它不是未观察训练人群的真实组成，也不是多步 Adam 更新的有效梯度组成。不能直接将已有 M 当作稳定未知 q_j 的校准样本。
3. 已知 payload 上的几何可达性可以作确定性计算。真实 q_j、合法校准流与条件均值关系是否可识别，以及未来完整机会名册是否可得，尚未建立；没有人为遮蔽现有组成制造统计问题。
4. 服务器只可使用当前合法历史前缀、已冻结 mu 和合法元数据。未来到达、隐藏组成和评价标签只归评价器，不读取测试预测标签选择配置。
5. 仅已到达、未消费、未过期、版本允许联合使用的更新可进入 I_t。H=4 不授权将已聚合的历史更新再次使用；现有缓存两轮重放不等于四窗候选池。当前生产候选消费/有效期清单尚未核验。
6. 与任务风险的联系需要共同模型状态、组内条件梯度均值一致、权重后的噪声条件均值保持和梯度有界。当前证据未核验这些条件；没有 T5 或预测改善主张。

统计假设逐项状态：唯一 unit-ID 去重、条件均值、流内稳定性、真实单次更新组成对应关系、加权比率偏差控制和未来外集合均未获得本协议 PASS。旧报告已明确首轮 unit-ID 去重未实现，但本轮未将它另行宣判为统计反例。

G0 首先确认方法身份冲突，随后终止。因此不把未完成的可识别性核验标成 STOP_UNIDENTIFIABLE，也不把当前组成已知自动推成所有未来信息已知。
''')
    registry_entries = [
        ('B-exact', '同运行时已知经验组成和实际权重约束的确定性距离优化', 'src/raven_mcs/metrics/reachability_optimization.py', '尚未核验数值证书及当前流程兼容性；不能降格为 oracle'),
        ('B-point', '相同 H/点估计/约束；无不确定性修正', None, 'PLANNED；不能授予序贯安全保证'),
        ('B-fixed', '同信息固定时点置信检测', None, 'PLANNED；重复查看未校正时仅不安全对照'),
        ('B-anytime', '同置信集合，最大列半径距离修正', None, 'PLANNED；G1 尚未开始'),
        ('B-robust', '同置信集合完整鲁棒可行性', None, '适用性及可实现性未完成，不能宣称已比较最强基线'),
        ('B-current-coverage', '现有覆盖 Gate；不同检测对象', 'src/raven_mcs/sag/r1l_design.py', '仅诊断对照；当前实现还控制 Design，存在身份冲突'),
    ]
    baseline_rows = list(csv.DictReader((ROOT / 'results_main_rebuild_r1/P0_VALIDATION_BASELINES_R2.csv').open(encoding='utf-8-sig')))
    write_json('BASELINE_REGISTRY.json', dict(status='PARTIAL_G0_STOP',
        detection=[dict(name=n, estimand=e, implementation=p, status=s) for n,e,p,s in registry_entries],
        task=dict(name='Traffic Uniform development, seed41001', status='TASK_BASELINE_NOT_CONFIRMED',
            RMSE_mu=253.1132, unit='vehicles/h', source='results_main_rebuild_r1/EXECUTION_REPORT.md',
            method_identity='aggregate_coverage local-loss cache; not configured-Design',
            central_202_0554_is_federated_baseline=False, development_47_01_percent_is_new_RAVEN_gain=False,
            R2_simple_baseline_rows=len(baseline_rows), R2_source='results_main_rebuild_r1/P0_VALIDATION_BASELINES_R2.csv'),
        literature_verification=dict(status='CANCELLED_AFTER_FIRST_G0_FAILURE',
            sources_prescribed_by_protocol=['Howard et al. arXiv:1810.08240', 'FedPALS arXiv:2411.03799v2', 'sequential feasibility / robust optimization neighbors'],
            new_searches_performed=0)))
    frozen = dict(status='DEFAULTS_RECORDED_NOT_G0_PASSED', protocol_version='v1', stage_order=['G0','G1','G2','G3','G4','G5'],
        H=4, eta=0.05, distance='L1', alpha_per_complete_run=0.05,
        development_seeds=[41001,41002,41003], confirmation_seeds=list(range(42001,42021)),
        dataset_order=['traffic','sensorscope','uair'], max_cpu_cores=8, max_cumulative_cpu_seconds=28800, gpu_training=0,
        main_improvement_metric='valid_decision_rate', minimum_improvement_percentage_points=2,
        delay_alternative_not_selected=True, cap_ess_deadline_D_resource_B='NOT_FROZEN_BEFORE_STOP',
        calibration_streams_and_alpha_allocation='NOT_FROZEN_BEFORE_STOP',
        synthetic_dimensions_and_sample_budget='NOT_FROZEN_BEFORE_STOP',
        no_parameter_search=True, no_method_change=True, no_test_tuning=True, no_resume_without_user_revision=True,
        protocol_line_count=len(protocol_text.splitlines()))
    write_json('FROZEN_PROTOCOL.json', frozen)
    write_md('PROOF_LEDGER.md', '''# 证明账本：未启动

G0 未 PASS；依用户层级顺序，不进入 G1。协议中提供的路线未转写为项目已完成证明。

| 项目 | 状态 | 原因 |
|---|---|---|
| T1 | SKIPPED | G0 STOP |
| T1b | SKIPPED | 尚未确定需要的实际统计分支 |
| T2 | SKIPPED | G0 STOP |
| T3 | SKIPPED | 完整未来名册及实际分支未冻结 |
| T4 | SKIPPED | G0 STOP |
| T5 | SKIPPED | 任务风险联系未核验，无相关主张 |
| T6 | SKIPPED | G0 STOP，未接入检测器或复核配对预测 |
''')
    cancelled = [
        'G0剩余可识别性、样本需求、成本估计、近邻来源和基线实现核验',
        'G1实际适用分支的T1/T1b/T2/T3/T4/T5/T6证明',
        'G2检测器接口实现及四条关键路径核验',
        'G3六类各200条合成轨迹，每条最多80次查看',
        'G4 Traffic 41001→41002→41003、SensorScope/U-Air条件回放',
        'G4正式确认42001–42020',
        'G5 H=1、H=8、最大半径替换、移除未来外集合消融与影子预测核验',
    ]
    now = datetime.now(timezone(timedelta(hours=8))).isoformat()
    budget = dict(new_training_runs=0, detector_implementations=0, synthetic_trajectories=0, real_replays=0,
        gpu_training_seconds=0, extra_calibration_units=0, extra_calibration_messages=0,
        audit_process_cpu_seconds=time.process_time()-cpu_start,
        audit_process_wall_seconds=time.perf_counter()-wall_start,
        measurement_scope='本脚本截至停止文档生成前的只读核验；此前交互式文件读取CPU未单独计量，不冒充全会话总CPU。没有运行任何检测/训练实验。')
    state = dict(status='STOP_METHOD_IDENTITY_MISMATCH', stop_code_origin='本协议0.2显式身份冲突条件的本地状态名；不是新增门槛',
        first_failure_stage='G0', timestamp=now, stages={'G0':'STOP', **{f'G{i}':'SKIPPED' for i in range(1,6)}},
        terminal=True, cancelled_tasks=cancelled, budget=budget,
        historical_stop_state_preserved=old_status['status'], detection_gain='NOT_EVALUATED',
        task_non_degradation='NOT_VERIFIED', prediction_gain='NO_EVIDENCE', new_RAVEN_gain_claim=False)
    write_json('EXECUTION_STATUS.json', state)
    write_json('BUDGET.json', budget)
    cancelled_md = '\n'.join('- '+x for x in cancelled)
    report = f'''# STOP_REPORT

日期：{now}。状态：STOP_METHOD_IDENTITY_MISMATCH。失败层：G0；G1–G5 全部 SKIPPED。

## 首个失败条件

用户协议0.2要求：“旧论文的 configured-Design 与代码的 aggregate_coverage 身份冲突若仍存在，涉及旧方法结果归属和下游核验的阶段不能启动”；1.4要求基线身份明确。本轮确认该冲突仍存在。状态名只是将该明确条件编码，不改变协议门槛。

论文预配置 Design 并仅诊断 coverage；实际 `raven_mcs` 注册为 aggregate_coverage，runner 以 Gate 驱动 Design，函数忽略静态配置。静态反例：预配置D=1、Gate=0，论文D=1，实际D=0。没有性能数值被伪装成新检测结果。

## 对应基线与影响

Traffic/41001 旧 Uniform 开发结果 RMSE_mu=253.1132 vehicles/h 的缓存继承冲突实现；它未确认跨种子及训练平台，不能作为 configured-Design 的已确认任务基线。Central-delivered 202.0554及47.01%是学习诊断，不是联邦或新RAVEN收益。B-exact须按真实组成和约束保留；B-anytime等尚未实现、核验或比较。coverage Gate对象不同，也不能将其缺陷当新检测器优势。

## 已花预算

新训练0条、GPU训练0秒、检测器实现0个、合成轨迹0条、真实检测回放0条、新增校准样本和消息均0。本次只读停止审计脚本CPU {budget['audit_process_cpu_seconds']:.6f}秒、墙钟 {budget['audit_process_wall_seconds']:.6f}秒；不含此前交互式读取的未计量CPU，不能称作全会话精确总CPU。未消耗8 CPU小时实验额度，也未启动旧112条训练。

## 已取消任务

{cancelled_md}

## 错误性质与适用范围

这是方法身份/实现语义不一致，尚未评价新检测器的统计错误率、检测收益或成本；不能据此断言数学路线错误或所有可达性检测无效。统计假设仍未放行。发现后没有外部追加检索、换方法、调门槛、改代码或续跑。协议虽允许独立数学证明，但用户要求G0 PASS才进入G1，本轮没有启动独立证明。

旧实验、论文及旧STOP保留；旧状态仍为 {old_status['status']}。新证据只写入 results_reachability_detector_v1。没有发布、推送或提交。

## 终点主张

- 检测收益：未评价。
- 任务性能不退步：未接入、未验证；不把纯诊断设想当实际配对证据。
- 预测收益/新RAVEN收益：没有对应证据，不作主张。

## 唯一协议修订候选（未执行）

另行授权一次 configured-Design 代码同步与身份核验，保留旧 coverage-controlled 路径和所有旧结果，产出窗口前D、独立Gate及缓存归属证据；通过后才可重新启动本协议G0，不自动恢复本停止状态。

## 失败来源定位

{links}
'''
    write_md('STOP_REPORT.md', report)
    write_md('G0_REPORT.md', '# G0_REPORT\n\nG0 STOP：方法身份冲突已在当前源码重现。检测对象、假设与基线登记只是部分核验，不满足PASS。具体失败、预算、取消队列及主张范围见 [STOP_REPORT.md](STOP_REPORT.md)。\n')
    write_md('EXECUTION_REPORT.md', '# EXECUTION_REPORT\n\n完整读取459行用户协议，使用ccf-experiment-designer执行G0只读审计。首个身份条件未通过，终止G1–G5。所有实验指标未评价；未产生新RAVEN收益。见 [STOP_REPORT.md](STOP_REPORT.md)、[G0_IDENTITY_EVIDENCE.json](G0_IDENTITY_EVIDENCE.json)。\n')
    after = {rel: digest(rel) for rel in protected}
    if before != after:
        raise RuntimeError('Protected input changed during audit; reports require integrity investigation.')
    write_json('PRESERVATION_CHECK.json', dict(protected_files_unchanged=True, scope='本脚本运行前后逐文件核对；脚本仅写入本目录', digests=after))
    print(json.dumps(dict(status=state['status'], stages=state['stages'], checks=checks, budget=budget, protected_files_unchanged=True), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
