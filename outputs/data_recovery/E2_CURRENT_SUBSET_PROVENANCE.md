# Current 62-timestamp subset provenance

Status: **TEST_SLICE_CONFIRMED**

62 timestamps are not a raw download bug; they are the test-split slice of a deliberately selected ~55×312 hourly dense window. Even the full 312h processed matrix yields only floor(311/6)=51 non-overlapping 6h windows (<100).

- Raw source: `data/raw/sensorscope/Sensorscope.zip`
- Processed all timestamps: 312 (311.0h)
- Supported-test timestamps: 62 (61.0h)
- Max 6h windows on supported-test: 10
- Max 6h windows on full processed matrix: 51
