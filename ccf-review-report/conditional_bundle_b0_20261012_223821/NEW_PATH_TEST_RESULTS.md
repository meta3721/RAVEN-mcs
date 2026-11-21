# 新增路径测试证据

结论：23项新路径、8项相关回归，合计31通过，无跳过。测试为隔离确定性fixture及已有纯聚合/设施回归，不是训练或控制收益实验。

最终完整日志 [audited_delivery.log](C:/Cursor/raven.mcs/results_conditional_bundle_b0_20261012_223821/audited_delivery.log)，JUnit [audited_delivery.xml](C:/Cursor/raven.mcs/results_conditional_bundle_b0_20261012_223821/audited_delivery.xml)；配置格式相关检查器修正后，最终语法 [final_facility-syntax.log](C:/Cursor/raven.mcs/results_conditional_bundle_b0_20261012_223821/final_facility-syntax.log)、环境 [final_facility-environment.log](C:/Cursor/raven.mcs/results_conditional_bundle_b0_20261012_223821/final_facility-environment.log)；结构化汇总 [NEW_PATH_TEST_RESULTS.json](C:/Cursor/raven.mcs/results_conditional_bundle_b0_20261012_223821/NEW_PATH_TEST_RESULTS.json)。

| 测试 | 结果 | pytest测试体墙钟 |
|---|---|---|
| test_corrected_preview_application_and_stale_rejection | PASS | 0.041s |
| test_missing_q_not_silently_replaced | PASS | 0.001s |
| test_replacement_out_of_order_and_physical_outcome | PASS | 0.002s |
| test_inflight_expiry_empty_close_and_mature_labels | PASS | 0.041s |
| test_future_checkpoint_invalid_tensor_and_stale_snapshot | PASS | 0.014s |
| test_design_freeze_and_gate_has_no_computation_effect | PASS | 0.028s |
| test_probability_frozen_per_attempt_and_failure_censoring | PASS | 0.002s |
| test_production_save_restore_same_suffix_and_no_overwrite | PASS | 3.946s |
| test_real_model_and_existing_trainer_connected_but_no_sgd | PASS | 0.164s |
| test_shared_stage1_exact_existing_formulas_and_legal_clipping | PASS | 0.001s |
| test_invalid_numeric_inputs_not_prediction_fallback | PASS | 0.001s |
| test_official_registration_uses_full_runner_lagged_inputs | PASS | 0.033s |
| test_probability_rejects_other_target_policy_context | PASS | 0.001s |
| test_official_missing_p_is_input_error | PASS | 0.005s |
| test_official_disk_restore_same_registration_suffix | PASS | 2.870s |
| test_competing_risk_and_censoring_arithmetic | PASS | 0.003s |
| test_client_marks_not_reassigned_and_frozen_download | PASS | 0.004s |
| test_joint_support_uses_multistep_path_and_no_real_mutation | PASS | 0.053s |
| test_snapshot_does_not_accept_future_or_hidden_fields | PASS | 0.050s |
| test_unsupported_prediction_fallback_and_hard_deadline | PASS | 0.030s |
| test_isolated_normal_and_controlled_cpu_timeout | PASS | 9.677s |
| test_public_future_registration_and_q_freeze | PASS | 0.024s |
| test_future_joint_mark_keeps_quality_and_registration_age_together | PASS | 0.002s |
| test_e0_3_p2_unique_across_repeated_solves | PASS | 0.049s |
| test_e0_3_rejects_nonpositive_lambda_beta | PASS | 0.001s |
| test_e0_4_debt_prefix_bound | PASS | 0.001s |
| test_coverage_mix_matches_matrix_product | PASS | 0.001s |
| test_p2_certificate_checks_ess_ball | PASS | 0.001s |
| test_weight_uniformity_epsilon | PASS | 0.001s |
| test_auditable_manifest_can_require_git | PASS | 0.097s |
| test_manifest_rejects_seed_bundle_mismatch | PASS | 0.007s |

## 可审查的实际值

- [audited_delivery-preview_application.json](C:/Cursor/raven.mcs/results_conditional_bundle_b0_20261012_223821/audited_delivery-preview_application.json)：完整P2实际alpha/beta/M/omega、d/ell、数值残差、原始/实际权重目标、实际张量应用。
- [audited_delivery-full_model_connection.json](C:/Cursor/raven.mcs/results_conditional_bundle_b0_20261012_223821/audited_delivery-full_model_connection.json)：真实CommonNDMF后端、原ClientTrainer、variance/debt及检查点；构造张量来源明确，SGD0。
- [audited_delivery-official_registration.json](C:/Cursor/raven.mcs/results_conditional_bundle_b0_20261012_223821/audited_delivery-official_registration.json)：正式register API、窗口冻结的非恒等ratio/p与[3,7]质量、窗口内修改忽略、下窗生效、旧消息不变。
- [audited_delivery-production_persistence.json](C:/Cursor/raven.mcs/results_conditional_bundle_b0_20261012_223821/audited_delivery-production_persistence.json)：正式manifest/来源记录、保存恢复动作和完整状态后缀一致。
- [audited_delivery-official_disk_restore.json](C:/Cursor/raven.mcs/results_conditional_bundle_b0_20261012_223821/audited_delivery-official_disk_restore.json)：正式会话恢复后下一次注册与控制器计量一致。
- [audited_delivery-public_registration.json](C:/Cursor/raven.mcs/results_conditional_bundle_b0_20261012_223821/audited_delivery-public_registration.json)：事前公开机会、在途版本保留、未来注册预测及逐尝试q冻结；全部测试概率明确isolated_test_input。
- [audited_delivery-risk_table.json](C:/Cursor/raven.mcs/results_conditional_bundle_b0_20261012_223821/audited_delivery-risk_table.json)：完成/失败/右删失的风险集算术，低支持拒绝。
- [audited_delivery-joint_support.json](C:/Cursor/raven.mcs/results_conditional_bundle_b0_20261012_223821/audited_delivery-joint_support.json)：共同消息束、一步CLOSE/跨窗WAIT差异；不当作普遍收益。
- [audited_delivery-isolation.json](C:/Cursor/raven.mcs/results_conditional_bundle_b0_20261012_223821/audited_delivery-isolation.json)：正常1.468750 CPU秒/7.551125墙钟秒，受控超时1.921875 CPU秒/2.119798墙钟秒，实际子进程终止。

## 开发迭代保留

development2：16通过/1设施失败；development3：16通过/1保存设施失败；development4：17通过；development5：20通过/1手工期待错误；final：28通过/1显式Git根定位回归；acceptance：28通过/1进程退出设施反馈；acceptance2：29通过；session_acceptance：8个会话测试通过；delivery_acceptance、final_delivery、audited_delivery均31通过。audited_delivery首次语法子检查把配置YAML当Python，日志保留，最终final_facility只对.py做语法检查后通过。没有删除/跳过失败测试。

早期Windows Job设置错误及legacy-manifest-once设施上限记录保留。历史manifest仅隔离复现一次，未证明全库稳定；新正式存储路径通过。原226项Design测试不重复，全库测试与实际训练/回放未运行。测试内容/脚本和最终源码归属在汇总JSON中；旧52保护文件不变。
