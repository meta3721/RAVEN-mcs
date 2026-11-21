# RAVEN-MCS创新与证据审查

日期：2026-10-15。技能：ccf-paper-reviewer。模式：scientific + writing，聚焦创新定位与证据承接；不改写正文，不运行实验。

## 结论

有清楚的建模与组合式贡献，但当前尚未形成足够突出的独立算法或理论突破；按CCF A类方法论文定位需要实质性修改。

创新不是空白，最有辨识度的中心是：在感知单元层面重建部署目标参考，并将其与当前有限窗口真正可实现的客户端混合分开处理。当前方法主要是既有统计与凸优化工具在MCS选择机制下的组合和具体化；独立理论及完整算法的必要性证据偏弱。写作可以让贡献更清楚，但不能单独补齐这个差距。

按当前证据，更有说服力的两条主线是“选择纠偏参考的可行投影”与“对齐结构和预测收益为何分离的机制研究”。这两者可以相互支持，但不可让负结果被包装成没有被证明的普遍不可能性结论。

## 范围、总体立场与置信度

- 评审稿：[main.pdf](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.pdf)，18页；[supplemental.pdf](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/supplemental.pdf)，16页；源码main.tex/appendix.tex/supplemental.tex。沿用上一轮全文阅读，并重新细读摘要、引言、相关工作、方法、主要理论与所有核心实验段落。
- 对照：[已有实验利用审计](C:/Users/szr/Desktop/record/1/paper-evidence-audit-20261015/UNUSED_AND_UNDERUSED_EXPERIMENTS.md)。未把晚于PDF编译的新协议或OF分支视为当前稿已验证方法。
- 目标：沿用用户此前CCF A类期刊目标与TMC研究语境，仅判断创新及其展示；未核对当前期刊政策，也不评投稿格式。
- 总体立场：实质性修改。不是接收概率，不是与历史评分的升降比较，也不是完整匿名审稿分数。
- 置信度：本稿定位与证据判断较高；全球独创性判断中等，仅定向核验最近邻，不声称穷尽先行工作。

## 创新究竟在哪里

### N1 感知单元层面的部署目标与到达分布区分

**判断：问题建模贡献成立；一般统计原理不新。**

机制：用原子时空单元的公开目标，区分机会R、观测O、可用更新U诱导的到达分布；区分部署组h与机会分层s。

已有支撑：命题1、NSW-Traffic风险差分、真实出租车机会失衡提供支持。两种评分改变幅度不同，但现有验证重评分在两个主数据集全部20种子选择相同配置。

尚欠缺：命题1是不同概率测度的一般性质；“部署目标不等于训练总体”已有目标感知FL先例。尚未证明该语义区分改善了决策或预测。

建议定位：保留为问题与估计对象贡献；突出感知单元、可观察历史和注册失败记录的区别，降低“风险不等价定理”作为主要理论突破的权重。

依据：[证据1](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:1153)；[证据2](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:1633)；[证据3](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:2199)；[证据4](https://arxiv.org/html/2411.03799v2)。

### N2 分层选择纠偏后的参考质量重建

**判断：场景化、组合式方法贡献；不是全新IPW估计原理。**

机制：机会目标比、观测逆概率与可用更新逆概率在各自信息边界下组合，客户端Hájek归一化与服务器质量归一化衔接。

已有支撑：命题2在A1–A3下恢复理想总体矩或群体质量；SensorScope的Design对照有正结构贡献。

尚欠缺：乘积逆概率和归一化是已知工具；主实验局部Hájek权重实际均匀，Use消融不显著。理想总体估计器并不自动等同多步陈旧模型更新的目标风险优化。

建议定位：说明三层分别可记录和估计所带来的操作能力；将未纠正/只纠正U/纠正O+U/完整纠正放在同一可行域和公开目标下理解，明确当前哪几层已被实证识别。

依据：[证据1](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:646)；[证据2](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:696)；[证据3](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:791)；[证据4](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:1182)；[证据5](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:2060)；[证据6](https://arxiv.org/html/2604.26604v1)。

### N3 将统计参考映射到有限窗口可行混合

**判断：最值得保留的核心机制；与已有目标校准重叠明显。**

机制：在当前活跃客户端的单纯形、单客户端上限和ESS约束中，对纠正参考作投影或带参考锚的校准；参考质量与可实现组成是两个对象。

已有支撑：实际训练规则比较中，SensorScope投影相对Uniform改善0.768 pp；原始纠正参考可能违反约束。多数小K窗口退化为Uniform，直接揭示可行域约束的作用。

尚欠缺：FedPALS已研究目标凸包、匹配与ESS；完整P2在SensorScope结构指标比简单投影差0.118 pp、耗时约27.1秒对18.5–20.0秒。额外目标项未显示主要价值。

建议定位：明确独立贡献来自何种时间可行域、选择纠正参考和信息限制；主文加入Uniform、原始参考和投影规则，公平展示完整P2与简单规则的关系。

依据：[证据1](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:860)；[证据2](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:931)；[证据3](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:1810)；[证据4](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:2080)；[证据5](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:2155)；[证据6](https://arxiv.org/html/2411.03799v2)。

### N4 跨窗口目标债务与长期对齐

**判断：机制定义完整；主要创新地位尚缺证据。**

机制：将本窗口未满足的群体服务质量积累为非负债务，后续聚合优先偿还。

已有支撑：有确定性记账界；默认配置Debt的结构贡献极小，去除后的相对变化约0.002%–0.014%。单独κ=1000投影加债务变体显示更大结构移动。

尚欠缺：记账界只有在债务相对有效步长质量次线性时才推出长期对齐；没有从所给算法与机会条件导出该次线性。κ=1000是不同规则，不能代表冻结RAVEN。

建议定位：默认稿将其定位为长期状态机制及条件性界；若升为主创新，需要可达性条件下债务控制的专门理论和独立收益证据。

依据：[证据1](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:904)；[证据2](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:2070)；[证据3](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:2089)；[证据4](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex:932)。

### N5 可行域、参考纠偏与预测收益的机制归因

**判断：当前最有辨识度的实证认识；需严格限定范围。**

机制：使用共同标尺，把计数权重到Uniform、Uniform到投影参考、Design开关及其他目标项分开，解释结构与预测为何分离。

已有支撑：FedAvg到RAVEN的组差距中，Uniform已解释SensorScope 68.96%、U-Air 83.07%；投影贡献0.768/0.286 pp；主表没有稳定预测领先，且部分Design设置有代价。

尚欠缺：不是算法模块；大部分实验尚不支持从质量对齐到学习收益的桥梁。oracle已评估配置的小收益不等于整个可行权重类的严格上界。

建议定位：把它写成带条件的研究发现；补充现有目标集中度、学习能力和几何结果，保留负结果，避免把未检测到效果写成效果不可能。

依据：[证据1](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:1803)；[证据2](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:2105)；[证据3](C:/Users/szr/Desktop/record/1/paper-evidence-audit-20261015/UNUSED_AND_UNDERUSED_EXPERIMENTS.md)。

### N6 稳定区间中的聚合覆盖诊断

**判断：辅助诊断贡献；不宜与主聚合算法并列为决定性创新。**

机制：用历史分数构造聚合覆盖下界，Gate单独记录；Design在窗口前配置，两者职责分开。

已有支撑：稳定区间交换性假设下有秩分位数覆盖保证；压力审计合并覆盖0.959，但U-Air a=1.00为0.750。

尚欠缺：核心覆盖技术属于标准分位数校准；CERTIFIED操作状态不证明交换性，Gate不驱动当前聚合决策。不能据此声称对任意漂移可靠。

建议定位：保留为条件性诊断和适用边界；减少引言中对它与Design关系的重复说明。

依据：[证据1](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:995)；[证据2](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:1375)；[证据3](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:2191)。

## 对照公开原始工作后的新颖性边界

本次只使用公开通用方法名检索，没有上传或搜索私有论文原句。以下是定向核验，不构成穷尽性新颖性检索。

- [FedIPW原文](https://arxiv.org/html/2604.26604v1)已经包括客户端层面的两阶段选择、IPW及利用目标总体摘要的校准。因此“两阶段纠偏加目标校准”不能独立作为本稿首创。RAVEN可区分的对象是感知单元与客户端选择的层级、顺序历史、可用更新以及逐窗口约束。
- [FedPALS原文](https://arxiv.org/html/2411.03799v2)已经处理目标分布与客户端聚合分布不同、凸包内外的目标匹配，以及匹配误差与ESS之间的权衡。因此“目标可能不可达”“凸组合匹配”和“ESS”分别都不是足够的新颖性依据。本文需说明选择纠正参考与移动窗口可行集耦合产生的新增能力。
- [Deville–Särndal校准估计原文](https://www.tandfonline.com/doi/abs/10.1080/01621459.1992.10475217)表明利用总体辅助信息校准权重属于成熟统计思想。这里只核验其原文摘要和出版信息，未声称检查了全文证明。
- [FedAU原始论文](https://openreview.net/pdf?id=ZKEuFKfCKA)的原始检索摘要明确以参与历史调整FedAvg权重。正文页本次受到OpenReview验证页阻挡；本审查不据此扩展它未被直接核对的具体能力。

RAVEN与这些工作存在实质场景差异，不等于RAVEN被完整覆盖；但应用对象差异也不能自动证明方法层面的重大突破。附录最近邻表漏列FedPALS尤其削弱定位，因为正文已明确承认它与匹配步骤的关系。FedIPW表项也应限定：它有总体校准，只是不等于本稿的逐窗口caps/ESS与参考锚。

## 量化评估

分项采用1–5分；总体采用定性立场，不把分项简单平均为录用分。对3分及以下项目逐项给出扣分与改变判断的条件。

- **问题与估计对象的辨识度：3.5 / 5；置信度较高。** 依据：原子感知目标、R/O/U信息边界和有限窗口组合有明确领域差异。 扣分：目标总体与训练总体区分本身已有先例。 改变判断的条件：用最近邻机制比较说明感知单元和窗口约束导致的不可替代能力。

- **方法机制的独立新增：2.5 / 5；置信度中等。** 依据：IPW、Hájek、校准与ESS都已有基础；完整P2未优于最简投影。 扣分：当前不能排除主要收益来自通用Uniform/投影及目标比。 改变判断的条件：明确主方法身份，并证明额外机制在既有工具之外解决的具体障碍；若收窄到组合贡献，降低算法突破表述。

- **理论的新增与主张承接：2.5 / 5；置信度中等偏高。** 依据：理想重建、强凸唯一性和固定状态非扩张成立有清楚条件；未连接到异步学习风险或无条件长期对齐。 扣分：多数结果属于通用原理实例化，尚未承接最重要的预测/长期主张。 改变判断的条件：围绕可行性损失、实际稳定误差或条件下债务控制建立有信息量的场景定理，或明确把现有定理定位为正确性而非理论突破。

- **实验对创新必要性的识别：2.5 / 5；置信度较高。** 依据：有配对运行、消融、几何与Uniform归因；多个组件没有实际贡献，真实U未测量。 扣分：大量结果仍不能证明完整系统优于简化机制；主骨干预测能力也限制效果解释。 改变判断的条件：先利用已完成的集中度、漂移、学习能力与几何结果；将Uniform/投影移入主表，支持范围与真实证据一致。

- **创新表达与证据组织：3 / 5；置信度较高。** 依据：摘要和引言明确区分重建与可行性，但四项贡献混合建模、方法、性质和归因。 扣分：标准性质占据高位，真实有效机制被配置说明和审计细节分散；摘要两数字有增量相加歧义。 改变判断的条件：围绕一个中心问题组织贡献层级，标清两组独立对照；按能力—证据排序，而非增加创新段落字数。

## 现有表述能否突出创新

已有优点是：摘要和引言已清楚出现“部署目标—选择后参考—窗口可行混合”三个对象；正文不再把所有FedAvg差距都归因于自身，也披露U-Air与真实移动场景的取舍。这些是可信度优势。

目前仍不能充分突出创新，原因不是创新段落太短，而是层级不清。引言四项贡献把问题建模、估计构造、标准正确性、复杂目标函数、实证归因并列；其中最复杂的完整目标函数恰好没有最强增量证据。读者难以确定本文到底发明了更好的完成算法，还是建立了目标质量校准框架，还是揭示了该类权重方法的局限。

1. **摘要的两个正数字不能相加。** +0.768 pp是投影相对Uniform的组差距改善；+0.922 pp是同活跃集Design因子的另一个对照。它们不是顺序加装实验，不能读成总改善1.690 pp。“further”须明确其对照关系。
2. **贡献一应是问题依据，贡献二和三才承载方法。** 命题1不能被排在读者预期的主要数学突破位置。
3. **贡献四是实证发现。** 有价值，但应回答为何原来的结构收益会被Uniform解释、剩余收益来自哪里，而不是充当另一个算法模块。
4. **压缩重复的配置与审计说明。** Design窗口前固定、Gate仅诊断、NoDesign不是完整目标重建均是必要边界；反复在引言和图注解释会打断科学问题。合并说明不能删除真实负结果或必要假设。
5. **“不能合成一个概率”需要更精确。** 按链式法则，顺序选择可写成联合概率的乘积；分开建模的价值在于可记录历史、分层估计和遗漏机制诊断，不是代数上禁止合并。
6. **“headroom/bound/ceiling”不能暗示全类最优上界。** 已评估真概率配置在给定骨干与更新步下收益小，仅说明这些被评估成员的表现；不证明所有可行权重策略都不可能有益，宽区间也不能推出0.5%等价。

## 决定性问题与可执行修复范围

### R1 最近邻重叠没有被充分正面处理（高）

证据：正文承认FedPALS的凸组合匹配，但附录最近邻表未列FedPALS；FedIPW原文也有目标总体校准，表中的“finite-support cal.=no”需要限定为本稿特定窗口约束。

处理：补充机制级比较，区分选择单位、可用信息、纠正参考、窗口caps/ESS、跨窗口状态和学习保证；不能仅凭应用名称不同确立独立创新。

修复类别与owner：ccf-paper-writer；如扩大检索则ccf-literature-searcher。

改变判断的条件：改变创新性判断的证据是不可替代的新增能力，而不是补更多引用。

位置：[来源1](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex:1766)；[来源2](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:300)。

### R2 完整P2的主方法地位与实证最有效机制不一致（高）

证据：主文已报告投影更快，SensorScope组指标优于冻结RAVEN；组匹配、方差、陈旧和默认债务贡献位于实际等价带内。

处理：厘清完整RAVEN、投影和κ=1000变体的不同方法身份；主表放入Uniform和投影，按结果决定哪些属于核心机制、哪些属于可选正则。

修复类别与owner：ccf-experiment-designer → ccf-paper-writer。

改变判断的条件：简化不能在未核对证据归属时冒充已评估完整方法；更多默认消融运行不会自动改变判断。

位置：[来源1](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:1823)；[来源2](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:2080)。

### R3 正确性定理不能代替新的学习能力或长期保证（高）

证据：命题1是测度区别；命题2是理想归一化纠偏；定理1由正锚项强凸导出唯一性；命题3固定M、活跃集及状态；债务界的长期后果另需次线性条件。

处理：按“问题依据、估计正确性、数值稳定性、长期条件”分层解读，不把它们合称异步学习性能保证。

修复类别与owner：ccf-paper-writer；新增证明另行开展。

改变判断的条件：若要提升理论贡献，需场景特有且有信息量的结果，而非给通用事实新增定理编号。

位置：[来源1](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:1153)；[来源2](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:1182)；[来源3](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:1248)；[来源4](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:1265)；[来源5](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:904)。

### R4 结构对齐尚不能支撑数据完成性能创新（高）

证据：SensorScope主表RAVEN RMSE7.9380高于训练均值7.647；U-Air NoDesign 1.1131高于1.054；真实T-Drive对FedAU/ObsUse约差2.4%。

处理：保留这些结果；把现有112条学习预验证作为新协议证据另列，不与旧测试主表拼接。先明确论文主要承诺是质量校准还是更好的完成。

修复类别与owner：ccf-experiment-designer → ccf-paper-writer。

改变判断的条件：方法有效性需要具备学习能力的公平任务和增量机制收益，不能靠重新命名评价指标消除。

位置：[来源1](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:1586)；[来源2](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:1857)；[来源3](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:1704)；[来源4](C:/Users/szr/Desktop/record/1/paper-evidence-audit-20261015/UNUSED_AND_UNDERUSED_EXPERIMENTS.md)。

### R5 核心消融未充分激活三层纠偏；真实U仍为空白（中）

证据：主协议p在层内恒定，q按客户端窗口共享，Local-Hájek在共同活跃集上等于FedAvg；Use消融调整后不显著。真实R有回放，测量O仅一块，无真实测量U。

处理：展示已有F1与六场景结果的真正作用；区分“公式中有三层”与“各层被实证证明必要”，保留真实/控制层标识。

修复类别与owner：ccf-experiment-designer → ccf-paper-writer。

改变判断的条件：增加相同构造下种子数不能替代激活机制或真实层证据。

位置：[来源1](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:1514)；[来源2](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:1800)；[来源3](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:2058)。

### R6 摘要和引言有创新层级与对照关系歧义（中）

证据：摘要“further +0.922”容易被读成在+0.768之上累计；贡献四是归因发现，贡献一与二交叠；Design/Gate配置说明多次重复。

处理：两数字各标对照，不相加；建立问题/核心机制/实证认识层级，压缩重复配置说明并保留必要定义。

修复类别与owner：ccf-paper-writer。

改变判断的条件：改表达可增强可读性，不能自行提高方法新增或实证有效性。

位置：[来源1](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:65)；[来源2](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:176)；[来源3](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:238)。

## 已完成但尚未利用的实验如何帮助创新

- **Traffic目标集中度梯度**：最直接检验“仅因目标分散而无收益”的解释。单区域所评估oracle改善约0.097%，是边界证据，不能改为预测领先结论。
- **112条学习能力轨迹**：将基础学习能力不足与权重机制无效区分开。Traffic/SensorScope集中验证过简单基线、U-Air未过；它是新协议验证，不替换原测试主表。
- **实际自由度与可调整质量**：从K≤3进一步到实际秩与可调整质量，增强为何投影有效或无效的解释；不能从几何本身推出预测收益。
- **200条漂移运行**：适合展示结构收益与预测代价的稳定性；不能证明任意漂移保证或债务次线性。
- **F1、六场景与训练权重规则**：比继续堆相同协议的种子更能说明三层纠偏中哪些机制已被激活。完整展示Uniform和投影尤其重要。
- **外生人口/311目标**：可增强部署目标的应用意义，但需先处理加载器争议，并明确固定预测重评分与重训练的区别。

这些结果主要能提升证据完整性和机制解释。它们不会改变IPW、校准、凸包和ESS已有先行工作的事实；也不能将独立OF分支的实验纳入原稿的主张。

## 优先顺序与下一owner

1. 先决定贡献中心与主方法身份。最有证据的中心是纠正参考的有限支持投影，以及结构对齐与预测效果分离的机制认识。保留完整P2也必须解释其额外作用，不得把投影变体收益直接记在完整RAVEN名下。
2. 用现有数据重组主证据，明确每条结论的条件、对照和实际量级；不需要为改善表达先启动大规模训练。
3. 将FedPALS/FedIPW纳入正面机制比较。若要主张CCF A类方法突破，仍需方法或场景特有理论的独立增量；单纯增加创新篇幅和未利用结果数量不足以完成这一点。
4. 下一owner是ccf-paper-writer，输入本报告与实验利用审计，负责创新主线及表述；只有涉及方法定义或新增证据方案时再由ccf-experiment-designer处理。本轮没有自动交接或修改正文。

## 检查与未核实项

已检查：当前稿身份；摘要/引言的贡献列表；最邻近方法定位；R/O/U权重和P2形式；理想重建与固定状态稳定性的适用条件；主表、消融、Uniform归因、实际训练规则、几何、预测敏感性、真实数据层次；前轮20组未充分利用证据。

未检查：所有证明逐行形式验证、所有运行重算、全面文献穷尽检索、当前TMC政策、所有引用元数据或历史稿评分。未运行训练、回放、求解器或硬件压力测试。

输出自检：问题均有来源或明确标为评审推断；评分条件完整；没有把未显著当等价；没有把0.768与0.922相加；没有将理想统计恢复当作多步异步学习保证；没有隐去不利结果。
