# Search notes: City Scanner NYC Pilot2 NO2 physical bounds

Date: 2026-09-11
Mode: quick (bound copy for Path A2 ingest freeze; not a Related Work survey)
Source-quality policy: applied (no MDPI)

## Public queries

1. `Wang City Scanner Scientific Data 2023 10.1038/s41597-023-02425-3 NO2 electro-signal`
2. `Hyperlocal Environmental Data with a Mobile Platform Zenodo 10.5281/zenodo.7961851 no2 ppb`
3. `Alphasense NO2-A43F datasheet range ppm` (Wang 2023 ref. 26; cited only as background)

## Screening

- Included: Wang et al. Sci Data 10:524 (2023); Zenodo record 7961851; Alphasense NO2-A43F product/datasheet as Wang's cited sensor spec (not used as ingest cap).
- Excluded: MDPI (none encountered); EPA/NAAQS ambient ppb caps (not in Wang/Zenodo ingest docs; would be invented).
- Not used as calibrated-ppb upper bound: Alphasense 20 ppm warranty range (20000 ppb). Wang applied a raw-mV filter, then released calibrated `no2` in ppb. Re-applying 20 ppm to the CSVs would be a new filter, not a copy.

## Copied bound (for TARGET_SPEC)

Wang et al., Scientific Data 10:524 (2023), Methods (data cleaning):

> we eliminate records with readings out of the reasonable ranges (<1 ug/m3 or >1000 ug/m3 for PM2.5, <200 mv or >900 mv for NO2 electro-signal)

Zenodo `10.5281/zenodo.7961851` field `no2`:

> nitrogen dioxide (no2) readings from the gas sensors after conversion and calibration. The unit is instantaneous concentrations in parts per billion (ppb).

## Freeze decision

- `no2_upper_bound_ppb = null`
- Drop non-finite lat/lon/time.
- Drop non-finite or `no2 < 0` from Y and from O=1.
- Do not reapply 200–900 mV to calibrated ppb files (wrong units; Wang already applied this upstream).
- Do not copy PM's 1000 µg/m³ onto NO2.
- Do not invent an EPA/ambient ppb cap.
