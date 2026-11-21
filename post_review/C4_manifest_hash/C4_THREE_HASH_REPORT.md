# C4 three-hash fix report

Date: 2026-09-11. Followed `C4_THREE_HASH_INSTRUCTION.md`. No commit. `MANIFEST.csv` not rewritten. No Table II cells changed. No training.

## Pre-check

`python RAVEN_MCS_PUBLIC_REPRO_R1/verify.py`:

```text
HASH_MISMATCH scripts/rebuild_table_ii.py
HASH_MISMATCH scripts/rebuild_table_ii_tolerance.py
HASH_MISMATCH tdrive/TD_R_FREEZE.json
checked=1883 mismatches=3
```

LF-normalized bytes already matched the frozen MANIFEST hashes (`lf_match True` on all three). Cause: CRLF on disk vs LF in the manifest.

## Before / after

| path | before bytes / sha256 | after bytes / sha256 | MANIFEST |
|---|---|---|---|
| `scripts/rebuild_table_ii.py` | 1876 / `941933767c7d330daa13c0ce2f2ef43627afbd25832059b53f021e2eb255c470` | 1816 / `43aa9f457ce7e725264f3e99704ce3a9c7131bdf420b6af895ddeea596ac3125` | same as after |
| `scripts/rebuild_table_ii_tolerance.py` | 3565 / `7dbf9d2b3f5c58efb2004079fc0afe90b3571c58eb24f14c20d9e4f0f0ee1c3a` | 3459 / `0ad624fc91727ca0ce57686ab7f384223db944afd79ceaa6532b4ee7ac1b2625` | same as after |
| `tdrive/TD_R_FREEZE.json` | 665 / `6159cccba359d2d782a78e9d9f7b223970dde7f3be0f9938743c443c64b7f270` | 647 / `6e34938b502500cba7e9e0a89f97d6c34cf4c34744ce612ee69b2fd745855ac5` | same as after |

Action: `b'\r\n'` → `b'\n'` only. `TD_R_FREEZE.json` still has `phi_train_unit=0.47352962798301473` and `device_note`.

## Post-check

From `RAVEN_MCS_PUBLIC_REPRO_R1/`:

- `scripts/rebuild_table_ii.py` → `OK Table II 4-decimal freeze matched` (exit 0). SCD cells unchanged: SensorScope `7.9380` / `8.6707` / `1.0139` / `1.2644`; U-Air `1.1131` / `1.1703` / `1.0165` / `1.2949`.
- `scripts/rebuild_table_ii_tolerance.py` → `OK descriptive +0.5% point-estimate percentages matched` (exit 0). T-Drive vs FedAU/ObsUse `2.39` / `2.43`; `within_0p5pct_point_tolerance` is false.
- `verify.py` → `checked=1883 mismatches=0` (exit 0).

## Not done

- Did not edit `MANIFEST.csv`.
- Did not run `scripts/build_public_repro_bundle.py`.
- Did not add City Scanner / Table XXI / Table XXII files.
- Did not change `.gitattributes`.
- Did not commit.
