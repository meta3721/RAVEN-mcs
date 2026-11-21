# IMPLEMENTATION_CHECK

首个 K>3 的投影窗口是 0，K=20，kind=activeset。
约束残差 0.0，独立目标差 1.2368433831111091e-17，求解状态 optimal。
同一次真实更新的公式最大绝对差是 1.1720399783522712e-07，局部步数是 2。
服务器向量在开跑前从模型参数存储中克隆出来。否则 state_dict 别名会让局部 SGD 改掉服务器即将读取的基准，第一条更新就不是 theta - eta * sum(alpha * u)。
Hájek 局部损失调用次数 72。K=2 的合成投影退化为 Uniform。
空窗口承接：{'window': 'synthetic_empty_frame_after_probe', 'active': False, 'theta_max_abs': 0.0}。
投影探针里的 solve_p2 调用次数是 0。共享的事后反事实审计已从五条部署路径移除；F 仍在自己的聚合器里求解 P2。
P/U 关闭的是 P2 的参考锚点惩罚，以及债务、即时校准、方差和陈旧惩罚。校正参考 beta 的构造仍在，P 仍直接投影 beta。uses_reference_penalty=False 并没有移除参考重构。src 没有修改。
