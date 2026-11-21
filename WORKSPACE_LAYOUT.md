# 工作区分区索引（workspace layout）

生成时间：2026-11-08 21:03　·　顶层条目 **156** 个　·　**项目文件 152,047 个 / 36.6 GB**

**口径说明。** 本索引统计的是项目文件，**不含** `.git`（≈6.8 GB / 7.3 万文件）、`.venv_new`（≈5.1 GB / 6.6 万文件）与 `__pycache__`（≈0.02 GB）。全盘实测合计 **294,642 个文件 / 49.41 GB**；上表 36.6 GB 与全盘 49.41 GB 的差额即这三项（分项由不同工具枚举，存在约 1 GB 的舍入口径差）。

用途：49 GB / 29 万文件的工作区靠肉眼无法导航。这份索引把每个顶层条目归到九类之一，并标注**能否移动**。

> **重要结论：不要用「移动目录」来整理。** 逐个名字做过引用检查，几乎所有目录都被别处引用（`tmp` 578 次、`outputs` 2 607 次、`evidence` 4 090 次、`deliverables` 1 972 次；`results_traffic_e2` / `results_w1_ladder` 被 `ccf-review-report/PAPER_CLAIM_EVIDENCE_MAP.md` 引用；`_handoff_sag_*` / `paper_ready_*` 被 `scripts/*.py` 引用）。移动任一目录都会打断论文证据链、脚本路径或报告索引。

| 类别 | 条目数 | 文件数 | 体积 |
|---|---:|---:|---:|
| 1 论文与投稿 | 18 | 31,765 | 3.63 GB |
| 2 代码与配置 | 21 | 1,804 | 0.01 GB |
| 3 数据 | 1 | 192 | 3.38 GB |
| 4 冻结证据与运行产物 | 6 | 63,365 | 4.37 GB |
| 5 实验轮次 | 67 | 45,183 | 23.35 GB |
| 6 评审与报告 | 14 | 339 | 0.03 GB |
| 7 文献检索 | 6 | 18 | 0.00 GB |
| 8 临时与代理工作区 | 21 | 7,702 | 1.11 GB |
| 9 系统与技能 | 2 | 1,679 | 0.69 GB |
| **合计** | **156** | **152,047** | **36.6 GB** |

## 1 论文与投稿

| 条目 | 文件 | 体积 | 最后修改 | 内容 / 用途 | 可移动性 |
|---|---:|---:|---|---|---|
| `deliverables` | 13,696 | 1657 MB | 2026-08-31 | 论文相关的封存/打包/参考材料 | 需批准 |
| `_paper_work` | 133 | 629 MB | 2026-08-30 | 论文相关的封存/打包/参考材料 | 需批准 |
| `RAVEN_MCS_FINAL_PAPER_DATA_ASSET_FREEZE_R1` | 5,029 | 531 MB | 2026-08-30 | 论文相关的封存/打包/参考材料 | 需批准 |
| `paper_ready_r2` | 4,806 | 249 MB | 2026-08-30 | 论文相关的封存/打包/参考材料 | 需批准 |
| `paper_ready_r1` | 4,756 | 241 MB | 2026-08-30 | 论文相关的封存/打包/参考材料 | 需批准 |
| `RAVEN_MCS_PUBLIC_REPRO_R1` | 2,134 | 180 MB | 2026-10-17 | 论文 Availability 引用的公开复现包（含 submission_evidence 索引） | 不可移动 |
| `post_review` | 523 | 51 MB | 2026-09-11 | 论文相关的封存/打包/参考材料 | 需批准 |
| `TO_OVERLEAF_paper_tmc_r1_clean` | 341 | 44 MB | 2026-11-04 | **规范论文目录**（main.tex / appendix.tex / supplemental.tex / 图 / bib） | 不可移动 |
| `参考文件` | 27 | 34 MB | 2026-11-08 | 论文相关的封存/打包/参考材料 | 需批准 |
| `RAVEN_MCS_SAG_G0_G1_EVIDENCE_SUBMISSION_R1` | 28 | 6 MB | 2026-08-30 | 论文相关的封存/打包/参考材料 | 需批准 |
| `ADVISOR_PACKAGE_TMC_R1` | 17 | 2 MB | 2026-09-14 | 论文相关的封存/打包/参考材料 | 需批准 |
| `paper_tmc_r1` | 18 | 2 MB | 2026-08-30 | 论文相关的封存/打包/参考材料 | 需批准 |
| `manuscript_evidence_closure_r1` | 60 | 1 MB | 2026-08-30 | 论文相关的封存/打包/参考材料 | 需批准 |
| `archive` | 10 | 1 MB | 2026-08-30 | 论文相关的封存/打包/参考材料 | 需批准 |
| `RAVEN_MCS_TMC_r1_overleaf` | 15 | 1 MB | 2026-09-05 | 论文相关的封存/打包/参考材料 | 需批准 |
| `RAVEN_MCS_FINAL_FIGURE_TABLE_PAPER_SPECIFICATION_SEAL_R1` | 90 | 0 MB | 2026-08-30 | 论文相关的封存/打包/参考材料 | 需批准 |
| `docs` | 47 | 0 MB | 2026-08-30 | 论文相关的封存/打包/参考材料 | 需批准 |
| `RAVEN_MCS_FINAL_TABLE_II_REPAIR_R1` | 35 | 0 MB | 2026-08-30 | 论文相关的封存/打包/参考材料 | 需批准 |

## 2 代码与配置

| 条目 | 文件 | 体积 | 最后修改 | 内容 / 用途 | 可移动性 |
|---|---:|---:|---|---|---|
| `scripts` | 623 | 5 MB | 2026-10-15 | 代码/配置/测试 | 不可移动 |
| `src` | 482 | 4 MB | 2026-10-13 | 代码/配置/测试 | 不可移动 |
| `configs` | 207 | 2 MB | 2026-10-12 | 代码/配置/测试 | 不可移动 |
| `tests` | 473 | 1 MB | 2026-10-12 | 代码/配置/测试 | 不可移动 |
| `tools` | 3 | 0 MB | 2026-09-20 | 代码/配置/测试 | 不可移动 |
| `.gitignore` | 1 | 0 MB | 2026-10-11 | 代码/配置/测试 | 不可移动 |
| `schemas` | 1 | 0 MB | 2026-08-30 | 代码/配置/测试 | 不可移动 |
| `pyproject.toml` | 1 | 0 MB | 2026-07-31 | 代码/配置/测试 | 不可移动 |
| `check_raven_final_figure_table_paper_specification_seal_r1.py` | 1 | 0 MB | 2026-08-28 | 代码/配置/测试 | 不可移动 |
| `check_raven_tableii_unit_scale_repair_r1.py` | 1 | 0 MB | 2026-08-28 | 代码/配置/测试 | 不可移动 |
| `check_raven_final_paper_data_asset_freeze_r1.py` | 1 | 0 MB | 2026-08-28 | 代码/配置/测试 | 不可移动 |
| `check_tdrive_real_mobility_protocol_seal_r1.py` | 1 | 0 MB | 2026-08-28 | 代码/配置/测试 | 不可移动 |
| `check_paper_data_metadata_and_claim_repair_r2.py` | 1 | 0 MB | 2026-08-28 | 代码/配置/测试 | 不可移动 |
| `check_raven_manuscript_evidence_closure_r1.py` | 1 | 0 MB | 2026-08-28 | 代码/配置/测试 | 不可移动 |
| `requirements-lock.txt` | 1 | 0 MB | 2026-07-31 | 代码/配置/测试 | 不可移动 |
| `Makefile` | 1 | 0 MB | 2026-07-31 | 代码/配置/测试 | 不可移动 |
| `.gitattributes` | 1 | 0 MB | 2026-08-03 | 代码/配置/测试 | 不可移动 |
| `environment.yml` | 1 | 0 MB | 2026-07-31 | 代码/配置/测试 | 不可移动 |
| `requirements.txt` | 1 | 0 MB | 2026-07-31 | 代码/配置/测试 | 不可移动 |
| `.vscode` | 1 | 0 MB | 2026-09-08 | 代码/配置/测试 | 不可移动 |
| `notebooks` | 1 | 0 MB | 2026-08-30 | 代码/配置/测试 | 不可移动 |

## 3 数据

| 条目 | 文件 | 体积 | 最后修改 | 内容 / 用途 | 可移动性 |
|---|---:|---:|---|---|---|
| `data` | 192 | 3379 MB | 2026-08-30 | 原始与处理后的数据（IoT 数据集） | 不可移动 |

## 4 冻结证据与运行产物

| 条目 | 文件 | 体积 | 最后修改 | 内容 / 用途 | 可移动性 |
|---|---:|---:|---|---|---|
| `artifacts` | 38,096 | 2717 MB | 2026-09-23 | 冻结证据 / 运行日志 / 快照（被报告与台账引用） | 不可移动 |
| `outputs` | 22,547 | 1434 MB | 2026-08-30 | 冻结证据 / 运行日志 / 快照（被报告与台账引用） | 不可移动 |
| `tdrive_protocol_seal_r1` | 89 | 176 MB | 2026-08-30 | 冻结证据 / 运行日志 / 快照（被报告与台账引用） | 不可移动 |
| `logs` | 2,459 | 32 MB | 2026-10-12 | 冻结证据 / 运行日志 / 快照（被报告与台账引用） | 不可移动 |
| `snapshots` | 56 | 4 MB | 2026-10-09 | 冻结证据 / 运行日志 / 快照（被报告与台账引用） | 不可移动 |
| `evidence` | 118 | 4 MB | 2026-08-30 | 冻结证据 / 运行日志 / 快照（被报告与台账引用） | 不可移动 |

## 5 实验轮次

| 条目 | 文件 | 体积 | 最后修改 | 内容 / 用途 | 可移动性 |
|---|---:|---:|---|---|---|
| `results_observed_feedback_autonomous_pilot_45001_recovery_20261015` | 521 | 7820 MB | 2026-10-15 | 单轮实验或诊断输出 | 不可移动 |
| `results_observed_feedback_autonomous_pilot_45001_20261014` | 740 | 4145 MB | 2026-10-14 | 单轮实验或诊断输出 | 不可移动 |
| `results_zero_safe_buffer` | 3,250 | 2938 MB | 2026-10-19 | 单轮实验或诊断输出 | 不可移动 |
| `results_of_v1_small_scope_20261018_190539` | 179 | 2607 MB | 2026-10-18 | 单轮实验或诊断输出 | 不可移动 |
| `results_observed_feedback_rolling_45011_20261014_s2` | 126 | 2556 MB | 2026-10-14 | 单轮实验或诊断输出 | 不可移动 |
| `results_calibration_first_20261013` | 92 | 1001 MB | 2026-10-13 | 单轮实验或诊断输出 | 不可移动 |
| `results_gate_dose` | 4,691 | 491 MB | 2026-10-07 | 单轮实验或诊断输出 | 不可移动 |
| `results_re_interval_development_44001_20261013` | 1,074 | 416 MB | 2026-10-13 | 单轮实验或诊断输出 | 不可移动 |
| `results_action_difference_revision_20261013` | 60 | 220 MB | 2026-10-13 | 单轮实验或诊断输出 | 不可移动 |
| `results_main_rebuild_r1` | 1,391 | 191 MB | 2026-10-12 | 单轮实验或诊断输出 | 不可移动 |
| `results_h_headroom` | 12,216 | 169 MB | 2026-10-06 | 单轮实验或诊断输出 | 不可移动 |
| `results_int_r` | 4,579 | 139 MB | 2026-09-05 | 单轮实验或诊断输出 | 不可移动 |
| `results_tdrive_rank` | 268 | 86 MB | 2026-09-21 | 单轮实验或诊断输出 | 不可移动 |
| `results_server_optimizer` | 1,730 | 74 MB | 2026-10-08 | 单轮实验或诊断输出 | 不可移动 |
| `results_traffic_e2` | 3,257 | 69 MB | 2026-10-10 | 单轮实验或诊断输出 | 不可移动 |
| `results_cityscanner_lowcost_screen` | 362 | 60 MB | 2026-10-18 | 单轮实验或诊断输出 | 不可移动 |
| `results_sag_g1` | 725 | 48 MB | 2026-08-31 | 单轮实验或诊断输出 | 不可移动 |
| `results_observed_feedback_continuation_45011_20261014` | 64 | 46 MB | 2026-10-14 | 单轮实验或诊断输出 | 不可移动 |
| `results_w1_ladder` | 2,368 | 38 MB | 2026-10-03 | 单轮实验或诊断输出 | 不可移动 |
| `results_active_set_repair` | 1,763 | 29 MB | 2026-09-27 | 单轮实验或诊断输出 | 不可移动 |
| `results_revision_feasibility_20261013_125348` | 70 | 26 MB | 2026-10-13 | 单轮实验或诊断输出 | 不可移动 |
| `results_h_response_shift` | 1,523 | 21 MB | 2026-10-05 | 单轮实验或诊断输出 | 不可移动 |
| `results_observed_feedback_acquisition_45011_20261014` | 58 | 20 MB | 2026-10-14 | 单轮实验或诊断输出 | 不可移动 |
| `results_targeted_reference_calibration` | 62 | 14 MB | 2026-10-25 | 单轮实验或诊断输出 | 不可移动 |
| `results_traffic_e1` | 653 | 14 MB | 2026-10-09 | 单轮实验或诊断输出 | 不可移动 |
| `results_observed_feedback_implementation_20261013` | 59 | 13 MB | 2026-10-13 | 单轮实验或诊断输出 | 不可移动 |
| `results_active_participation` | 60 | 13 MB | 2026-10-20 | 单轮实验或诊断输出 | 不可移动 |
| `results_conditional_reference_projection` | 97 | 13 MB | 2026-10-19 | 单轮实验或诊断输出 | 不可移动 |
| `results_conditional_bundle_b0_20261012_223821` | 235 | 11 MB | 2026-10-12 | 单轮实验或诊断输出 | 不可移动 |
| `results_design_gate_alignment_v1` | 1,608 | 11 MB | 2026-10-12 | 单轮实验或诊断输出 | 不可移动 |
| `results_c1_cityscanner` | 114 | 9 MB | 2026-09-11 | 单轮实验或诊断输出 | 不可移动 |
| `results_path_a_hajek` | 112 | 9 MB | 2026-09-11 | 单轮实验或诊断输出 | 不可移动 |
| `results_joint_ou` | 113 | 8 MB | 2026-09-11 | 单轮实验或诊断输出 | 不可移动 |
| `results_p2_new_target` | 111 | 6 MB | 2026-09-10 | 单轮实验或诊断输出 | 不可移动 |
| `results_exogenous_target` | 30 | 4 MB | 2026-10-02 | 单轮实验或诊断输出 | 不可移动 |
| `results_new_block_traffic` | 175 | 4 MB | 2026-10-07 | 单轮实验或诊断输出 | 不可移动 |
| `results_observed_feedback_persistent_cost_20261014` | 24 | 2 MB | 2026-10-14 | 单轮实验或诊断输出 | 不可移动 |
| `results_support_consumption_audit` | 20 | 2 MB | 2026-10-19 | 单轮实验或诊断输出 | 不可移动 |
| `results_observed_feedback_readiness_20261014` | 24 | 2 MB | 2026-10-14 | 单轮实验或诊断输出 | 不可移动 |
| `results_seed_path_audit_r1` | 45 | 2 MB | 2026-10-02 | 单轮实验或诊断输出 | 不可移动 |
| `results_support_consumption` | 32 | 1 MB | 2026-10-19 | 单轮实验或诊断输出 | 不可移动 |
| `results_c1_kill` | 18 | 1 MB | 2026-09-10 | 单轮实验或诊断输出 | 不可移动 |
| `results_regime_b_endpoints` | 52 | 1 MB | 2026-10-06 | 单轮实验或诊断输出 | 不可移动 |
| `results_prop3_audit` | 7 | 1 MB | 2026-09-28 | 单轮实验或诊断输出 | 不可移动 |
| `results_m1_attribution` | 14 | 1 MB | 2026-10-18 | 单轮实验或诊断输出 | 不可移动 |
| `results_observed_feedback_rolling_45011_20261014_s1` | 17 | 1 MB | 2026-10-14 | 单轮实验或诊断输出 | 不可移动 |
| `results_gatekeeping` | 183 | 0 MB | 2026-10-03 | 单轮实验或诊断输出 | 不可移动 |
| `results_cityscanner_full_vs_projection_20261018` | 7 | 0 MB | 2026-10-18 | 单轮实验或诊断输出 | 不可移动 |
| `results_calibration_diagnostic_20261013_122013` | 48 | 0 MB | 2026-10-13 | 单轮实验或诊断输出 | 不可移动 |
| `results_xw_pool` | 7 | 0 MB | 2026-10-18 | 单轮实验或诊断输出 | 不可移动 |
| `results_observed_feedback_preparation_20261013` | 19 | 0 MB | 2026-10-13 | 单轮实验或诊断输出 | 不可移动 |
| `results_estimand_selection` | 13 | 0 MB | 2026-10-07 | 单轮实验或诊断输出 | 不可移动 |
| `results_reachability_detector_v1` | 15 | 0 MB | 2026-10-12 | 单轮实验或诊断输出 | 不可移动 |
| `results_endpoint_screen` | 6 | 0 MB | 2026-10-05 | 单轮实验或诊断输出 | 不可移动 |
| `results_group_identity` | 9 | 0 MB | 2026-10-02 | 单轮实验或诊断输出 | 不可移动 |
| `results_aggregate_total` | 7 | 0 MB | 2026-10-05 | 单轮实验或诊断输出 | 不可移动 |
| `results_nodesign_supplement` | 31 | 0 MB | 2026-09-24 | 单轮实验或诊断输出 | 不可移动 |
| `results_evidence_axis` | 3 | 0 MB | 2026-10-07 | 单轮实验或诊断输出 | 不可移动 |
| `results_paper_ceiling` | 6 | 0 MB | 2026-10-11 | 单轮实验或诊断输出 | 不可移动 |
| `results_oracle_root_cause` | 6 | 0 MB | 2026-10-06 | 单轮实验或诊断输出 | 不可移动 |
| `results_reachability_method_prep_20261012_220855` | 7 | 0 MB | 2026-10-12 | 单轮实验或诊断输出 | 不可移动 |
| `results_ceiling_class_r1` | 5 | 0 MB | 2026-09-29 | 单轮实验或诊断输出 | 不可移动 |
| `results_traffic_struct` | 5 | 0 MB | 2026-10-09 | 单轮实验或诊断输出 | 不可移动 |
| `results_reachability_v2_p0_20261012_215621` | 8 | 0 MB | 2026-10-12 | 单轮实验或诊断输出 | 不可移动 |
| `results_text_repairs` | 3 | 0 MB | 2026-10-10 | 单轮实验或诊断输出 | 不可移动 |
| `results_two_constant` | 2 | 0 MB | 2026-10-10 | 单轮实验或诊断输出 | 不可移动 |
| `results_table2_audit` | 4 | 0 MB | 2026-09-24 | 单轮实验或诊断输出 | 不可移动 |

## 6 评审与报告

| 条目 | 文件 | 体积 | 最后修改 | 内容 / 用途 | 可移动性 |
|---|---:|---:|---|---|---|
| `ccf-review-report` | 231 | 31 MB | 2026-11-06 | 评审、修复报告、项目状态与变更记录 | 不可移动 |
| `ccfa-review-reports` | 88 | 2 MB | 2026-10-18 | 评审、修复报告、项目状态与变更记录 | 不可移动 |
| `_acl_reports` | 9 | 0 MB | 2026-10-11 | 评审、修复报告、项目状态与变更记录 | 不可移动 |
| `DESIGN_GATE_ALIGNMENT_REPORT.md` | 1 | 0 MB | 2026-10-12 | 评审、修复报告、项目状态与变更记录 | 不可移动 |
| `ISSUES.md` | 1 | 0 MB | 2026-08-03 | 评审、修复报告、项目状态与变更记录 | 不可移动 |
| `STATUS.md` | 1 | 0 MB | 2026-08-03 | 评审、修复报告、项目状态与变更记录 | 不可移动 |
| `SAG_IMPLEMENTATION_PLAN.md` | 1 | 0 MB | 2026-08-29 | 历史修复计划文档 | 需批准 |
| `CHANGELOG.md` | 1 | 0 MB | 2026-08-03 | 评审、修复报告、项目状态与变更记录 | 不可移动 |
| `REVIEW_ccf_raven_tmc_r1_c1hybrid.md` | 1 | 0 MB | 2026-09-10 | 评审、修复报告、项目状态与变更记录 | 不可移动 |
| `SAG_G1_R1_REPAIR_PLAN.md` | 1 | 0 MB | 2026-08-30 | 历史修复计划文档 | 需批准 |
| `SAG_G1_R1B_SEMANTIC_REPAIR_PLAN.md` | 1 | 0 MB | 2026-08-30 | 历史修复计划文档 | 需批准 |
| `README.md` | 1 | 0 MB | 2026-07-31 | 评审、修复报告、项目状态与变更记录 | 不可移动 |
| `SAG_G1_R1C_REPAIR_PLAN.md` | 1 | 0 MB | 2026-08-30 | 历史修复计划文档 | 需批准 |
| `SAG_G1_R1D_PLAN.md` | 1 | 0 MB | 2026-08-30 | 历史修复计划文档 | 需批准 |

## 7 文献检索

| 条目 | 文件 | 体积 | 最后修改 | 内容 / 用途 | 可移动性 |
|---|---:|---:|---|---|---|
| `literature-search-20260919-raven-mcs-citation-verify` | 3 | 0 MB | 2026-09-19 | 文献检索产物（ccf-literature-searcher 输出） | 需批准 |
| `literature-search-20260922-exogenous-mobile-datasets` | 3 | 0 MB | 2026-09-22 | 文献检索产物（ccf-literature-searcher 输出） | 需批准 |
| `literature-search-20261009-concentrated-target` | 3 | 0 MB | 2026-10-10 | 文献检索产物（ccf-literature-searcher 输出） | 需批准 |
| `literature-search-20260911-cityscanner-no2-bounds` | 3 | 0 MB | 2026-09-11 | 文献检索产物（ccf-literature-searcher 输出） | 需批准 |
| `literature-search-20261010-selection-corrected-aggregation` | 3 | 0 MB | 2026-10-10 | 文献检索产物（ccf-literature-searcher 输出） | 需批准 |
| `literature-search-20260910-mcs-mobile-field-datasets` | 3 | 0 MB | 2026-09-10 | 文献检索产物（ccf-literature-searcher 输出） | 需批准 |

## 8 临时与代理工作区

| 条目 | 文件 | 体积 | 最后修改 | 内容 / 用途 | 可移动性 |
|---|---:|---:|---|---|---|
| `tmp` | 6,557 | 744 MB | 2026-11-06 | 临时脚本 / 代理工作目录 / 备份（README 类报告引用其路径） | 需批准 |
| `.upstream_backup` | 30 | 292 MB | 2026-10-11 | 临时脚本 / 代理工作目录 / 备份（README 类报告引用其路径） | 需批准 |
| `_r13_build` | 356 | 32 MB | 2026-11-08 | 临时脚本 / 代理工作目录 / 备份（README 类报告引用其路径） | 需批准 |
| `.rb_work` | 385 | 31 MB | 2026-10-07 | 临时脚本 / 代理工作目录 / 备份（README 类报告引用其路径） | 需批准 |
| `_tmp_pack` | 70 | 8 MB | 2026-09-20 | 临时脚本 / 代理工作目录 / 备份（README 类报告引用其路径） | 需批准 |
| `_tmp_ref` | 180 | 3 MB | 2026-09-27 | 临时脚本 / 代理工作目录 / 备份（README 类报告引用其路径） | 需批准 |
| `.m7_work` | 58 | 1 MB | 2026-10-18 | 临时脚本 / 代理工作目录 / 备份（README 类报告引用其路径） | 需批准 |
| `.r11_work` | 11 | 1 MB | 2026-10-05 | 临时脚本 / 代理工作目录 / 备份（README 类报告引用其路径） | 需批准 |
| `.sync_diag` | 20 | 1 MB | 2026-10-04 | 临时脚本 / 代理工作目录 / 备份（README 类报告引用其路径） | 需批准 |
| `_handoff_sag_v1.1` | 4 | 0 MB | 2026-08-30 | 临时脚本 / 代理工作目录 / 备份（README 类报告引用其路径） | 需批准 |
| `.pytest_cache` | 5 | 0 MB | 2026-10-07 | 临时脚本 / 代理工作目录 / 备份（README 类报告引用其路径） | 需批准 |
| `.r3_work` | 13 | 0 MB | 2026-10-06 | 临时脚本 / 代理工作目录 / 备份（README 类报告引用其路径） | 需批准 |
| `.s1_work` | 3 | 0 MB | 2026-10-06 | 临时脚本 / 代理工作目录 / 备份（README 类报告引用其路径） | 需批准 |
| `_handoff_sag_g1_r1e` | 2 | 0 MB | 2026-08-30 | 临时脚本 / 代理工作目录 / 备份（README 类报告引用其路径） | 需批准 |
| `_handoff_sag_g1_r1d` | 1 | 0 MB | 2026-08-30 | 临时脚本 / 代理工作目录 / 备份（README 类报告引用其路径） | 需批准 |
| `_handoff_sag_g1_r1` | 1 | 0 MB | 2026-08-30 | 临时脚本 / 代理工作目录 / 备份（README 类报告引用其路径） | 需批准 |
| `_handoff_sag_g1_r1c` | 1 | 0 MB | 2026-08-30 | 临时脚本 / 代理工作目录 / 备份（README 类报告引用其路径） | 需批准 |
| `_handoff_sag_g1_r1b` | 1 | 0 MB | 2026-08-30 | 临时脚本 / 代理工作目录 / 备份（README 类报告引用其路径） | 需批准 |
| `.codex-remote-attachments` | 1 | 0 MB | 2026-10-14 | 临时脚本 / 代理工作目录 / 备份（README 类报告引用其路径） | 需批准 |
| `baseline-references-to-download.md` | 1 | 0 MB | 2026-09-19 | 未归类 | 需批准 |
| `_probe_new` | 2 | 0 MB | 2026-10-07 | 临时脚本 / 代理工作目录 / 备份（README 类报告引用其路径） | 需批准 |

## 9 系统与技能

| 条目 | 文件 | 体积 | 最后修改 | 内容 / 用途 | 可移动性 |
|---|---:|---:|---|---|---|
| `CCFA-Skills` | 1,333 | 387 MB | 2026-10-11 | DSH 运行时与 CCFA 技能库 | 不可移动 |
| `.dsh` | 346 | 298 MB | 2026-10-11 | DSH 运行时与 CCFA 技能库 | 不可移动 |

## 空间分析与处置建议

### 体量集中在 2026-10-13~19 的四轮观测反馈试点

| 目录 | 体积 | 日期 |
|---|---:|---|
| `results_observed_feedback_autonomous_pilot_45001_recovery_20261015` | 7.82 GB | 2026-10-15 |
| `results_observed_feedback_autonomous_pilot_45001_20261014` | 4.15 GB | 2026-10-14 |
| `data` | 3.38 GB | 2026-08-30 |
| `results_zero_safe_buffer` | 2.94 GB | 2026-10-19 |
| `artifacts` | 2.72 GB | 2026-09-23 |
| `results_of_v1_small_scope_20261018_190539` | 2.61 GB | 2026-10-18 |

最大的**六**个 2026-10-13~19 试点合计 **21.07 GB**（其中前四个 17.51 GB），占项目文件的 **58 %**、全盘 **43 %**。它们都是 `results_*`，属于实验轮次而不是已发布证据，**是否长期保留由你决定**（删除后无法从论文侧复原）。

### 三档处置

| 档 | 动作 | 候选 | 可回收 |
|---|---|---|---|
| A | 可直接删除（可再生） | `.pytest_cache`、`.sync_diag`、`_probe_new`、`_r13_build` 的 `build_*` 子目录 | 小（< 0.05 GB） |
| B | 打包归档到 `_archive_2026-11/`（保留但不占顶层） | 6 个 `literature-search-*`、7 个 `_handoff_sag_*`、5 个 `SAG_*_PLAN.md`、`.upstream_backup` | ≈ 0.3 GB |
| C | **需你逐项确认后**才可删 | 17 GB 的四轮试点 + 其余 `results_*` 中已不再引用的轮次 | 最高 20+ GB |

**我没有执行任何 A/B/C 动作。** 删除证据类目录不可逆，且部分目录仍被索引与报告引用；按项目一贯纪律，这类操作必须先由你点头。

