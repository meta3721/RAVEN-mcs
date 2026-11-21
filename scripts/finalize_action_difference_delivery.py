"""Stage E: verify preserved evidence and deliver reports; no new method trials."""
import ast,csv,json,math
from pathlib import Path
from action_difference_revision_budget import ROOT,OUT,REPORT
from raven_mcs.utils.hashing import sha256_file

def load(name):return json.loads((OUT/name).read_text(encoding='utf-8'))
def report(name,text):
    with (REPORT/name).open('x',encoding='utf-8') as f:f.write(text)

if __name__=='__main__':
    original=load('PROTECTED_BEFORE.json')
    changed=[p for p,h in original.items() if not Path(p).is_file() or sha256_file(p)!=h]
    assert not changed,changed
    a=load('A_REVIEW.json');b=load('B_FACILITY_RESULT.json');c=load('C_RESULT.json');frozen=load('C_FROZEN_INPUTS.json')
    assert a['status']==b['status']=='PASS'
    assert load('B_ADMISSION_CONTRACT_PASS.json')['status']=='PASS'
    assert load('B_PAIR_IDENTITY_PASS.json')['status']=='PASS'
    assert c['status']=='FAIL_NO_CERTIFIABLE_ACTION_ON_FROZEN_EARLY_CASE' and not c['D_authorized_to_run']
    assert c['input_state_unchanged'] and c['training']==c['new_trajectories']==0
    assert sha256_file(REPORT/'CANDIDATE_CHECK_FROZEN.md')==frozen['spec_sha256']
    assert sha256_file(ROOT/'scripts/check_action_difference_candidate.py')==frozen['script_sha256']
    branches=load('C_BRANCHES.json');assert len(branches)==33
    for key,w in c['witnesses'].items():
        assert math.isclose(branches[w['positive_branch']]['deltas'][key],w['subset_max'],abs_tol=1e-14)
        assert math.isclose(branches[w['negative_branch']]['deltas'][key],w['subset_min'],abs_tol=1e-14)
        assert w['subset_max']>1e-7+1e-10
    assert any(w['subset_min']<-(1e-7+1e-10) for w in c['witnesses'].values())
    targets=list((ROOT/'src/raven_mcs_execution').glob('*.py'))+[
        ROOT/'scripts'/name for name in ('action_difference_revision_budget.py','coordinated_windows_cpu_meter.py',
        'prepare_coordinated_meter.py','review_action_difference_failure.py','check_coordinated_checkpoint.py',
        'check_root_admission_contract.py','check_pair_identity_addendum.py','check_action_difference_candidate.py',
        'finalize_action_difference_delivery.py')]
    for p in targets:ast.parse(p.read_text(encoding='utf-8-sig'),filename=str(p))
    with (OUT/'ACTION_DIFFERENCE_BRANCH_RESULTS.csv').open('x',encoding='utf-8',newline='') as stream:
        fields=['branch','primary_kind','primary_quality','primary_time','tail','WAIT_offset','CLOSE_score','WAIT_score',
                'delta','P2_branch_all_plans','cache_branch_all_plans','CPU_branch_all_plans','wall_branch_all_plans','evidence_role']
        writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader()
        for row in branches:
            scores=dict(row['scores'])
            for key,value in row['deltas'].items():
                writer.writerow(dict(branch=row['branch'],primary_kind=row['primary']['kind'],primary_quality=row['primary']['quality'],
                    primary_time=row['primary']['time'],tail=row['tail'],WAIT_offset=key,CLOSE_score=scores[0.],WAIT_score=scores[float(key)],
                    delta=value,P2_branch_all_plans=row['P2'],cache_branch_all_plans=row['cache'],CPU_branch_all_plans=row['CPU'],
                    wall_branch_all_plans=row['wall'],evidence_role='legal_subset_counterexample_not_full_bounds'))
    # One cancellation record, not an invented real-state result.
    with (OUT/'EXISTING_STATE_PROBE_RESULTS.csv').open('x',encoding='utf-8',newline='') as stream:
        fields=['status','reason','state_id','time','pool_group','classification','CLOSE_legal','WAIT_legal',
                'v3_width','candidate_width','proven_action','P2','CPU','wall']
        writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader()
        writer.writerow(dict(status='NOT_RUN',reason='C_GATE_FAILED'))

    report('FAILURE_REVIEW.md',r'''# 原44001分支失败复核

A：PASS。旧数据、六份报告及其失败身份保留；本批没有续采。

原CSV共有989行。主集合20<t<100的已观测前缀为20.1—98.9，共789点，时间网格完整且无重复，所有快照路径存在。总动作差异、区间激活、区间机制差异均为0；分类为427个UNKNOWN_FIXED_TIME_2、346个CPU_TIMEOUT、16个RULE_FORCED。完整D为799点，尚缺10点。保留已有789点时，最大差异为10/799=1.251564%，小于原5%筛查线；至少需要ceil(799×0.05)=40个差异点。因此，不建议补齐原分支用于挽救这一筛查项。

这是必要条件的确定性上界，既不是统计显著性检验，也不是所有种子或整个研究方向的失败证明。T100模型及I(100)标签仍未完成；不能将前缀当完整采集或计算正式校准通过率。从t80恢复会替换已观测尾部，应另立分支，不能称为补齐原98.9状态，更不能覆盖原失败。

科学障碍分开处理：

- 粗界：可跟踪计划×场景记录中10183/10496=97.0179%的k=0，属于该记录层，不是97.02%的决策失败率。早期未知让独立全后缀绝对分数包络缺乏动作区分；仅调整名称、q数值或删除client不能解决支持缺口。
- 计算：346/789=43.8530%为超时后备。CSV中的P2/cache为空，旧Decision的默认0不能解释成未求解。未完成区间也不能用于证明这些点本来无区分能力。各开销的细分因果尚未计量；C失败后没有启动D的成本拆分。
- 调度与保存：旧根进程费用已包含外层监视，但旧内部保存时机未以根剩余额度统一准入，终止前未提交最新尾部。t80成对文件可恢复，98.9观察日志不是等价恢复点。本批B修复独立设施，未恢复旧轨迹。

[A原始复核证据](C:/Cursor/raven.mcs/results_action_difference_revision_20261013/A_REVIEW.json)。[旧CSV](C:/Cursor/raven.mcs/results_re_interval_development_44001_20261013/DECISION_METRICS.csv)。旧报告和旧结果的逐文件保留核验见[最终核验](C:/Cursor/raven.mcs/results_action_difference_revision_20261013/FINAL_VERIFICATION.json)。本批费用见[BUDGET_LEDGER.md](C:/Cursor/raven.mcs/ccf-review-report/action_difference_revision_20261013/BUDGET_LEDGER.md)。
''')

    report('BUDGET_CHECKPOINT_FIX.md',r'''# 限定计量协调与成对保存修复

B：PASS，独立设施验证通过。没有恢复v3采集入口，没有训练，也没有重做CPU燃烧或全项目测试。设施通过不代表生产采集已经接入或获准继续。

实际代码：

- [根预算接口](C:/Cursor/raven.mcs/src/raven_mcs_execution/budget.py)：唯一准入来源为根进程发布的互斥累计CPU；tree+driver各计一次，不额外加PID或内部Job。每次启动规划前必须提供包含外部监视的operation_root_ceiling，控制器2 CPU秒不能替代根操作费用上界。数据过期、根命名空间变化或已结束会拒绝新操作；反馈年龄按最大CPU速率扣减。
- [外层协调计量](C:/Cursor/raven.mcs/scripts/coordinated_windows_cpu_meter.py)：沿用旧Job设施，新增50毫秒根账反馈。指令、阶段与全批剩余取最小值；任一先耗尽即停止。旧windows_cpu_meter.py保留。调用预算入口[scripts/action_difference_revision_budget.py](C:/Cursor/raven.mcs/scripts/action_difference_revision_budget.py)记录失败、进程树与驱动，避免重复计费。
- [成对提交](C:/Cursor/raven.mcs/src/raven_mcs_execution/paired_checkpoint.py)：临时模型→临时私有生产者→哈希及内容身份/终点/游标校验→文件就位→原子发布.complete.json。恢复只接受完成标记、匹配方法/种子/跨运行时间命名空间、有效文件哈希与一致T/时钟游标。半对文件不属于恢复点。

一次必要的代表性保存测量使用旧t80实际大小的只读数据：模型44,534,030字节、私有文件14,639,710字节。完整写入、发布和读回CPU为2.734375秒，墙钟2.990260秒。事前保存余量取2×测量CPU+0.5=5.96875秒；这是测量基础上的工程余量，不是普适最坏情况保证。第一次测量在根账有充足额度时进行，初始1秒占位参数没有被当成生产保存保证。序列化布局变化不删除状态字段，私有输出更紧凑。

同一个确定性设施用例覆盖外部驱动费用增长、跳过新规划并申请保存、保存后停止、模型写完但私有文件未写时中断，以及旧完整点可读。外部增长为明确标记的建模账输入；真实测试费用仍由外部根计量。已发布02_before_stop完整点可验证，03_interrupted只留下pending，不能被选为完整点。旧legacy成对点仍可读。身份补充检查拒绝私有tick偏移；准入补充检查拒绝省略完整根费用上界，均复用同一用例及原测量，没有新增保存基准或轨迹。

normal保存间隔50个0.1网格点，near-budget为10点，并在下一根操作会侵入保存余量时先保存。保存费用纳入根账。生产调用还需绑定循环和实测完整根操作上界，不能只套用2秒控制器预算；间隔只能限制已成功提交之间的尾部，不能保证每种硬中断下尾部为零。如果已经没有保存余量，拒绝新保存并保留最后完整点。原始v3科学包和旧结果没有改写。

普通开发失败均保留：导入错误未启动子Job，保守计1 CPU秒；工作区不允许hardlink，首个提交实现失败后改为Windows原子独占rename。没有删测试或放松成对提交条件。对应失败调用也纳入阶段额度。没有再次证明Job计量；没有将设施成功解读为科学成功。

[单用例证据](C:/Cursor/raven.mcs/results_action_difference_revision_20261013/B_FACILITY_RESULT.json)、[完整根准入](C:/Cursor/raven.mcs/results_action_difference_revision_20261013/B_ADMISSION_CONTRACT_PASS.json)、[配对身份](C:/Cursor/raven.mcs/results_action_difference_revision_20261013/B_PAIR_IDENTITY_PASS.json)、[保存完成标记](C:/Cursor/raven.mcs/results_action_difference_revision_20261013/facility_pairs_rename/02_before_stop.complete.json)。实际计费与墙钟见[BUDGET_LEDGER.md](C:/Cursor/raven.mcs/ccf-review-report/action_difference_revision_20261013/BUDGET_LEDGER.md)。
''')

    report('ACTION_DIFFERENCE_CANDIDATE.md',r'''# 一次局部候选：共同允许未来下的动作差值

状态：C最终失败，停止该修订推进；novelty=needs-search。不是已实现并验收的生产方法，不声称共同随机数或配对差值本身具有独创性。

问题仍是稀疏服务/质量支持下的部署几何跨窗口停止。旧v3先求各计划的绝对驻留分数包络，早期未知会使共同项无法有效抵消。候选的实质变化是直接对Δ_p(z)=J_p(z)−J_CLOSE(z)构造覆盖联合合法未知集合Z的界；不更改μ、P2、驻留评分、H8、四场景等权、Δ0.1、D4、age5、风险门槛、最小客户端数、聚合约束或原实验筛查线。

外生输入包括注册/观测日程、公共资源和基础服务随机量、历史下载lag；资源外生且无共享竞争是沿用的适用条件。分支状态包括当前版本、open时间、pool、pending、替代顺序、age、消费集合、debt、q/p与质量摘要、last_release和驻留分数。真实训练CPU下界、模型版本和stage1转换可能使完成时间/标记依赖动作。同一随机源不能被用来强制这些量相同。Z必须覆盖两条动作分支的合法变化；同client未知标记只允许公共目录支持，无概率支持的分支不填成概率。

差值推导：在N个网格、4场景下，Δ_p=(1/(4N))Σ_sΣ_t[score(S_p,s,t)−score(S_C,s,t)]。若每个合法联合分支的局部差值都被l_s,t和u_s,t覆盖，则其等权和给出有效[LΔ,UΔ]。直接求联合差值的极值也有效。只在已证明两边评分相关状态及未来转换完全相同的网格，才能把该项置零；pool相同不足以证明再汇合。未来版本、年龄过期、较新消息替代、debt、消费与完整P2约束均由原生命周期内核传播。找不到联合结构时只能回到约[-1.22,1.22]的差值粗界，不能因先作差而声称变窄。

充分条件沿用指令：存在合法WAIT计划p满足UΔ_p<−1e−7，则该见证计划优于CLOSE；所有合法WAIT均满足LΔ_p>1e−7，则CLOSE优于全部WAIT；否则保留已声明后备。这只是有限经验预测域内的充分条件，不是部署风险保证。本次没有完成全Z外包络算法或证明：事前冻结的反例检查已阻断继续条件。

唯一早期未知检查事前见[CANDIDATE_CHECK_FROZEN.md](C:/Cursor/raven.mcs/ccf-review-report/action_difference_revision_20261013/CANDIDATE_CHECK_FROZEN.md)。now22、open20、T100，四个客户端；未知在22.2和22.25登记。固定offset为0、0.1、0.5、1、2（等于原候选规则在该状态的合法集合），两种首动作均合法。原完整P2与H8驻留评分实际调用，33个合法有限分支、每个4等权场景，198次P2、946次cache命中。人工目录明确允许fixture四客户端全部172群组；它不是Traffic真实目录。q=0.5仅为隔离用例输入，不是动态校准概率。已知μ来自旧冻结目标，不读取44001真实未来完成或私有通知。计算前后实际runner状态一致，SGD=0。

33点只是完整联合集合的合法子集：两边同完成时间/标记的对角情形在此子集中允许，不是对全Z的约束。每个WAIT存在正差值的合法反例，因此任何正确全Z上界都不能小于−1e−7；同时0.1、0.5、1三个WAIT各有负差值反例，阻止CLOSE所需的全部正下界。代表数值：WAIT0.1的子集范围[-0.2495515382,0.4980050618]；WAIT0.5为[-0.6946652414,0.5008050618]；WAIT1为[-0.1066255814,0.5110785718]；WAIT2为[0.0002500000,0.0502582230]。这些是子集极值，不是全Z外界，也不证明WAIT2在全Z一定更差。

原实际浮点内核的容差与反例符号有充足间隔（判定阈值1e−7，记录附加1e−10数值余量）；未提出新的真部署误差保证。所有计划都有阻止稳健WAIT的正反例，至少一个计划有阻止全WAIT正下界的负反例。因此不存在能在本状态同时正确覆盖这些合法情况并通过指定动作判据的界；C为FAIL_NO_CERTIFIABLE_ACTION_ON_FROZEN_EARLY_CASE。不移动未知时点、不换初态、不添加预测器、不借client标记、不改评分继续尝试。

33分支内核CPU4.296875秒、墙钟5.171111秒；完整C调用（含启动与监视）计费7.343750 CPU秒。这个总量不是单决策2秒验证；生产2秒可行性没有建立。没有以放宽时间预算换取证书。C失败只针对这个冻结验收，不证明所有状态或整个配对差值研究方向不可能。

[全部分支、闭窗版本/消费/debt轨迹](C:/Cursor/raven.mcs/results_action_difference_revision_20261013/C_BRANCHES.json)、[结果CSV](C:/Cursor/raven.mcs/results_action_difference_revision_20261013/ACTION_DIFFERENCE_BRANCH_RESULTS.csv)、[判定及反例索引](C:/Cursor/raven.mcs/results_action_difference_revision_20261013/C_RESULT.json)、[实际检查代码](C:/Cursor/raven.mcs/scripts/check_action_difference_candidate.py)。CSV中每个WAIT行重复该分支的全计划CPU/P2，不能跨WAIT行累加成本。
''')

    report('EXISTING_STATE_PROBE.md',r'''# 已有状态检查：未启动

状态：NOT_RUN_C_GATE_FAILED。C未通过，按C→D门槛取消D。没有选择12个真实状态，没有运行候选优化，没有读取真实未来、应用模型更新或模拟新轨迹，也没有拆分旧暖启动/序列化/启动/求解/退出成本。此处不存在实测动作、区间宽度或单决策2秒可行性结果。

若未来另获批准，原选择规则仍是pool3–9与≥10两组，每组按UNKNOWN_FIXED_TIME_2、CPU_TIMEOUT分别取最早/时间中位/最晚，去重且最多12点；合法因果快照缺失则标未知，不补选有利点。当前只记录规则，没有事后筛选成功状态。输入须限注册时合法快照与t≤20冻结资料；旧诊断q不能替代动态校准。

[结果CSV](C:/Cursor/raven.mcs/results_action_difference_revision_20261013/EXISTING_STATE_PROBE_RESULTS.csv)只有取消记录，状态/时间/区间/P2/CPU字段空白表示未执行，不是0或通过。C的人工有限分支证据独立存放，不改名成真实开发状态结果。恢复D需要用户对新的方法准备或修订范围作决定，余额不授权继续。
''')

    report('NEXT_STAGE_REQUEST.md',r'''# 下一阶段请求

唯一建议：暂停这一次动作差值方法修订。状态保持WAITING_USER_REVIEW。

A验证了旧分支确定性上界，B独立设施修复通过，C冻结早期未知检查最终失败，因此D取消。新候选没有提供获准进入真实状态验证所需的动作区分，不申请新的限定真实开发采集。没有800秒恢复请求，也不恢复t80分支替换旧失败。

设施代码、所有反例和旧资产保留。若用户希望继续研究，需要明确批准新的方法定义/不确定集合依据及限定准备预算；不能把本批剩余额度作为改状态、追加预测器、移动未知时点或重试其他候选的授权。若不继续，可保留设施修复并终止此候选。当前不自动实施任何方法变更。

校准七条、q拟合、充分训练、配对主实验、B1、20种子确认均未启动。检测收益、任务性能不退步、预测收益均没有新增对应证据；旧性能结果保持RESULTS_NOT_REVALIDATED。既有性能门槛没有放宽。完整开发比较、概率依据、完整外部基线、资源与独创性核验仍属于以后经批准的阶段，不能据设施测试或人工反例申请正式确认。

预算详见[BUDGET_LEDGER.md](C:/Cursor/raven.mcs/ccf-review-report/action_difference_revision_20261013/BUDGET_LEDGER.md)。报告目录只存MD；机器证据、CSV、日志、设施配对文件在results_action_difference_revision_20261013。
''')

    report('FAILURE_REPORT.md',r'''# 最终失败报告：C早期未知动作区分未通过

最终状态：WAITING_USER_REVIEW；A、B有效，C失败，D及该候选生产实现取消。失败不是普通编译问题；不在本批内通过换初态、移未知时点或改方法来消除。

预期：一个事前冻结、两种首动作均合法且含早期未知的有限检查，应证明正确覆盖全部合法分支的差值界能给出v3没有的动作区分。实际：33个子集分支中，每个合法WAIT都有正差值反例，且至少一个WAIT有负差值反例。判据为存在UΔ<−1e−7或所有LΔ>1e−7，两者均被反例排除。

可复核反例索引（0基）及Δ=WAIT−CLOSE：

- WAIT0.1：branch1，+0.4980050618059713；branch12，−0.24955153822655318。
- WAIT0.5：branch4，+0.5008050618059710；branch9，−0.6946652414243555。
- WAIT1：branch6，+0.5110785717952528；branch13，−0.10662558139534836。
- WAIT2：branch0，+0.05025822295804261；branch10，+0.0002500000000000835（此项没有负反例，不影响上述CLOSE失败证明）。

任何覆盖全Z的外上界至少覆盖对应正反例；WAIT0.1等计划的外下界必须覆盖其负反例。故这次冻结检查不可能满足原稳健动作充分条件。子集极值不是全Z外界，不把该结果解释成所有状态下不可能改进。风险证书、真实控制收益和预测收益均未建立。

确定原因：原评分/P2/生命周期允许不同合法服务/质量情况改变动作排序，正确联合覆盖无法在该初态固定一个见证动作。共享输入不使版本、消费或debt相同；全部闭窗状态保存在原始分支证据中。尚未证明的猜测包括其他状态能否缩窄界、真实目录是否更受限、成本是否可优化；这些没有转成新测试或结论。生产2秒计算能力和12个真实状态探测未验证。

仍有效：A原CSV及10/799上界；B实际根费用反馈、保存准入、原子完成标记与半对拒绝、旧完整点可读。B的导入和hardlink普通错误在原规格内修复，失败日志计费并保留，未删除验收条件。C检查代码采用原完整P2驻留内核，只读传播克隆预测状态，没有训练和真实采集。

已消耗预算见[BUDGET_LEDGER.md](C:/Cursor/raven.mcs/ccf-review-report/action_difference_revision_20261013/BUDGET_LEDGER.md)及[逐调用原始账](C:/Cursor/raven.mcs/results_action_difference_revision_20261013/FINAL_BUDGET.json)。上限300 CPU秒（设施120、证据与机制180），SGD/GPU/q拟合/新增轨迹均为0；历史实耗缺口继续UNKNOWN。取消任务：D12状态筛选/探测、D开销拆分与快路径建议、候选生产控制器、v3续采、七条校准、B1和正式确认。

旧结果、原失败与六份旧报告全部保留，最终保留核验见[FINAL_VERIFICATION.json](C:/Cursor/raven.mcs/results_action_difference_revision_20261013/FINAL_VERIFICATION.json)。继续需要用户批准新的方法准备范围；本批唯一建议为暂停此修订，未自动转向其他候选。
''')

    assert all(p.suffix=='.md' for p in REPORT.iterdir())
    result=dict(status='PASS',old_files_checked=len(original),old_files_changed=changed,
        frozen_spec_and_script_unchanged=True,new_python_syntax_files=len(targets),
        A='PASS',B='PASS',C=c['status'],D='NOT_RUN_C_GATE_FAILED',
        reports_md_only=True,SGD=0,GPU=0,q_fit=0,new_trajectories=0,
        final_state='WAITING_USER_REVIEW',performance='RESULTS_NOT_REVALIDATED')
    with (OUT/'FINAL_VERIFICATION.json').open('x') as stream:json.dump(result,stream,indent=2)
    print(json.dumps(result))
