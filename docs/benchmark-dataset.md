# Benchmark Dataset

The benchmark dataset contains 30 synthetic cases. Each supported pathway has exactly six cases:

- `CANCER_2WW`
- `CANCER_FDS_28`
- `CANCER_62`
- `RTT_18_WEEK`
- `UEC_4_HOUR`

Cases are intentionally synthetic and use the `SYN-BENCH-` identifier prefix. They cover within-target, warning, at-target, breached and substantially breached examples so deterministic target logic and agent preservation can be checked without live data.

Run the dataset validator:

```bash
python3 -m app.main validate-benchmark --json
```

The validator checks case count, pathway distribution, unique IDs, synthetic-only flags, expected-output coverage, expected-output checksums, pathway-rule checksum and evidence checksum.

