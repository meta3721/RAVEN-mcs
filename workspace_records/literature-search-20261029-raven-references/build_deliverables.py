from pathlib import Path
import json,re,csv,collections,unicodedata

out=Path(__file__).parent
src=out/'sources'
papers=[]

def add(id,key,title,authors,venue,group,role,kind,insight,complete,numeric,observation,placement,boundary,evidence,quality,**bib):
 papers.append(dict(id=id,key=key,title=title,authors=authors,year=2025,venue_or_source=venue,group=group,role=role,paper_type=kind,insight_score=insight,completeness_score=complete,numeric_evidence_score=numeric,overall_label='A' if role=='优先纳入' else 'B',source_status='正式发表；原始来源/出版登记已核',supported_observation=observation,relevance_note=placement,boundary=boundary,link=evidence,quality_note=quality,bib=bib))

add('fast','li2025fast',
'FAST: A Lightweight Mechanism Unleashing Arbitrary Client Participation in Federated Learning',
'Li, Zhe and Nabavirazavi, Seyedsina and Ying, Bicheng and Iyengar, Sitharama and Yang, Haibo',
'IJCAI 2025','参与与优化','优先纳入','pure method',4,4,4,
'FAST 使用偶发 snapshot 机制支持大部分训练阶段的任意客户端参与，并分析非凸及强凸收敛。',
'Section II participation-aware FL：与 FedAU、相关参与去偏并列，说明参与不规则可通过聚合之外的训练机制处理。',
'它对 snapshot 轮有专门要求；没有证明本文 R/O/U 识别或硬约束下部署目标质量可达。',
'https://ijcai.org/proceedings/2025/628',
'已检查原文的收敛假设与 §5；Fashion-MNIST、CIFAR-10、Shakespeare，客户端参与和数据异质性实验。评分为检索阶段判断，未复现实验。',
type='inproceedings',booktitle='Proceedings of the Thirty-Fourth International Joint Conference on Artificial Intelligence',pages='5644--5652',doi='10.24963/ijcai.2025/628')

add('focus','ying2025focus',
'Exact and Linear Convergence for Federated Learning under Arbitrary Client Participation is Attainable',
'Ying, Bicheng and Li, Zhe and Yang, Haibo',
'NeurIPS 2025','参与与优化','优先纳入','theory/proof',4,4,3,
'FOCUS 用时变图与 push-pull 策略处理客户端参与和漂移，分析不同目标条件下的收敛。',
'Section II participation-aware FL：补足 2025 年优化理论进展，避免将“处理未知参与”写成本文独有贡献。',
'线性率有强凸或 PL 等条件；参与假设含正概率。不能引用为任意非凸、永久缺失支持下的无条件精确收敛。',
'https://proceedings.neurips.cc/paper_files/paper/2025/hash/395409679270591fd2a70abc694cf5a1-Abstract-Conference.html',
'已检查 Assumption 1、Theorem 1 与附录 G；CIFAR-10 上包含 FedAU、MIFA、SCAFFOLD 参照。理论证据强，任务范围有限。',
type='inproceedings',booktitle='Advances in Neural Information Processing Systems',volume='38',doi='10.52202/085713-1340')

add('phpfl','wu2025phpfl',
'A Fair Federated Learning Method for Handling Client Participation Probability Inconsistencies in Heterogeneous Environments',
'Wu, Siyuan and Jia, Yongzhe and Xiang, Haolong and Xu, Xiaolong and Zhang, Xuyun and Qi, Lianyong and Dou, Wanchun',
'NeurIPS 2025','参与与优化','优先纳入','pure method',4,4,4,
'PHP-FL 研究模型异质及参与概率不一致，通过双端对齐和重要性驱动参数更新改善准确率与客户端表现公平性。',
'Section II 参与偏差/公平性段：作为 2025 年直接相关工作，同时区分表现公平性与部署组质量对齐。',
'其模型异质、知识对齐、客户端准确率公平性与本文同骨干及质量组成目标不同，不能直接等同。',
'https://proceedings.neurips.cc/paper_files/paper/2025/hash/dcc0ac74ac8b95dc1939804acce0317d-Abstract-Conference.html',
'已检查 §5：Fashion-MNIST、CIFAR-10，三种参与模式、准确率/公平性指标及 DEAL/ISPU 消融。',
type='inproceedings',booktitle='Advances in Neural Information Processing Systems',volume='38',doi='10.52202/085713-5019')

add('masfl','yan2025momentum',
'Momentum-Driven Adaptivity: Towards Tuning-Free Asynchronous Federated Learning',
'Yan, Wenjing and Zhong, Xiangyu and Wang, Xiaolu and Zhang, Ying-Jun Angela',
'ICML 2025','异步与陈旧控制','优先纳入','pure method',4,4,4,
'MasFL 通过历史下降方向减轻异步陈旧累积；AdaMasFL 进一步引入自适应归一化，分析收敛与调参依赖。',
'Section II asynchronous/staleness-aware FL：更新异步优化背景，明确本文聚合质量校准与优化加速的研究边界。',
'它改变优化器和更新协议，不应未经适配和重训就当成本文现有实验的已比较基线。',
'https://proceedings.mlr.press/v267/yan25f.html',
'已检查原文实验：CIFAR-10、Fashion-MNIST，对照 CA2FL/FADAS，并评估异步程度和学习率条件。',
type='inproceedings',booktitle='Proceedings of the 42nd International Conference on Machine Learning',series='Proceedings of Machine Learning Research',volume='267',pages='70410--70441',publisher='PMLR')

r=json.loads((src/'defedavg.json').read_text(encoding='utf-8'))
add('defedavg','wang2025defedavg',r['title'][0],
'Wang, Xiaolu and Li, Zijian and Jin, Shi and Zhang, Jun',
'IEEE TMC 24(1), 2025','异步与陈旧控制','优先纳入','pure method',4,4,3,
'DeFedAvg 允许不同客户端基于陈旧全局模型异步本地训练，并分析异质客户端下的线性加速。',
'Section II 异步方法段：与 FedAsync、staleness control、MasFL 共同支撑异步优化现状。',
'原始预印本为 2024，正式 TMC 卷期为 2025；此处按正式版本计数，不能把两个版本当两篇。',
'https://doi.org/'+r['DOI'],
'正式元数据核至 24(1):435–448；原始作者预印本 HTML 已检查实验与 wall-clock 模型，含 Fashion-MNIST/CIFAR-10。未直接取得最终排版 PDF。',
type='article',journal='IEEE Transactions on Mobile Computing',volume='24',number='1',pages='435--448',doi=r['DOI'])

r=json.loads((src/'cafe.json').read_text(encoding='utf-8'))
add('cafe','min2025cafe',r['title'][0],
'Min, Sitao and Asif, Hafiz and Wang, Xinyue and Vaidya, Jaideep',
'IEEE TKDE 37(5), 2025','缺失机制与联邦补全','优先纳入','pure method',4,4,4,
'Cafe 根据客户端缺失机制的互补性与可观测样本量形成个性化聚合权重，研究异质缺失条件的联邦插补。',
'Section II 新增简短“联邦缺失数据处理”段：这是比泛泛 FL 背景更近的机制来源。',
'不能写“既有联邦插补不考虑缺失机制或聚合权重”；本文应强调部署目标、顺序选择校正及窗口可执行约束。',
'https://pmc.ncbi.nlm.nih.gov/articles/PMC12048026/',
'已检查原始作者稿的机制、MNAR 模拟、RMSE/分布距离/下游指标及五次随机重复；2026 PMC 开放时间不改变正式 2025 年份。',
type='article',journal='IEEE Transactions on Knowledge and Data Engineering',volume='37',number='5',pages='2266--2281',doi=r['DOI'])

r=json.loads((src/'darn.json').read_text(encoding='utf-8'))
add('darn','zhang2025darn',r['title'][0],
'Zhang, Yan and Liang, Shuwei and Miao, Xiaoye and Wu, Yangyang and Yin, Jianwei',
'PVLDB 18(10), 2025','缺失机制与联邦补全','优先纳入','pure method',4,4,4,
'DARN 直接对不完整表格进行联邦预测，利用缺失分布互补性和观测样本量确定个性化权重。',
'Section II 联邦缺失数据段，与 Cafe 并列；用于区分“补全后预测”和“直接不完整数据预测”。',
'它包含分类和回归，但不依赖先插补；不能写成纯插补方法，也不能把个性化缺失互补性等同于本文部署组目标。',
'https://www.vldb.org/pvldb/vol18/p3531-miao.pdf',
'已检查原文表 3–5 与实验设置：Bank/Higgs/Covertype/Gas，分类与回归、多缺失互补场景及消融。',
type='article',journal='Proceedings of the VLDB Endowment',volume='18',number='10',pages='3531--3544',doi=r['DOI'])

r=json.loads((src/'nonaligned.json').read_text(encoding='utf-8'))
add('nonaligned','liu2025nonaligned',r['title'][0],
'Liu, Wenbin and Du, Hao and Wang, En and Luan, Dongming and Yang, Bo and Yang, Yongjian and Wu, Jie',
'IEEE/ACM IWQoS 2025','稀疏移动群智补全','优先纳入','pure method',3,4,4,
'该文通过尺度对齐、双向处理及 ST-/Cross-Mamba 整合非对齐多尺度感知数据，用于稀疏 MCS 补全。',
'Section II Sparse MCS completion：补足 2025 多尺度与异构观测范围的进展。',
'文中的 alignment 是空间/尺度组成关系，不是本文部署目标质量对齐；评估为三类数据源、六个变量/子数据集。',
'https://cis.temple.edu/~jiewu/research/publications/Publication_files/iwqos2025-final14.pdf',
'已检查原文 §VI：空气质量 PM2.5/PM10、天气湿度/温度、TaxiBJ P1/P2，含不同尺度/采样率比较。',
type='inproceedings',booktitle='2025 IEEE/ACM 33rd International Symposium on Quality of Service (IWQoS)',pages='1--10',publisher='IEEE',doi=r['DOI'])

r=json.loads((src/'strucformer.json').read_text(encoding='utf-8'))
add('strucformer','kang2025strucformer',r['title'][0],
'Kang, Xu and Tian, Shouceng and Kou, Feifei and Shi, Lei and Ren, Jiadong',
'ICASSP 2025','稀疏移动群智补全','优先纳入','pure method',3,'待全文核准','待全文核准',
'StrucFormer 将低秩结构先验融入 Transformer 的嵌入、注意力和正则化，用于稀疏群智感知数据推断。',
'Section II Sparse MCS completion：代表结构先验与 Transformer 结合的 2025 方法，适合一句背景定位。',
'目前仅核到出版登记和出版商摘要；不引用未经查验的性能提升数字，不预先认定为可直接复现的强基线。',
'https://ieeexplore.ieee.org/abstract/document/10890429/authors',
'已核作者、正式会议、DOI、1–5 页与方法摘要；原文受访问限制，完整性与数字证据不强行打分。',
type='inproceedings',booktitle='ICASSP 2025 - 2025 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP)',pages='1--5',publisher='IEEE',doi=r['DOI'])

r=json.loads((src/'bias_survey.json').read_text(encoding='utf-8'))
add('bias_survey','benarba2025bias',r['title'][0],
'Benarba, Nawel and Bouchenak, Sara',
'ACM Computing Surveys 57(11), 2025','偏差概念与边界','优先纳入','survey',4,4,'N/A survey',
'该综述区分人口统计偏差、表现相关偏差与贡献相关偏差，并整理缓解方法及其保证。',
'Introduction 背景或 Section II 开头：支撑偏差分类，帮助避免把质量组成对齐泛称为所有形式的公平。',
'综述用于概念和文献覆盖；具体机制优先引原始论文。它不能证明本文的实验优势。',
'https://doi.org/10.1145/3735125',
'已核正式元数据和出版商可检索正文的分类/综述范围；综述不评方法数值效果，数字证据记 N/A survey。',
type='article',journal='ACM Computing Surveys',volume='57',number='11',pages='1--36',note='Article 291',doi=r['DOI'])

add('fedrenyi','ma2025fedrenyi',
'Federated R\u00e9nyi Fair Inference in Federated Heterogeneous System',
'Ma, Zhiyong and Shi, Yuanjie and Yan, Yan and Chen, Jian',
'UAI 2025','公平性边界','条件性备选','pure method',4,4,4,
'FedR\u00e9nyi 聚合本地公平性统计并近似缺失客户端更新，以研究异步、异质系统中的群体公平与准确率。',
'仅在正文明确讨论统计/预测群体公平时引用；可用于说明其与本文部署组成目标的差异。',
'公平性统计指标不等于部署质量差；不能用它替本文证明预测公平。若正文不讨论该边界，可不加入。',
'https://proceedings.mlr.press/v286/ma25a.html',
'已检查原文数值表：ADULT、COMPAS、DRUG、DUTCH，准确率、公平性及综合指标，含系统异质分析。',
type='inproceedings',booktitle='Proceedings of the Forty-first Conference on Uncertainty in Artificial Intelligence',series='Proceedings of Machine Learning Research',volume='286',pages='2804--2843',publisher='PMLR')

add('fedback','cummins2025fedback',
'Controlling Participation in Federated Learning with Feedback',
'Cummins, Michael and Er, Guner Dilsad and Muehlebach, Michael',
'L4DC 2025','控制与反馈边界','条件性备选','pure method',4,4,3,
'FedBack 用积分反馈控制每个客户端的参与率，基于 ADMM 联邦学习分析全局收敛。',
'仅在讨论参与控制/跨轮反馈与本文 debt 状态的关系时引用，适合 Related Work 的一句范围比较。',
'其动作是主动控制客户端参与；本文主要在既有可用集合上校准权重，不能把两类方法写成相同协议。',
'https://proceedings.mlr.press/v283/cummins25a.html',
'已检查原文 §5：MNIST/CIFAR-10、100 客户端和 ADMM/FedAvg/FedProx 参照；方法假设与本文不同。',
type='inproceedings',booktitle='Proceedings of the 7th Annual Learning for Dynamics and Control Conference',series='Proceedings of Machine Learning Research',volume='283',pages='174--186',publisher='PMLR')

def norm(s):return re.sub(r'[^a-z0-9]','',unicodedata.normalize('NFKD',s).lower())
old=json.loads(Path('C:/Users/szr/Desktop/record/1/tmp/citation_audit_20261028/bib_entries.json').read_text(encoding='utf-8'))
oldtitles={norm(x['title']) for x in old};olddois={x.get('doi','').lower() for x in old if x.get('doi')}
for p in papers:
 p['already_in_bib']=norm(p['title']) in oldtitles or p['bib'].get('doi','').lower() in olddois
 if p['already_in_bib']:raise ValueError('Unexpected existing bibliography entry: '+p['id'])
assert len(papers)==12 and sum(p['role']=='优先纳入' for p in papers)==10
(out/'papers.json').write_text(json.dumps(papers,ensure_ascii=False,indent=2),encoding='utf-8')
columns=['key','title','year','venue_or_source','link','role','group','paper_type','insight_score','completeness_score','numeric_evidence_score','overall_label','source_status','supported_observation','relevance_note','boundary','quality_note','already_in_bib']
with (out/'papers.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=columns);w.writeheader();w.writerows({k:p[k] for k in columns} for p in papers)

def bibtex(p):
 b=dict(p['bib']);typ=b.pop('type');fields=dict(title=p['title'],author=p['authors'],year=str(p['year']),**b,url=p['link'])
 # Protect method names and abbreviations from bibliography case folding.
 fields['title']='{'+fields['title']+'}'
 return '@'+typ+'{'+p['key']+',\n'+',\n'.join('  '+k+'={'+v+'}' for k,v in fields.items())+'\n}\n'
(out/'recommended_2025.bib').write_text('\n'.join(bibtex(p) for p in papers if p['role']=='优先纳入'),encoding='utf-8')
(out/'optional_2025.bib').write_text('\n'.join(bibtex(p) for p in papers if p['role']!='优先纳入'),encoding='utf-8')

lines=['# RAVEN-MCS 引用补充文献检索','',
'日期：2026-10-29。标准模式；目标是为现有论文补充真实、相关的 2025 文献，并检查近期机制进展。未修改论文、未恢复实验。','',
'## 可直接使用的结果','',
'筛选结果为 10 篇优先纳入的新增 2025 正式论文，以及 2 篇须有对应讨论才引用的备选。12 篇均与当前 54 条 reference.bib 按标题和已有 DOI 去重，未发现重复；标题、作者和正式发表信息已核至官方论文集、出版商登记或原始作者稿。','',
'上轮审计的已引用 2025 文献为 5 篇。若后续作者在正文中实质引用这 10 篇，且编译后的计数核准，2025 可达到 15 篇。此处只是候选包，不宣称论文已经达到该数量。2026 数量已经满足要求，无需更改首发/卷期年份凑数。','',
'交付：recommended_2025.bib（10 篇）、optional_2025.bib（2 篇）、papers.csv/json（来源、放置位置与边界）、insertion-plan.md（写作交接），sources/ 保存已获取的公开原文与注册元数据。','',
'## 分组与优先级','',
'- 参与与优化：FAST、FOCUS、PHP-FL。','- 异步与陈旧控制：MasFL/AdaMasFL、DeFedAvg。','- 缺失机制与联邦数据处理：Cafe、DARN。','- 稀疏移动群智补全：Non-Aligned Multi-Scale、StrucFormer。','- 偏差概念：Bias in Federated Learning 综述。','- 条件性备选：FedRényi（预测群体公平）、FedBack（主动参与控制）。','',
'## 每篇文献与引用边界','']
for i,p in enumerate(papers,1):
 lines += [f"### {i}. {p['title']}",'',f"- 正式来源：{p['venue_or_source']}；状态：{p['source_status']}。",f"- 原始/稳定链接：[{p['title']}]({p['link']})。",f"- 类型/优先级：{p['paper_type']}；{p['role']}。",f"- 原文支持的要点：{p['supported_observation']}",f"- 推荐位置（本次检索判断）：{p['relevance_note']}",f"- 引用边界：{p['boundary']}",f"- 初评 I/C/N：{p['insight_score']}/{p['completeness_score']}/{p['numeric_evidence_score']}。{p['quality_note']}",f"- BibTeX 键：`{p['key']}`。",'']
lines += ['## 与本文定位最有关的三点','',
'1. Cafe 与 DARN 表明“根据缺失机制/互补性确定联邦权重”已有直接工作。本文的差异应落在部署目标、原子感知单元上的 R/O/U 顺序选择以及当前窗口的硬可执行约束，不能仅声称“考虑非随机缺失并重新加权”。','2. FAST、FOCUS、PHP-FL 表明 2025 年处理任意/非均匀参与已有多种机制。本文宜区分参与优化、表现公平性与感知单位代表质量，而不笼统否定既有方法。','3. MasFL 与 DeFedAvg 处理异步优化和陈旧更新，不自动解决部署目标组成问题。本文可将两者写作互补技术。将其列为 Related Work 不等于已经完成相应实验比较。','',
'## 近期更新：不混入 2025 补额','',
'- [CoRe-Fed, AAAI 2026](https://ojs.aaai.org/index.php/AAAI/article/view/39628)：联合嵌入对齐与参与历史相关聚合，适合继续检查本文 debt/history 相关表述的边界。正式元数据为 40(29):24458–24466，DOI 10.1609/aaai.v40i29.39628。本轮核对到摘要和正式书目，未作完整方法评审。','- [Toward Efficient and Scalable Asynchronous Federated Learning via Stragglers Version Control, TMC 2026](https://cis.temple.edu/~jiewu/research/publications/Publication_files/Toward_Efficient_and_Scalable_Asynchronous_Federated_Learning_via_Stragglers_Version_Control.pdf)：DVAFL 通过版本控制处理慢客户端更新，正式 PDF 为 25(2):2627–2643，属于可补充的异步机制背景。DOI 10.1109/TMC.2025.3609568 中的 2025 不能取代正式卷期 2026。','- 上轮已核的 FedIPW 2026、FedPALS v2、SEAFL IPDPS 2025 和 FLOSS ACM 2025 仍应保留或更新，不重复算作新增文献。','',
'## 质量评分口径与未完成项','',
'I/C/N 分别为洞见、完整性、实验数字证据的检索阶段 1–5 初评；不是对论文录用概率的评分，也不表示复现成功。评分依据原始机制、可见证明和实验设计。综述的实验数字证据不适用。StrucFormer 只有元数据与摘要通过核验，完整性和数字证据保留待全文核准，不伪造评分。','',
'公开原文重点阅读：FAST、FOCUS、PHP-FL、MasFL、Cafe、DARN、Non-Aligned、FedRényi、FedBack；DeFedAvg 阅读 2024 作者预印本 HTML，并以出版商登记的 2025 TMC 信息生成正式条目。StrucFormer 和综述未获得本地完整排版 PDF。','',
'## 下一步写作交接','',
'建议由 ccf-paper-writer 按 insertion-plan.md 做局部整合，由 ccf-integrity-auditor 再核对实际引用、年份计数及语境。不因本次检索自动启动实验或宣称新基线收益。','',
'## 检索检查','',
'公开关键词检索、来源过滤、标题/DOI 去重、发表年份核验、类型标注、引用位置和机制边界已完成。无新数据集检索任务；无实验数值填入本文；无未发表材料对外搜索。个别原文不可直接访问已逐条标明。']
(out/'papers.md').write_text('\n'.join(lines),encoding='utf-8')

plan=['# 相关工作整合位置与边界','',
'本文件供后续写作使用，不表示已经编辑论文。对应的稿件是上轮审计的已编译版本；修改前需确认当前有效 TeX。','',
'1. Sparse MCS completion 段：加入 liu2025nonaligned、kang2025strucformer，分别对应非对齐多尺度整合、低秩结构先验。与既有 STEI/Rethinking/Pyramid/MapT-STC 按具体技术分句，避免堆成一长串引用。','2. 异步/陈旧控制段：加入 wang2025defedavg、yan2025momentum，说明它们聚焦收敛与效率；本文研究部署目标质量与有限窗口聚合权重。','3. 参与方法段：加入 li2025fast、ying2025focus、wu2025phpfl，分别对应 snapshot、push-pull 和参与概率不一致下的表现公平。现有 FedAU/Sun 2025/FLOSS 等仍按各自机制引用。','4. 在相关工作中增加一小段联邦不完整数据处理：加入 min2025cafe、zhang2025darn。先明确缺失机制/互补性加权已有基础，再解释本文顺序选择参考重建与约束窗口校准的范围。','5. Introduction 背景或 Related Work 起句加入 benarba2025bias，支撑偏差概念分类；一篇综述足够，不作为方法效果证据。','6. 仅当保留预测群体公平的讨论时加入 ma2025fedrenyi；仅当讨论参与控制和反馈时加入 cummins2025fedback。可选条目不承担补额任务。','',
'验收条件：','',
'- 10 篇优先项均有真实对应论断后，才计入 2025 目标；只写入 bib 不计数。','- 保留论文现有实验结论和已披露范围；文献报告的结果不得写成 RAVEN 自己的结果。','- 不将目标质量对齐与预测公平、尺度对齐或个性化补全混为一谈。','- 不把预印本、正式版本和修订版重复计数；年份由所引正式版本确定。','- 沿用独立方括号引用，不产生压缩区间；从实际 bbl/PDF 核验最终 2025 ≥15、2026 ≥5。','- 本轮只交付文献，不修改 reference.bib/main.tex，不自动启动数值实验。']
(out/'insertion-plan.md').write_text('\n'.join(plan),encoding='utf-8')

screen=[(p['title'],'保留：'+p['role']) for p in papers]
screen += [
('FedImpute: Personalized federated learning for data imputation with clusterer and auxiliary classifier','真实 ESWA 2025；未进优先包，Cafe/DARN 更接近缺失机制加权和更强定位需要。'),
('Indirect-Communication Federated Learning via Mobile Transporters','真实 TMC 2025；未进优先包，本文无 transporter 路由机制，关系较间接。'),
('CoRe-Fed: Bridging Collaborative and Representation Fairness via Federated Embedding Distillation','保留 2026 更新提示；不计入 2025。'),
('Toward Efficient and Scalable Asynchronous Federated Learning via Stragglers Version Control','保留 2026 更新提示；DOI 含 2025，不按 DOI 改年份。'),
('A New Data Completion Perspective on Sparse CrowdSensing: Spatiotemporal Evolutionary Inference Approach','已引用 2025，去重不新增。'),
('Rethinking the Effect of Sparse Data Completion on Sparse Mobile Crowdsensing Tasks','已引用 2025，去重不新增。'),
('Debiasing Federated Learning with Correlated Client Participation','已引用 2025，去重不新增。'),
('SEAFL: Enhancing Efficiency in Semi-Asynchronous Federated Learning through Adaptive Aggregation and Selective Training','已引用，更新为正式 IPDPS 2025 不增加去重数量。'),
('FLOSS: Federated Learning with Opt-Out and Straggler Support','已引用正式 2025，arXiv 2026 修订不新增。'),
('Who Trains Matters: Federated Learning under Enrollment and Participation Selection Biases','已引用 2026，不新增。'),
('Overcoming Label Shift with Target-Aware Federated Learning','已引用 2024/v2 2025，不能假定已录用或算独立新增。'),
('Federated Multiple Imputation for Variables that Are Missing Not At Random in Distributed Electronic Health Records','医学任务较远；PMC 标 2025 上网但会刊 2024，不能直接用于 2025 补额。'),
('FedHAN: A Cache-Based Semi-Asynchronous Federated Learning Framework Defending Against Poisoning Attacks in Heterogeneous Clients','安全攻击是主要任务，与当前论文范围偏离，未选。'),
('The Power of Bias: Optimizing Client Selection in Federated Learning With Heterogeneous Differential Privacy','主要约束来自隐私预算，本论文无此机制，未选。'),
('Federated causal discovery with missing data in a multicentric study on endometrial cancer','因果发现及医疗目标不同，未选。'),
('AFBS: buffer gradient selection in semi-asynchronous federated learning','与异步相关，但发表状态/正文机制未完整核验，未纳入已核候选。'),
]
assert len(screen)==28
notes=['# 检索记录','',
'目的：补充与既有 RAVEN-MCS 主张匹配的正式文献，优先填补 2025 年缺口；不是新实验设计或方法改写。','',
'## 使用的公开检索式','',
'- 2025 crowdsensing data completion / data inference','- federated learning biased client participation 2025 ICML ICLR NeurIPS','- asynchronous federated learning 2025 staleness / client heterogeneity','- federated missing not at random / missing complementarity / federated imputation','- FAST / FOCUS / PHP-FL / Momentum-Driven Adaptivity / DeFedAvg 公开题名','- Cafe / DARN / StrucFormer / Non-Aligned Multi-Scale 公开题名','- Bias in Federated Learning: A Comprehensive Survey','',
'## 来源与处理','',
'检索发现优先用论文题名与公开关键词；核验使用 NeurIPS/IJCAI/PMLR/PVLDB 官方论文集、IEEE/ACM 出版商、作者公开原文、PMC 作者稿和 Crossref 精确 DOI 登记。排除 MDPI、mdpi-res 及低质量/不相关来源；搜索命中这些域未进入推荐和评分。','',
'Crossref 原始元数据保存至 sources/*.json；公开原文保存八份 PDF 及其抽取文本。DeFedAvg PDF 下载因证书校验失败，没有关闭校验绕过，改读 arXiv 原始 HTML。StrucFormer 正文访问受限，未假定读过全文。','',
'## 集中筛选的 28 条记录','']
for title,status in screen:notes += ['- '+title+'：'+status]
notes += ['','## 未知与清理','',
'- StrucFormer 的完整数字证据和复现细节待原文；推荐范围限已核摘要。','- 综述有正式元数据与出版商可检索内容，未取得完整本地 PDF，不将它用于方法数值证明。','- 搜索曾将某篇材料邻近的 arXiv:2412.12837 与综述混在结果中；打开原始 arXiv 后发现是另一篇隐私攻击论文，已排除该链接映射，未写入候选 BibTeX。','- 部分模糊搜索或网页保护导致不可直接打开时，不据“无全文”判论文虚假；只记录实际核到的层级。','- 该检索未重跑任一实验，论文文件未编辑。','',
'## 写作交接','',
'以 insertion-plan.md 将每篇来源对应到具体语义位置；严格区分原文事实与本文差异判断。候选包中的对比属于文献机制比较，不表示完成其模型复现。']
(out/'search-notes.md').write_text('\n'.join(notes),encoding='utf-8')

canvas='''import {Stack,Row,Grid,H1,H2,Text,Table,Button,useState,useHostTheme} from "cursor/canvas";
const papers=__PAPERS__;
export default function Literature(){
 const theme=useHostTheme();const [filter,setFilter]=useState("优先纳入");
 const rows=papers.filter(p=>filter==="全部"||p.role===filter);
 return <Stack gap={20} style={{padding:24,background:theme.bg.editor,color:theme.text.primary}}>
 <H1>RAVEN-MCS · 2025 文献候选包</H1>
 <Text tone="secondary">2026-10-29 · 正式来源核验、标题/DOI 去重 · 28 条集中筛选</Text>
 <Grid columns={3} gap={24}>
 <Stack gap={4}><Text tone="secondary">优先新增</Text><H2>10 篇</H2><Text>2025 年正式发表</Text></Stack>
 <Stack gap={4}><Text tone="secondary">条件性备选</Text><H2>2 篇</H2><Text>公平统计 / 主动反馈控制</Text></Stack>
 <Stack gap={4}><Text tone="secondary">整合后可能计数</Text><H2>5 + 10 = 15</H2><Text>须实际引用并重编译核准</Text></Stack>
 </Grid>
 <div style={{padding:14,background:theme.fill.tertiary}}><Text weight="semibold">最值得补入的机制背景</Text><Text>Cafe 与 DARN 已利用缺失机制或互补性确定个性化聚合权重。RAVEN 的定位应明确部署目标、顺序选择与有限窗口可执行约束。加入文献不表示已经完成这些方法的实验比较。</Text></div>
 <H2>按引用目的查看</H2>
 <Row gap={8} wrap>{["优先纳入","条件性备选","全部"].map(x=><Button key={x} onClick={()=>setFilter(x)}>{x}{filter===x?' · 当前':''}</Button>)}</Row>
 {rows.length>0&&<Table headers={["论文 / 来源","分组与状态","原文支持要点","建议位置 / 边界"]} rows={rows.map(p=>[
 <Stack key={p.id} gap={4}><a href={p.link} target="_blank" rel="noreferrer" style={{color:theme.text.link}}>{p.title}</a><Text size="small">{p.venue_or_source}</Text></Stack>,
 <Stack key={p.id+'group'} gap={4}><Text>{p.group}</Text><Text size="small" tone="secondary">{p.role} · 正式发表</Text></Stack>,
 p.supported_observation,
 <Stack key={p.id+'note'} gap={4}><Text size="small">{p.relevance_note}</Text><Text size="small" tone="secondary">{p.boundary}</Text></Stack>
 ])} striped/>}
 <H2>使用条件</H2>
 <Text>10 篇优先项与旧 reference.bib 没有重复。StrucFormer 的元数据与摘要已核，完整性和实验数字仍待全文核准。所有推荐都须绑定具体论断；综述用于概念，不能代替原始机制证据。</Text>
 <Text tone="tertiary" size="small">来源：官方会议论文集、出版商登记、作者公开原文和 PMC。实验保持暂停；论文尚未被本次检索修改。完整评分、书目与候选边界见同目录 papers.md / papers.csv / recommended_2025.bib。</Text>
 </Stack>;
}
'''.replace('__PAPERS__',json.dumps(papers,ensure_ascii=False))
(out/'raven-literature-2025.canvas.tsx').write_text(canvas,encoding='utf-8')
print('Wrote',len(papers),'papers; main',sum(p['role']=='优先纳入' for p in papers),'duplicates',sum(p['already_in_bib'] for p in papers))
