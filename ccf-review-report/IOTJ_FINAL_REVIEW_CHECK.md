# IoTJ门户Final Review核对

日期：2026-11-11。只读核查，不登录或点击提交，不修改稿件。

输入：C:/Users/szr/.codex/attachments/2a6e5578-e691-4747-8e3e-7b99e673db11/已粘贴的文本.txt，以及本地规范main.tex。

## 判断

门户元数据总体自洽，但不应标记为全部通过：4张PNG附件与本地源码显式引用的PDF不匹配；源码照片路径及其在门户的保留情况未验证；其余作者ORCID及当前稿的AI披露需要落实。

## 已核对

- Regular Article、标题、摘要内容与当前规范稿一致；摘要长度满足此前核验口径。
- 四位作者顺序Zuru Shi/Tian Wang/Houbing Herbert Song/Anfeng Liu；提交人为Zuru Shi，通信作者Anfeng Liu。邮箱、国家与单位对应正确。
- 五条完整单位、四所母大学匹配正确。北京师范大学母机构位于北京，不影响其发表地址使用珠海。
- NSFC与U24A20248一致。4个叶级关键词与研究相关，Area分组标题的重复显示不是重复关键词错误。
- 已确认的未发表、无会议前身/相关公开版本、作者同意、无并投，与投稿信和表单一致。
- Code=Yes和Data to share=No与“有本地代码、未另外共享数据”的安排自洽。补充PDF分类、label和description合适。

## 提交前处理

1. Main源码引用fig1_raven_problem_framework.pdf、fig2_e2_risk_noninterchangeability.pdf、fig_g3_tdrive_h_mass.pdf和fig_w1_design_gate.pdf，门户附件却是相应PNG。应上传真正的矢量PDF原文件，不是重命名扩展名。仅已上传的main.pdf能显示图片，并不能证明源码可编译。
2. 照片引用authors/*.jpg，而清单只显示basename；此信息不足以判定平台是否保留子目录。核对源码构建日志/预览或适配平铺上传目录。共享导航、书目及supplemental.aux已经列入，但未实际取得门户生成的编译结果。
3. 汇总只显示Zuru Shi的ORCID，校验位有效，但这不证明账号身份或其余作者ORCID关联。需核对三位教师的实际ORCID；不凭总结页缺项直接断言他们没有ORCID。官网要求所有作者有ORCID。
4. 当前本地main.tex未见Acknowledgment及AI生成内容披露。结合已确认实际使用，按最终保留内容在稿件中披露工具、涉及位置和用途；不把纯语法编辑与内容生成混为一类。更新后重新上传PDF/源码。
5. 汇总未列Conflict of Interest，不据此判断已填或未填。返回该栏目确认已作真实选择；若存在需披露冲突，按平台要求处理。
6. 投稿信在粘贴文本中被压成一段。若只是汇总导出如此，不构成问题；若实际编辑框也无换行，可恢复自然段，属于可读性调整。

## 政策来源

- https://ieee-iotj.org/guidelines-for-authors/（ORCID等）
- https://journals.ieeeauthorcenter.ieee.org/become-an-ieee-journal-author/publishing-ethics/guidelines-and-policies/submission-and-peer-review-policies/（AI生成内容披露）

本轮未拿到门户最终生成PDF、编译日志或实时文件存储结构，不据此宣称系统渲染及目录识别已通过。
