# Evidence zero-certified-mass NaN repair

R1d serialized `target_mass_certified` with `float(x or nan)`.
A true 0.0 is falsy in Python, so certified mass 0 became NaN.
That matches C_COV_DYNAMIC_WINDOW.csv warm-up rows: `C_cov_LCB=0.0` and empty `target_mass_certified`.

Repair: `optional_float` in `src/raven_mcs/sag/evidence.py`.
- 0.0 -> 0.0
- None -> NaN
- positive -> positive

C_cov_LCB formula is unchanged. R1d artifacts were not rewritten.
R1e builders use the repaired helper.
