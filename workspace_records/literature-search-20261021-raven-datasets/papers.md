# RAVEN-MCS 新研究的数据集检索与用途判断

日期：2026-10-21（Asia/Shanghai）。技能：ccf-literature-searcher；标准数据集检索。目标仍按移动感知/TMC研究理解。用户可联系资源开展小规模真实采集。本轮未训练、未修改论文、未注册账号或联系第三方。

**结论：存在更适合特定新问题的数据，但尚未确认一个公开数据集同时提供真实移动客户端、可靠参考观测和完整的测量—发送—到达账本。优先评估 BelAir 的移动轨迹，使用 EPA PurpleAir 作为独立参考验证块，再由小规模自采补齐真实 O/U 事件。**各数据集独立评估，不能跨城市拼接为共址真值。

这里的“更合适”指身份、参考标签和协议可核查性更符合研究问题，尚不意味着新方法会得到更大收益。未运行学习充分性、覆盖度或并发窗口统计。

## 1. 最值得进一步读取的候选

### 1.1 BelAir：优先移动主数据候选

[作者数据仓库](https://data.mendeley.com/datasets/89vgprbzv3/1)；[2023正式论文](https://www.frontiersin.org/journals/environmental-health/articles/10.3389/fenvh.2023.1232867/full)。数据 DOI：10.17632/89vgprbzv3.1，CC BY 4.0。论文实际发表于 Frontiers in Environmental Health；仓库仍保留投稿 Environment International 的旧说明。

2021年1—9月、Antwerp：17台真实车载设备 IMEC1–17，另3台在R817参考站旁保留共址。公开CSV含 Dev、date、Lat、Lon、Speed、NO2_ppb、PM1/PM2.5/PM10、Temp、Hum、NO2；清洗版另有 Moving。两CSV为994,157,966及845,752,687字节；只分段读取头尾合计96 KiB，未全量下载。

**用途判断：**它比将网格当客户端更适合验证真实设备异质性、重复路线与新增支持获取，NO2可作为优先审计对象。17台设备不保证每个窗口都有足够并发或组成自由度，仍需数据审计。

**必须保留的边界：**清洗版删除不完整行并裁剪空间，不能用它还原全部缺测过程。清洗前表也经过厂商测量处理。公开表头无R817参考列；NO2和NO2_ppb只是单位不同。尚未确认三台固定节点是否在完整文件中。论文报道约94%记录停车，配置还包括不同采样周期，不能把每条记录都称移动测量或把固定10秒网格空槽当失败。未见逐事件上传/ACK字段。

**下一项必要核查：**按真实 Dev 流式检查完整性、时区、采样配置、重复路段、设备间重叠及参考数据是否可获得。先保留清洗前数据，禁止全文件一次载入当前电脑内存。

### 1.2 OpenSense Zurich：长期移动复核候选

[O3/CO档案](https://doi.org/10.5281/zenodo.3355208)；[UFP档案](https://doi.org/10.5281/zenodo.3298842)。CC BY 4.0。10辆电车，时间、WGS84经纬度、HDOP、Tram ID均可追踪。O3覆盖2012—2016，CO覆盖2014—2016；UFP覆盖2012—2014。

已读取Zenodo API；O3/CO压缩包HEAD返回200，约191.5/588.1 MB，未下载。**CO列是工作电极电压，不能直接当浓度**；O3/CO还需逐设备校准，参考数据要另取。UFP已校准并删除故障样本。适合真实设备和长期路线，数据清理负担比单纯换CSV更大。无已确认的逐测量上传失败账本。建议先核查O3或UFP的小时间段，不先处理全部多年份数据。

### 1.3 Google Air View California：高质量移动外部验证

[官方目录与schema](https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_AirView_California_Unified_2015_2019)；[完整元数据](https://docs.google.com/document/d/1If15JccoJcN01Jg3ljN3V-qUFS0HywKAd4OsQ-_JXJo/view)。2015—2019，4辆汽车，1 Hz；Car_Identifier、Date_Time、位置、速度、多污染物及量程标记。CC BY-NC 4.0，Earth Engine访问需账号权限。

元数据列约4200万点；本轮未导出。数据有时间响应校正、QA和道路吸附，并非原始通信事件。仪器检查或共址比较不等于每个位置都有独立真值。适合重复采样与跨地区外部验证；仅4个真实客户端，不能靠切成许多网格声称大规模真实联邦。应先在服务器侧选地区、时间和污染物，避免下载全量。

### 1.4 EPA PurpleAir 共址数据：优先独立参考验证

[AMT 2021论文](https://amt.copernicus.org/articles/14/4617/2021/)；[EPA数据记录](https://catalog.data.gov/dataset/dataset-development-and-application-of-a-united-states-wide-correction-for-pm2-5-data-coll)；[公开数据包](https://pasteur.epa.gov/uploads/10.23719/1522388/Data_DevelopmentUSPAcorrection_210408.zip)。

已读取4.15 MB压缩包。主表实查12,430行、49个ID、9,707个唯一ID×Date；2017-09-30—2020-01-13。PM25FM为共址FRM/FEM参考，另有低价设备读数及温湿度。论文的50设备/39站口径与当前CSV实体数不同，不混用。主表为日均、QA后产品，适合验证估计是否接近独立参考，不能验证高频移动或真实U。

**重要数据陷阱：**已有全数据拟合校正列及含参考目标的ratio/diff列，不能作为训练输入；同日同设备可对应多种参考方法，需处理重复。直接验证记录见[本地字段核查](C:/Users/szr/Desktop/record/1/dataset_dense_reference_evidence/verified_candidates.md)。EPA许可按公开数据及包内元数据处理，不将论文许可机械套用到所有上游资产。

### 1.5 AirQo 2021：小时级参考的小型备选

[官方竞赛数据说明](https://zindi.africa/competitions/airqo-low-cost-air-quality-monitor-calibration-challenge/data)。Kampala三个固定站，低价设备与参考同高、相距不足1m，小时级，目标ref_pm2_5，含site、时间、坐标和环境变量。Train约2 MB，Test无目标；未接受条款下载。当前AirQo条款同时列CC BY 4.0和非商业限制，竞赛再分发规则需单独确认。

适合便宜的参考校准实验；三站不足以支撑大规模参与选择。同机双传感器不是两个独立客户端；整理后的表不能恢复O/U事件。

### 1.6 Beijing Multi-Site / EPA AQS：受控时空验证

[UCI Beijing Multi-Site](https://archive.ics.uci.edu/dataset/501/beijing+multi+site+air+quality+data)为12固定站、420,768站点小时槽、2013—2017、约7.8 MB，CC BY 4.0。列有station与时间、污染物及气象；缺失记NA但无原因，schema未含坐标。适合轻量学习和人工遮挡验证，只对原本有观测的评估位置拥有标签。

[EPA AQS文件目录](https://aqs.epa.gov/aqsweb/airdata/download_files.html)及[schema](https://aqs.epa.gov/aqsweb/airdata/FileFormats.html)提供站点、参数、POC、坐标、时间、测量方法与质量信息。选一地区、一污染物、数月即可控制数据量。AQS monitor是测量序列身份，并不总是一台不变的物理设备；需按FRM/FEM筛选参考方法，结合运行期及采样日程解释缺失。API需key，预生成文件可直接取。

两者可改善参考和时空协议的可核查性；固定站不是移动客户端，AQS归档更新时间也不是U的服务器到达时间。未访问位置不能由插值变成真值。

### 1.7 METR-LA / PEMS-BAY：学习与补全机制的异域复核

[DCRNN作者仓库](https://github.com/liyaguang/DCRNN)；[ICLR 2018论文](https://arxiv.org/html/1707.01926)。分别207/325固定检测器，5分钟速度，带真实传感器ID、时间索引及坐标。可以先取子图、短时间段和轻量基线验证模型是否真正学习。

原任务为预测，改成补全需明确另建协议。没有真实测量请求或上传失败日志。PeMS上游存在插补，当前分发H5的逐点原始/插补标记尚未核实，因此不能把所有非零值叫原始真值。软件MIT不自动等于源数据再分发许可。本轮未下载H5，也没有承诺当前电脑能跑全套DCRNN。

### 1.8 AERPAW Dataset-16：真实U的候选线索，尚未通过字段验收

[官方Dryad档案](https://datadryad.org/dataset/doi%3A10.5061/dryad.w0vt4b939)；[项目页](https://aerpaw.org/dataset/lorawan-gateway-performance-and-vehicle-tracking-data/)。2025发布，CC0；约1.33 MB。档案描述发端packet ID、sent_timestamp、遥测，以及收端rx_time、RSSI/SNR、gateway ID和failed_tx_packages.csv。

下载实际返回人机校验HTML，未获得7z。失败文件究竟是本地发送错误、空口丢包还是其他事件，尚未确认。档案与所链2026论文的发送周期/载荷/DR配置不一致，可能为不同campaign，禁止拼接。它有希望为真实交付过程提供机制验证，但不含空气质量参考或完整未测量O账本；不能嫁接到BelAir后声称同场真实O/U。

## 2. 其他筛查结果

- [Warsaw RI-URBANS自行车](https://doi.org/10.18150/MYFYSJ)：CC0、实际读取两季表；只有一个platformid，适合采集方案参考，不能把mission变成真实客户端。ref为仪器字段，不是外部环境真值。
- [Intel Berkeley](https://db.csail.mit.edu/labdata/labdata.html)：54节点、epoch和传感值，适合真实多节点观察缺口；跳号不能分辨未采样和未上传。体量约34 MB gzip。
- [WSN工业特征集](https://github.com/apanouso/wsn-indfeat-dataset)：传感与链路特征联合，但每行汇总500条记录，不能还原逐事件O/U；CC BY-NC-SA 4.0。
- [FedScale数据说明](https://raw.githubusercontent.com/SymbioticLab/FedScale/master/benchmark/dataset/README.md)：workload与设备环境轨迹来自不同来源；可作真实轨迹驱动模拟，不能替代同设备同时间的联合观测。
- [Breathe London mobile](https://www.data.gov.uk/dataset/abdd95eb-a630-457f-bdff-cf61759beccb/breathe-london-mobile-monitoring1)：现行目录列中位数产品，原始逐车辆数据及历史mobile许可未完全核实，暂不作为立即可用主数据。
- [SenMooVe](https://www.govdata.de/suche/daten/senmoove-air-quality-monitoring-in-public-transport-vehicles)：车内空气与状态项目，实际包schema/许可未核实；车内舒适性与城市室外暴露是不同任务。
- [SSS vehicular dataset](https://pmc.ncbi.nlm.nih.gov/articles/PMC13015738/)：初筛发现3车短时采集；当前原文访问出现校验，下载/schema未完成验收，不作正式推荐。
- [Sensor.Community](https://sensor.community/en/index-new/)：公开低价设备流适合作补充，但发布端缺口无法分解O/U，参考质量需要独立核查。
- [Copenhagen Air View](https://datavejviser.dk/katalog/open-data-dk/c164949b-a729-4648-8012-28ddd6514223)：已发现官方地图发布入口，尚未核实原始逐车时序，暂不推荐替代原始轨迹。

## 3. 如何服务下一轮实质研究

推荐数据结构是三个独立证据块：

1. **移动支持机制：BelAir优先，OpenSense复核。**明确真实设备、时间、空间支持，检验补测/获取新支持是否改变任务可判断性。
2. **独立测量质量：EPA PurpleAir优先，AirQo补充。**研究校准与统计决策能否接近独立参考；不把二者当BelAir的参考标签。
3. **本地小规模新采集：补真实O/U与独立审计。**至少能关联采样机会、设备本地测量是否成功、发送尝试、服务器接收及时间、重复/重传、独立参考观测。保留一部分事先随机安排的审计采集，不能只请求模型认为重要的点。

可由这些数据支撑的新问题包括：少量参考测量下的区域统计估计；预算下取得缺失支持的价值；支持不全时部署决策的可识别边界。它们都允许简单估计器成为最优实现，不预设完整RAVEN必须获胜。现有方法应保留为候选或结构基线。

下一步应先对首选数据作字段、真实并发、覆盖和参考可用性审计，再决定研究问题。当前没有依据承诺这些候选能改善RMSE、消除旧可行域退化或保证投稿层次。

## 4. 搜索与评价范围

筛查19类候选，保留13个数据资源条目（DCRNN两集合并为一类）在[papers.csv](C:/Users/szr/Desktop/record/1/literature-search-20261021-raven-datasets/papers.csv)中，并在正文突出适用者。CSV分类对象是数据发布条目，统一记为pure benchmark，不把关联的原论文也归为纯基准论文。评分是基于已读发布材料的数据贡献与可复核性初筛，不是对原论文的完整同行评审；数据资源的算法数值证据记N/A benchmark。A/B/C表示本任务检索优先级，不是CCF等级；已确认字段与未核查项分别保留。

选择次序是：先审计BelAir的真实并发、覆盖与NO2测量质量；若要先以最低计算成本验证独立参考辅助估计，则从已取得的EPA PurpleAir小包开始。后者主要是PM2.5，而BelAir优先对象是NO2，两者只能作为不同污染物/任务的独立验证块，不能当同一物理场的标签。自采污染物与设备配置需由实际参考仪器资源决定。

只使用原作者、官方机构、论文或数据仓库作为结论依据；搜索使用公开主题词，没有上传私稿。部分记录核查到文件，部分只到schema/API，层级已注明。完整查询、待决项见[search-notes.md](C:/Users/szr/Desktop/record/1/literature-search-20261021-raven-datasets/search-notes.md)，与新方向的连接见[idea-grounding.md](C:/Users/szr/Desktop/record/1/literature-search-20261021-raven-datasets/idea-grounding.md)。
