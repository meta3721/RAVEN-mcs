# 接口隔离检查

通过：是。要求标签文件：是。

已检查的内容：

- training_refuses_V：通过（detail=training entry refuses labels for split V）
- training_refuses_A：通过（detail=training entry refuses labels for split A）
- training_refuses_T：通过（detail=training entry refuses labels for split T）
- file_absent_labels_A.csv：通过
- file_absent_labels_T.csv：通过
- A_T_reference_values_withheld：通过（leaked_rows=0）
- panel_has_no_concentration_column：通过
- excluded_table_has_no_concentration_column：通过
- training_reads_D_fit：通过（n=195）
- training_reads_D_tune：通过（n=99）
- training_D_is_only_D_fit_plus_D_tune：通过（n=294，expected=294）
- training_frame_D_fit：通过（n=195）
- training_frame_refuses_A：通过
- features_have_no_reference_column：通过

训练入口只接受 D_fit 与 D_tune，二者合并为 D。V、A、T 的训练读取会拒绝。A/T 标签文件不存在。

未检查：没有训练模型，没有改写 A/T 标签副本后比较预测。预测不变性：NOT_RUN。
