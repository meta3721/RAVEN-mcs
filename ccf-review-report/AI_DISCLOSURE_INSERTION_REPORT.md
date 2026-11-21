# AI披露加入与回退说明

本轮将用户确认的完整声明加入规范main.tex，第1742行；PDF第13页。
位置：VIII. Conclusion之后，Data and Code Availability之前；无编号Acknowledgment。

除这一段插入外，main.tex与备份逐字节一致；supplemental.tex未修改。未改变字体、页边距、作者简介、论文结果或图表。两份PDF因交叉引用顺序重编译。

## 页数与检查

正文由14增至15页；附录仍14页。声明使最后一位作者简介移至第15页。尝试缩短披露措辞后仍为15页，因此最终保留完整获确认声明，未以压缩正文或修改IEEE模板的方式强行维持14页。若保持先前正文14页及附录不大于正文的目标，后续需单独处理约一段披露所占版面。

机器检查详见：C:\Cursor\raven.mcs\tmp\ai_disclosure\verification.json。无未定义引用、待重编译提示或Overfull；字体均嵌入，无Type 3。

## 回退

完整修改前备份：C:\Cursor\raven.mcs\ccf-review-report\backups\ai_disclosure_before_20261111_162925.zip

若后续尚未修改稿件，可从备份恢复main.tex和两份PDF及其辅助文件。若已有其他修改，优先精确删除Acknowledgment标题及本次披露段，保留其他改动，再交叉编译main/supplemental两遍。

已提供精确回退脚本：C:\Cursor\raven.mcs\tmp\ai_disclosure\rollback_disclosure.py。该脚本只删除本次完整披露块并重新编译；若块已被修改或无法唯一匹配，会停止而不写入。它不会恢复或覆盖正文其他修改。执行方式：

```powershell
& 'C:/Users/szr/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' 'C:\Cursor\raven.mcs\tmp\ai_disclosure\rollback_disclosure.py'
```

当前需上传更新后的main.tex、main.pdf和supplemental.pdf；若投稿源文件含supplemental.aux，也同步更新。备份ZIP、内部报告和回退脚本无需上传。
