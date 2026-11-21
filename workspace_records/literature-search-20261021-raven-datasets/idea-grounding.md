# 新方向的数据依据

日期：2026-10-21。以下为检索事实及研究推断，不是已证明创新或已授权实验。

## 八张证据卡

1. **BelAir**：17真实移动设备、清洗前后点记录、校准说明。原语：真实设备和机会性路线。可支持采样支持研究；完整参考与U未核实。[源](https://data.mendeley.com/datasets/89vgprbzv3/1)
2. **OpenSense**：10电车、长期GPS/Tram ID，污染物原始度不同。原语：路线重复与设备校准。迁移须按污染物单位和处理状态核验。[源](https://doi.org/10.5281/zenodo.3355208)
3. **Google Air View**：真实汽车、秒级实验室级仪器数据，公开元数据。原语：高质量移动外部验证；只有4客户端且不是全域真值。[源](https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_AirView_California_Unified_2015_2019)
4. **PurpleAir**：低价设备与FRM/FEM配对。原语：独立参考误差与分设备/地区验证；日均整理数据不能推导交付过程。[源](https://amt.copernicus.org/articles/14/4617/2021/)
5. **AirQo**：小时级近距离共址参考，3站。原语：廉价小型统计推断验证；设备数和许可需约束主张。[源](https://zindi.africa/competitions/airqo-low-cost-air-quality-monitor-calibration-challenge/data)
6. **AQS/Beijing**：可追踪站点的时空记录。原语：学习充分性与受控遮挡。不能把未覆盖城市位置或真实NA当已知真值/原因。[AQS](https://aqs.epa.gov/aqsweb/airdata/FileFormats.html)；[Beijing](https://archive.ics.uci.edu/dataset/501/beijing+multi+site+air+quality+data)
7. **AERPAW**：官方称有发送、接收、失败文件。原语：实际交付账本候选。档案可读，包未成功下载，逐包可识别性未知。[源](https://datadryad.org/dataset/doi%3A10.5061/dryad.w0vt4b939)
8. **DCRNN/FedScale**：公开的交通和异源系统轨迹。原语：可重复的受控机制试验；不能替代联合真实O/U。[DCRNN](https://github.com/liyaguang/DCRNN)；[FedScale](https://raw.githubusercontent.com/SymbioticLab/FedScale/master/benchmark/dataset/README.md)

## 对研究方向的影响（推断）

- **独立参考辅助的区域统计估计**：由PurpleAir/AirQo验证估计质量，再由自采验证实际目标与采样机制。最小问题是相同参考预算下能否比简单分层估计/残差校正获得更可靠的决策。既有PPI/active inference已覆盖通用思想，新意必须来自实际约束。
- **真正获取缺失支持**：BelAir/OpenSense可描述机会性路线，但历史数据不包含所有未执行路线的结果。实际补测/补传的效果需要自采或可核对的干预数据。不要把同一批记录重采样写成新增支持。
- **支持不全时的决策可识别性**：有标签子域可用于检验区间/判定；未观测区域需明确范围或附加假设。要超过简单缺失质量界，需要新的紧界、采集成本结果或可检验机制。
- **真实两阶段记录的测量研究**：小规模自采应把机会、测量、交付分开记录，研究选择如何改变统计结论。AERPAW可借鉴账本，尚不能宣称已有可直接迁移的完整空气质量联合数据。

## 保留的约束

选择新数据的依据必须是科学问题与可核查性，不是筛到RAVEN取胜为止。各块独立验证，跨城市记录不能当配对真值。自采应有事前确定、已知抽样概率的审计部分；随机邀请而无实际参考测量不足以识别未测量区域。没有任何本轮结果证明新方法的收益或投稿准备度。
