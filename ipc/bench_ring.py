
"""Benchmark copying pop() against zero-copy peek_view() + advance()."""

import os
import tempfile
import time

from ipc.ring_buffer import RingBuffer


ITERATIONS = 200_000
CAPACITY = 1024
RECORD_SIZE = 32
PAYLOAD = b"\x01" * RECORD_SIZE


def benchmark(mode):
    with tempfile.TemporaryDirectory() as temp_dir:
        path = os.path.join(temp_dir, "benchmark.ring")
        rb = RingBuffer(path, capacity=CAPACITY)

        try:
            # Fill the ring before timing.
            for _ in range(CAPACITY):
                if not rb.push(PAYLOAD):
                    raise RuntimeError("Could not fill ring buffer")

            start = time.perf_counter_ns()

            for _ in range(ITERATIONS):
                if mode == "pop":
                    record = rb.pop()
                    if record is None:
                        raise RuntimeError("pop() returned no record")
                    del record
                else:
                    view = rb.peek_view()
                    if view is None:
                        raise RuntimeError("peek_view() returned no record")
                    view.release()

                    if not rb.advance():
                        raise RuntimeError("advance() failed")

                # Keep occupancy constant for both benchmarks.
                if not rb.push(PAYLOAD):
                    raise RuntimeError("Could not refill ring buffer")

            elapsed_ns = time.perf_counter_ns() - start
            elapsed_seconds = elapsed_ns / 1_000_000_000
            ops_per_second = ITERATIONS / elapsed_seconds

            return elapsed_seconds, ops_per_second
        finally:
            rb.close()


def main():
    for mode, label in [
        ("pop", "Copying pop()"),
        ("view", "Zero-copy peek_view() + advance()"),
    ]:
        elapsed, throughput = benchmark(mode)
        print(f"{label}:")
        print(f"  Iterations: {ITERATIONS:,}")
        print(f"  Time:       {elapsed:.4f} seconds")
        print(f"  Throughput: {throughput:,.0f} operations/sec")
        print()


if __name__ == "__main__":
    main()
