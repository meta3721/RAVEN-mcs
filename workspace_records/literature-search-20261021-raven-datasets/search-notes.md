# 搜索记录与证据边界

日期：2026-10-21。范围：更适合移动感知实用价值研究的数据集；此前研究头脑风暴的支持材料。没有训练或开始新实验。

## 安全查询

- mobile air quality monitoring dataset vehicle timestamp GPS open data -site:mdpi.com
- OpenSense Zurich dataset download tram sensors
- Breathe London mobile monitoring dataset figshare
- Geo-temporal vehicular environmental sensing dataset
- SenMooVe dataset csv license
- Copenhagen Air View dataset download
- Sensor.Community data archive csv sensor_id license
- 分支检索：UCI Beijing Multi-Site、EPA PurpleAir correction dataset、AirQo calibration challenge、EPA AQS schema；AERPAW LoRaWAN vehicle tracking data、Intel Berkeley labdata、DCRNN METR-LA PEMS-BAY、WSN industrial feature dataset、FedScale dataset README。

## 候选筛查台账

保留重点：BelAir、OpenSense、Google Air View California、EPA PurpleAir、AirQo、Beijing Multi-Site、EPA AQS、DCRNN两集、AERPAW（待字段验收）。补充/条件候选：Warsaw、Intel Berkeley、WSN工业特征、UCI Air Quality 360。降级：FedScale不能作联合原生记录，Breathe London和Copenhagen原始粒度不清，SenMooVe任务与可用schema待核实，SSS短时及访问未完成，Sensor.Community缺参考与分阶段事件。共19类；METR-LA/PEMS-BAY按共同发布来源计一类。

MDPI来源按技能政策排除；第三方目录仅发现线索，最终数据事实尽量回到原作者/机构。没有从关键词未同时出现推断创新。

## 实际读取层级

- BelAir：公开文件API；两CSV头16 KiB和尾32 KiB各一次，206，合计96 KiB；未全量下载或统计全体ID。
- OpenSense：Zenodo API已读、O3/CO HEAD 200；UFP文件HEAD曾EOF；未全量下载。
- Google Air View：官方schema与完整元数据；未登录Earth Engine导出。
- PurpleAir、UCI360：两个公开小包已读取，合计约5.7 MB。主CSV行数/schema由文件计算，详见本地核查备忘录。
- Warsaw：两季CSV直接读取并统计，未保存大包；platformid唯一值31。
- AirQo、Beijing、AQS：官方schema、规模及许可说明；未为本任务取完整数据，未注册key或接受竞赛条款。
- DCRNN：作者README、论文、坐标表和上游处理说明；未下载H5，插补状态未查实。
- AERPAW：官方元数据、README和公开API；拟取1.33MB包实际仅收到4309字节校验HTML，不是7z。浏览器无可用会话，API下载要求token。没有绕过访问控制。自动审批通过读取，不存在安全拒绝；先前额度失败与网站校验应区分。
- SenMooVe：官方GovData和Fraunhofer项目页；Mobilithek下载未成功。

## 已发现的文档—文件差异

1. BelAir原CSV没有Moving，清洗版才有；20台系统中17台车载；论文出版去向已变，仓库说明陈旧。
2. PurpleAir论文设备计数与当前主CSV计数不同；目标泄漏列和重复日期需要处理。
3. Warsaw官网任务次数与文件mission数不同，平台只有一个；battery常量、status/ref含义不能猜。
4. UCI360网页行数/时间范围与CSV不同，部分参考目标极缺失，旧用途限制与当前许可并列。
5. AirQo当前条款同时出现CC BY与非商业限制，需保留版本及竞赛规则。
6. AERPAW档案与所链2026论文的周期、载荷和DR配置不同，不能混用或用模拟接收概率代替失败事件。

## 仍未知

- BelAir真实ID全体、三固定节点是否在公开表、R817参考时序可得性、真实每窗并发和采样配置变化。
- OpenSense可匹配的外部参考记录与所需校准成本。
- 所有候选在新任务上的学习充分性、数据重叠与模型收益。
- DCRNN分发文件逐点原始/插补标记、原始数据再分发权限。
- AERPAW失败文件类型和packet联结；是否足以构成实际U标签。

## 下一阶段接口

检索支持原有头脑风暴：真实支持获取、独立参考辅助推断、部分识别。尚未决定其中一个主线，未调用实验设计或改稿。首项动作应是一个主候选的数据审计，不能把检索推荐视作正式实验通过。用户自采资源的设备种类、地点、参考条件和预算仍未明确。
