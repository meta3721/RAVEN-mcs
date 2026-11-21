# E2_TRAFFIC_FORMAL_RUNS_R1 Report

## 1. Executive conclusion
- Status: `READY_FOR_E2_TRAFFIC_PAPER_ANALYSIS`
- Accepted runs: 600 / 600
- Next: `E2-TRAFFIC-PAPER-ANALYSIS-R1`

## 2. Frozen configuration
- Profile: PROFILE-S1
- Registry SHA256: `7d9b8292522b6fbcc15d83ebb065fc8a73b79787ed643aea49c48f30596acbc7`
- Runtime commit: `b01db69e8554a33446c438c060ac464dcfadac24`

## 3. Formal seeds
- 30001–30020 inclusive

## 4–9. Identity / traces / completion / retries / semantics / numerical
See machine-readable audits under `artifacts/e2_traffic_formal_runs_r1/audits/`.

## 10–11. Performance & paired statistics
See `formal_statistics.csv` and `paired_comparisons.csv`.
No superiority claim is made from means alone; paired tests and CIs are reported transparently.

## 12. Runtime summary
- min/median/max seconds: 65.39359370000602 / 70.90141689999655 / 144.80172179997317

## 13–14. Tests and gates
{
  "E2F-G1": true,
  "E2F-G10": true,
  "E2F-G2": true,
  "E2F-G3": true,
  "E2F-G4": true,
  "E2F-G5": true,
  "E2F-G6": true,
  "E2F-G7": true,
  "E2F-G8": true,
  "E2F-G9": true
}

## 15. Known limitations
- Mean CI uses fixed normal approximation (z=1.96).
- Wilcoxon signed-rank uses scipy default zero omission; no family-wise correction.

## 16. Next-step recommendation
- `E2-TRAFFIC-PAPER-ANALYSIS-R1`
