# 固定站点与独立参考数据：核查摘录

核查日期：2026-10-21。仅使用官方数据页、发布机构、论文原始页面和作者数据包；排除 MDPI。研究用途判断与源事实分开。没有训练、没有联系第三方。下载仅两个小包：UCI 360 为 1,543,989 bytes；EPA PurpleAir 为 4,153,094 bytes。

## 优先结论

- 若要引入真实独立参考测量，优先 **EPA PurpleAir 共址数据**、**AirQo 2021 校准数据**；前者设备更多，后者为小时级但只有三个站点。
- 若仅补强时空补全基准，**UCI Beijing Multi-Site** 最省事；**EPA AQS 单一区域子集**更便于解释参考方法、QA 与缺失原因。
- **UCI Air Quality 360** 可做低成本的漂移/校准诊断，但单设备不宜包装为真实多客户端联邦数据。
- 五者均不提供本任务所需完整的真实上传到达 U 日志。参考仪器只支持其采样时间和地点的参考观测；不能把插值区域场当真值，不能把固定站点当移动客户端。

## 1. EPA PurpleAir / U.S.-wide correction（优先）

状态：Barkjohn, Gantt, Clements，AMT 2021 正式发表；method + benchmark。论文与官方公开数据配套。

来源：[论文](https://amt.copernicus.org/articles/14/4617/2021/)，[官方数据记录](https://catalog.data.gov/dataset/dataset-development-and-application-of-a-united-states-wide-correction-for-pm2-5-data-coll)，[下载](https://pasteur.epa.gov/uploads/10.23719/1522388/Data_DevelopmentUSPAcorrection_210408.zip)，[补充表](https://amt.copernicus.org/articles/14/4617/2021/amt-14-4617-2021-supplement.pdf)，[EPA 数据许可](https://pasteur.epa.gov/license/sciencehub-license.html)。数据 DOI：10.23719/1522388；论文 DOI：10.5194/amt-14-4617-2021。

公开包直接核验：Full24hrdataset.csv 有 12,430 行、49 个 ID、9,707 个唯一 ID×Date，日期 2017-09-30 至 2020-01-13。PM25FM、PM25cf1 无缺失；RH 有 17 个 NA。论文叙述分析范围为 50 个设备、39 个站点、16 州，与当前 CSV 实体数不同，不能互换。CSV 主要字段：Date、ID、region、FEMorFRM、FEMorFRMtype、PM25FM、PM25cfatm、PM25cf1、颗粒物计数、TempC、RH、Dewpoint。PM25FM 为独立 FRM/FEM；其余两列为 PurpleAir 双通道平均。补充表 S2 给 PA ID→AQS site，S1 给坐标。

缺失/泄漏：表已日均、QA、地区再平衡，不能由空日期解释上传失败。ID×Date 有 2,199 个重复组，须处理同日多参考方法。已有 PM25PAlinearcor、PM25PARHcor 是全数据拟合校正；ratio*/diff* 含参考目标，不能作为预测特征。ratioPARHcor_FM 的 NA 部分是参考浓度 <1 时人为置空，不能算传感器缺测。

适用（推断）：跨设备/地区异质性、质量感知与参考误差评估；不适合高频移动轨迹或真实 U 缺失。体积 4.15 MB ZIP、主 CSV 6.42 MB；CPU 子集处理轻量。EPA 许可页默认公有领域，须保留包内元数据限制。尚未逐一核对补充表站点映射与 AQS 当前记录。

## 2. AirQo Low-Cost Air Quality Monitor Calibration Challenge 2021

状态：官方 2021 已结束竞赛，pure benchmark；不要声称为 CCF 论文基准。

来源：[官方数据与字段说明](https://zindi.africa/competitions/airqo-low-cost-air-quality-monitor-calibration-challenge/data)，[AirQo 数据条款](https://airqo.net/legal/airqo-data)，[AirQo 共址校准说明](https://docs.airqo.net/airqo-docs/the-airqo-use-case-ml-based-approach)。

三个 Kampala 固定参考站：US Embassy、Makerere、Nakawa；小时采样，站点数据约 4:2:1。字段包括 created_at（UTC+3）、site、pm2_5、pm10、s2_pm2_5、s2_pm10、humidity、temp、lat、long、altitude、地形/植被/道路距离，目标 ref_pm2_5。低价设备与参考同高、距离不足 1m；双传感器是同一设备内部冗余，不能算两个独立移动客户端。

PM 字段据数据说明应无 NaN，温湿度有少量缺失；训练表约 2 MB，测试约 487.1 KB，测试无目标。真正自建时间/留站评估只能从有标签训练表划分。下载页要求接受条款，本次未下载、未核实行数和时间跨度。AirQo 当前条款写 CC BY 4.0，同时另列非商业限制；比赛再分发许可未确认，不能只写“完全自由商用”。

适用（推断）：小时级真实参考与传感器偏差；三站限制了大规模联邦参与者主张。它为经整理校准集，不能据缺行恢复 U 或原始 O 形成机制。

## 3. UCI Beijing Multi-Site Air Quality（id=501）

状态：UCI 正式数据 DOI 10.24432/C5RK5G；相关论文 Zhang et al., Proceedings of the Royal Society A 2017，DOI 10.1098/rspa.2017.0457。数据候选按 pure benchmark 看待；相关论文是环境统计分析，不是联邦补全系统。

来源：[UCI 数据](https://archive.ics.uci.edu/dataset/501/beijing+multi+site+air+quality+data)，[原始论文](https://pmc.ncbi.nlm.nih.gov/articles/PMC5627385/)。

12 个国控固定站，420,768 站点小时槽；2013-03-01 至 2017-02-28；6 污染物及6气象变量。字段：No、year/month/day/hour、PM2.5/PM10/SO2/NO2/CO/O3、TEMP/PRES/DEWP/RAIN/wd/WSPM、station。station 为名称，不是设备/参与者 ID；官方列出的 CSV schema 无经纬度。气象值匹配最近气象站，不是各污染站独立气象观测。缺失为 NA，但未给每条缺失原因/测量与上传的分离证据。

UCI 列主 ZIP 7.6 MB、总包 7.8 MB，CC BY 4.0。未下载。适用（推断）：小规模空间补全、固定站之间的关系；只对有观测且被隐藏的格子有评价真值。没有低成本-参考配对，也没有全城市空间真值或真实 U。

## 4. EPA AQS / AirData（按区域子集）

状态：持续维护的官方观测数据库/system-tool，不绑定单篇算法论文。

来源：[官方数据库](https://www.epa.gov/aqs)，[文件与大小目录](https://aqs.epa.gov/aqsweb/airdata/download_files.html)，[CSV schema](https://aqs.epa.gov/aqsweb/airdata/FileFormats.html)，[API](https://aqs.epa.gov/aqsweb/documents/data_api.html)，[数据字典](https://aqs.epa.gov/aqsweb/documents/AQS_Data_Dictionary.html)。

推荐样本键：State Code+County Code+Site Num+Parameter Code+POC+Date GMT+Time GMT。POC 区分同站同污染物的不同监测器；还有 Latitude/Longitude/Datum、Sample Measurement、Units、MDL、Uncertainty、Qualifier、Method Type/Code/Name。Method Type 可区分 FRM、FEM 和非参考方法，不能把全部 AQS 读数自动叫参考级。Qualifier/Null code 区分计划采样未完成及异常/QA；缺行也可能是非每日采样或设备不在运行期，须结合 monitor 描述与采样日程。

参考与校准：监管测量、方法和 QA/QC 可审计；某区域的保留站可作参考点，不能代表无站位置真值。2024 全国 hourly_88101 ZIP 64,793 KB、8,139,551 行（页面标截至 2026-06-25）；本次未下载。建议只取一城市/州、一污染物和数月。API 需注册 key；预生成文件公开直链。官方明确 AQS 环境监测数据为公有领域：[使用说明](https://www.epa.gov/outdoor-air-quality-data/do-i-need-request-permission-use-monitoring-data-and-graphics-airdata)。页面搜索可核实、正文抓取返回 502；另以 EPA 通用许可页交叉核查。

适用（推断）：空间参考基线、QA 可解释缺失与传感器方法异质性。AQS 是迟后归档库，提交/更新时间不等同逐样本真实 U 日志。

## 5. UCI Air Quality（id=360；只作诊断）

状态：UCI DOI 10.24432/C59K5F；De Vito et al., Sensors and Actuators B: Chemical 129(2):750–757，2008，正式论文，DOI 10.1016/j.snb.2007.09.060；method + benchmark。

来源：[UCI](https://archive.ics.uci.edu/dataset/360/air+quality)，[出版社原始论文记录](https://www.sciencedirect.com/science/article/pii/S0925400507007691)。

单个固定多传感器设备，5 金属氧化物通道与共址认证分析仪参考 CO/NMHC/C6H6/NOx/NO2，另有 T/RH/AH。真实 CSV 用分号分隔、逗号小数，Date 为 DD/MM/YYYY、Time 为 HH.MM.SS，最后有两个空列；没有站点/参与者 ID 或坐标。

实查：9,357 个有日期行，2004-03-10 至 2005-04-04。网页写 9,358、2004-03 至 2005-02，存在元数据差异。缺失 -200 可保存为 -200,0；各参考列缺失数为 CO 1,683、NMHC 8,443、C6H6 366、NOx 1,639、NO2 1,642。自然缺失原因未知，不能当 U。

包 1.54 MB，CSV 0.785 MB，极轻量。UCI 页面同时写 CC BY 4.0 与旧的仅科研/禁止商业表述，应记录冲突。适用（推断）：校准漂移、异质通道与参考标签稀疏诊断；单设备无法支撑真实空间联邦客户端。

## 可复用的研究判断

从五者可得到两种互补证据：固定站点的时间/空间观测用于补全；低价传感器-独立参考配对用于评估补全输出在传感器偏差下是否仍接近物理参考。这一组合不能补出真实移动或真实上传到达；小规模新采集应单独记录设备本地测量与服务器到达时间，参考仪器保留独立观测。
