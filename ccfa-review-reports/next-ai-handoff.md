# RAVEN-MCS 交接（给下一轮对话）

日期：2026-10-11。工作区 `C:\Cursor\raven.mcs`。稿件 `TO_OVERLEAF_paper_tmc_r1_clean/main.tex`，证明在 `appendix.tex`，由 `supplemental.tex` `\input{appendix}`。本文件只记录后续任务用得上的内容。

2026-10-10 的审稿 `ccfa-review-reports/raven-mcs-tmc-review.md` 在常数句和可用性段上已经落后于当前 `main.tex`。以本文件 2026-10-11 核对过的正文为准。

## 硬约束

- 不 commit、不 push，除非用户明确要求。
- 作者保持 `****` 和 Anfeng Liu。不要把 Overleaf 密码写入仓库。
- 不覆盖 `tdrive_protocol_seal_r1/`。
- 不恢复 X1。不摄入 PATH_A NO2。
- 不运行 `build_public_repro_bundle.py` 的完整 `build()`。
- 协议不得让执行者改 `src/` 或论文。新输出只进新目录。
- 不改冻结表的单元格，除非用户授权。
- 不把 S1′ 表写成已完成结果。不在主表加常数列。不把 TS1 数字放进摘要。
- 不加 FedAdam 的 bib，除非先检索。
- 不删种子 30005。不为了追 Evidence 再开预测余量实验，也不为了把余量压到 0.5% 以下而加种子。
- 不把 `raven-mcs-traffic-concentrated-target-experiment-design.md` 的约 640 次运行当作抬 Significance 的手段。Phase 0 重算可以做；正式重训不该为这个分数启动。
- Python：`.venv_new\Scripts\python.exe`。Shell 是 PowerShell，不能用 `&&`。避免内联 `python -c` 的 f-string；临时脚本放 `.m7_work/` 并在用完后删除。
- 本会话曾用环境变量 `GIT_AUTHOR_NAME` / `GIT_COMMITTER_*` = `raven-mcs` / `raven-mcs@local` 提交，没有改 git config。第一次提交因 “Author identity unknown” 失败。已推送的只有 S1′ prompt 提交 `43bb8eb`（先前会话）。论文修改、审稿、文献检索目录、结果目录当时未提交。2026-10-11 未再跑 git status。是否已提交：不确定。

## 已确认事实

### 稿件主张现在写成什么样

- 摘要的正结果是结构投影：SensorScope 上相对均匀权重 +0.768 个百分点组失配。协议表不是 RMSE 胜利。
- RMSE 定义（`main.tex` 约 1606–1613，2026-10-11 读到的句子）同时写了两个常数：
  - 用被评分的测试标签拟合的常数：SensorScope 2.088，U-Air 0.678，NSW-Traffic 1.007。
  - 只用训练划分的训练均值预测器：7.647，1.054，1.007。
  - 测试均值 7.657、−0.807、0.003；训练均值 0.301、0、0。
  - 正文写明 SensorScope 与 U-Air 的绝对列对着训练均值预测器读。
- 主表题注（约 1885–1888）重复了 SensorScope 2.088 / 7.647 与 U-Air 0.678 / 1.054。
- 这些印刷值对得上 `results_traffic_struct/round_v1/TWO_CONSTANTS.json` 的四舍五入：
  - SensorScope：`oracle_constant_rmse` 2.0877500904618667，`deployable_constant_rmse` 7.647115745777104，`test_mean` 7.657185180649601，`train_mean` 0.3005773489727914，`n_test` 3410，`frozen_fedavg_rmse` 7.914361980993586。
  - U-Air：`oracle_constant_rmse` 0.6780523853857164，`deployable_constant_rmse` 1.0537137345464347，`test_mean` −0.8065715077068707，`train_mean` 约 0，`n_test` 1908，`frozen_fedavg_rmse` 1.210848485707097。这个 1.2108 不是主表印出的 U-Air FedAvg 1.1119。
  - NSW-Traffic：`oracle_constant_rmse` 1.0066933864830503，`deployable_constant_rmse` 1.0066970463463054，`test_mean` 0.0027145411515688053，`train_mean` 约 0，`n_test` 6192，`frozen_fedavg_rmse` 为 null。
- 可用性段（约 2315–2320）现在指向 `results_traffic_e1/` 种子 30006–30020，以及 `results_traffic_struct/` 和 `TWO_CONSTANTS.json`。2026-10-10 审稿说可用性段没写这些路径；该说法对当前文件不成立。
- `reference.bib` 仍无 Deville / Särndal。相关工作已引用 FedIPW（`morishita2026who`）和 FedPALS（`listozec2024overcoming`），并写投影是与 FedPALS 相同的匹配步骤、对象换成部署组组成。文献检索目录：`literature-search-20261010-selection-corrected-aggregation/`。缺失引用是 Deville and Särndal, JASA 1992，doi:10.1080/01621459.1992.10475217。不要把 FedPALS 图像精度或 FedIPW 合成损失当成 RMSE 基线重跑。FedPALS 会议录用：不确定（检索时未核实）。

### NSW-Traffic Adam 相对数（文件核对过）

`results_traffic_e1/round_v1/TE1_VERDICT.json`：

- 种子 30006–30020，`n` 15，`verdict` `NO-GO-H`。
- `mean_H` −0.014921178351331239，`sd_H` 0.07459317883372397。
- bootstrap 10000 次，`rng` 20261007，区间 [−0.0542302207818337, +0.0175677080705695]。
- `MDE80` 0.05802695298194278。
- `screen_mean_H_for_reference` −0.0807。
- `kr_le3_share_confirm_fedavg` 0.15081907510478937。
- Adam：`beta1` 0.9，`beta2` 0.99，`eta_s` 0.003，`tau` 0.001，`local_steps` 2。
- `frozen_const.c_val` 0.994486828129759，`weighted_mean` 0.008777590873050613，`n` 6192。`TE1_FROZEN_CONST.json` 写明这是验证集加权标准差，不是正文的测试集常数 1.007。

正文局限段把相对数印成 −1.49%、[−5.42%, +1.76%]、5.80%，并写该可检出效应分辨不了 0.5% 的门槛。同一段仍印绝对 RMSE：窗口 FedAvg 0.967、oracle-margin 0.973，范围 [0.659, 1.572] 与 [0.795, 1.459]。先前按字面搜索 0.967 / 0.973 无匹配，是因为这两个数是均值的三位四舍五入，文件里没有预存这个字符串。2026-10-11 从 `results_traffic_e1/round_v1/tables/TE1_CONFIRM.csv` 的 `test_RMSE_mu_fedavg_window` 与 `test_RMSE_mu_raven_simoracle` 重算：种子 30006–30020，均值 0.9671307414990941 与 0.9730551331123445，四位是 0.9671 / 0.9731。极小极大是 0.6593202441884811、1.5715634690992348 与 0.7951529670181027、1.459448903957183，三位即印出的区间。这 15 对与对应 `final_metrics.json` 的 `RMSE_mu` 逐格相等：`runs/C1_fedavg/traffic/fedavg_window/seed*` 与 `runs/C1_simoracle/traffic/raven_simoracle/seed*`。oracle-margin 臂是 `raven_simoracle`。相对测试拟合常数 1.0066933864830503，两臂均值低 3.930% 与 3.341%。15 个种子里 FedAvg 有 5 个、oracle 有 6 个高于该常数；“低于常数”只对两臂均值成立，区间本身已经跨过 1.007。

协议正文的 bootstrap 种子是 20261002（约 1631 行）。TE1 文件的 bootstrap rng 是 20261007。印出的区间与 TE1 文件一致。

同一局限段：原服务器步上四个冻结联邦成员的 \(\mathrm{RMSE}_{\mu}\) 在 0.002% 内一致；参数相对初值移动 0.26%–0.40%。窗口 FedAvg 比集中式参照高 2.8%–3.0%；该参照是 Adam、\(10^{-3}\)、池化训练单元上 20 个大小为 32 的 minibatch。句子写明比较的是两套更新规则和步数预算。\(\Delta_{\mathrm{group}}\) 降 0.0079 [0.0051, 0.0110]，\(\Delta_{c\text{-}s}\) 降 0.0099 [0.0067, 0.0132]，写明是预测对比之后才计的。

先前会话对 TS1 的计算（本轮未重开逐种子文件）：`Delta_group` 均值 0.007875，区间 [0.005050, 0.011032]；`Delta_c_s` 均值 0.009940，区间 [0.006725, 0.013242]。种子 30012 的 `Delta_group` −0.00265；种子 30006 的 `Delta_c_s` −0.000867。去掉种子 30007 会把 TE1 均值翻到约 +0.09%。这三条是先前会话数字，本轮未重算。

### 证明（本对话改过，并在 2026-10-11 复核仍在）

命题 4（`main.tex` 约 1364–1374）：换序条件是两个权重向量下 \(\sum_g\mu_g(\mathrm{RMSE}_{g,a}^2-\mathrm{RMSE}_{g,b}^2)\) 符号相反；方向导数仅在 \(\mathrm{RMSE}_{\mu}>0\) 时写出。附录证明改为 “squared identity”，删掉了 “after taking square roots”。

命题 3 附录：真边际 Design 比值改为 \(\zeta=\pi^{\mathrm{tar}}/\max\{\pi^{\mathrm{opp}},\pi_{\min}\}\)（Design on），与实现相同的下截断。P2 非扩张改为 “proved later in this supplement”，指向 `eq:app_reference_nonexpansive`。正文仍写该界在有无 A6a 时都成立，A6a 只把 \(\varepsilon_{\mathrm{stab},r}\) 变为 0。A6a 在已发布迹上不成立，命题以带稳定化误差的形式使用。A6b 未检验：正文如此写。

\(L_\pi\le 2\times 10^{13}\) 在 \(\pi^{\mathrm{tar}}_{\max}\le 1\)、\(\pi_{\min}=10^{-6}\)、\(p_{\min}=0.05\) 时算术成立：\(1/(\pi_{\min}^2 p_{\min})=2\times 10^{13}\)。这是包络，不是数值证书。

定理 1：在 `eq:cap_ess` 下均匀向量属于 \(\mathcal{C}_r\)；目标里的 \(\lambda/2\) 与 Hessian \(\lambda_g M^\top M+\lambda_\beta I+\lambda_v V_r\) 一致；\(\lambda_\beta>0\) 给出唯一解。这不保证有限精度求解日志等于该最优解。

债务界 (27)：因子 2 来自 \(\mathbf{1}^\top\mathbf{D}_R=0\)。\(M_r\) 的列在单纯形上（正文 \(\mathbf{c}^{g}_{k,r}\in\Delta^{|\mathcal G|-1}\)）。

定理 2：\(k_n=\lceil(n+1)(1-\alpha)\rceil\)，\(\alpha=0.05\) 时 \(n_{\min}=19\)。覆盖是条件于假设 1 的 \(\ge 1-\alpha\)。CERTIFIED 不证明该假设。

`supplemental.tex` 在 `\input{appendix}` 前把 proposition 计数器设为 4。文件头注释 “Prop. 1–3” 相对正文四个命题是过时的。附录对命题 1–4 是重述证明，不另占编号。

公式编号曾对 `main.aux`：`eq:opp_event_law`=1，`eq:debt_bound`=27，`eq:design_factor`=32，`eq:hajek_phi`=35，`eq:g4_beta`=38。aux 是否在后来的正文编辑后仍一致：不确定，本轮未重编译。

### Holm 与主表（先前会话核对，本轮未重算）

- 消融 40 格与星号对上 `TO_OVERLEAF_paper_tmc_r1_clean/figure_data/FIG_E4_E4_COMPONENT_ABLATION.csv`。不要用 `artifacts/e4_ablation_semantic_integrity_repair_r1/E4_ABLATION_PAIRED_TESTS_R2.csv`：那是旧族，SensorScope Obs 被标成显著，当前族不是。
- 主表 U-Air 的 θ 替换：FedAvg RMSE 1.1119±0.0603 来自 `results_active_set_repair/round_v1/E2_UAIR_SUMMARY.csv`，不是 `RAVEN_MCS_PUBLIC_REPRO_R1/tables/TABLE_II_MAIN_EFFECTIVENESS.csv` 里的 θ 之前的 1.18824。TwoStage RMSE 1.2202±0.0672、RAVEN-Design RMSE 1.1954±0.0635 是 `results_seed_path_audit_r1/C3_CELL_DIFF.csv` 记录的替换。其余列仍在 TABLE_II。
- 未绑上逐种子文件的一格：SensorScope RAVEN-NoDesign WorstGroupRMSE 8.6711±0.0481。
- `artifacts/e3_formal_runs_r1/E3_FORMAL_HOLM_RESULTS.csv`：U-Air raven vs twostage 在 θ 之前的物理 RMSE 上显著（`p_raw` 1.907e-6）。该配对 p 没有在 θ 序列上重算。正文 “no Holm-significant RMSE win” 的局部范围是 NoDesign 对无 Design 基线，不是“没有任何检验显著”。

### O / U 与服务器步（先前会话读代码，本轮未重读 `src/`）

- U 不是 Evidence 轴上的 \(\mathrm{RMSE}_{\mu}\) 预测。正式路径是 `src/raven_mcs/e3/real_runner/stage2_r3.py` 的 `compute_usable_r3`。`q_use_true` 是 `estimate_q_true_mc`，在冻结 prestate 下对该模拟器做蒙特卡洛，不是对 Y 的回归。
- 设备层概率 0.3/0.5/0.2；`p_compute` 0.70/0.90/0.98；`p_network` 0.80/0.95/0.99。UTC 块 2 和 3 把 `p_cs` 乘 0.75、`p_ns` 乘 0.80。
- 实测 U：没有任何块。实测 O：只有 City Scanner Pilot 2。R 在 T-Drive 和 City Scanner 两块上是真实的。SS、U-Air、NSW-Traffic 的 R/O/U 是构造控制。
- 旧 Bernoulli 路径 `complete_aligned.py` 的 `mean_usable_rate` 0.60 不是正式 e3 路径。
- 服务器：客户端 \(u_i=\Delta_i/(\gamma E_{\mathrm{loc}})\)，服务器 \(\theta\leftarrow\theta-\eta\sum\alpha_i u_i\)，\(\eta=0.01\)，每窗口一次。等价服务器学习率 \(1/E_{\mathrm{loc}}\)。\(K_r\le 3\) 把权重钉在均匀（\(E_{\min}=3\)）。SensorScope 1877 个活跃窗口中 78.6% 如此。U-Air Design-on 1402 中 90.2%；Design-off 1515 中 79.0%。

### 筛选文件里的目标浓度与余量

`results_text_repairs/round_v1/BLOCK_SCREEN.json`：

- `traffic|4 UTC blocks`：`top1_share` 0.25，`effective_groups` 4.0，`n_groups` 4。四段目标是均匀的。`traffic|full`：172 组，接近均匀（`top1_share` 0.005813953488372094）。
- `tdrive_speed|4 UTC blocks`：`top1_share` 0.514396062707023，`effective_groups` 3.2911741495390023。
- slack 来自各种子 30001 的 `window_metrics.json`，不是十五种子总体：Traffic `share_kr_gt3` 0.8888888888888888，`median_kr` 12，`max_kr` 26，`n_active` 99。SensorScope 0.24742268041237114。U-Air 0.19696969696969702。
- 十五种子确认集的 \(K_r\le 3\) 份额是 TE1 的 0.150819，对应 \(K_r>3\) 约 0.849，不是 0.889。

### 审稿分数（2026-10-10，绝对就绪）

4/10，lean reject。权重：Originality 0.10，Significance 0.15，Soundness 0.20，Evidence 0.25，Clarity 0.15，Reproducibility 0.10，Related work 0.05。分数：3，2，4，3，3，3，3。加权均分 3.05/5 不是立场。决定轴是 Evidence 3 与 Significance 2。相对 2026-10-09 的加权进展是 0。

Significance 2 的原因：部署目标 RMSE 没有可检出的 oracle-margin 余量；SensorScope 结构余量是 0.768 个百分点；Adam 上的失配下降是预测对比之后才计的。抬到 3 的条件是读者被要求接受的贡献就是结构投影加上这个写明的预测零结果。不是再训一个模型。

Evidence 3 在 2026-10-10 的扣分是常数身份和 0.967/0.973 无文件。常数身份已被后来的正文区分（见上）。0.967/0.973 的逐种子来源已在 2026-10-11 对上 `TE1_CONFIRM.csv` 与 30 个 `final_metrics.json`（见上）。审稿文件 `raven-mcs-tmc-review.md` 仍写“无文件”，分数没改。审稿表自己的升级条件是两件事都做完且相对结构主张不动；文件对上了，但正文局限句仍没有点名 `TE1_CONFIRM.csv`。是否把 Evidence 从 3 改到 4：本轮没有改审稿分数。

## 假设

- 训练均值常数 7.647 / 1.054 / 1.007 是 `TWO_CONSTANTS.json` 的 `deployable_constant_rmse`，测试拟合常数是 `oracle_constant_rmse`。印刷值与该文件一致。该文件的 `note` 字段没有写明 oracle 常数的构造句子；“用测试标签拟合”是当前正文的措辞，与先前会话把 2.088 当成测试标签常数的判断一致。文件内部没有单独一句定义 oracle 的公式：不确定 json 生成脚本是否还在。
- U-Air `frozen_fedavg_rmse` 1.2108 属于 θ 重计分之前或另一条评分路径。它与主表 1.1119 不是同一格。不要用它去改主表。
- 命题 3 在补上下截断之后，\(L_\pi\) 对两侧都使用 \(\max\{\pi,\pi_{\min}\}\) 的映射成立，因此“不假设 A6a”可以保留。本轮没有重编译，也没有用数值例子再攻击修改后的证明。
- 集中目标实验若得到正结果，只说明合成 \(\kappa\) 目标上投影可以移动 \(\mathrm{RMSE}_{\mu}\)。它不自动把 Significance 从 2 抬到 3，因为 NSW 四段目标是均匀的，而 T-Drive 四段目标已经 top-1 51.4% 且正文仍把 FedAU-Window / ObsUse-Window 排在前面。

## 未决问题

- 0.967 / 0.973 与区间已对上 `TE1_CONFIRM.csv` 及 30 个 `final_metrics.json`（见上）。“两臂低于常数”只对均值成立：FedAvg 5/15、oracle 6/15 个种子高于测试拟合常数。不要把逐种子都低于常数写成已核对。
- SensorScope RAVEN-NoDesign WorstGroupRMSE 8.6711±0.0481 的逐种子文件。
- U-Air Design-on 对 TwoStage 的 RMSE 配对检验在 θ 序列上是否仍显著。θ 之前的文件是显著的；θ 之后未重算。
- \(\kappa=1\) 的四个 Traffic 区域质量都是 0.25，优先区域规则没有唯一最大值。`TE2_FROZEN_PREREG.json`：不确定是否已写。实验设计文档要求先冻结再跑；平局打破规则在该文档里没有写死。
- 设计文档表内有效组数 3.2、2.5、2.1 与 \(1/\sum p^2\) 不一致。按该定义 \(\kappa=2,5,10\) 约为 3.57、2.29、1.64。份额 40%、62.5%、76.9% 是对的。
- Phase 0 重算现有检查点得到的 sd，不是新目标下重训对比的 sd。用它当停止规则可以挡住过噪的重算；用很小的重算 sd 当作重训有功效，不成立。
- Deville and Särndal 是否写入正文：用户尚未授权。
- `main.tex` 当前 sha256：不确定。2026-10-09 审稿时的 sha256 是 `6FC9BE0B8689B6C8849B2A07F55A84E25B2D8360BBFFCFB54F11A0C93C1C2B95`，此后文件改过，该哈希不能再当当前身份。
- 页数、模板、匿名性、bib 元数据：2026-10-10 审稿未重审。
- git 工作区是否仍只推送了 `43bb8eb`：不确定。

## 关键决策、原因、失败尝试

1. 预测余量路线关闭。TE1 判决 `NO-GO-H`。最小可检出效应 5.80%，大于观察到的 1.49%，也大于 0.5% 的门槛。加种子去打 0.5% 被明确拒绝。筛选均值 −8.07% 是种子 30005，不在确认集 30006–30020 里。
2. 常数句曾经只有测试拟合常数，读者会把 2.088 当成可部署常数，从而把表内约 7.94 读成远差于常数。对着训练均值常数 7.647，冻结 FedAvg 7.914 只高约 3.49%（`frozen_vs_deployable_pct` 3.494732446858295）。用户一度未授权写入这句；后来正文被改成两个常数并列。本对话中的助手没有写 1606–1613 和 1885–1888 的现句，也没有写可用性段的 `results_traffic_e1` 指向。那些句子在 2026-10-11 读取时已经在文件里。谁写入：不确定。不要把它们改回“一个未加定义的常数预测器”。
3. 证明完整性审计（claim-audit，未改科学结论）发现两处真实缺口，并已改文字：命题 4 的 “changes sign” 超出证明；命题 3 的 \(L_\pi\) 写在未下截断的 \(\pi^{\mathrm{opp}}\) 上，而假设不含 A6a。修复是改证明里的 \(\zeta\) 定义和命题 4 的逻辑句，不是收窄“不依赖 A6a”。
4. Holm 旧文件会把 SensorScope Obs 标成显著。原因是当前族里 gen-2 Inst 的原始 p 排在前面，Holm 的累计最大值把 0.05154 带到 Obs 上。使用 `FIG_E4` 与 `E4_FINAL_STATISTICS_R2` 的原始 p，不要用那份旧配对表。U-Air 预测百分数在 θ 之后变了，Wilcoxon 原始 p 不变，所以星号不变。
5. 集中目标方案 `ccfa-review-reports/raven-mcs-traffic-concentrated-target-experiment-design.md` 作为机制检验可以保留，作为 Significance 修复不成立。原因：它把均匀的 NSW 四段目标换成 \(\kappa=5\)（一个区域 62.5%），并保留已经不能移动 \(\theta\) 的服务器步。T-Drive 已经有 51.4% 的 top-1，且不是 RAVEN 的 RMSE 胜利。Phase 0 的方差是重算方差。88.9% 余量是单种子。优先区域在 \(\kappa=1\) 上四向平局。
6. 相关工作不要声称“投影操作是新的”。要补的是 Deville–Särndal。不要把未跑过的方法加进 RMSE 表。
7. 2026-10-11 补上 0.967 / 0.973 的来源：`TE1_CONFIRM.csv` 测试列的 15 种子均值，逐种子等于 `final_metrics.json` 的 `RMSE_mu`。先前字面搜索落空是因为文件没有存四舍五入后的字符串。没有改正文，也没有改审稿分数。
8. 2026-10-11 把 Significance 读法和正文负面表述登记在 `ccfa-review-reports/raven-mcs-defensive-prose-diagnosis-20261011.md`。用户拒绝再写一条预测零结果。该记录不授权删句或改分。

## 下一轮不要做的事

- 不要为了 Significance 启动 TE2 的 80+320+240 次训练。
- 不要把 0.967 / 0.973 改绑到别的文件。来源是 `TE1_CONFIRM.csv` 的测试列均值，不是 `TE1_VERDICT.json`。
- 不要用 `TWO_CONSTANTS.json` 的 U-Air `frozen_fedavg_rmse` 1.2108 替换主表 1.1119。
- 不要用 `E4_ABLATION_PAIRED_TESTS_R2.csv` 或 θ 之前的 TABLE_II 去否定当前主表。
- 不要重写证明或正文，除非用户点名要改。Deville 引用、Holm 句子的局部范围，都还没有新的写作授权。2026-10-10 审稿把常数句和可用性路径列成未决写作项；这两处当前文件已经有句子，先读再决定要不要改。
- 不要把“预测零结果”追加进摘要或引言。负面表述的清单在 `raven-mcs-defensive-prose-diagnosis-20261011.md`，未授权删改。
