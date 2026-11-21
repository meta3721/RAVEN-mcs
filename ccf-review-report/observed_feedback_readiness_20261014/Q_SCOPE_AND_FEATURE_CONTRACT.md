# OF-v1：q事件、编码与适用身份契约

日期：2026-10-14。技能：ccf-experiment-designer，design。本文件冻结后续开发的唯一编码方案；本批没有实现编码器、拟合或验证概率。状态：CONTRACT_DEFINED / PRODUCTION_Q_PENDING。

## 事件和两种删失

qπ=Pπ(I(100)=1 | H_reg,R=1,E=1)。注册范围[0,100)，I指τ≤100的成功实际服务器提交包含该key；alpha=0的提交key也算消费。E仅为注册版本年龄≤5，R为合法观测校正质量非空。它们不是正性证明。计算失败、网络失败、替代和版本过期可使消费事件提前成熟为0；成功提交成熟为1。

预算前缀的尚未成熟记录为I_right_censored，不填0。真正处理到T100且完成唯一终点关闭后，剩余key行政成熟为I=0；服务仍未完成者同时physical_service_censored_at=100。消费成熟与物理服务完成是两个独立过程，消费已过期的消息仍可能稍后物理完成。前缀尚待服务者也单记物理删失，不与消费删失共用字段。R0/E0保留账与合法工作，不作为上述条件概率的训练样本。

当前AttemptRecord已实现消费mature/censor和physical_outcome，但没有独立physical_service_censored_at/reason字段。下一批补字段和恢复序列化；本批不凭pending推造服务终止时间。已成熟标签可以列支持统计，但拟合资料优先使用完整T100独立run；不能只抽前缀已成熟样本当无删失随机样本。

## 实际源码核对

RegistrationFeatures包含age、device/network、slack、P/F计数、配置hash、as_of、history_json/hash、clock_run_id与service_parameters_hash。registration_features记录注册前Q/V/L、elapsed、已交付P和公开F；当前本次尚未完成的私有stage1未进入历史。EvidenceQTable对asdict(features)整体哈希精确查表，其中含连续历史、run_id/as_of。该表只保留精确接口证据；未见run不能靠相同字典key泛化。没有外部对应证据时返回Pending，不能编表或沿用43001/44001的旧方法q。

完整history_json是合法归档，history_hash用于追溯。拟合器使用下列固定数值编码，不用hash、key、run_id或UTC作为预测变量。编码仍未证明足以消除消费选择；良好ECE/Brier不等于IPW无偏。

## 唯一编码：OFq-public-state-1

拟合单元为R1/E1注册。目录N=43、G=172及mu在部署前固定。device/network公开类别按冻结服务目录的字典序分别one-hot，未知类别拒绝，不以测试集构造字典。数值列按以下顺序固定，除列出的四个交互项外不增加交互、特征或阈值搜索：

1. age0,…,age5：注册版本年龄六列one-hot。
2. remaining=(100−t)/100；elapsed=(t−o)/4；slack=(o+4−t)/4。
3. P_count/43；F_count/43；P_mean_age/5；F_mean_age/5；P_oldest_age/5；F_oldest_age/5。F只用公开header和当前v，不含私有完成时间。
4. L_ell；L_age；L_duration/4；L_gap=min(t−L.time,100)/100；has_L。L为空前四列填0且has_L=0，这不是虚拟ell=0释放。
5. Q_size=||Q||1/(1+||Q||1)；Qhat·(Pbar−mu)；Qhat·(L.omega−mu)。Pbar为当前已交付合法composition的等权平均，不是P2最优组成。Qhat=Q/(1+||Q||1)。对应P/L为空时对齐列填0并用has_P/has_L区分。
6. P_distance=0.5||Pbar−mu||1；P_effective_n_mean/(1+P_effective_n_mean)；P_total_mass_mean/(1+P_total_mass_mean)；has_P。
7. V_mean/(1+V_mean)；V_max/(1+V_max)；has_V。V来自过去成功更新；V空时前两列0。
8. root_remaining_fraction=当前注册前根账effective_remaining/本批CPU硬上限；根账sample_age秒；root_sample_valid。不得用最终剩余额度反填。
9. 四列固定乘积：remaining×elapsed、remaining×P_count/43、remaining×age/5、elapsed×[Qhat·(Pbar−mu)]。

共有6+3+6+5+3+4+3+3+4=37个数值列，另加两套公开类别one-hot及截距。age/5由one-hot确定，只用于上述交互。规模归一化均用事前常数或x/(1+x)，不由全样本均值/验证数据归一化。符号对齐列允许[-1,1]，其他指标在其明确的合法范围内。没有当前P2预览列：等权Pbar只聚合已经可见的质量，避免额外求解和事后回填。完整归档保留全部Q/V/L/已交付P/公开F，以便检查编码信息损失；不能看拟合结果后无审批扩列。

当前history_json缺少注册前根资源快照；这三列须下一批在注册前原子采样并保存。没有样本时不事后回填旧账。本批没有给旧记录补列。resource_sample_valid=0只用于记录缺项，模型预测返回Pending；有效根账要求原命名空间、未finished、age≤1秒且有效余量≥0。

## 缺失、支持与拟合器

支持域为完全相同的政策/学习/服务/目标/端点身份，目录类别已知，t∈[0,100)、age∈{0,…,5}、P/F≤43、合法deadline、有效根账、全部非缺失必需数值有限。L/P/V空是结构缺失，上述flag和填值已有事前规则；其他缺失、未知类别或越域返回Pending，不静默裁剪成“有支持”。实际服务如允许同client多个F而超过43，本schema不自动放大；先报告支持不适用，等审批，而不是开新预测特征。

后续唯一拟合器为带截距的logistic ridge：平均二元交叉熵+0.5||w||²，截距不惩罚、lambda=1，无类别重权和超参搜索。优化器L-BFGS，零初始化，最多200迭代，梯度无穷范数≤1e−6；非有限、未收敛或单一标签时Pending。未来拟合申请至多120 CPU秒、GPU0；这不是本批授权。该规格不把原q_min=.05变成概率估计下界：预测sigmoid数值与逆概率裁剪分别记录，数值失格拒绝。样本不足/分层支持缺口照实披露，不能因小样本数值有效就升级角色。

独立run而非消息随机拆分；拟合与验证run用途预冻结。前缀不以未消费填0，第一条成本轨迹不据其结果选特征或正则。验证按run聚类报告Brier、ECE（固定10个[0,.1,…,1]箱）、log loss、样本/事件/删失与各公开层支持；验收沿用已有科学协议，没有本批另设宽松校准通过线。无独立证据只能fitted_not_validated，不称calibrated_estimate。

## 身份、发布和接口

适用身份必须有OF-v1全部控制常数、完整P2及约束、mu/目录/data/target版本、configured Design及stage1 p/ratio估计器、a/p/pi clipping、观察/抽样/缺失机制、CommonNDMF具体架构/参数形状、完整局部SGD和服务器学习率、local_steps1/LR0.01、样本协议、scaler/feature_schema、初始模型数值来源与hash，以及服务模型代码/参数/资源/通知机制、T100、本编码/拟合器版本。仅“model=CommonNDMF”不足。

区分环境family适用身份与每run实现参数清单：随机种子不入预测，但实际服务参数、生成器版本、learning/service独立RNG身份、根CPU硬上限必须保存；跨参数复用只有事前声明family且独立证据覆盖才允许，否则Pending。

每run保存run_id/origin_utc/unit和逻辑→实际UTC桥；原控制时钟没有证明恒定墙钟速率，不能以origin+逻辑时刻直接算UTC。q发布包记录published_at_utc、源run截至的真实通知UTC和证据完成时间、目标run收到包的UTC/逻辑时刻、有效窗口边界。目标注册必须晚于接收/发布；窗口中不换模型，旧消息q不变。当前as_of只支持单run逻辑比较，跨run桥待实现；不把源逻辑20借给目标20、不无依据置0。

未来接口PublicStateEncoder.encode(reg,archived_history,root_sample,identity)->features/version/support_reason；FrozenLogisticQ.predict_at_registration验证发布桥/身份/支持后返回冻结值。公共PredictorPolicyIdentity含编码/超参/具体参数artifact id及q版本，和闭环运行身份一起归档；避免参数artifact的hash自引用，可用非递归独立清单。现有policy_context_hash须补闭环q身份，不能只比环境配置hash。

角色分别为dependency_pending、isolated_test_input、diagnostic_prior、fitted_not_validated、calibrated_estimate及结构排除角色。当前schema已知diagnostic_prior但runner/preview授权链未接通，fitted_not_validated未实现；本批不修改生产接受条件。生产消费只接获准验证证据的冻结模型。π_boot使用固定Beta(1,1)均值.5；拟合后π(q)改变闭环选择，π_boot标签只能训练候选，不能证明π(q)已校准。冻结q之后另获批准的独立π(q)采集/验证才能形成对应证据；本批不拟合、不启动。

现有门槛、39条开发、充分训练及独立确认保留。编码契约清楚不代表正性、风险恢复、控制或预测收益。
