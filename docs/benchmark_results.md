# ChronosMatch Benchmark Results

## 1. Simulator and Matching Engine Benchmark

This benchmark records the simulator and matching-engine output.

- Number of orders: 100
- Benchmark script: `benchmarks/benchmark_simulator.py`

| Metric | Result |
|---|---:|
| Orders generated | 100 |
| Orders processed | 100 |
| Trades produced | 77 |
| Orders in statistics | 100 |
| Best bid | 10026 |
| Best ask | 10034 |
| Last trade price | 10026 |

The simulator successfully generated and processed 100 orders. The matching
engine produced 77 trades, and the statistics recorded all 100 orders.

## 2. Ring Buffer Access Benchmark

This benchmark compares copying access using `pop()` with zero-copy access
using `peek_view()` followed by `advance()`.

### Test configuration

| Parameter | Value |
|---|---:|
| Iterations | 200,000 |
| Ring buffer capacity | 1,024 records |
| Record size | 32 bytes |
| Benchmark script | `ipc/bench_ring.py` |
| Platform tested | Windows |
| Python version | 3.14.7 |

### Results

| Operation | Execution Time | Throughput |
|---|---:|---:|
| Copying `pop()` | 0.9053 seconds | 220,909 operations/sec |
| Zero-copy `peek_view() + advance()` | 1.0866 seconds | 184,053 operations/sec |

In this particular run, copying `pop()` achieved higher throughput than
zero-copy access. Avoiding a data copy does not always guarantee higher measured
performance because acquiring and releasing a memory view and advancing the
buffer also have overhead.

### Limitations

- The measurements represent individual Windows benchmark runs.
- Results may vary depending on system load and hardware.
- Linux benchmark results have not yet been verified.
- Repeated testing is required before drawing broader conclusions.

## 3. Overall Conclusion

The simulator benchmark demonstrates successful order processing and trade
generation. The ring-buffer benchmark confirms that both copying and zero-copy
access methods work for 200,000 iterations. These are separate measurements
and should not be treated as a direct comparison of matching-engine latency.
