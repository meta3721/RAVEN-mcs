# TABLE-II — Main effectiveness

**Source.** `05_PROVENANCE/FINAL_TABLE_SOURCES/TABLE_II_MAIN_EFFECTIVENESS.csv`  
**SHA256.** `1aa0706f6479b1cac7504e3cffba8eb6a3df7bf9a2a378cc1a689603b49fad86`

**Datasets.** SensorScope, U-Air only.  
**Core methods.** FedAvg-Window, FedAsync-Window, TimeAlign-Agg, Local-Hajek, TwoStage-Hajek, RAVEN-MCS.  
**Optional rows.** Inst-Cal, Debt-Cal (already in source). Reference-only (Central, SimOracle) may move to Appendix if width requires.

**Metrics.** RMSE_μ, Tail RMSE, Δ_group, Δ_{c,s} as mean±std; Holm tags are not numerical-best marks.

**Forbidden.** Traffic E3; T-Drive; universal RMSE wording.
