# Dataset candidates for measured O or U (user chose new corpus)

Do not train until `TARGET_SPEC.json` is `LOCKED` with non-empty `human_signoff`.
Do not mix into Table II / `tab:tdrive_hybrid` / `tab:cityscanner_hybrid`.
Do not overwrite `tdrive_protocol_seal_r1/` or `data/processed/cityscanner_nyc_pm25/`.
U remains controlled unless a later lock supplies device logs (none of the public
candidates below have upload/compute/deadline fields).

## Audit: NYC Pilot2 dual-sensor (same Zenodo 10.5281/zenodo.7961851)

Pilot2 PM rows 515917 (5 vehicles). Pilot2 NO2 rows 491866 (same 5 SensorIDs).
GPS never missing; PM never missing in the PM files; NO2 never missing in the NO2 files.
The streams are **not** the same timestamps:

| Join | PM-only | NO2-only | intersection |
| --- | ---: | ---: | ---: |
| SensorID + unix second | 107109 | 83045 | 408774 |
| 500 m × 30 min cell-slots (PM-kept bbox) | 2126 | 1867 | 12985 PM / 12726 NO2 / **14852 union** |

If \(Y=\) PM2.5 and \(R=\) union cell-slot GPS from either stream:

- \(O=1\) on 12985 slots (finite PM)
- \(O=0\) on **1867 / 14852 = 12.57%** (NO2 GPS visit, no kept PM)

That is a measured observation layer, not \(p_{\mathrm{obs}}=0.35\).
It is **not** vehicle presence without any logger, and **not** network \(U\).

Pilot1 has no NO2 file; including it would collapse \(O\) to \(R\) on those dates.

## Candidates

| ID | Y | R | O | U | Why / blocker |
| --- | --- | --- | --- | --- | --- |
| **A. CS_NYC_P2_DUAL_SENSOR_MEASURED_O** (recommended) | mean finite `pm25` | union PM∪NO2 GPS cell-slots, Pilot2 only | finite PM in that cell-slot | `compute_usable_r3`, \(s_{\max}=5\) | Same CC BY 4.0 record already licensed; 12.6% measured \(O=0\); cells still clients |
| B. CS_NYC_P2_Y_NO2_MEASURED_O | mean finite `no2` | same union | finite NO2 | same controlled U | 14.3% \(O=0\); new Y vs appendix XXI; NO2 range filters must freeze before RMSE |
| C. OpenSense Zurich O3-only | ozone ppb | tram GPS | collapsed (0 GPS-without-ozone) | controlled | Do not lock |
| C2. OpenSense O3∪UFP (2012-04–2014-12) | ozone | union O3∪UFP GPS | **17.54%** UFP-only of 2 008 764 cell-slots | controlled | Measured O exists; 500 m×30 min is too large for the current ranking driver; coarsen or shorten **before** RMSE |
| — PRIVA'MOV | none for MCS completion | GPS | WiFi/GSM presence ≠ sensing O | WiFi-only upload ≠ this paper’s U | NDA, not unrestricted public |
| — T-Drive GPS gaps | speed from same GPS | trajectory | none | gap-as-U is a proxy | Forbidden as jointly measured network |

Boston (one lab vehicle) and Beirut remain out of A unless a separate lock.

## If A is locked

- New processed dir: `data/processed/cityscanner_nyc_p2_measured_o/`
- New traces: `artifacts/e3_joint_ou_cs_p2_eventtraces_v1/`
- New results: `results_joint_ou/round_v1/`
- Seeds **33001–33010** (do not reuse 32001 EventTraces)
- Recompute train slots and \(\phi\) into `GO.json` before traces; Design on iff \(\phi=0\)
- Keep \(O=0\) units in EventTrace occupancy **without inventing Y**
- One smoke on the new EventTrace path, then full 10-seed matrix
- Kill bar frozen before RMSE: SCD paired mean relative vs **both** FedAU and ObsUse \(\le -0.5\%\) on WorstGroupRMSE **or** RMSE_μ
- Label: measured-\(O\) hybrid, controlled \(U\); not end-to-end MCS; clients are cells
