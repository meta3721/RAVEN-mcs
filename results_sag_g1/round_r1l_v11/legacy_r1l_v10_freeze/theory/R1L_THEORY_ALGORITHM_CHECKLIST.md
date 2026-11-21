# Theory-algorithm consistency checklist

1. Every symbol in Theorem 1 is defined in the glossary before use. PASS
2. C_t has one meaning: realized aggregate coverage. PASS
3. C_hat_t is never called a certificate. PASS
4. C_LCB,t is the only certified scalar lower bound. PASS
5. Gate_t uses C_LCB,t and tau_cov only. PASS
6. alpha = 0.05 everywhere. PASS
7. n_min is exactly 19. PASS
8. Warm-up 8 is forbidden for nominal 95% certification. PASS
9. Pairwise lower bounds removed from the formal Gate path. PASS
   (`aggregate_stable_regime` is the window_runner default; pairwise modes are diagnostic.)
10. Current mask absent from legal pre-window inputs. PASS
11. Theorem 1 requires a certified stable regime. PASS
12. Corollary 2 is derived from Theorem 1. PASS
13. Proposition 2 prevents overclaiming under arbitrary drift. PASS
14. RESET leads to Gate OFF. PASS
15. WARMUP leads to Gate OFF. PASS
16. Algorithm cannot silently clip k=n. PASS
17. Experimental oracle is not a current-window training input. PASS
18. Stress a is public; mask identity is not. PASS
19. Historical C_j used only after window j completes. PASS
20. All proofs are complete (no 'Proof sketch'). PASS
