# B：限定实现与关键路径

状态PASS，新增SGD=0。实际代码位于 C:\Cursor\raven.mcs\results_of_v1_small_scope_20261018_190539：gap_local.py（新授权、控制器、显式本地恢复适配），stage_b.py（验证），stage_c.py（唯一采集入口），run_metered.py（调用既有根计量）。未改写旧科学包、旧四臂入口、协议或参数；source_closure核验一致。

GapAuthorization为独立严格子类，唯一策略GAP20-fixed-reference、seed45001、calibration_only、CPU1000、SGD5000、GPU0、单臂。沿用旧config.source仅作为父科学配置来源，approval_source明确指向本次授权；不使用旧四臂授权冒充新策略。旧授权拒绝新策略，新授权拒绝45011。旧注册概率身份保持，新增注册使用新scope与run时钟。

真实t35检查点只作接口核验：控制器B=-0.06872155353900815、动作WAIT，与A公式一致；随后执行明确标记的SGD0预览提交检查。实际backend.apply收到的keys/alpha/eta与完整P2预览一致，实际模型版本增加1、L真实刷新、c_ref仍为0.9168365859958755；本检查不是自主轨迹，不用于效用比较。完整P2及Q不变。

终点、暖启动CLOSE/WAIT、deadline、K<3优先级全部通过；优先级检查使用调用桩，不执行合成轨迹。新身份的模型/生命周期/生产者RNG/固定参考配对保存恢复哈希相等，合法验证点：C:\Cursor\raven.mcs\results_of_v1_small_scope_20261018_190539\B_checkpoints\SGD0_post_apply.complete.json。旧恢复工厂保持原样，新身份需通过本地restore_gap恢复。C不得从此t35验证状态启动。

开发失败记录全部保留：B_RESULT_attempt1元组/列表比较误报；attempt2初始化预留过大导致预算准入拒绝；attempt3优先级测试试图构造含未来登记的历史时刻快照，被合法校验拒绝。分别统一序列比较、按已测成本收紧初始化预留、改用仅测分支优先级的调用桩；不修改科学定义、信息校验或费用门槛。attempt4通过。根费用见charge_B*.json。

C入口已做语法编译核验，运行前核验2GiB可用内存并另保留512MiB保存/增长余量；运行持续低于2GiB达30秒则合法保存暂停。所有新训练由真实CommonNDMF/ClientTrainer执行，不读取t>20旧更新作为自主载荷。

C终审已核对ARM_FROZEN_PLAN的全部本地源文件哈希、核心source_closure、私有生产者游标及最终配对点。后续若获续行授权，应先核对冻结的local_source_hashes和private.local_adapter_hash，再通过本地restore_gap读取新授权；旧restore_pair工厂不识别新策略，未被改写。stage_c目录采用排他创建，不能直接重跑已完成臂。
