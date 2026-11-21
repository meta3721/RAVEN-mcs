# 本轮复现与交付索引

目录：p0_p1_20261022_161223。P0 INVALID_RUN / P1 NOT_RUN / WAITING_USER_REVIEW。

## 实际执行命令

~~~powershell
$r = 'C:/Users/szr/Desktop/record/1/results_targeted_reference_calibration/p0_p1_20261022_161223'
& "$r/.venv/Scripts/python.exe" -X utf8 "$r/meter.py" P0 inspect_source.py
& "$r/.venv/Scripts/python.exe" -X utf8 "$r/meter.py" P0 prepare_data.py
& "$r/.venv/Scripts/python.exe" -X utf8 "$r/meter.py" P0 explain_p0_failure.py
~~~

worker中OMP_NUM_THREADS、MKL_NUM_THREADS、OPENBLAS_NUM_THREADS、NUMEXPR_NUM_THREADS均为1。版本见environment.json；使用任务局部.venv，复用基础NumPy/pandas，缺失scikit-learn/scipy/psutil安装到局部环境。

## 实现范围

- prepare_data.py：P0数据、身份、参考/设备选择、支持与隔离流程；本批在参考冲突分支停止。
- data_access.py：限定白名单及用途的标签接口。
- isolation_check.py：合格面板的综合隔离检查实现，本批未到条件；explain_p0_failure.py记录同一检查目前可执行的访问拒绝/门禁/事件键核验。
- run_p1.py、score_p1.py：**仅停止门禁**，本目录状态下退出码2且不读取训练数据。不是完整P1数值程序，未通过开发验收；P0停止后未继续依赖开发。
- meter.py、usage.py：累计CPU/墙钟、RSS计量；局限见RESOURCE_AND_BUDGET.md。
- explain_p0_failure.py：只整理已有失败及D_fit实例，不拟合模型。

prepare_data拒绝覆盖已有终态。需要重现时，在新的、获准目录复制脚本与官方源文件、source_S_tables_pdfpage文本，准备相同环境再执行前两条命令；不要改写当前P0_status.json或历史失败。

## 产物有效性

P0_DATA_AUDIT.md、FAILURE_REPORT.md、SOURCE_IDENTITY_REVIEW.md：真实发现。
site_map.csv：源身份索引。
reference_events_metadata.csv：候选事件键，每键1行；381键参考不一致，**不能充当已批准查询存储**。
conflicts.csv、conflicts_by_site_split.csv、conflict_examples_D_fit_only.csv：完整失败定位及仅D_fit数值实例。
protocol_freeze.json：原门槛/日期/模型规则不变。
representative_devices.csv、split_manifest.csv、evaluation_panel.csv：**仅表头、未完成**，不是0站点/0日期的有效结果。
ISOLATION_CHECK.md：已执行和未执行分开。
P1_CALIBRATION_REPORT.md：NOT_RUN；无比较CSV、model_freeze、模型或预测，不填零。
NEXT_STAGE_REQUEST.md：等待参考身份问题的处理决定，不进入P2。

原包、RAVEN论文、训练代码、协议及历史STOP报告均未修改。A/T参考未提供给模型、未输出其数值分布/误差。所有新产物在本目录。
