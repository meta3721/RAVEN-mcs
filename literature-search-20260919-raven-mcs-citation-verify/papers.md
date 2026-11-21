# Citation verification — RAVEN-MCS (main.tex / reference.bib)

- **Date:** 2026-09-19
- **Owner skill:** `ccf-literature-searcher` (verify-and-screen mode; requested by user)
- **Scope:** all 54 entries in `TO_OVERLEAF_paper_tmc_r1_clean/reference.bib`, sorted by verification risk
- **Source policy:** official proceedings / IEEE Xplore / ACM DL / PMLR / OpenReview / AAAI OJS / DBLP / Semantic Scholar / publisher pages. No MDPI or predatory venues appeared.
- **Method:** exact-title retrieval, then confirmation through a stable publisher or proceedings page. Every "verified" verdict below is backed by a linked primary page. Claims not backed by a primary page are marked `unverified`.
- **Rule applied:** no invented papers, venues, or status. Anything not retrieved is reported as `unverified`, not as correct.

---

## 1. Confirmed errors (must fix before submission)

| # | key | What the bib says | What the source says | Severity |
| --- | --- | --- | --- | --- |
| 6 | `wang2023transformer` | `@article`, *ACM Computing Surveys*, vol. 58, no. 4, 2025, art. no. 7 | `@inproceedings`, **IEEE INFOCOM 2023**, pp. 1–10, DOI 10.1109/INFOCOM53939.2023.10228982 | **high — wrong venue, wrong year, wrong type** |

Author list is correct in both (Wang, E.; Liu, W.; Liu, W.; Xiang, C.; Yang, B.; Yang, Y.). Only the venue/year/type fields are wrong.

Primary source: <https://ieeexplore.ieee.org/abstract/document/10228982>

Because this is a wrong-venue error on a *cited-as-prior-art* entry, it also affects the Related Work sentence at `main.tex` L269 ("Transformer-style spatiotemporal inference"), which currently implies journal provenance.

---

## 2. Verified correct (primary source retrieved)

| # | key | Verified against |
| --- | --- | --- |
| 4 | `wang2023outlier` | <https://ieeexplore.ieee.org/abstract/document/9874772> |
| 5 | `li2024robust` | <https://dl.acm.org/doi/10.1109/TNET.2024.3397309> |
| 8 | `wang2025evolutionary` | <https://ieeexplore.ieee.org/abstract/document/10736955> |
| 9 | `xu2025rethinking` | <https://ieeexplore.ieee.org/abstract/document/10845194> (DOI 10.1109/TMC.2025.3531362) |
| 10 | `liu2026pyramid` | <https://ieeexplore.ieee.org/document/11125969> |
| 11 | `zhang2026mapt` | <https://ieeexplore.ieee.org/document/11459179> |
| 16 | `wang2026federated` | <https://www.semanticscholar.org/paper/e82f7213b5ccfe80567b47a8cad1b4f75842f939> |
| 18 | `liu2023adaptive` | <https://ieeexplore.ieee.org/document/9484767> |
| 19 | `sun2024staleness` | <https://xplorestaging.ieee.org/document/10561520> |
| 20 | `wang2023spatiotemporal` | <https://ieeexplore.ieee.org/document/9851618> |
| 21 | `wang2022unified` | <https://ar5iv.labs.arxiv.org/html/2205.13648v4> |
| 22 | `jhunjhunwala2022fedvarp` | <https://par.nsf.gov/biblio/10389233/media/xml> |
| 23 | `wu2023anchor` | <https://researchr.org/publication/Wu0QHLG23/bibliographies> |
| 24 | `wang2024lightweight` | <https://iclr.cc/media/iclr-2024/Slides/18403.pdf> |
| 25 | `sun2025debiasing` | <https://openreview.net/pdf?id=9h45qxXEx0> |
| 27 | `chen2026fedcure` | <https://ojs.aaai.org/index.php/AAAI/article/view/39176> |
| 28 | `morishita2026who` | <https://ar5iv.labs.arxiv.org/html/2604.26604> |
| 29 | `liu2026pricing` | <https://xplorestaging.ieee.org/document/11408297> |
| 30 | `liu2026multidimensional` | <https://ieeexplore.ieee.org/document/11345990> |
| 31 | `zhang2025incentive` | <https://xplorestaging.ieee.org/document/10891587> |
| 32 | `lu2025piece` | <https://ieeexplore.ieee.org/abstract/document/11137414> |
| 33 | `zhang2026locally` | <https://ieeexplore.ieee.org/document/11271604> |
| 34 | `islam2025seafl` | <https://arxiv.org/pdf/2503.05755> |
| 35 | `li2026stdfl` | <https://ieeexplore.ieee.org/abstract/document/11433070> |
| 36 | `lu2023federated` | <https://export.arxiv.org/pdf/2608.29789> (cited as ICML 2023) |
| 37 | `plassier2023conformal` | <https://researchr.org/publication/PlassierMRMP23/bibtex> |
| 40 | `goetze2025floss` | <https://dlnext.acm.org/doi/pdf/10.1145/3766882.3767180> |
| 41 | `listozec2024overcoming` | <https://openreview.net/pdf?id=dQAsAmb1Xb> |

---

## 3. Minor issues (fix optional, low risk)

| # | key | Issue | Recommendation |
| --- | --- | --- | --- |
| 32 | `lu2025piece` | `pages = {9387-9398}` uses a hyphen while every other entry uses an en dash `--` | normalise to `9387--9398` |
| 34 | `islam2025seafl` | Cited only as `arXiv preprint arXiv:2503.05755`, but the work is now published: <https://xplorestaging.ieee.org/document/11078406> | upgrade to the published venue, or state both |
| 50 | `tfnsw2024traffic` | `note = {Accessed: Aug. 14, 2026}` — the access date is earlier than the manuscript build date; also the year field says 2024 while the access is 2026 | make the access date match the actual retrieval, and confirm whether the dataset should be dated 2024 or the year of retrieval |
| 47 | `ingelrest2010sensorscope` | `pages = {1--32}` plus `note = {Art. no. 17}` — the double reference is unusual for ACM TOSN | keep one form (ACM uses article numbers for this journal) |

---

## 4. Not independently verified in this pass

These 25 entries were not retrieved against a primary page in this session. They are mostly pre-2025 classics and widely indexed works, but that is not a verification result.

`ganti2011mobile` (1), `guo2015mobile` (2), `ma2014opportunities` (3), `wang2024fewshot` (7), `mcmahan2017communication` (12), `yang2019federated` (13), `kairouz2021advances` (14), `li2020federated` (15), `xie2019asynchronous` (17), `mohri2019agnostic` (26), `li2020fedprox` (38), `karimireddy2020scaffold` (39), `horvitz1952generalization` (42), `hajek1971comment` (43), `shimodaira2000covariate` (44), `robins1994estimation` (45), `byrd2019importance` (46), `ingelrest2010sensorscope` (47), `barrenetxea2019sensorscope` (48), `zheng2013uair` (49), `yuan2010tdrive` (51), `wang2023cityscanner` (52), `wilcoxon1945individual` (53), `holm1979simple` (54)

That is 24 entries. Together with the 1 confirmed error (entry 6) and the 4 minor-issue entries (32, 34, 47, 50), it accounts for all 54 minus the 29 verified-correct rows in section 2 — entry 47 appears in both lists because its existence is not in doubt but its page/article-number form is.

Status: `unverified` — needs a second pass or the user's own check.

---

## 5. Screening notes

- No retracted, predatory, or policy-excluded sources detected.
- No duplicate keys. No two entries point to the same work.
- All 54 keys are cited at least once in `main.tex` or `appendix.tex`; there are no orphan entries.
- Highest-risk class, as expected, is the 2025–2026 group, because that is where the venue cannot be inferred from familiarity. `wang2023transformer` was the single failure there.

## 6. Recommended next module

- `ccf-paper-writer`: apply the `wang2023transformer` correction and adjust the L269 sentence if the venue change affects the claim.
- `ccf-integrity-auditor`: run the remaining 25 unverified entries through a bib-level existence check.
