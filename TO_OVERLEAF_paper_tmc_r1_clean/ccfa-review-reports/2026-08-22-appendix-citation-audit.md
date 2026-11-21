# 附录引用审计报告

## 核心结论

**正文对附录只有 4 处引用，全部是"Appendix~A"文字引用，且全部指向附录 A（理论证明部分）。**

- 附录 B、C、D、E（实验补充证据）**在正文中零引用**
- 附录的全部 8 张表（Table IV-XI）**在正文中零引用**
- 附录的 15 个可引用 label（app:*）**在正文中零 `\ref` 使用**

附录 A 的 4 处引用全部为**硬编码文字 "Appendix~A"**（非 `\ref{app:...}` 动态引用），因此即使附录章节重排（如 A→B），正文也不会自动更新。

---

## 一、正文对附录 A 的 4 处引用（全部）

| # | 正文位置 | 引用内容 | 指向的附录内容 | 性质 |
|---|---|---|---|---|
| 1 | **L1050**（Sec V-E 债务界之后） | "The full derivation is given in **Appendix~A**." | 附录 A-D：Target-Debt Accounting Bound 的完整证明 | 文字引用 |
| 2 | **L1205**（Prop 1 陈述之后） | "\emph{Proof.} See **Appendix~A**." | 附录 A-A：Proposition 1 的完整证明 | 文字引用 |
| 3 | **L1269**（Prop 2 陈述之后） | "\emph{Proof.} See **Appendix~A**." | 附录 A-B：Proposition 2 的完整证明 | 文字引用 |
| 4 | **L1292**（Thm 1 陈述之后） | "\emph{Proof.} See **Appendix~A**." | 附录 A-C：Theorem 1 的完整证明 | 文字引用 |

**注意**：这 4 处引用的目标是"Appendix A"，而附录 A 实际包含 6 个子节（A-A 到 A-F）。正文引用粒度只到"A"，没有精确到 A-A/A-B/A-C/A-D。

---

## 二、附录 B-E 及全部附录表的引用情况（零引用）

### 附录 B：Supplementary Risk-Semantic Evidence（B-A, B-B）
| 内容 | label | 正文是否引用 |
|---|---|---|
| B-A Balanced No-Harm Control（Table IV） | app:e1_balanced / tab:app_e1_balanced | ❌ 无 |
| B-B Complete E2 Statistics（Table V） | app:e2_full_stats / tab:app_e2_daligned | ❌ 无 |

### 附录 C：Local-Hájék Degeneracy Analysis（C, Table VI）
| 内容 | label | 正文是否引用 |
|---|---|---|
| Local-Hajek 退化审计 | app:local_hajek / tab:app_local_hajek | ❌ 无 |

### 附录 D：P2 Feasibility Diagnostics（D, Table VII, VIII）
| 内容 | label | 正文是否引用 |
|---|---|---|
| P2 可行性认证覆盖（Table VII） | app:p2_diagnostics / tab:app_p2_coverage | ❌ 无 |
| Warning 审计与声明边界（Table VIII） | tab:app_p2_warning_audit | ❌ 无 |

### 附录 E：Additional Existing Experimental Context（E-A, E-B, E-C）
| 内容 | label | 正文是否引用 |
|---|---|---|
| E-A Full E3 Method Context（Table IX, X） | app:e3_full_context / tab:app_e3_sensorscope / tab:app_e3_uair | ❌ 无 |
| E-B Runtime Diagnostic（Table XI） | app:runtime / tab:app_runtime | ❌ 无 |
| E-C w/o-Design Provenance | app:design_provenance | ❌ 无 |

---

## 三、其他发现

1. **正文对附录表的间接文字提及**：正文 Sec VII 提到了 "774-window check"（对应附录 E-C）、"9666 client-windows"（对应附录 C）、"6438 P2 windows"（对应附录 D）等**数字**，但没有用 `\ref{tab:app_...}` 指向这些附录表。读者无法从正文跳到对应附录表。
2. **正文引用了 Table II/III（主文表）**，但附录的 Table IV-XI 编号是延续主文表格编号的（IV 之后），主文没有 `\ref` 指向 IV-XI。
3. **附录内部引用正常**：附录内部（证明之间）大量使用 `\eqref{eq:app_*}` 互相引用，这部分完整。
4. **4 处 "Appendix~A" 为硬编码**：建议改为 `Appendix~\ref{app:complete_proofs}` 以支持自动编号。

---

## 四、建议（可选，供你决策）

| 问题 | 风险 | 建议 |
|---|---|---|
| 附录 B-E 正文零引用 | 审稿人可能认为这些内容"可有可无"；补充证据的价值未被正文利用 | 在 Sec VII 相应位置加 `\ref{tab:app_*}` 指针（如 E1 处指 Table IV、E2 处指 Table V、Hajek 退化处指 Table VI、P2 审计处指 Table VII/VIII、完整 E3 上下文处指 Table IX/X） |
| 4 处硬编码 "Appendix~A" | 附录重排时引用不更新 | 改为 `\ref{app:complete_proofs}` |
| 引用粒度只到 A | 读者无法直达 A-B/A-C | 可在 Prop/Thm 的 "See Appendix~A" 改为指向具体子节（如 `\ref{app:proof_prop2}`） |
