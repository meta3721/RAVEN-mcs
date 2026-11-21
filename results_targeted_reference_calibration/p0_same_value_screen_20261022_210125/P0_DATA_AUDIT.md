# P0 重算审计

状态：`INSUFFICIENT_DATA`。P1：`NOT_RUN`。评价面板：`WRITTEN`。

本轮没有拟合模型，没有计算 RMSE、ContrastMAE、5% 收益或 2% 组差。这些门槛只写在冻结配置里。

## 来源

- 主表：`Data_DevelopmentUSPAcorrection_210408/Full24hrdataset.csv`，解析 12430 行、49 个 ID、9707 个 ID×日期。
- 完全重复折叠 38 行。之后的联结使用折叠后的行，源行号仍是 CSV 行号。
- 全表缺失：PM25cf1 0，RH 17，TempC 184，PM25FM 0。缺失记号只认 `NA` 和空字符串。
- 字典说明 `PM25FM` 与 `PM25cf1` 的单位是 µg/m³。负参考值保留。
- EPA 日文件来自只读缓存，没有重新下载。88101 扫描 654337 行，窗口内目标站点保留 13110 行。88502 扫描 237637 行，保留 351 行。88502 只用来核对未联结行，没有替补 88101。
- 站点映射沿用已核对的 `site_map.csv` 字节副本。West/North 以源表 `region` 为准。

## 旧键复算

旧键“站点 + 日期 + 参考型号”在 West/North、2019-01-26—2019-06-28 内有 381 个多值键，涉及 7 个站、142 日、965 行。这只是对照已关闭的失败记录，不把该记录改成通过。

## 新事件键联结

一行在参数为 88101、方法名完全相同、算术平均与 `PM25FM` 十进制精确相等、并且采样时长按仪器固定时，才算命中一个监测键。恰好一个键为 `UNIQUE`。两个或更多键且每个键的平均都等于该源值时为 `SAME_VALUE_MULTI_MONITOR`，全部键按 POC、方法代码、事件类型排序保留，不填写单一 POC。零个键，或命中键的平均并不都等于该源值，该行不可用。重力法 `R & P Model 2025` 用 `24 HOUR`。BAM-1020、BAM-1022、T640 用 `1 HOUR`。`T640X` 名称包含 `T640`，按同一连续 FEM 规则使用 `1 HOUR`，没有改用别的时长去促成联结。`24-HR BLK AVG` 不并入，也不与 `1 HOUR` 平均。同一键只因污染物标准重复且均值已经相同才合并。

| 对象 | 数量 |
| --- | ---: |
| 窗口内 West/North 且有参考值的源行 | 2987 |
| 恰好一个事件键 | 2970 |
| 同值多监测键 | 16 |
| 零个事件键 | 1 |
| 不是恰好一个键的源行 | 4551, 6209, 6869, 7578, 7818, 7833, 8342, 8402, 8717, 8738, 8747, 8781, 8842, 11956, 11990, 12004, 12375 |
| 第3节复核 | 一致 |
| 同一新事件键的不同参考值 | 0 |
| EPA 键内多个算术平均 | 0 |

源行 8402 的核对：设备 IA3，站点 19-153-0030，日期 2019-01-27，段 D_fit，联结状态 UNRESOLVED_NO_EXACT_MONITOR，身份数 0，88502 命中 0。D_fit 参考文字是 12.6。

88502 对未联结行的精确方法、时长和均值命中数：0。这些命中没有用来替补。

IA3 在 2019-01-27 的设备日：Met One BAM-1022 Mass Monitor w/ VSCC or TE-PM2.5C - Beta Attenuation → EXCLUDED_AMBIGUOUS_MONITOR，源行 8027|8230；R & P Model 2025 PM-2.5 Sequential Air Sampler w/VSCC - Gravimetric → EXCLUDED_UNRESOLVED_ROW，源行 8402|8465

## 排除的设备日

第3节复核一致后，才使用同值多键规则。两个或更多键的算术平均都等于同一个源值时，参考值就是这个共同浓度，全部键按 POC、方法代码、事件类型排序保留，不指定其中一个 POC。同一设备日出现两个不同参考值时标为 `EXCLUDED_AMBIGUOUS_MONITOR`。任一源行没有可用监测键时，整个设备日为 `EXCLUDED_UNRESOLVED_ROW`。没有取最小 POC，没有保留第一条，没有平均，也没有按与传感器的距离挑选。

| 排除原因 | 设备日 |
| --- | ---: |
| EXCLUDED_AMBIGUOUS_MONITOR | 421 |
| EXCLUDED_UNRESOLVED_ROW | 1 |

有效参考日只统计上述规则下的有效设备日。代表设备的有效配对日还要求 `PM25cf1` 不是缺失；RH 和 TempC 缺失不取消配对，留待以后用 D_fit 中位数填充。本轮不填充、不拟合。

## 站点筛选

候选站点 22 个，其中至少有一个有效参考设备日的站点 21 个。没有有效参考日的站点：06-071-0306。

型号先比 D、V、A、T 四个时段的覆盖数，再比 154 天内唯一有效参考日，平局按型号名称字典序。代表设备按 154 天有效配对日数，平局按 ID 字典序。支持不足则剔除该站点，不换设备，也不换型号。

| site_id | group | device_id | reference_type | paired_days_154 | D_fit | D_tune | D | V | A | T | included | reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 06-037-9033 | West | CA10 | Met One BAM-1020 Mass Monitor w/VSCC - Beta Attenuation | 124 | 26 | 13 | 39 | 23 | 13 | 49 | true |  |
| 06-067-0010 | West | CA1 | R & P Model 2025 PM-2.5 Sequential Air Sampler w/VSCC - Gravimetric | 50 | 9 | 5 | 14 | 9 | 10 | 17 | false | D=14<20;V=9<10;T=17<20 |
| 06-079-8002 | West | CA2 | Met One BAM-1020 Mass Monitor w/VSCC - Beta Attenuation | 135 | 28 | 14 | 42 | 28 | 26 | 39 | true |  |
| 06-083-0011 | West | CA5 | Met One BAM-1020 Mass Monitor w/VSCC - Beta Attenuation | 125 | 19 | 10 | 29 | 24 | 28 | 44 | true |  |
| 06-083-1008 | West | CA6 | Met One BAM-1020 Mass Monitor w/VSCC - Beta Attenuation | 86 | 21 | 14 | 35 | 28 | 23 | 0 | false | T=0<20 |
| 06-083-2004 | West | CA4 | Met One BAM-1020 Mass Monitor w/VSCC - Beta Attenuation | 132 | 24 | 12 | 36 | 27 | 25 | 44 | true |  |
| 06-083-2011 | West | CA3 | Met One BAM-1020 Mass Monitor w/VSCC - Beta Attenuation | 150 | 26 | 14 | 40 | 27 | 27 | 56 | true |  |
| 06-111-0007 | West | CA19 | Met One BAM-1020 Mass Monitor w/VSCC - Beta Attenuation | 31 | 0 | 0 | 0 | 0 | 3 | 28 | false | D=0<20;V=0<10;A=3<10;D_fit=0<1;D_tune=0<1 |
| 06-111-2002 | West | CA18 | Met One BAM-1020 Mass Monitor w/VSCC - Beta Attenuation | 1 | 0 | 0 | 0 | 0 | 0 | 1 | false | D=0<20;V=0<10;A=0<10;T=1<20;D_fit=0<1;D_tune=0<1 |
| 06-111-3001 | West | CA17 | Met One BAM-1020 Mass Monitor w/VSCC - Beta Attenuation | 129 | 20 | 9 | 29 | 28 | 28 | 44 | true |  |
| 19-103-2001 | North | IA9 | R & P Model 2025 PM-2.5 Sequential Air Sampler w/VSCC - Gravimetric | 61 | 13 | 6 | 19 | 13 | 8 | 21 | false | D=19<20;A=8<10 |
| 19-113-0040 | North | IA2 | Met One BAM-1020 Mass Monitor w/VSCC - Beta Attenuation | 52 | 6 | 6 | 12 | 8 | 10 | 22 | false | D=12<20;V=8<10 |
| 19-153-0030 | North | IA3 | Met One BAM-1022 Mass Monitor w/ VSCC or TE-PM2.5C - Beta Attenuation | 51 | 7 | 6 | 13 | 13 | 8 | 17 | false | D=13<20;A=8<10;T=17<20 |
| 19-163-0015 | North | IA11 | R & P Model 2025 PM-2.5 Sequential Air Sampler w/VSCC - Gravimetric | 54 | 13 | 7 | 20 | 13 | 8 | 13 | false | A=8<10;T=13<20 |
| 19-163-0020 | North | IA12 | R & P Model 2025 PM-2.5 Sequential Air Sampler w/VSCC - Gravimetric | 9 | 0 | 0 | 0 | 0 | 0 | 9 | false | D=0<20;V=0<10;A=0<10;T=9<20;D_fit=0<1;D_tune=0<1 |
| 50-021-0002 | North | VT1 | Teledyne T640 at 5.0 LPM - Broadband spectroscopy | 33 | 0 | 0 | 0 | 1 | 0 | 32 | false | D=0<20;V=1<10;A=0<10;D_fit=0<1;D_tune=0<1 |
| 53-033-0057 | North | WA1 | Met One BAM-1020 Mass Monitor w/VSCC - Beta Attenuation | 143 | 25 | 14 | 39 | 23 | 26 | 55 | true |  |
| 53-061-1007 | North | WA3 | Met One BAM-1020 Mass Monitor w/VSCC - Beta Attenuation | 121 | 27 | 13 | 40 | 27 | 28 | 26 | true |  |
| 55-025-0041 | North | WI4 | Teledyne T640 at 5.0 LPM - Broadband spectroscopy | 39 | 7 | 2 | 9 | 1 | 0 | 29 | false | D=9<20;V=1<10;A=0<10 |
| 55-087-0009 | North | WI2 | Teledyne T640 at 5.0 LPM - Broadband spectroscopy | 3 | 0 | 0 | 0 | 1 | 0 | 2 | false | D=0<20;V=1<10;A=0<10;T=2<20;D_fit=0<1;D_tune=0<1 |
| 55-133-0027 | North | WI6 | Teledyne T640X at 16.67 LPM - Broadband spectroscopy | 28 | 11 | 8 | 19 | 9 | 0 | 0 | false | D=19<20;V=9<10;A=0<10;T=0<20 |

## 评价面板

固定站点 8 个，West 6 个，North 2 个。
组内当日门槛：West 5，North 3。
V 可评价日 0。T 可评价日 0。T 七天块 0 个，块号 []。块从 2019-05-04 起每 7 天一块，块内至少一天可评价即计入。

未通过的面板条件：fixed_sites=8 < 10；North_sites=2 < 4；V_evaluable_days=0 < 20；T_evaluable_days=0 < 40；T_blocks=0 < 7。

## 接口

训练读取拒绝检查通过 3 项。完整接口结果见 ISOLATION_CHECK.md。预测不变性未运行。

没有训练模型，因此不声称预测不变性已经验证。
