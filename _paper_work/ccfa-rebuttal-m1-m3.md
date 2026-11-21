# Rebuttal — M1（新颖性偏增量）与 M3（Use 层无孤立效应）

**Mode:** rebuttal（逐条回复，英文草稿可直接粘贴，中文为内部策略）
**Venue and constraints:** IEEE TMC（CCF-A）；响应信无硬性字数上限，保持每点 120–180 词
**Response format:** issue-grouped（按 concern 分组，先给策略再给英文草稿）

---

## Issue Table

| ID | Concern | Severity | Strategy | Promised change |
|---|---|---|---|---|
| M1 | 技术新颖性偏增量（IPW/Hájek + 凸规划组合） | major | 承认部件为标准工具，把贡献定位到"语义分离 + 三层信息边界 + 重建→校准联合链" | 引言加定位句 + 重写贡献 bullet 2/3 + 结论段 |
| M3 | 第三层 Use 无孤立经验效应 | major | 承认 E4 结果，论证三层条件历史不同（理论独立）而经验上 Use 为"建模完备性"而非"独立必需" | 摘要/bullet 2/结论改为"分层信息边界"措辞 |

---

## Response Strategy

1. **先承认后划界（M1）**：不回避"部件是标准工具"，而是把审稿人的注意力从"部件"转移到"联合 + 语义"。用论文自有的证据（§II 的 FedAU 对比、§III 的顺序信息边界、§IV 的 P2、Prop 1/2/Thm 1）证明这条链在现有文献里没有先例。
2. **理论独立 ≠ 经验必要（M3）**：区分"三层的条件历史不同"（理论成立，§III）与"Use 的孤立边际效应"（经验无，E4）。把贡献措辞从"correcting all three layers"降为"layered information boundary"。
3. **保守承诺**：只承诺"措辞/定位"改动，不承诺新实验（除非作者授权）。

---

## Draft Response（英文，可直接粘贴）

### M1 — Novelty

We thank the reviewer for this precise concern. We agree that the individual building blocks are standard: the inverse factors and H\'ajek normalization are classical survey-sampling tools (Horvitz--Thompson, H\'ajek), and the calibration step is a small convex program. Our claim is therefore not a new estimator, but a new *joint formulation* whose necessity does not follow from any single block.

Three points support this. First, the deployment-target versus arrival-risk semantic separation (Proposition 1) is a framing that prior MCS and federated-completion work does not adopt; it changes what the method should align to. Second, the layered correction exists because the three mechanisms condition on different pre-outcome histories (Section III: $O$ on $\mathcal{H}^{\mathrm{obs}}$, $U$ on $\mathcal{H}^{\mathrm{use}}$), so no single missingness probability can replace them; this is the reason the reconstruction is staged rather than a one-shot weight. Third, the feasibility-aware calibration (Section IV) addresses a problem that reconstruction alone does not solve: a statistically faithful reference can be unrealizable in the current mobile window, and a feasibility-only aggregation can silently drift from the target. Proposition 1, Proposition 2, and Theorem 1 together support this joint chain, not any component in isolation.

We have revised the Introduction to state this positioning explicitly, and rewritten contributions (2) and (3) to foreground the joint mechanism chain over the individual tools.

### M3 — Third-layer (usable-update) correction

We agree with the reported evidence and we do not claim that the usable-update factor is empirically indispensable in the tested Complete-aligned family; the ablation study states this openly. Our point is narrower and is theoretical rather than empirical.

The opportunity, observation, and usable-update mechanisms condition on different pre-outcome histories (Section III), so they are distinct statistical objects even when one factor's isolated marginal effect is small in a given configuration. The usable-update factor completes the update-side stage of the two-stage selection model; its null isolated effect in the Complete-aligned family means the tested scenario does not stress update-side censoring, not that the layer is conceptually redundant.

We have revised the abstract, contribution (2), and the conclusion to describe the correction as a *layered information-boundary* reconstruction and to state that the isolated contribution of each layer is reported by the ablation rather than presupposed. If the reviewer considers it necessary, we can add an update-side-stressed configuration (e.g., high drop-out or deadline-tight windows) to test the usable-update factor where it is designed to act; we have not included this experiment here to avoid overstating the current evidence.

---

## Promised Paper Changes

| 位置 | 改动 | 状态 |
|---|---|---|
| Abstract | "by explicitly correcting ... layers" → "through a layered correction in which ... each use only their own ... information" | done |
| Introduction（bullet 前） | 新增定位句：contribution is a joint formulation rather than a new estimator | done |
| Contribution 1 | 结尾补"semantic distinction ... is the premise the rest operationalizes" | done |
| Contribution 2 | 重写为"layered reconstruction + standard building blocks + 报告各层孤立贡献" | done |
| Contribution 3 | 补"neither step alone is sufficient" + "small convex program with reference-anchoring regularizer" | done |
| Conclusion | 新增一段：individual mechanisms deliberately standard + 三层经验角色 | done |

> 说明：以上均为措辞/定位改动，**未改动任何数字、结果、定理、实验**。

## Revision Ledger

| Concern | Action | Manuscript location | Owner | Status |
|---|---|---|---|---|
| M1 novelty | 加定位句 + 重写 bullet 2/3 + 结论段 | §I Introduction、§Conclusion | ccf-paper-writer | done |
| M3 Use 无效应 | 摘要/bullet 2/结论 改"layered information boundary" | Abstract、§I、§Conclusion | ccf-paper-writer | done |
| （可选）Use 场景补实验 | update-side-stressed 配置 | §VI E4 | ccf-experiment-designer | 未承诺（待作者授权） |

## Claims / Promises to Avoid

- 不承诺"新实验已做"（当前只承诺措辞改动；补实验仅在作者授权后进行）。
- 不声称"改动后评分必升"。
- 不声称接受概率。
- 不把 M3 的 null effect 说成"其实有效"——保持与 E4 数据一致。

## Next CCFA Owner

- `ccf-integrity-auditor`：核验改动后 claim–evidence 一致性、引用存在性、BibTeX。
- `ccf-submission-checker`：重新编译 main.tex、查页数/格式。
- `ccf-experiment-designer`（可选）：若作者授权，设计 update-side-stressed 补实验。

## Checklist Status

- 语气平静、factual、证据锚定：✅
- 先答 high-impact（novelty / missing evidence）：✅
- 只承诺可行改动（措辞，未承诺新实验）：✅
- 未发明结果/基线/引用：✅
- 未声称接受概率：✅
