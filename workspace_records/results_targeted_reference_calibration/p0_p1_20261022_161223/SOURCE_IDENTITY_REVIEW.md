# 来源身份核查

- 原包未改动：C:/Users/szr/Desktop/record/1/dataset_dense_reference_evidence/epa_purpleair_2021.zip
- 数据DOI10.23719/1522388；内部主表Data_DevelopmentUSPAcorrection_210408/Full24hrdataset.csv。
- [原文](https://amt.copernicus.org/articles/14/4617/2021/)，DOI10.5194/amt-14-4617-2021；核对§2.2.2、§3.2.2。
- [官方补充](https://amt.copernicus.org/articles/14/4617/2021/amt-14-4617-2021-supplement.pdf)单次下载保存；S1为PDF4—5页，S2为PDF6—7页。site_map.csv保存每行表号、页码、提取文本行号及S1坐标。
- S4的同站点T640不同POC不能直接恢复CSV逐行身份；未额外检索或猜测联结。
- 字典确认PM浓度µg/m³。NA仅作缺失，不删除负参考或自行设离群规则。TempC缺184，RH缺17，与原文§3.2.2一致。
- 全源49设备均有S2/S1映射。DE1仅在补充表，未在原CSV；其代码疑点没有进入本次输入。WI1的S1坐标疑点标注保留，其不在固定日期窗。
- 原文整体设备数不替代当前加工CSV计数；原数据已有QA及Iowa抽样，本次不把它解释为未经选择的区域总体。
