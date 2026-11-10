# ChronosMatch Engine Benchmark

## Test Configuration
- Seed: 42
- Engine: CythonOrderBook
- Benchmark runs: 1,000 and 1,000,000 orders

## Results

| Metric | 1,000 Orders | 1,000,000 Orders |
|---|---:|---:|
| Throughput (orders/sec) | 20027.80 | 11717.34 |
| P99 latency (ns) | 220500 | 465100 |
| Elapsed time (sec) | 0.0499306 | 85.3436218 |

## Observations
- Both benchmark runs completed successfully.
- The larger workload had lower throughput.
- P99 latency increased under the larger workload.
- CythonOrderBook was used for both runs.

## Methodology
Orders were generated using seed 42 and processed through the benchmark's order-book path.
These results measure the benchmarked order-book path, not the complete ring-buffer pipeline.
