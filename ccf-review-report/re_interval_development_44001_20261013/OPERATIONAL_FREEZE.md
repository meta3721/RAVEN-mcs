# 44001开发采集：事前范围与接线记录

日期2026-10-13；技能ccf-experiment-designer，design模式。执行授权来自用户本轮消息及指定的 `re-interval-v3-single-development-acquisition-instruction-20261013.md`。以下准备与唯一轨迹属于同一批准批次。

方法：reachability_stop/conditional-bundle-RE-interval-v3。角色development_activation_cost_only。种子44001，T100、网格0.1、暖启动20、GPU0、局部SGD最多5000步、批次CPU最多2700秒、每次规划仍最多2 CPU秒。μ、完整P2、评分系数、风险支持门槛和未知截断规则沿用已冻结版本。

种子用途审计只搜索可访问的运行清单、配置、协议、种子计划和资产名称，没有重扫所有论文/项目文本。16024项匹配用途的元数据文件未发现44001既往选择或执行；无未读错误。证据是原始目录 `SEED_REVIEW.json`。审计不证明不可访问历史或二进制内容中从未用过该种子。

新增 `DevelopmentAuthorization` 只允许本批准来源、方法、44001、development_activation_cost_only和5000步。原 `CalibrationAuthorization` 仍拒绝44001，原43001授权和源码闭包未改动。真实后端直接调用原ClientTrainer/完整Hájek局部目标，保留E0的实际训练，R0按原无观测语义处理。

独立接线核验使用一个确定性用例、SGD0，没有模拟服务抽样或新轨迹。核对真实训练入口参数、R0/E0记录、诊断先验隔离、原授权拒绝、实际张量提交及新版保存恢复。补齐恢复后的实时观测估计器与后端授权字段后，重验同一用例通过；首次资产也保留。接线测试不是训练或性能证据。

实际轨迹入口是 `scripts/run_re_interval_development.py`，直接使用新版session、DynamicWindowRunner、IsolatedController、q/stage1类型与保存接口；未调用旧connect_full_runner。原生产者只复用无关方法的数据读取、通知顺序及窗口后估计更新逻辑；注册类型、授权、随机源、同运行服务冻结均重新绑定。

模型初始数值由原声明的初始化seed43001重建，并与原初始模型内容身份比较；没有读取旧策略终态模型。44001是owner/开发身份，真实服务与观测使用44014，局部dropout使用44030，规划使用SeedSequence[44001,tick,scenario,94031]。这些用途分别进入冻结清单。

从原已发布的无标签公共目标目录复用元数据，测量读取明确过滤TRAIN。CommonNDMF维度32/32、head[128,64,32,1]、dropout0.1、原Hájek SGD、local_steps1、LR0.01及TRAIN scaler不变。服务仍为原受控模拟服务，单CPU、无共享队列竞争，采样计算时间以下限映射实测局部CPU；不称为物理设备部署。

q在calibration_only入口使用新版Beta(1,1)均值0.5诊断先验；它不是已校准概率。π身份包含该先验和新版闭环规则；本批不拟合q，不将旧43001标记纳入新服务核。t≤20历史取自本运行全部注册的R/client/资源/age/时钟，条件服务资料冻结后不回填未来。

统计集合D事前定为20<t<100的常规网格点，完整轨迹799点。总动作差异保留规则强制、后备和超时；机制差异要求两种动作都合法、区间已证明且不同于同状态影子动作，并以整个D作主分母。fixed_time_2不更新模型或消费消息，不能作为配对收益基线。

冻结原始资料在 `C:/Cursor/raven.mcs/results_re_interval_development_44001_20261013/ACQUISITION_FROZEN_PLAN.json`。这份接线记录不预告机制或科学结果；最终结果另交报告。43002–43008、q校准、B1和正式确认均不属于本批执行范围。
