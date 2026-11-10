# ChronosMatch Engine Report

## 1. Introduction

ChronosMatch is a zero-copy, high-frequency trading engine designed to process binary order records, match buy and sell orders, and publish executed trades with low overhead.

The engine uses Python for orchestration and a Cython-based matching core for optimized order-book operations.

## 2. System Architecture

The main processing flow is:

```text
Order Generator
      |
      v
Order Ring Buffer (mmap)
      |
      v
Engine Loop
      |
      v
Matching Engine
      |
      v
Order Book Adapter
      |
      +------> Python Order Book
      |
      +------> Cython Book Core
      |
      v
Trade Ring Buffer
      |
      v
Statistics and Dashboard
```

The adapter selects the Cython implementation when the compiled extension is available. Otherwise, it falls back to the Python implementation.

## 3. Python Reference Order Book

The Python implementation is available in `engine/order_book.py`.

Its main responsibilities are:

- Maintaining separate bid and ask price levels.
- Matching incoming orders against existing opposite-side orders.
- Applying price-time priority.
- Supporting partial order fills.
- Keeping unfilled quantities in the order book.
- Providing the best bid, best ask and order-book snapshot.

Buy orders match with the lowest available sell price. Sell orders match with the highest available buy price.

Trades execute at the resting order's price. Orders at the same price are processed in FIFO order.

## 4. Cython Optimized Order Book

The optimized implementation is available in:

- `engine/book_core.pyx`
- `engine/book_adapter.py`

The Cython core uses C structures, pointers and dynamically allocated linked-list nodes to store orders.

Separate bid and ask arrays maintain price levels, with head and tail pointers supporting FIFO order insertion and removal.

Its main features include:

- C-level order storage.
- FIFO matching at each price level.
- Partial order execution.
- Best bid and best ask retrieval.
- Quantity calculation at individual price levels.
- Memory allocation and deallocation using `calloc()` and `free()`.

The default maximum supported price is 100000. Prices outside the configured range are rejected.

## 5. Matching Engine

The matching engine is implemented in `engine/matching_engine.py`.

Its responsibilities include:

1. Reading and unpacking incoming order records.
2. Calculating order latency when a valid timestamp is available.
3. Passing orders to the selected order book.
4. Generating trade IDs and timestamps.
5. Publishing executed trades to the trade ring buffer.
6. Updating order counts, trade counts and best bid/ask statistics.

If the trade ring buffer is full, the engine raises a `BufferError`.

## 6. Binary Data Format

ChronosMatch uses fixed-size binary records instead of JSON or Pickle for its order and trade messages.

### Order Record

Defined in `ipc/record.py`.

| Field | Size |
|---|---:|
| Order ID | 8 bytes |
| Price | 8 bytes |
| Quantity | 4 bytes |
| Side | 1 byte |
| Padding | 3 bytes |
| Timestamp | 8 bytes |
| Total | 32 bytes |

### Trade Record

Defined in `ipc/trade.py`.

| Field | Size |
|---|---:|
| Order ID | 8 bytes |
| Price | 8 bytes |
| Quantity | 4 bytes |
| Side | 1 byte |
| Padding | 3 bytes |
| Timestamp | 8 bytes |
| Trade ID | 8 bytes |
| Buyer ID | 8 bytes |
| Seller ID | 8 bytes |
| Padding | 8 bytes |
| Total | 64 bytes |

BUY is represented by 0 and SELL by 1.

## 7. Memory-Mapped Ring Buffer

The ring buffer is implemented in `ipc/ring_buffer.py` using Python's `mmap` module.

It provides:

- Fixed-size record storage.
- Head and tail position tracking.
- Push and pop operations.
- Full and empty buffer checks.
- Zero-copy record access through `peek_view()` and `advance()`.

The implementation follows a single-producer, single-consumer design.

The current engine loop uses the `pop()` method to consume order records.

## 8. Performance Benchmark

The benchmark is implemented in `engine/bench_engine.py`.

It measures order-book processing throughput, P99 latency and total elapsed time.

### Test Configuration

- Random seed: 42
- Engine: CythonOrderBook
- Workloads: 1,000 and 1,000,000 orders

### Benchmark Results

| Metric | 1,000 Orders | 1,000,000 Orders |
|---|---:|---:|
| Throughput (orders/sec) | 20027.80 | 11717.34 |
| P99 Latency (ns) | 220500 | 465100 |
| Elapsed Time (sec) | 0.0499306 | 85.3436218 |

### Observations

- Both benchmark workloads completed successfully.
- Throughput decreased with the larger workload.
- P99 latency increased under the larger workload.
- The Cython order book was used in both runs.

These results measure the order-book benchmark path, not the complete ring-buffer processing pipeline.

## 9. Testing and Validation

The project includes tests covering:

- Python order-book matching.
- Cython order-book operations.
- Python and Cython matching parity.
- Order-book adapter selection.
- Engine-loop processing.
- Trade journal integration.
- Binary record handling.
- Ring-buffer operations.
- Statistics and dashboard functionality.

These tests help validate matching correctness, data handling and integration between project components.

## 10. Current Limitations

- The Cython order book uses a configured maximum price range.
- Finding the best available price involves scanning price levels.
- The current engine loop uses polling to check for incoming orders.
- The benchmark measures order-book performance rather than end-to-end pipeline latency.
- Performance can vary with workload size and system configuration.

## 11. Conclusion

ChronosMatch combines Python orchestration, Cython-based order matching, binary data records and memory-mapped ring buffers.

The project implements price-time priority, partial order execution, trade publication, performance measurement and monitoring support.

The Python reference implementation and optimized Cython implementation provide two matching paths, with automatic fallback when the compiled extension is unavailable.

The system provides a foundation for further optimization and integration testing of a low-latency trading engine.
