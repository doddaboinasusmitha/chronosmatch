# Benchmark Results

## 1. Overview

This document records the measured performance of the memory-mapped ring buffer using `ipc/bench_ring.py`.

The benchmark compares:
- Copying access using `pop()`.
- Zero-copy access using `peek_view()` followed by `advance()`.

## 2. Test Configuration

| Parameter | Value |
|---|---:|
| Iterations | 200,000 |
| Ring buffer capacity | 1,024 records |
| Record size | 32 bytes |
| Benchmark script | `ipc/bench_ring.py` |
| Platform tested | Windows |
| Python version | 3.14.7 |

## 3. Benchmark Results

| Operation | Execution Time | Throughput |
|---|---:|---:|
| Copying `pop()` | 0.9053 seconds | 220,909 operations/sec |
| Zero-copy `peek_view() + advance()` | 1.0866 seconds | 184,053 operations/sec |

## 4. Analysis

In this benchmark run, copying `pop()` achieved higher throughput than zero-copy `peek_view() + advance()`.

This shows that avoiding a data copy does not always guarantee higher measured performance. The result depends on the operations performed and their overhead.

The zero-copy method provides access to ring-buffer data through a memory view without creating a separate record copy. However, acquiring and releasing the view and advancing the buffer also take time.

## 5. Limitations

- These measurements represent one Windows benchmark run.
- Results may vary depending on system load and hardware.
- Linux benchmark results have not yet been verified.
- No separate `benchmark_engine.md` file was present in the repository during this report preparation.

## 6. Conclusion

The benchmark confirms that both ring-buffer access methods work with 200,000 iterations. In this particular run, `pop()` was faster. Further repeated testing on Windows and Linux is required before drawing broader performance conclusions.
