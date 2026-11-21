# GROUP_MAPPING_SOURCE_AUDIT

Search terms: `h(i)`, `deployment_group`, `group_id`, `coarse_group`, `coarse_time_group`, `fine_group`, `target_group`, `spatial_group`, `time_block`, `group_map`, `mu`, `target_mu`, `M_r`, `composition_matrix`, `Delta_group`, `WorstGroupRMSE`, `use_coarse_time_groups`.

## Paper / sealed manuscript (not code)

| file | current behavior | SS groups | U-Air groups | source | uses public metadata | train-only | current-window | labels | test outcome |
|---|---|---:|---:|---|---|---|---|---|---|
| `RAVEN_MCS_FINAL_FIGURE_TABLE_PAPER_SPECIFICATION_SEAL_R1/01_SEMANTICS/FINAL_H_S_MANUSCRIPT_SEMANTICS_R1.json` | `h(i)` = 4 UTC TOD blocks; `s(i)` = spatial×time-block×weekday | 4 | 4 | sealed writing spec | yes (`absolute_time`) | μ from train mass | no | no | no |
| `.../05_PROVENANCE/FINAL_TABLE_SOURCES/TABLE_I_DATASET_PROTOCOL.csv` | same 4 UTC groups | 4 | 4 | Table I protocol | yes | train-split mass | no | no | no |
| `_handoff_sag_v1.1/RAVEN_MCS_v2_Sections_III_VI_PostAudit_Final.txt` | `h(i)` application-level vs `s(i)` opportunity stratum; μ = ∑ 1{h(i)=g} ϖ | unspecified numeric | unspecified numeric | theory | public/train-side | yes | no | no | no |
| `post_review/G2_external_baselines/PROTOCOL.md` | WorstGroupRMSE on UTC six-hour blocks via `RepeatableTimeOfDayMapper`; “paper’s four-group partition, **not** 144/220 runtime h(i)” | 4 | 4 | G2 endpoint | yes | μ-weights as RMSE_μ | no | no | no |

## Runtime group encodings in code

| file | function/class | current behavior | SS | U-Air | source of mapping | public | train-only | current-window | labels | test outcome |
|---|---|---|---:|---:|---|---|---|---|---|---|
| `src/raven_mcs/e3/target_pair/target_wiring.py` | `production_target_bundle` | Align frozen **spatial×time** artifact onto dataset `target_group` encoding. `n_groups_runtime=len(group_ids)`. **Forbids** `n_groups_frozen==4` for SS/U-Air (treats 4 as illegal time-only). | 220 | 144 | `E3_*_TARGET_SEMANTICS_R2.json` | yes | frozen TEST μ then runtime zero-pad | no | no | no |
| `src/raven_mcs/experiments/sag_runtime.py` | `prepare_sag_bundle` | SAG G0/G1/R1 used `n_groups = n_groups_runtime` and that μ vector. Rejects RepeatableTimeOfDayMapper fallback. | 220 | 144 | production_target_bundle | yes | frozen TEST μ | no | no | no |
| `src/raven_mcs/training/window_runner.py` | `build_full_runner` / `FullWindowRunner` | If caller passes `n_groups==4`, rebuilds μ with `RepeatableTimeOfDayMapper` on **test** split. SAG experiments passed runtime 220/144 instead. `use_coarse_time_groups=False` in G0/G1/R1. | caller | caller | caller `n_groups` / `target_mu` | yes | **test** split if rebuilt | no | no | no |
| `src/raven_mcs/data/window_dataset.py` | `extract_window_slice` | Default: `unit.target_group` (spatial×time int). If `coarse_time_groups==4`: `floor(absolute_time)%24 // 6` on **hour-since-epoch** AtomicUnit field — **not** `RepeatableTimeOfDayMapper`. | 220 default | 144 default | processed `target_group` or broken hour formula | mixed | no | no | no | no |
| `src/raven_mcs/data/target.py` | `RepeatableTimeOfDayMapper` | `(utc hour // 6)` on datetime `absolute_time`. Paper h(i). | 4 | 4 | public timestamps | yes | n/a (map) | no | no | no |
| `src/raven_mcs/data/target.py` | `FrozenTimeBlockMapper` | Split sorted `time_index` into 4/8 quantile blocks. Not the UTC TOD map. | 4 or 8 | 4 or 8 | time_index ranks | yes | uses all slots in frame | no | no | no |
| `src/raven_mcs/data/target.py` | `GroupMapper` | Reads a column named as h(i) in comments. | column cardinality | column cardinality | column | depends | depends | no | no | no |
| `src/raven_mcs/data/processed_dataset.py` | `_encode_target_group` | Encodes string spatial×time `target_group` to 0..G-1. | 220 | 144 | atomic `target_group` | yes | encoding includes all splits | no | no | no |
| `src/raven_mcs/correction/hajek.py` | `group_mass` | `m_{k,r,g}=∑ O a 1{h(i)=g}` using whatever integers `extract_window_slice` put in `target_groups`. | `n_groups` arg | `n_groups` arg | runner | n/a | n/a | uses current O | no | no |
| `src/raven_mcs/metrics/distribution.py` | `delta_group` | `‖ω̂−μ‖_1` in whatever dimension the runner used. | len(μ) | len(μ) | runner μ | n/a | n/a | n/a | no | no |
| `src/raven_mcs/e3/real_runner/runner.py` | `_predict` / `_mu_weights_for_test` | Groups = fine `u.target_group`. RMSE_μ / WorstGroup in SAG G1 used this space. | 220 | 144 | processed encoding | yes | test units | no | **uses Y for RMSE** | test Y for metric, not for mapping |
| `src/raven_mcs/experiments/run_sag_g1.py` | `_worst_group_rmse` | max RMSE over `pred["groups"]` (fine groups in G1). | 220 | 144 | `_predict` | yes | test | no | Y | Y |
| `src/raven_mcs/sag/certificates.py` | `compute_service_bound` | `B_srv = √n_groups * (...)`. G1/R1 passed runtime |G|. | 220 | 144 | CertificateContext | n/a | n/a | no | no | no |
| `post_review/G2_external_baselines/run_g2.py` | evaluation groups | `RepeatableTimeOfDayMapper` on test `absolute_time` | 4 | 4 | paper mapper | yes | test times | no | Y for RMSE | Y |

## Why G1/R1 logged |G|≈220/144

SAG called `prepare_sag_bundle` → `production_target_bundle` → `n_groups_runtime`. Window records used fine `unit.target_group`. `use_coarse_time_groups=False`. That is the E3 pair-domain encoding, not paper `h(i)`.

## Decision for R1b

Use the paper 4-block `RepeatableTimeOfDayMapper` map for μ, M, ω, Δ_group, |G|, B_srv, and R1b WorstGroupRMSE. Keep `s(i)` / `π^{tar}_{k,s}` on sealed opportunity strata. Do not merge groups to manufacture Gate ON; the 4-group map is the already-frozen paper object.
