# CITATION_REPAIR_AND_UPDATE_REPORT

日期：2026-10-29。执行入口：用户指定的 citation-repair-and-update-instructions.md。使用 ccf-paper-writer 做局部写作修订、ccf-humanization 检查公开表述、ccf-integrity-auditor 核对引用语境与元数据。实验保持暂停。

## 交付结论

- 已恢复与原PDF相对应的有效稿源，实际修改规范 main.tex、reference.bib，并通过 LaTeX→BibTeX→LaTeX 的顺序构建更新两份PDF及bbl/aux。
- 正文 **14页**，补充材料 **14页**；修改前也分别为14页。没有改变字号、模板、页边距或行距。
- 正文实际引用 **46** 个不同来源：**2025年15篇，全部正式发表；2026年7篇，其中正式发表6篇、预印本1篇**。两项数量要求通过。
- 六个指定条目均已处理；Hájek原始章节的完整页码仍未直接核准。NSW原书目“2024”没有发布依据，已移除，改用有记录的资源下载身份。未宣称所有历史书目细节均已闭合。
- 摘要、引言、贡献、方法、公式、理论、实验和结论保持恢复基线原文；新增讨论限于 Related Work。正文这一区域外逐字比对一致，appendix.tex、supplemental.tex与恢复基线按字节一致。没有训练、推理、评分、统计重算或实验方法改名。

规范交付：[正文PDF](<C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.pdf>)；[补充PDF](<C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/supplemental.pdf>)；[正文源码](<C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex>)；[统一书目](<C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/reference.bib>)。

## 1. 有效稿源、备份与恢复

开始检查时main.tex、appendix.tex、supplemental.tex均为0字节，现存两份PDF均为14页。先原样备份异常源码、PDF、书目和编译记录，未用Git HEAD或较早整篇稿覆盖当前版本。

完整来源为2026-10-26数据图修订前的备份，加该轮最终逐行差异：

- [完整备份](<C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/figures/_backup/data_figures_before_revision_20261026_221941>)。
- [该轮最终差异](<C:/Cursor/raven.mcs/ccf-review-report/DATA_FIGURES_REVISION_DIFF.md>)。
- 按差异的每个上下文/删除行校验后重建main.tex、appendix.tex；supplemental.tex沿用该轮未修改的备份。重建的make_figures.py与当前实际脚本完全一致，作为版本核对依据；未改写绘图脚本。
- 在引用修订前重新编译，正文14页及补充14页的逐页抽取文本，**28页全部与保存的原PDF完全一致**。这是文本与版本对应核验，不是PDF二进制字节相同的声明。记录见 [恢复核验](<C:/Cursor/raven.mcs/tmp/citation_repair_20261029/recovery_pdf_comparison.json>)。

本轮备份：[citation_repair_20261029_090941](<C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/revision_backups/citation_repair_20261029_090941>)。根层main.tex等保留原0字节状态；`recovered_baseline/`保存核定恢复后的三份完整TeX；原reference.bib、main.pdf、supplemental.pdf位于备份根层。已有图一及数据图备份全部保留。

回退时：没有后续修改可使用recovered_baseline中的完整TeX及根层原reference.bib/PDF恢复引用修订前状态；**不要恢复根层0字节TeX**。如已发生后续编辑，仅合并还原Related Work和本轮书目字段，依据备份内citation_revision.diff操作，随后重建正文和补充。不要整份覆盖后来修改过的main.tex。没有更改Git索引或提交用户已有改动。

## 2. 六项指定修复与两项待核细节

1. [wang2024fewshot](<C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/reference.bib:266>)：作者字段第四位从`Yang, Xu`改为`Xu, Yang`，PDF由Y. Yang改为Y. Xu；加入DOI `10.1109/INFOCOM52122.2024.10621156`。保留INFOCOM 2024、1831–1840等已核字段。依据：[INFOCOM官方日程](https://infocom.info/infocom24/day/3)中Yang Xu及原审计的精确DOI记录。
2. [xie2019asynchronous](<C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/reference.bib:333>)：保留旧键，采用OPT 2020 workshop身份；year从2019改为2020，去掉混在正式会议信息后的2019预印本标记，加入[OPT官方论文清单](https://opt-ml.org/oldopt/opt20/papers.html)。未虚构页码或DOI。FedAsync实验身份未变。
3. [islam2025seafl](<C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/reference.bib:547>)：`@misc`/arXiv改为IPDPS 2025正式`@inproceedings`；509–519；DOI `10.1109/IPDPS64566.2025.00052`；六位作者全部录入。依据：[作者机构公开发表清单](https://faculty.ecnu.edu.cn/_s16/xf2/main.psp)及[正式DOI](https://doi.org/10.1109/IPDPS64566.2025.00052)。只计一篇2025论文。
4. [wang2024lightweight](<C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/reference.bib:142>)：保留ICLR 2024作者、题名、年份和官方原文URL，删除854–893页码；未用29653猜测终页。正文及补充由同一bib重建。来源：[ICLR正式论文页](https://proceedings.iclr.cc/paper_files/paper/2024/hash/03a9a9c1e15850439653bb971a4ad4b3-Abstract-Conference.html)。
5. [sun2025debiasing](<C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/reference.bib:123>)：保留ICLR 2025作者、题名、年份和原文URL，删除28564–28595页码；未用16492猜测终页。来源：[ICLR正式论文页](https://proceedings.iclr.cc/paper_files/paper/2025/hash/464917b6103e074e1f9df7a2bf3bf6ba-Abstract-Conference.html)。
6. [chen2026fedcure](<C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/reference.bib:373>)：Shuqing Cao→Shuqin Cao、Dawei Wang→Wei Wang；加入DOI `10.1609/aaai.v40i25.39176`及官方URL；保留40(25):20418–20426、2026。依据：[AAAI正式记录](https://ojs.aaai.org/index.php/AAAI/article/view/39176)。

**ICLR导出冲突的实际发现：**本轮下载的两份官方BibTeX本身仍携带上述争议页码，不能把“官方导出”直接等同于页码已核准。保存原始导出fedau_official.bib、debiasing_official.bib，采用其可核身份字段并按本次明确指令省略争议页码、导出中的年份型volume与编者；未声称完整照抄了官方导出。未关闭TLS校验；部分出版商或馆藏访问403/证书链失败时转用已核公开记录，未据此补造字段。

**Hájek：**[hajek1971comment](<C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/reference.bib:414>)保留。新核到[CiNii馆藏记录](https://ci.nii.ac.jp/ncid/BA8882938X)，确认1971、Godambe/Sprott、Holt/Rinehart/Winston、Toronto等书籍身份；仍未得到原始评论章节。多份研究文献只引p.236，原审计另有236–242引证，不能据此闭合终页。本轮遵照指令保留已有236–242，不猜改，不计为“原章页码核验通过”。后续需要该书相应扫描页或完整目录/章节记录。

**NSW：**[tfnsw2024traffic](<C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/reference.bib:455>)去掉无依据的year=2024，保持为未注明发布年份的数据资源；不把2026下载时间当发布年份。采用实际资源所属数据集UUID入口，并写明snapshot downloaded Jul.31,2026。原书目Aug.14访问日期未发现独立日志，故不继续把它当作实际采集时间；未以当前网页更新时间替换版本。

实际身份来自 [traffic原始下载记录](<C:/Cursor/raven.mcs/data/raw/traffic/provenance.json>)、[traffic manifest](<C:/Cursor/raven.mcs/data/manifests/traffic_manifest.json>)、[配置](<C:/Cursor/raven.mcs/configs/dataset/traffic.yaml>)：

- 数据集UUID `ef2b0bd2-db1e-48f3-9ea1-2bb9e6bc6504`。
- `road_traffic_counts_station_reference.csv`：资源ID `c65ad7b4-0257-4cc6-953e-5299ac8d27ba`；2026-07-31 02:51:00 UTC下载，774192字节，HTTP 200。
- `road_traffic_counts_hourly_permanent.zip`：资源ID `bca06c7e-30be-4a90-bc8b-c67428c0823a`；2026-07-31 02:51:05 UTC下载，865087746字节，HTTP 200。
- manifest记录创建于2026-07-31；未重新下载或遍历大体积ZIP。发布年份和出版商版本号仍未知，论文不再声称“2024版”。

其他规范化：Kairouz条目按作者公开原文补齐59位作者，SEAFL补齐6位，整个bib不再有手填`and others`；是否以et al.显示由IEEEtran决定。按标准简称统一期刊/会议名称，去掉与PMLR出版者及卷号重复的系列全称。正式新增条目保留DOI；无DOI的PMLR论文保留原文URL，不重复展开可由DOI定位的长网址；全部公开原文位置见下节。City Scanner的524由页码格式改为Art.no.524，保持数据标识和许可不变。没有猜测缺失字段。

## 3. 原句/旧引用到新句/新引用的逐项对应

原句和完整差异均保存在备份内citation_revision.diff；下列位置均指最终规范源码。替换以论断为单位，不做全局键替换，未从bib删除旧条目。

- 原“Sparse MCS completion infers missing spatiotemporal values…”的通用引文`guo2015mobile`、`ma2014opportunities`：移除该处重复背景；引言的Ganti奠基引用保留。改为 [main.tex:197](<C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:197>) 起的近期具体机制，不用Cafe/DARN替代MCS概念出处。
- 原同一句中的`wang2023spatiotemporal`：不再用泛化“spatiotemporal”串引铺陈研究现状；[main.tex:200](<C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:200>) 用`liu2025nonaligned`、`liu2026pyramid`明确讨论尺度整合。不是把相关性建模称为部署质量对齐。
- 原同一句中的`wang2023outlier`：删除背景中的重复条目；引言的`li2024robust`仍支撑稳健稀疏感知背景。没有改动实验模型或对应结果。
- 原同一句中的`wang2023transformer`：由 [main.tex:201](<C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:201>) 的`kang2025strucformer`具体说明低秩先验与Transformer组合；不移植其未经全文核准的性能结论。
- 原“Federated completion keeps records … asynchronous …”中的`yang2019federated`、`kairouz2021advances`、`li2020federated`：移除重复泛述；FedAvg定义出处和`wang2026federated`保留。[main.tex:212](<C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:212>) 用`benarba2025bias`支撑偏差分类，其余机制各引原论文。
- 原异步串引中的`liu2023adaptive`：不再作为整个异步现状的额外泛引；[main.tex:205](<C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:205>) 保留FedAsync、TimeAlign所据staleness来源、SEAFL和STDFL，随后用DeFedAvg、MasFL/AdaMasFL分别说明异构异步分析与历史动量。没有替换实验基线旁的出处。
- 原“Participation-aware FL … convergence analysis, update-memory correction, and sampling”中的`jhunjhunwala2022fedvarp`、`wu2023anchor`：移除该背景目录式枚举；当前稿没有二者的实验方法行或作为定理前提的调用。保留原参与分析`wang2022unified`，在 [main.tex:219](<C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:219>) 起分别引FAST、FOCUS和PHP-FL说明新机制。没有把FedAU-Window改成新方法。
- 原FedAU/相关参与方法句：FedAU、Sun2025、FedCure、FLOSS全部保留；新句补充具体近期机制及其条件。
- 新增 [main.tex:225](<C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:225>) 的Cafe/DARN相邻讨论：前者个性化插补，后者直接预测；明确缺失机制加权已有基础，没有声称RAVEN首次使用这些工具。
- 原FedIPW/FedPALS比较：保留入组/参与分解、有限信息人口校准、凸目标标签匹配、凸包外目标与样本ESS的已有能力；局部压缩重复的RAVEN说明，保留原子R/O/U参考到硬约束窗口聚合的差异。IPW/Hájek、协变量偏移、缺失识别、Byrd的引用保持实质用途。

既有五篇2025与七篇2026实际引用全部保留。数据来源、Wilcoxon/Holm、FedAvg/FedAsync/FedAU/TimeAlign及最近邻FedIPW/FedPALS仍在其实际语境中。摘要、引言及结论未发现需要本轮改写的排他性主张，故不改。

## 4. 十篇新增来源及实际用途

以下均为2025正式发表版本，每篇只计一次；公开资料与本地证据包互相对应。来源包：[literature-search-20261029-raven-references](<C:/Users/szr/Desktop/record/1/literature-search-20261029-raven-references>)；papers.json、papers.csv均读取12条记录，REFERENCE_LEDGER读取47条历史记录。

- **liu2025nonaligned**：[main.tex:201](<C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:201>)；[liu2025nonaligned](<C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/reference.bib:649>)。整合非对齐多尺度观测；只说明空间尺度/组成关系的处理，不等同于部署质量对齐。 正式信息：IEEE/ACM IWQoS 2025, 1–10, 10.1109/IWQoS65803.2025.11143411。来源：[公开原文/出版记录](https://cis.temple.edu/~jiewu/research/publications/Publication_files/iwqos2025-final14.pdf)；本地` sources/nonaligned.pdf、nonaligned.txt、nonaligned.json；原文摘要与方法`。

- **kang2025strucformer**：[main.tex:202](<C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:202>)；[kang2025strucformer](<C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/reference.bib:659>)。低秩结构先验与Transformer结合；仅写摘要可核的方法概述，无性能数字。 正式信息：ICASSP 2025, 1–5, 10.1109/ICASSP49660.2025.10890429。来源：[公开原文/出版记录](https://ieeexplore.ieee.org/abstract/document/10890429/authors)；本地` sources/strucformer.json及已核摘要；全文未取得`。

- **wang2025defedavg**：[main.tex:208](<C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:208>)；[wang2025defedavg](<C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/reference.bib:616>)。异构客户端的异步训练分析，不作为已复现的新实验基线。 正式信息：IEEE TMC 24(1):435–448 (2025), 10.1109/TMC.2024.3461852。来源：[公开原文/出版记录](https://doi.org/10.1109/TMC.2024.3461852)；本地` sources/defedavg.json、既有公开原文核验记录；按正式卷期2025而非DOI中的2024计年`。

- **yan2025momentum**：[main.tex:210](<C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:210>)；[yan2025momentum](<C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/reference.bib:605>)。MasFL历史动量缓解陈旧累积，AdaMasFL增加自适应梯度归一化。 正式信息：ICML 2025, PMLR 267:70410–70441。来源：[公开原文/出版记录](https://proceedings.mlr.press/v267/yan25f.html)；本地` sources/masfl.pdf、masfl.txt；摘要及历史下降方向机制`。

- **li2025fast**：[main.tex:220](<C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:220>)；[li2025fast](<C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/reference.bib:578>)。snapshot之间允许任意参与，snapshot要求客户端均匀参与；不写成无条件任意参与保证。 正式信息：IJCAI 2025, 5644–5652, 10.24963/ijcai.2025/628。来源：[公开原文/出版记录](https://ijcai.org/proceedings/2025/628)；本地` sources/fast.pdf、fast.txt；原文明示snapshot阶段fully random/uniform participation`。

- **ying2025focus**：[main.tex:222](<C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:222>)；[ying2025focus](<C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/reference.bib:587>)。时变图与push–pull；线性率限强凸或Polyak–Łojasiewicz及正参与概率条件。 正式信息：NeurIPS 38 (2025), 10.52202/085713-1340。来源：[公开原文/出版记录](https://proceedings.neurips.cc/paper_files/paper/2025/hash/395409679270591fd2a70abc694cf5a1-Abstract-Conference.html)；本地` sources/focus.pdf、focus.txt；Assumption 1及强凸/PL收敛分析`。

- **wu2025phpfl**：[main.tex:223](<C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:223>)；[wu2025phpfl](<C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/reference.bib:596>)。不等参与概率与模型异质下的预测表现公平，不等同部署组组成对齐。 正式信息：NeurIPS 38 (2025), 10.52202/085713-5019。来源：[公开原文/出版记录](https://proceedings.neurips.cc/paper_files/paper/2025/hash/dcc0ac74ac8b95dc1939804acce0317d-Abstract-Conference.html)；本地` sources/phpfl.pdf、phpfl.txt；摘要及其模型异质/参与机制`。

- **min2025cafe**：[main.tex:226](<C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:226>)；[min2025cafe](<C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/reference.bib:627>)。缺失互补性和观测样本量用于个性化联邦插补聚合。 正式信息：IEEE TKDE 37(5):2266–2281 (2025), 10.1109/TKDE.2025.3537403。来源：[公开原文/出版记录](https://pmc.ncbi.nlm.nih.gov/articles/PMC12048026/)；本地` sources/cafe.json及公开作者稿；不按PMC于2026开放的时间改出版年`。

- **zhang2025darn**：[main.tex:227](<C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:227>)；[zhang2025darn](<C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/reference.bib:638>)。缺失互补性和观测量服务直接不完整表格预测，不称纯插补方法。 正式信息：PVLDB 18(10):3531–3544 (2025), 10.14778/3748191.3748213。来源：[公开原文/出版记录](https://www.vldb.org/pvldb/vol18/p3531-miao.pdf)；本地` sources/darn.pdf、darn.txt、darn.json；原文3531页摘要明确without relying on imputed values`。

- **benarba2025bias**：[main.tex:213](<C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:213>)；[benarba2025bias](<C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/reference.bib:669>)。人口、表现与贡献相关偏差的分类，仅用作综述背景。 正式信息：ACM CS 57(11), Art.291, 1–36 (2025), 10.1145/3735125。来源：[公开原文/出版记录](https://doi.org/10.1145/3735125)；本地` sources/bias_survey.json的出版商登记摘要和正式元数据；不作为方法数值证明`。

两篇备选FedRényi、FedBack未加入：本轮无需扩展预测公平或主动参与控制主线，十篇优先来源已各自有实质用途且满足数量要求。没有引用以凑数，也没有将其列为已比较SOTA。

## 5. 实际引用计数与去重

计数由规范TeX的cite键、各自aux的citation键、最终bbl条目三方集合一致后取得，并核对PDF书目编号完整；不是统计整个bib或正文中的引用出现次数。

- **正文：46个来源**。1945: 1（1正式发表）；1952: 1（1正式发表）；1971: 1（1正式发表）；1979: 1（1正式发表）；1994: 1（1正式发表）；2000: 1（1正式发表）；2010: 2（2正式发表）；2011: 1（1正式发表）；2013: 1（1正式发表）；2017: 1（1正式发表）；2019: 2（1数据资源、1正式发表）；2020: 1（1正式发表）；2022: 1（1正式发表）；2023: 3（3正式发表）；2024: 5（4正式发表、1预印本）；2025: 15（15正式发表）；2026: 7（6正式发表、1预印本）；undated: 1（1数据资源）。
- **补充：5个来源**。2023: 1（1正式发表）；2024: 2（1预印本、1正式发表）；2026: 2（1预印本、1正式发表）。
- **去重并集：46个来源**。1945: 1（1正式发表）；1952: 1（1正式发表）；1971: 1（1正式发表）；1979: 1（1正式发表）；1994: 1（1正式发表）；2000: 1（1正式发表）；2010: 2（2正式发表）；2011: 1（1正式发表）；2013: 1（1正式发表）；2017: 1（1正式发表）；2019: 2（1数据资源、1正式发表）；2020: 1（1正式发表）；2022: 1（1正式发表）；2023: 3（3正式发表）；2024: 5（4正式发表、1预印本）；2025: 15（15正式发表）；2026: 7（6正式发表、1预印本）；undated: 1（1数据资源）。

- 修改前正文47个：2025=5、2026=7；补充5个：2025=0、2026=2；并集47个。修改后移除11个仅背景用途的旧引用，新增10篇，47−11+10=46；旧bib条目保留。
- 全bib为64条，其中18条未进入正文/补充；不计入达标数量。2025正式15篇均有正文定位；2026按正式论文单计也有6篇，仍满足至少5篇。
- 两篇预印本分别为FedPALS（首发2024，2025修订不重计）与FedIPW（2026）。SEAFL正式版替换原预印本，不重复计数。NSW不再借访问/下载年计入任何论文年份。

## 6. 编译、版式与一致性验收

- 工具链：项目现有MiKTeX pdflatex / BibTeX / IEEEtran，禁用自动安装与shell escape；Python调度串行、低优先级，数值库线程设1。未加载模型或调用实验入口。
- 最后一轮8次顺序工具调用均退出0：正文、补充各一次LaTeX、一次BibTeX，再各两次LaTeX；两个aux均稳定。两份PDF均14页。
- 两份BibTeX日志warning计数均0；无未定义引用/交叉引用、无重复标签提示、无Overfull。仍有模板既有epstopdf“shell escape未开启”提醒；当前使用的PDF/PNG资源无需该转换，不影响构建成功，未打开shell escape。
- 目视阅读正文第2、3页的相关工作和逐个方括号，第13、14页的正文/书目过渡及完整书目，补充第14页的书目：未见裁切、重叠、缺字或超宽网址。贡献编号、图一和原图注保留。
- 两份源码均保留`\usepackage[nocompress]{cite}`；生成PDF抽取文本未检出`[n]–[m]`形式的引用区间，目视也保持逐个方括号。数学、页码及年份区间没有全局替换。
- 所有新增引用均解析；无重复DOI、重复规范化题名、重复键或手填and others。本文的实际实验基线没有被改名或替换为新文献方法。
- Related Work近似英文词数（去cite/label/ref命令、按字母词及内部连字符计）**282→235，减少47词**；引用扩展和信息重组未改实验数字。正文/补充页数净变化0。
- humanization：用具体机制取代长串引文；减少重复的“本文不做……”式收尾。FAST采样、FOCUS强凸/PL/参与条件，以及规模对齐、表现公平、部署质量的区别保留；未增加优先性或效果主张。

结构化复核、构建日志及完整差异保存在本轮备份和tmp/citation_repair_20261029。主要记录：FINAL_CITATION_AUDIT.json、recovery_pdf_comparison.json、citation_build_records.json、citation_revision.diff。这些是修订核验记录，不是新增实验结果。

## 7. 仍未解决的事项

1. Hájek原评论的题名细节及236–242完整范围仍需原章扫描或可靠逐章目录。馆藏只闭合书籍身份；不能据二手一致引证认定终页已验证。
2. NSW原始发布年份/出版商版本号未知。已去掉未经核准2024；目前可追溯的是实际2026-07-31资源快照，未据此声称数据于2026发布。
3. StrucFormer只采用已核摘要概述，未取得全文；本轮没有为它加入性能或复现结论。
4. 两条ICLR印刷页码与官方导出冲突仍未解析到完整印刷范围；规范书目省略页码，保留出版身份及原文入口，避免错误范围继续流入两份PDF。

本轮实现与编译已经完成；上述元数据边界不阻断已核引用的整合，也不构成恢复实验的授权。
