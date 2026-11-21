# 停止 TMC 冲刺：决定报告

**日期：** 2026-09-13  
**对象：** RAVEN-MCS → IEEE Transactions on Mobile Computing 正刊  
**范围：** 是否继续以方法/系统贡献冲 TMC。无新训练、无改表。

---

## 决定

**停止向 IEEE TMC 正刊冲刺。**

关闭 2026-09-12 方案中的路线 A（T-Drive 四象限剩余 49 次训练）、路线 B（受限支持 Design、Δ–RMSE 耦合、hybrid 上再消融 Use/Debt），以及路线 C（联合实测 \(R/O/U\)；仓库内做不到）。

本决定的含义是：现有证据已经足够判断，继续 GPU 实验关不掉 TMC 方法刊的拒稿轴，且会掉进无界补实验。它不否认问题表述和协议工作的价值，也不指定下一投稿目标。

---

## 理由

TMC 正刊作为方法/系统刊，需要题名方法在目标预测端点上优于强基线，并在真实移动过程上成立。当前稿同时缺这两项，而且缺的不是措辞。

**审稿层。** 2026-09-12 三份独立盲审 Overall 为 6 / 5 / 4，Significance 均为 3。共通轴：唯一真实出租车排序用的是 RAVEN-NoDesign，且相对 FedAU/ObsUse 超出论文自定 +0.5% 容差；主表是站迹协议 \(R\)；\(U\) 从未实测；E4 上 \(\Delta_{\mathrm{group}}\) 几乎不带动 \(\mathrm{RMSE}_\mu\)。写作关闭已经做完。下一分只能来自实验或改定位。

**实现层。** 2026-09-13 完成 go/no-go 第一步（只对照理论与代码，不训练）。Table II 路径对齐手稿 Algorithm 1：调度器按 φ 在 `raven`（ζ 常开）与 `raven_wo_design`（ζ=1）之间切换，Gate 不开关 Design。SensorScope 上 Design 合法，ζ 分母与协议抽样同源。因此主表预测偏弱，不是 Gate 接错或 φ 失效，而是合法条件下收益有限。

继续冲刺所依赖的 X1（四象限、φ=0、Design 开）关不掉轴。该 φ=0 来自训练原子上四区 \(\mu_{h(i)}\) 全正，几乎自动开 Design，测不到 \((k,s)\) 支撑缺口。ζ 分母仍是冻结合成 \(\pi^{\mathrm{opp}}\)（等客户 × 尾块指数），不是真实占用频率，也不是论文滞后 \(P_r\)。跑完 49 次：过门槛会被问分母是否命题对象；不过门槛也不能写成理论已证伪。修分母必须改代码再重训，即无界补实验。

代码注册表里的 `raven_mcs`（Design:=Gate）与手稿相反，且未进入任何已发表表。把它训成新主方法同样是换方法，不是复核现稿。

---

## 支撑事实（均已在账本，无新数字）

| 证据 | 数字 | 含义 |
| --- | --- | --- |
| Table II SensorScope RAVEN-Design | RMSE_μ 7.9380，WorstGroup 8.6707 | 合法 Design；主表协议 \(R\) |
| Table II U-Air RAVEN-NoDesign | 1.1131 / 1.1703 | 困难支持上关掉题名矫正 |
| T-Drive hybrid NoDesign vs FedAU/ObsUse | WorstGroup +2.39% / +2.43% | 唯一真实出租车排序未过自定容差 |
| 同表强制 Design | 1.1242 / 1.3355 | φ>0 时硬开更差 |
| E4 SensorScope 去 Design | Δ_group +1.237%，RMSE +0.005% | 结构与预测脱钩 |
| E4 U-Air 去 Design | RMSE −6.553% | φ>0 时 Design 伤预测 |
| City Scanner 访问占用 | FedAvg 0.2379 / 0.2489 最低 | 真实访问 \(R\) 上不是题名方法赢 |
| Pilot 2 实测 \(O\)（PM） | Hájek 0.7097/0.7273 vs SCD 0.7135/0.7311 | 实测层上 Hájek 更低 |
| PATH_A（NO2，实验室、未进稿） | vs Hájek RMSE rel. ≈ −0.05%；vs FedAU ≈ +0.44% | 不构成接收头条 |
| Holm 家族（四项 20-seed WorstGroup） | 全部不显著 | 不能用显著性撑主故事 |
| 联合 \(R/O/U\) | \(U\) 全程对照 `compute_usable_r3` | 本仓库关不掉 |

φ 冻结维持：SensorScope 0/10285；U-Air 2016/5688 = 35.4%；T-Drive 135268/285659 = 47.4%。

X1 维持杀停：φ 0/285659 已冻；10 条 EventTrace 在盘；训练 1/50（仅 FedAvg 种子 31001）；Hájek 烟测于窗 45/178 按授权终止。不恢复矩阵。

Hájek 实现始终乘 Design 比。T-Drive 上 Hájek 1.1254 与强制 Design 1.1242 接近，均差于 NoDesign 1.1069。这与「φ>0 时硬开有害」一致，不能把 NoDesign vs Hájek 读成同一套矫正去掉 P2。

---

## 即刻冻结

- Table II 与 T-Drive hybrid 数字不改。
- 不恢复 X1，不 `--force`，不重算 φ，不重跑 T-Drive 178×60。
- PATH_A 不入库、不进 Table II、不写成赢了 Hájek。
- 不把 `pi_opp` 改成滞后占用后「试 1–3 个 seed」。
- 不把 `raven_mcs` 训成新主方法。
- 不新开城市，不把 GPS 叠到 SensorScope/U-Air，不重调 φ / \(p_{\mathrm{obs}}\) / \(s_{\max}\) / 网格。
- 作者栏、公开包哈希、页数可会前处理，不构成重新开冲的理由。

改投、降级为协议/负结果稿、或搁置，不在本报告范围内。
