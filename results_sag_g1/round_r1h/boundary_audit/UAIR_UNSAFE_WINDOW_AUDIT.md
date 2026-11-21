# U-Air unsafe window audit

Completeness computed before oracle join.

## window 0
- UTC: 2014-05-09T21:00:00+00:00 → 2014-05-09T22:00:00+00:00
- time_index: 211
- raw span: 2014-05-09 21:00:00+00:00 .. 2014-05-09 21:00:00+00:00 (3600.0s / 3600.0s)
- split truncation L/R: True / False
- first_n/last_n: True / False
- records/entities: 36 / 36
- prev/next raw: True / True contiguous True / True
- completeness: FULL_BOUNDARY complete=True
- oracle_safe (joined after): False C=0.0455696202531645

## window 1
- UTC: 2014-05-09T22:00:00+00:00 → 2014-05-09T23:00:00+00:00
- time_index: 212
- raw span: 2014-05-09 22:00:00+00:00 .. 2014-05-09 22:00:00+00:00 (3600.0s / 3600.0s)
- split truncation L/R: False / False
- first_n/last_n: True / False
- records/entities: 36 / 36
- prev/next raw: True / True contiguous True / True
- completeness: FULL_INTERIOR complete=True
- oracle_safe (joined after): False C=0.0455696202531645

## window 2
- UTC: 2014-05-09T23:00:00+00:00 → 2014-05-10T00:00:00+00:00
- time_index: 213
- raw span: 2014-05-09 23:00:00+00:00 .. 2014-05-09 23:00:00+00:00 (3600.0s / 3600.0s)
- split truncation L/R: False / False
- first_n/last_n: True / False
- records/entities: 36 / 36
- prev/next raw: True / True contiguous True / True
- completeness: FULL_INTERIOR complete=True
- oracle_safe (joined after): False C=0.0455696202531645

## window 51
- UTC: 2014-05-12T00:00:00+00:00 → 2014-05-12T01:00:00+00:00
- time_index: 262
- raw span: 2014-05-12 00:00:00+00:00 .. 2014-05-12 00:00:00+00:00 (3600.0s / 3600.0s)
- split truncation L/R: False / False
- first_n/last_n: False / True
- records/entities: 36 / 36
- prev/next raw: True / True contiguous True / True
- completeness: FULL_INTERIOR complete=True
- oracle_safe (joined after): False C=0.0379746835443038

## window 52
- UTC: 2014-05-12T01:00:00+00:00 → 2014-05-12T02:00:00+00:00
- time_index: 263
- raw span: 2014-05-12 01:00:00+00:00 .. 2014-05-12 01:00:00+00:00 (3600.0s / 3600.0s)
- split truncation L/R: False / False
- first_n/last_n: False / True
- records/entities: 36 / 36
- prev/next raw: True / False contiguous True / False
- completeness: FULL_BOUNDARY complete=True
- oracle_safe (joined after): False C=0.0379746835443038
