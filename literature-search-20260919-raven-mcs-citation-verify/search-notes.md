# Search notes — RAVEN-MCS citation verification

Date: 2026-09-19 · Skill: `ccf-literature-searcher` (verify-and-screen)

## Purpose

The user asked whether the cited references contain further problems after one entry
(`wang2023transformer`) was confirmed to carry a wrong venue. Deliverable shape requested:
confirmation of the cited works, not new literature discovery.

## Queries used (public, no private manuscript text)

1. "Spatiotemporal Transformer for Data Inference and Long Prediction in Sparse Mobile CrowdSensing" venue journal conference
2. "Spatio-Temporal Pyramid-Based Multi-Scale Data Completion in Sparse Crowdsensing" TMC volume 25
3. "Rethinking the Effect of Sparse Data Completion on Sparse Mobile Crowdsensing Tasks" TMC 2025
4. "MapT-STC" One-Shot Spatiotemporal Data Completion Cold-Start Sparse Crowdsensing
5. "A New Data Completion Perspective on Sparse CrowdSensing: Spatiotemporal Evolutionary Inference Approach"
6. "Federated Learning-Based Distributed Data Completion in Sparse Mobile CrowdSensing" TMC 2026
7. "Data Pricing via Uncertainty Quantification for Sparse Mobile CrowdSensing" TSC
8. "Multidimensional Trust Evaluation and Task Match Based Workers Recruitment Scheme for MCS" TDSC
9. "Locally Differentially Private Truth Discovery for Sparse Crowdsensing" TKDE
10. "PIECE" Multi-Version Model Marketplace Federated Learning TIFS
11. "STDFL" Spatio-Temporal-Aware Dynamic Federated Learning Spatial Crowdsourcing TMC
12. "An Incentive Mechanism for Privacy Preserved Data Trading with Verifiable Data Disturbance" TDSC
13. "Debiasing Federated Learning with Correlated Client Participation" ICLR 2025
14. "FedCure" Participation Bias Semi-Asynchronous Federated Learning Non-IID AAAI 2026
15. "SEAFL" Semi-Asynchronous Federated Learning arXiv 2503.05755
16. "FLOSS: Federated Learning with Opt-Out and Straggler Support" PACMI 2025
17. "Overcoming Label Shift in Target-Aware Federated Learning" arXiv 2411.03799
18. "Adaptive Asynchronous Federated Learning in Resource-Constrained Edge Computing" TMC 22(2) 2023
19. "Outlier-Concerned Data Completion ... Sparse CrowdSensing" ToN 31(2) 2023
20. "Robust Data Inference and Cost-Effective Cell Selection for Sparse Mobile Crowdsensing" ToN 2024
21. "Staleness-Controlled Asynchronous Federated Learning" TMC 23 2024
22. "Spatiotemporal Urban Inference and Prediction in Sparse Mobile CrowdSensing: A Graph Neural Network Approach" TMC 22(11)
23. "Anchor Sampling for Federated Learning with Partial Client Participation" ICML 2023
24. "A Lightweight Method for Tackling Unknown Participation Statistics in Federated Averaging" ICLR 2024
25. "Federated Conformal Predictors for Distributed Uncertainty Quantification" ICML 2023
26. "Conformal Prediction for Federated Uncertainty Quantification Under Label Shift" ICML 2023
27. "A Unified Analysis of Federated Learning with Arbitrary Client Participation" NeurIPS 2022
28. "FedVARP: Tackling the Variance Due to Partial Client Participation" UAI 2022

## Source tiers consulted

Tier 1 (primary): IEEE Xplore document pages, ACM Digital Library DOI pages, AAAI OJS,
PMLR, OpenReview, ICLR proceedings pages, publisher PDFs.
Tier 2 (indexing): Semantic Scholar, researchr, DBLP-style bibliographies, NSF PAR.
Tier 3 (used only to locate a Tier 1 link): general web search snippets.

## Exclusions applied

- No MDPI venues appeared among the 54 entries.
- No retracted works detected.
- No predatory or paywalled-only-without-identifier sources recommended.

## Known limits of this pass

- The search index returned source links, not always full metadata pages, so volume/issue/page
  fields could not be confirmed for every entry. Those are reported as `unverified`, never as
  correct. 24 of 54 entries remain unverified.
- 2026-dated entries are treated as published because the current date is 2026-09-19.
- The "pages 1–10" IEEE Xplore display for INFOCOM 2023 was investigated: Xplore commonly shows
  article-level page ranges for conference papers indexed per-article rather than as a
  continuously paginated proceedings volume. This is a display convention, not a placeholder.
  The DOI (10.1109/INFOCOM53939.2023.10228982) disambiguates the record regardless.
