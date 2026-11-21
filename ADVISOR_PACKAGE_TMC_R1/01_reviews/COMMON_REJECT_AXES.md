# 三份盲审共通拒稿轴

材料：Grok 6（只看 PDF）、Deepseek 4（稿+公开包）、GPT 5（稿+公开包）。均为 2026-09-12 20:25 之后的独立评审。

## 分数差在尺子，不在事实上

| 维度 | Grok | GPT | Deepseek | 是否共通致命 |
| --- | ---: | ---: | ---: | --- |
| Overall | 6 | 5 | 4 | 共识：不可直接接收 |
| Significance | 3 | 3 | 3 | 是：无系统向预测赢 |
| Evidence | 4 | 3 | 3 | 是：结构/容差撑主故事 |
| Soundness | 4 | 4 | 3 | Deepseek 额外扣：两方法 + Gate 0.750 |
| Reproducibility | 3 | **2** | 4 | GPT 把 verify 失败打最重；Grok 未跑包 |
| 立场 | borderline / major | major / 偏负 | weak reject | 都不是 desk reject |

Grok 略高：主张已经写窄，且没把哈希失败算进证据。  
Deepseek 略低：把 E4「\(\Delta\) 不买 RMSE」和覆盖度定理 0.750 当方法缺陷。  
GPT 居中：科学与 Deepseek 同类，打包（verify 2 mismatches、CS 未入包）扣在 Reproducibility=2。

## 关不掉的科学轴（实验或改定位）

| 轴 | 三份是否都写 | 现有表上的事实 | 写作能否关 | 哪个实验能关 |
| --- | --- | --- | --- | --- |
| R1 真实移动上题名方法未赢 | 都写 | T-Drive NoDesign +2.39%/+2.43%；CS 访问占用 FedAvg 最低；Pilot 2 Hájek 最低 | 否 | **X1** 四象限 Design-on 出租车矩阵；过门槛才关「输给 FedAU/ObsUse」 |
| R2 主表是协议 \(R\) | 都写 | Table II SensorScope/U-Air always-on | 只能降级为主开发表 | 不能把 Table II 改成移动表；需独立 hybrid |
| R3 无联合测量 \(R/O/U\) | 都写 | \(U\) 全是 `compute_usable_r3` | 只能写局限 | **X8** 新语料；当前仓库阻塞 |
| R4 两套方法 / \(\phi\) 启发式 | 都写 | SS/CS/NSW Design；UA/TD NoDesign | 只能命名，不能合成一个 estimand | **X5** 受限支持；**X1** 使出租车 Design 合法打开 |
| R5 \(\Delta\) 与 RMSE 脱钩 | Deepseek=major；另两份=moderate | E4 SS Design：\(\Delta_{\mathrm{group}}+1.24\%\)，RMSE +0.005% | 只能改贡献句 | **X4** 耦合实验；不响应则永久改贡献 |
| R6 Use/Debt 空转 | 都写 | E4 Use 全 n.s.；Debt \(\ll 0.5\%\) | 可降级模块 | **X6** 在 hybrid 家族消融；或裁掉 |
| R7 实测层上不赢 Hájek | Grok/GPT 点名 XXII | XXII：Hájek 0.7097/0.7273 vs SCD 0.7135/0.7311 | 已诚实 | 实验室 PATH_A 技术上 `hajek_bar=true` 但效应 \(\approx 0.05\%\)，且仍输 FedAU；**不建议当头条** |
| R8 Gate 名义 95% vs 0.750 | 仅 Deepseek major | Table XVII U-Air \(a=1.00\) validity 0.750；Gate 不切换 Design | **可降级出贡献** | 可选加大 \(n_{\mathrm{cert}}\)；不是 P0 GPU |

## 共通但可会前处理（非科学瓶颈）

| 轴 | Grok | GPT | Deepseek | 动作 |
| --- | --- | --- | --- | --- |
| 作者 `****` + 真名 | fail 上传 | P0 | P0 | 补全作者块 |
| 14 页 / MOPC | uncertain | moderate | moderate | 压到 12 或接受超页费 |
| `verify.py` 1886/2 | 未跑包 | Repro=2 | 写出 | 刷新 MANIFEST |
| CS 表未入点名包 | 写出 | major | 写出 | 入包或从摘要/结论降级 |
| 混合表 10 种子无显著性 | — | — | moderate | **X3** 配对检验，无需重训 |
| E2 未在真实 \(R\) 上复算 \(D_{\mathrm{aligned}}\) | — | — | moderate | **X2** 用现有 T-Drive 迹，无需重训 |

## 明确不要做的事

- 不要为了过 +0.5% 去改 \(\phi\) 阈值、改目标图、改 \(p_{\mathrm{obs}}\)。
- 不要把 PATH_A（NO2）并入 Table II，或写成「优于所有基线」。
- 不要把 GPS 间隔、客户端掉线、Bernoulli \(U\) 标成实测 \(U\)。
- 不要把 TEST10 的 +0.48% 写成 20 种子或显著性结论。
- 不要再把时间花在主文润色上指望 Overall 过 6。
