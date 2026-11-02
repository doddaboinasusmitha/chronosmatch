# Zero-Copy Data Flow in ChronosMatch

## 1. Introduction

ChronosMatch uses a memory-mapped ring buffer to share fixed-size records between processes.

The ring buffer is implemented using Python's `mmap` module. It supports both normal record copying and zero-copy record access.

Zero-copy access reduces unnecessary data copying when reading records from the mapped buffer.

## 2. Memory-Mapped Ring Buffer

The ring buffer is stored in a file and mapped into memory using `mmap`.

Its layout contains:

- A 64-byte header.
- A fixed-size record area.
- Head and tail counters to track produced and consumed records.
- A capacity value to define the maximum number of records.

The producer writes records into the buffer, and the consumer reads and consumes them.

## 3. Zero-Copy Reading

ChronosMatch provides two methods for zero-copy reading.

### peek_view()

The `peek_view()` method returns a Python `memoryview` that directly references the next record inside the memory-mapped file.

It does not create a separate copy of the record.

Example:

```python
view = ring.peek_view()

if view is not None:
    print(view)
```

### advance()

The `advance()` method moves the tail counter to consume the current record.

It does not copy the record data.

Example:

```python
view = ring.peek_view()

if view is not None:
    try:
        process_record(view)
    finally:
        view.release()

    ring.advance()
```

The memoryview should be released before consuming or reusing the underlying buffer slot.

## 4. Normal Copying Method

The `pop()` method reads the next record and converts it into a new `bytes` object.

Example:

```python
record = ring.pop()
```

This creates a copy of the record data.

The simulator and `ipc/check_pipe.py` currently use this normal copying method.

## 5. Data Flow in the Trade Journal

The `ipc/journal.py` module uses the zero-copy reading methods.

Its processing flow is:

1. Read the next trade using `peek_view()`.
2. Decode the memoryview using `unpack_trade()`.
3. Release the memoryview.
4. Insert the decoded trade into SQLite.
5. Commit the database transaction.
6. Consume the trade using `advance()`.

Although the ring-buffer read uses a zero-copy memoryview, decoding creates Python data objects and SQLite performs database storage operations. Therefore, the complete journaling pipeline is not zero-copy.

## 6. Where Copying Happens

| Operation | Data handling |
|---|---|
| `mmap` access | Shared mapped memory |
| `peek_view()` | Zero-copy memoryview |
| `advance()` | Updates tail counter without copying |
| `pop()` | Copies record into a bytes object |
| `push()` | Copies supplied record bytes into mapped memory |
| `unpack_trade()` | Decodes record into Python data |
| SQLite insertion | Stores decoded values in the database |
| Order ledger | JSON serialization and file writing |

## 7. Benchmarking

The `ipc/bench_ring.py` module compares:

- Normal copying using `pop()`.
- Zero-copy reading using `peek_view()` and `advance()`.

The benchmark helps evaluate the performance difference between the two approaches.

Actual performance depends on the system, workload, and record size.

## 8. Conclusion

ChronosMatch supports zero-copy reading through memory-mapped files, `peek_view()`, and `advance()`.

The approach reduces record copying during ring-buffer consumption. However, decoding, database insertion, and other processing steps may still involve data conversion or copying.

Therefore, ChronosMatch uses zero-copy access in selected parts of its data flow rather than providing a completely zero-copy pipeline.