# E3 Multidataset Real Runner Canary R1 Report

## 1. Executive decision
**READY_FOR_E3_FORMAL_RUNS**

## 2. Canary purpose / non-performance attestation
Integrity-only Canary; see E3_CANARY_NO_PERFORMANCE_SELECTION_ATTESTATION.md

## 3. Parent evidence integrity
E1/E2/stratum-reuse seals preserved; sealed Traffic five not rerun.

## 4. Canary seed audit
seed=31001 disjoint from formal 30001-30020

## 5. Dataset identity checks
Frozen processed hashes matched for sensorscope/uair/traffic

## 6. Phase-1 sentinel execution
11/11 accepted

## 7. Phase-2 execution
17/17 accepted

## 8. SensorScope execution integrity
11 methods @ 31001 accepted

## 9. U-Air execution integrity
11 methods @ 31001 accepted

## 10. Traffic new-method execution integrity
6 new methods @ 31001 accepted

## 11. Traffic sealed-run protection
Sealed five excluded; duplicate scheduling blocked

## 12. EventTrace identity
One shared EventTrace family per dataset @ 31001

## 13. Delta_c_s integrity
client×opportunity-stratum; see E3_CANARY_DELTA_CS_AUDIT.csv

## 14. atomic-rho / RMSE_rho integrity
atomic rho_i^arr produced for applicable new runs

## 15. Head/Tail integrity
Frozen partitions used

## 16. SimOracle integrity
M_MC=2000 fixed-prestate path executed

## 17. Central reference integrity
Central-All / Central-Delivered executed on real data / EventTrace deliveries

## 18. applicability/N/A integrity
Central structural metrics remain N/A (not zero)

## 19. checkpoint/artifact integrity
Checkpoints + final_metrics present for all accepted runs

## 20. Ledger audit
status=PASS

## 21. test results
{'unit': 0, 'integ': 0, 'full': 0, 'pip': 0}

## 22. Gate results
See gate_results.json after check script

## 23. runtime/resource summary
platform=Windows-10-10.0.26200-SP0; max_workers=1

## 24. formal readiness decision
**READY_FOR_E3_FORMAL_RUNS**

## 25. exact next-round authorization
E3-FORMAL-RUNS-R1 (do not auto-start)
