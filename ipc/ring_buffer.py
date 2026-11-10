import mmap
import struct
import time

from ipc.record import ORDER_SIZE

HEADER_FORMAT = "<QQQ"
HEADER_SIZE = 64


class RingBuffer:
    """Single-producer, single-consumer memory-mapped ring buffer."""

    def __init__(
        self,
        path,
        capacity=1024,
        create=True,
        record_size=ORDER_SIZE,
        timeout=5.0,
        retry_interval=0.1,
    ):
        if record_size <= 0:
            raise ValueError("record_size must be positive")
        if create and capacity <= 0:
            raise ValueError("capacity must be positive")
        if timeout < 0:
            raise ValueError("timeout must be non-negative")
        if retry_interval <= 0:
            raise ValueError("retry_interval must be positive")

        self.record_size = record_size

        if create:
            with open(path, "wb") as file:
                file.truncate(HEADER_SIZE + capacity * record_size)

        deadline = time.monotonic() + timeout

        while True:
            try:
                self._file = open(path, "r+b")
                break
            except FileNotFoundError:
                if create or time.monotonic() >= deadline:
                    raise TimeoutError(
                        f"Timed out waiting for ring buffer file: {path}"
                    )
                time.sleep(
                    min(retry_interval, max(0, deadline - time.monotonic()))
                )

        self._mm = None

        try:
            self._mm = mmap.mmap(self._file.fileno(), 0)

            if create:
                struct.pack_into(
                    HEADER_FORMAT, self._mm, 0, 0, 0, capacity
                )

            self.capacity = struct.unpack_from("<Q", self._mm, 16)[0]

            if self.capacity <= 0:
                raise ValueError(
                    "Ring buffer header capacity must be positive"
                )

            expected_size = HEADER_SIZE + self.capacity * self.record_size

            if len(self._mm) != expected_size:
                raise ValueError(
                    f"Ring buffer file size mismatch: expected {expected_size} "
                    f"bytes, got {len(self._mm)} bytes"
                )

        except Exception:
            if self._mm is not None:
                self._mm.close()
            self._file.close()
            raise

    def _head(self):
        return struct.unpack_from("<Q", self._mm, 0)[0]

    def _tail(self):
        return struct.unpack_from("<Q", self._mm, 8)[0]

    def __len__(self):
        return self._head() - self._tail()

    def is_empty(self):
        return len(self) == 0

    def is_full(self):
        return len(self) >= self.capacity

    def push(self, record):
        """Add a record. Return False if the buffer is full."""
        if len(record) != self.record_size:
            raise ValueError(
                f"Expected {self.record_size} bytes, got {len(record)} bytes"
            )

        head = self._head()
        tail = self._tail()

        if head - tail >= self.capacity:
            return False

        offset = HEADER_SIZE + (head % self.capacity) * self.record_size
        self._mm[offset:offset + self.record_size] = record
        struct.pack_into("<Q", self._mm, 0, head + 1)

        return True

    def peek_view(self):
        """Return a zero-copy memoryview of the next record."""
        tail = self._tail()

        if self._head() == tail:
            return None

        offset = HEADER_SIZE + (tail % self.capacity) * self.record_size
        return memoryview(self._mm)[offset:offset + self.record_size]

    def advance(self):
        """Consume the next record after processing it."""
        tail = self._tail()

        if self._head() == tail:
            return False

        struct.pack_into("<Q", self._mm, 8, tail + 1)
        return True

    def pop(self):
        """Read and remove the next record, returning independent bytes."""
        view = self.peek_view()

        if view is None:
            return None

        try:
            record = bytes(view)
        finally:
            view.release()

        self.advance()
        return record

    def close(self):
        """Close the memory map and file safely."""
        if self._mm is not None and not self._mm.closed:
            self._mm.close()

        if not self._file.closed:
            self._file.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


if __name__ == "__main__":
    print("RingBuffer module loaded successfully.")
