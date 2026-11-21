# V2.3 实验设计方案 — 与「复用/封存/守卫」相关的检索结果

来源：`参考文件/RAVEN-MCS_V2.3_实验设计方案.docx`（mtime 2026-07-26 20:39，405 866 B）
提取正文 26859 字符，533 行。

## 1. 概念级命中

| 概念组 | 命中行数 |
| --- | --- |
| 守卫/封锁类 | 0 |
| 复用/重跑类 | 2 |
| 封存/封印类 | 13 |
| 金丝雀/canary | 0 |
| E2/E3 协议块 | 3 |
| 种子号 | 0 |
| NSW/交通 | 7 |

## 2. 逐条上下文（去重后按行号）

- L21: [List Number] 层B：论文主证据。在SensorScope、U-Air和NSW Traffic Volume上运行受控机会与两阶段选择实验，完整回答RQ1–RQ6。
- L25: [List Bullet] 第1–4节：明确研究问题、冻结规则、硬件软件和代码结构。
- L44: [Heading 1] 2. 论文—实验一致性的冻结规则
- L47: 冻结项 | 必须遵守的实现口径
- L93: 版本冻结 | 首次通过G0–G7后保存environment.yml、requirements-lock.txt和pip-freeze.txt。
- L114: NSW Traffic Volume | 交通流；主受控数据集 | 小时交通量 | 多站点、强日周期；必须做传感器可用性和质量审计
- L122: NSW Traffic Volume | Transport for NSW / Data.NSW Traffic Volume Counts | https://data.nsw.gov.au/data/dataset/2-nsw-roads-traffic-volume-counts-api | 当前门户提示数据质量与传感器可用性问题，必须执行质量门。
- L137: Traffic数据特别风险 / Transport for NSW公开门户已提示数据质量与传感器可用性问题。因此学生必须先输出station_quality_report.csv，再选择站点和连续时间段。若无法形成至少30站点×336小时的可靠矩阵，不得静默换数据；应先向教师报告，并将PEMS-BAY作为“需修改论文数据集描述”的备选方案。
- L153: [List Bullet] 测试段只在最终冻结配置后运行一次；测试结果不得反向修改配置。
- L157: 目标组h用于评价和债务；机会分层s用于估计重复机会概率。两者可以相同，也可以让s比h更粗以降低设计比估计方差。所有粒度必须在验证段冻结。
- L160: [List Bullet] 扩展目标：服务加权目标，例如交通主干道/重点空气监测区域权重为普通区域的2倍；权重在训练前固定。
- L300: [List Number] 冻结配置后生成frozen_config.yaml和hash；随后才能运行测试段和20种子主实验。
- L302: 避免组合爆炸 / 不要对所有参数做笛卡尔积。采用分阶段验证和小规模预筛：每阶段最多20–30个候选配置，先3个种子筛选，再用5个种子确认；最终冻结后跑20种子。
- L320: [Heading 2] 13.3 E2：目标风险错位证据
- L325: [Heading 2] 13.4 E3：主性能结果
- L388: 指标实现检查 / 有效训练分布中，记录i未参与当前本地目标时w_{k,r,i}=0。所有学习率加权分布以S_R=Ση_r I_r归一化。测试到达权重由冻结的机会和选择模型预测，不能拿训练到达计数直接映射到未来绝对时间槽。
- L403: [List Bullet] 求解器失败可以使用预注册fallback求解器重跑，但必须在manifest标记。
- L448: 第1周 | 下载与审计数据；冻结processed数据；完成G0。 | data_audit_report、dataset_manifest
- L451: 第4周 | Balanced和Oracle硬门；冻结参数流程。 | G6–G7报告、frozen_config
- L461: 真实交通数据质量不足 | 高 | 先做站点质量门；不足时报告教师并决定是否将PEMS-BAY作为正式替代。
- L467: 测试泄漏 | 高 | 配置冻结、测试只运行一次、manifest记录选择阶段。
- L478: [List Bullet] 论文中的每个结论都能指向一个CSV/JSON和一条可重跑命令。
- L494: experiment: E3_main_complete / dataset: sensorscope / seed: 26001 / split: /   train: 0.60 /   validation: 0.20 /   test: 0.20 /   warmup_fraction_of_train: 0.20 / clients: /   K: 50 /   local_steps: 5 /   risk_set_mean: 7 / window: /   num_windows: 300 /   duration: 1.0 /   max_staleness: 5 / scenario: /   name: complete_aligned /   opportunity_skew: 1.0 /   mean_observation_rate: 0.20 /   mean_u
- L514: # 1. 数据审计与预处理 / python scripts/audit_data.py --dataset sensorscope / python scripts/prepare_data.py --dataset sensorscope --freeze /  / # 2. 硬门 / pytest -q / python scripts/run_experiment.py experiment=E1_balanced seeds=26001,26002,26003,26004,26005 / python scripts/check_hard_gates.py outputs/E1_balanced /  / # 3. 主实验 / python scripts/run_grid.py experiment=E2_misalignment --seeds-file configs/se
- L520: [Small Text] [R4] Transport for NSW, NSW Roads Traffic Volume Counts API, https://data.nsw.gov.au/data/dataset/2-nsw-roads-traffic-volume-counts-api (accessed 2026-07-26).

## 3. 文档的全部标题（章节结构）

- L14: [Heading 1] 文档摘要
- L24: [Heading 1] 目录与阅读顺序
- L31: [Heading 1] 1. 实验目标与研究问题
- L32: [Heading 2] 1.1 总体目标
- L34: [Heading 2] 1.2 必须回答的研究问题
- L44: [Heading 1] 2. 论文—实验一致性的冻结规则
- L63: [Heading 1] 3. 实验执行阶段与硬门
- L65: [Heading 2] 3.1 八项前置硬门
- L77: [Heading 2] 3.2 运行停止规则
- L82: [Heading 1] 4. 软硬件环境与可复现设置
- L83: [Heading 2] 4.1 推荐环境
- L95: [Heading 2] 4.2 硬件建议
- L99: [Heading 2] 4.3 随机性控制
- L103: [Heading 1] 5. 代码仓库与产物结构
- L108: [Heading 1] 6. 数据集选择、下载与审计
- L109: [Heading 2] 6.1 数据集角色
- L117: [Heading 2] 6.2 官方来源与下载记录
- L125: [Heading 2] 6.3 数据审计硬门
- L139: [Heading 2] 6.4 建议预处理口径
- L147: [Heading 1] 7. 公共目标、数据划分与客户端测量构造
- L148: [Heading 2] 7.1 时间划分
- L154: [Heading 2] 7.2 原子单元、目标组和机会分层
- L158: [Heading 2] 7.3 目标分布
- L162: [Heading 2] 7.4 客户端测量异质性
- L168: [Heading 1] 8. 机会流与两阶段非随机选择模拟器
- L169: [Heading 2] 8.1 固定事件轨迹原则
- L174: [Heading 2] 8.2 受控机会生成
- L181: [Heading 2] 8.3 第一阶段：观测选择
- L187: [Heading 2] 8.4 第二阶段：计算—网络—过期事件
- L196: [Heading 2] 8.5 六类选择场景
- L208: [Heading 1] 9. 共同数据补全骨干与训练协议
- L209: [Heading 2] 9.1 主同骨干：Common-NDMF
- L224: [Heading 2] 9.2 局部训练与更新归一化
- L230: [Heading 2] 9.3 FLAMF-Original外部复现
- L235: [Heading 1] 10. 对比方法与精确定义
- L252: [Heading 1] 11. RAVEN-MCS核心实现细节
- L253: [Heading 2] 11.1 第一阶段权重与ESS
- L260: [Heading 2] 11.2 第二阶段参考
- L264: [Heading 2] 11.3 目标债务与P2
- L272: [Heading 2] 11.4 滞后方差代理
- L275: [Heading 1] 12. 参数设置与验证策略
- L276: [Heading 2] 12.1 默认参数
- L295: [Heading 2] 12.2 调参顺序
- L304: [Heading 1] 13. 完整实验矩阵
- L305: [Heading 2] 13.1 E0：单元测试与合成真值检查
- L315: [Heading 2] 13.2 E1：Balanced不伤害硬门
- L320: [Heading 2] 13.3 E2：目标风险错位证据
- L325: [Heading 2] 13.4 E3：主性能结果
- L331: [Heading 2] 13.5 E4：消融实验
- L345: [Heading 2] 13.6 E5：支持性与可达性
- L350: [Heading 2] 13.7 E6：估计误差、漂移与截断
- L356: [Heading 2] 13.8 E7：识别边界与总体校准残差
- L360: [Heading 2] 13.9 E8：规模与系统开销
- L365: [Heading 2] 13.10 E9：T-Drive-Speed真实轨迹一致性实验
- L371: [Heading 1] 14. 指标公式与实现注意事项
- L390: [Heading 1] 15. 统计检验与报告规范
- L391: [Heading 2] 15.1 重复次数
- L395: [Heading 2] 15.2 配对统计
- L401: [Heading 2] 15.3 结果异常处理
- L406: [Heading 1] 16. 论文图表与输出清单
- L428: [Heading 1] 17. 质量保证与自动化测试
- L445: [Heading 1] 18. 建议时间计划与分工
- L458: [Heading 1] 19. 风险清单与应对措施
- L470: [Heading 1] 20. 最终验收标准
- L471: [Heading 2] 20.1 可进入论文主表的必要条件
- L479: [Heading 2] 20.2 高质量实验的最低证据链
- L492: [Heading 1] 附录A：建议默认配置示例
- L496: [Heading 1] 附录B：逐窗口输出字段
- L512: [Heading 1] 附录C：主运行命令建议
- L516: [Heading 1] 附录D：数据与方法参考资料
- L524: [Heading 1] 附录E：学生提交给教师的最终实验包

## 4. 与「可复现/冻结/交付」相关的段落原文

- L5: 供学生直接实施的高质量、可复现、可审计实验计划
- L9: 实验性质 | 半合成受控实验 + 真实轨迹一致性实验
- L22: [List Number] 层C：真实轨迹一致性。在T-Drive-Speed上使用真实车辆移动轨迹构造机会流，验证方法在非均匀真实移动模式下仍成立。
- L25: [List Bullet] 第1–4节：明确研究问题、冻结规则、硬件软件和代码结构。
- L26: [List Bullet] 第5–8节：完成数据审计、公共目标构造、机会分层和两阶段事件模拟。
- L33: 构建一套可复现的窗口化异步联邦数据补全实验平台，系统比较“原始到达分布优化”与“部署目标风险优化”的差异，并验证RAVEN-MCS在机会不平衡和两阶段非随机选择下的有效性、稳健性、理论一致性及系统开销。
- L44: [Heading 1] 2. 论文—实验一致性的冻结规则
- L47: 冻结项 | 必须遵守的实现口径
- L56: 测试一致性 | 所有方法共享相同测试单元、测试掩码、公共特征和目标权重。
- L68: G0 数据完整性 | 数据哈希固定；时间划分无重叠；训练归一化参数未使用验证/测试数据。 | 必须通过
- L69: G1 事件复现 | 同一seed下所有方法的R、O、E、U、计算时延、网络时延完全相同。 | 必须通过
- L79: [List Bullet] 如果一个场景的目标支持N_g^eff不足或窗口可达误差过大，应标记为“stress/unsupported”，不得混入理论一致性主表。
- L80: [List Bullet] 若RAVEN与Oracle差距过大，优先审计机会比、p/q校准和截断率，而不是立即提高λ参数。
- L82: [Heading 1] 4. 软硬件环境与可复现设置
- L93: 版本冻结 | 首次通过G0–G7后保存environment.yml、requirements-lock.txt和pip-freeze.txt。
- L105: raven-mcs/ / ├── configs/ / │   ├── dataset/          # SensorScope, U-Air, Traffic, T-Drive / │   ├── scenario/         # balanced, complete, drift, hidden-confounding / │   ├── method/           # baselines, ablations, RAVEN / │   └── experiment/       # E0...E9 / ├── data/ / │   ├── raw/              # 只读原始数据 / │   ├── interim/          # 清洗、对齐、审计结果 / │   └── processed/        # 固定split与公共目标 / 
- L107: 每个run的manifest.json至少包含：Git commit、dirty状态、数据哈希、配置哈希、环境哈希、所有seed、运行开始/结束时间、主机信息、求解器状态、是否通过硬门、是否可进入主表。
- L108: [Heading 1] 6. 数据集选择、下载与审计
- L114: NSW Traffic Volume | 交通流；主受控数据集 | 小时交通量 | 多站点、强日周期；必须做传感器可用性和质量审计
- L115: T-Drive-Speed | 真实移动轨迹；外部一致性实验 | 网格—时间平均速度 | 机会流来自真实出租车轨迹，验证移动偏置
- L125: [Heading 2] 6.3 数据审计硬门
- L127: 审计项 | 通过标准
- L134: Hash | raw/interim/processed均生成SHA256；处理脚本版本写入manifest。
- L142: SensorScope | 选择连续312个时间片、55个稳定传感器作为复现起点；随后可扩展到更长区间。 | 负值/极端值依据变量物理范围标记；短缺失仅用于构建公共参考，不作为客户端已观测。
- L143: U-Air | 优先采用36个1 km×1 km区域、264个小时的可复现设置；随后扩大时间范围。 | 统一PM2.5单位；对极端污染值保留但记录winsorization敏感性。
- L153: [List Bullet] 测试段只在最终冻结配置后运行一次；测试结果不得反向修改配置。
- L157: 目标组h用于评价和债务；机会分层s用于估计重复机会概率。两者可以相同，也可以让s比h更粗以降低设计比估计方差。所有粒度必须在验证段冻结。
- L222: 为什么使用Common-NDMF / 它满足论文中一般可微f_θ的要求，能在所有方法间完全共享模型容量和局部优化协议，并能对未来时间槽使用公共时间特征预测。FLAMF-Original仍作为外部系统基线单独复现，但不用于组件级公平比较。
- L230: [Heading 2] 9.3 FLAMF-Original外部复现
- L232: [List Bullet] 先在SensorScope N=55、T=312和原论文2–5客户端设置上复现实验趋势；通过后再接入本研究窗口事件。
- L234: [List Bullet] 无法完全复现时，必须报告复现差异，不得把TimeAlign-Agg错误命名为FLAMF。
- L300: [List Number] 冻结配置后生成frozen_config.yaml和hash；随后才能运行测试段和20种子主实验。
- L302: 避免组合爆炸 / 不要对所有参数做笛卡尔积。采用分阶段验证和小规模预筛：每阶段最多20–30个候选配置，先3个种子筛选，再用5个种子确认；最终冻结后跑20种子。
- L365: [Heading 2] 13.10 E9：T-Drive-Speed真实轨迹一致性实验
- L388: 指标实现检查 / 有效训练分布中，记录i未参与当前本地目标时w_{k,r,i}=0。所有学习率加权分布以S_R=Ση_r I_r归一化。测试到达权重由冻结的机会和选择模型预测，不能拿训练到达计数直接映射到未来绝对时间槽。
- L403: [List Bullet] 求解器失败可以使用预注册fallback求解器重跑，但必须在manifest标记。
- L433: test_event_trace_identity | 所有方法读取相同EventTrace hash。
- L441: test_manifest_complete | 所有主表run均有数据/config/git/environment hash。
- L447: 时间 | 任务 | 交付物
- L448: 第1周 | 下载与审计数据；冻结processed数据；完成G0。 | data_audit_report、dataset_manifest
- L451: 第4周 | Balanced和Oracle硬门；冻结参数流程。 | G6–G7报告、frozen_config
- L452: 第5周 | E2错位证据与E3主结果，先5种子审计再20种子。 | 主CSV、主表初稿
- L455: 第8周 | 系统开销E8、统计检验、论文图表和复现包。 | 最终报告、paper_artifacts、release
- L462: FLAMF复现困难 | 中高 | 把TimeAlign-Agg作为主要同骨干对比；FLAMF只作为外部基线，明确复现差异。
- L466: Oracle反而更差 | 高 | 审计MC q、设计比方向、质量m与ESS混用、归一化和事件共享。
- L467: 测试泄漏 | 高 | 配置冻结、测试只运行一次、manifest记录选择阶段。
- L473: [List Bullet] run的manifest完整，配置、数据、事件和代码可重建。
- L499: run_id, seed, dataset, method | 身份与复现
- L514: # 1. 数据审计与预处理 / python scripts/audit_data.py --dataset sensorscope / python scripts/prepare_data.py --dataset sensorscope --freeze /  / # 2. 硬门 / pytest -q / python scripts/run_experiment.py experiment=E1_balanced seeds=26001,26002,26003,26004,26005 / python scripts/check_hard_gates.py outputs/E1_balanced /  / # 3. 主实验 / python scripts/run_grid.py experiment=E2_misalignment --seeds-file configs/se
- L526: [List Bullet] DATA_AUDIT_REPORT.md：每个数据集质量、split、支持和哈希。
- L529: [List Bullet] paper_artifacts/tables/*.tex与*.csv。
- L530: [List Bullet] paper_artifacts/figures/*.pdf、*.png和plot_data/*.csv。
- L531: [List Bullet] 所有run的manifest、resolved config、原始逐窗口metrics和日志。
- L533: [List Bullet] 一页LIMITATIONS.md：弱支持、错设、隐藏混杂、真实轨迹半合成部分和无法复现项。