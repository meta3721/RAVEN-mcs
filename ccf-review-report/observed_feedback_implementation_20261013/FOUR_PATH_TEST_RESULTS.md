# 四条关键路径验收

一个常驻worker依次执行，四项PASS。原始证据包括全部实际alpha/beta/mass/M/omega/ell/age、求解状态/残差、决策B各项、成熟/删失、模型及恢复摘要。新增字段验收是同一四用例范围的补齐，早期失败和成功记录保留。

1. 历史反馈：各用8次实际完整P2暖启动释放构造Q方向，再空关闭到20；v=8、Q约(0.03,0)/(0,0.03)，满足有限时域且有实际历史，不填任意大debt。当前3列、elapsed0.4、最近质量相同，P2组成与实际距离相同，动作CLOSE/WAIT，B=0.020873786408/0.019126213592；κ=0后均WAIT，P2原始Q仍保留，实际目标差-0.018000000000。零质量变化/b=0时0.4的B=0.020000000000为WAIT，0.5的B=0.025000000000为CLOSE；参数与阈值未改。172维冻结μ输入适配通过，不称真实Traffic可达行为。

2. 生命周期：注册p/q/非恒等Design比率冻结，私有未完成质量扰动不改变snapshot，扰动摘要若试图完成则被注册哈希拒绝；R0为outside_R、E0为structural_zero，均不进入逆概率分母。较新替代、失败、K不足、age5过期、暖启动与deadline小K完整P2、空关闭Q/V/L/v不变、前缀删失及T100行政终止均通过。终点只关闭一次，共7个不同key消费，没有重复。Gate0/RESET及Gate1/WARMUP不切换Design。实现消费遍历preview全部keys而不筛正权重；当前实际权重样本没有零权重，不额外声称已触发零权重实例。

3. 缓存：时钟与公开inflight-only变化复用同一numeric并生成新绑定；旧绑定仍被拒绝、旧fingerprint未修改；B随elapsed增长0.005，没有动作缓存。Q/V/版本/配置source/池删项及真实入池/替代/消费使key失效。当前实际输出与未缓存新路径、原完整preview在既有容差内一致。记录d=null。该用例cache统计solves=17、hits=3，solver计数包含解析完整P2，不能称全是凸求解器调用。

4. 提交/恢复：真实CommonNDMF及ClientTrainer适配，手工实际更新张量经完整权重提交，模型差与权重计算一致，v/Q/V/L含omega在成功后更新；SGD调用被拦截。真实backend在模型改变后故意方差更新失败，runner进入FAULT_QUARANTINED，不标成功消费、不继续正常snapshot、不发布完整恢复点；诊断文件保留部分模型变化。成功使用已有成对库保存/恢复新方法、q/p/Design、源代码、模型/历史版本、方差、时钟和torch/numpy/python RNG及stateless SGD配置；恢复动作、实际P2和规范状态一致。旧v3身份拒绝。真实后端的非隔离模式PendingQ产生明确缺依赖错误，没有常数或固定窗口后备。

最终30个完整请求最大保守根上界0.645000 CPU秒，全部≤2；提交/存储费用另列。Startup、相同用例普通错误修复及所有父/子/监视成本计入整批。未执行大池冷启动、真实训练、真实新轨迹、随机回放、论文实验或概率校准。

[原始证据](C:/Cursor/raven.mcs/results_observed_feedback_implementation_20261013/final_fields_validation/FOUR_PATH_RESULT.json)；[请求CSV](C:/Cursor/raven.mcs/results_observed_feedback_implementation_20261013/REQUEST_COSTS.csv)。
