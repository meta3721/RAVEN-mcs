# SCD phi report (SensorScope / U-Air)

This round measures zero-target mass fraction. It does not rewrite Algorithm 2.

Decision: **PASS**.

## Dataset summary

| dataset | phi_train_unit | phi_train_pair | phi_et_occ | phi_et_unique | G1 expected | match G1 |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| sensorscope | 0 | 0 | 0 | 0 | 0.0 | True |
| uair | 0.3544303797 | 0.25 | 0.2546875 | 0.3516934046 | 0.2546875 | True |

Counts:

- sensorscope: train units 0/10285; train pairs 0/440; ET appearances 0/64000; ET unique 0/9429; atomic hash ok=True
- uair: train units 2016/5688; train pairs 72/288; ET appearances 13040/51200; ET unique 1973/5610; atomic hash ok=True

## Seed span (always-on traces 30001-30020)

- sensorscope: phi_et_occ_seed in [0, 0]; phi_et_unique_seed in [0, 0]
- uair: phi_et_occ_seed in [0.2140625, 0.278125]; phi_et_unique_seed in [0.2501339047, 0.305511811]

## Paper number 25.5%

- G1 / manuscript 25.5% is `phi_et_occ` on U-Air = 0.2546875 (25.5%). Wiring match: True.
- Transferable candidate `phi_train_unit` on U-Air = 0.35443037974683544 (35.4%). One-decimal match to 25.5: False.

## Table-sign preview (not applied)

Freeze `phi_scd := phi_train_unit`. Preview rule: Design ON iff phi_scd = 0.
SensorScope phi_train_unit = 0 (ON); U-Air phi_train_unit > 0 (OFF).
This report does not rewrite Algorithm 2 and does not change method keys.
