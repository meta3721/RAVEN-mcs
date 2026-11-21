# RAVEN-MCS：IoTJ初投稿准备度检查

核验日期：2026-11-11。使用ccf-submission-checker；默认常规研究论文首次投稿，未按特刊或返修要求检查。本轮只检查，不修改规范论文、不上传稿件、不启动实验。

## 判断

**当前文件已具备IoTJ初投的基本格式与技术条件；但不宜标为“无需处理即可提交”。应先完成实际AI生成内容的披露核对，并由作者确认ORCID、共同作者同意及无并投/既往发表情况。补齐这些事项后，可以提交初审，不需要为了形式要求重新训练或强行压至8页。**

这不是录用预测，也不替代完整科学评审。

## 已通过的文件检查

- 当前入口为`TO_OVERLEAF_paper_tmc_r1_clean/main.tex`及`main.pdf`，补充入口为`supplemental.tex`、`appendix.tex`及`supplemental.pdf`。使用11月11日8:00生成的当前PDF，没有回退到以前版本。
- 两份PDF均14页，Letter尺寸612×792 bp，未加密；正文约4.459 MB，补充约0.741 MB。正文包含四位作者及作者简介，补充也保留相同作者顺序。
- IEEEtran的journal双栏模板；作者姓名、单位、邮箱、通讯作者和基金说明已写入，不再是旧占位信息。单匿名审稿允许评审看到作者身份，无须按双匿名会议另行匿名化。[IoTJ作者指南](https://ieee-iotj.org/guidelines-for-authors/)
- 摘要为单段，空格分词约210词，英文词法口径约211词；无引用和展示公式，满足150—250词的公开要求。关键词已存在；系统内仍须选择对应分类。[IoTJ作者指南](https://ieee-iotj.org/guidelines-for-authors/)
- 两份PDF字体均嵌入，无Type 3。当前日志和隔离重编译日志均未发现Overfull、缺字、字体警告、未定义引用/文献、重复label/destination或PDF字符串警告。现有Underfull及禁用shell-escape提示没有被误称为“零提示”。
- 在独立临时目录复制必要源码、书目和12个实际图片资源后，顺序执行8次LaTeX/BibTeX，全部成功，aux稳定，仍为14/14页。重编译版本与当前PDF的28页文本逐页去空白比较一致，支持源码与当前PDF对应。
- 两份PDF全部28页均已渲染并查看页面联系图，首末页、作者信息、四张正文图、四张补充图及表格未见明显遮挡或裁切。图1仍在系统模型、正文第3页；本轮没有重做图形或调整排版。
- 论文主题涉及移动感知、智能城市场景和分布式感知数据处理，与IoTJ公布的IoT数据分析、传感及应用范围有合理对应。这是范围适配判断，不是编辑送审或接收承诺。[IoTJ范围说明](https://ieee-iotj.org/)

## 提交前必须解决或确认

### 1. AI生成内容披露：当前未见，需要按实际保留内容处理

当前正文没有AI使用披露。IEEE要求对实际使用的AI生成文字、图、图像及代码在致谢中说明工具、相关位置和用途；仅编辑与语法增强不强制披露，但建议说明。[IEEE当前投稿政策](https://journals.ieeeauthorcenter.ieee.org/become-an-ieee-journal-author/publishing-ethics/guidelines-and-policies/submission-and-peer-review-policies/)

本项目的实际工作记录包括生成式段落修订和图1矢量绘图代码编写，不能不加核对地把全过程视为纯语法校对。请依据当前最终保留的内容确定范围；如果仍采用这些生成内容，应提交前补充准确声明。后续由作者重写或移除的内容不应被无依据地列入。本判断不依赖AI检测器分数，也没有把AI声明擅自写入稿件。

### 2. 作者与投稿声明：文件无法证明，须作者在系统中确认

- 四位作者均有有效ORCID，并按系统要求关联。PDF没有印ORCID不等于违反要求，但不能据此确认账号已完成。[IoTJ作者指南](https://ieee-iotj.org/guidelines-for-authors/)
- 全体作者认可署名、顺序、单位及提交版本；当前稿内信息存在不等于已取得全部作者同意。
- 没有同稿或近似稿在其他期刊/会议并行审理；如有会议前身、已发表近似稿或相关投稿，应准确披露、引用并说明差异。当前文件不足以判断这些事实，未默认其不存在。[IEEE投稿与既往发表政策](https://journals.ieeeauthorcenter.ieee.org/become-an-ieee-journal-author/publishing-ethics/guidelines-and-policies/submission-and-peer-review-policies/)

### 3. 附件与门户预览：补充材料须随当前初稿交付

正文依赖补充证明与协议说明，应将当前`supplemental.pdf`作为供评审阅读的独立补充文件同时上传。IEEE接受PDF补充材料，要求单独标记并上传。[IEEE补充材料说明](https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/prepare-supplementary-materials/)

当前文档使用相对文件名的跨PDF链接；投稿系统可能重命名或合并文件，不能保证远程跳转仍可用。正文的明确层级引用和补充Reading guide仍有定位作用。提交前应检查系统生成的整合预览，确认两个文件都可见、图表和引用完整；本轮没有登录门户或实点验证其最终显示。

正式入口是[IEEE Author Portal—IoTJ](https://ieee.atyponrex.com/journal/iot)。本地未找到独立投稿信；公开IoTJ指南没有使我确认它是统一必填项，因此不将其缺失判为硬性违规，按门户当前字段准备即可。图形摘要也不是本次查到的普遍必交项。

## 页数与费用：不要混淆项目目标和期刊规定

官网说明超过前8个正式出版页收取175美元/页的强制超页费；本次查阅的IoTJ公开网页及作者指南PDF未列出“14页是初投最大页数”。因此当前14页本身不能据此判为不合规。14页及补充不超过正文是本项目约束，当前满足；具体文章类型是否另有门户限制，尚未登录核验。[IoTJ作者指南PDF](https://ieee-iotj.org/wp-content/uploads/2025/04/IEEE-IoTJ-Author-Guidelines.pdf)

若最终出版长度仍为14页，单按该超页费率估算为`(14−8)×175=1050美元`；不是现在提交就收取的费用，也不是最终账单，且不含可选OA、彩色印刷或税费。2026年IEEE Open列出的混合期刊OA标准价为2800美元；IoTJ网页/PDF有不同历史OA数字，应以投稿系统及适用协议核定，不能把旧价格当最新报价。[IEEE 2026 APC说明](https://open.ieee.org/for-authors/article-processing-charges/)

## 非阻断建议与科学评审边界

- PDF作者元数据正确，但Title、Subject和Keywords元数据为空。建议补齐，未找到其为IoTJ拒绝初投的公开硬条件。
- 当前Data and Code Availability如实说明作者持有材料尚无公开链接。本轮未查到IoTJ对所有普通研究论文一律强制公开代码的要求，因此不单凭该点判不合规；但审稿复现便利性较弱。未核定任何旧复现包与当前方法身份一致，不建议不经检查就上传旧包。
- 当前最强应用证据仍是两种City Scanner协议中的组失配改善，而不是预测、时间或全部端点全面领先。正文保留了预测排名代价、站点模型与训练均值参照的关系、复杂校准与简单投影的取舍、以及未通过非劣性的结果。这些会影响科学评审，但不是IEEE模板是否允许提交的条件。
- 未逐条复核45条参考文献的元数据/支持关系，未逐式重证理论，未重放或重跑实验，没有给出相似度查重结果或接收概率。不能把“编译和格式通过”理解成这些事项已通过。
- 项目中未找到ccfa.yaml；这只表示没有该技能的统一状态跟踪，不是论文违规或初投阻断项。

## 留档与保护

本轮没有改动规范TeX、PDF、图、算法或实验数据。隔离构建前后对规范源码及两份PDF做逐字节一致检查，结果通过。

本地检查证据位于`tmp/iotj_readiness_20261111/`：`inspection.json`、`pdf_source_comparison.json`、字体清单、8次构建输出及28页渲染。`build/`中的PDF仅用于核验，不是新的规范稿或另一套final。

结论保持为：**格式文件可用于IoTJ初投；先完成AI披露核对与作者/系统声明，再提交。无需为此次合规检查新增实验。**
