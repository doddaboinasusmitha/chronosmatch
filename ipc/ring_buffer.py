import mmap
import struct

from ipc.record import ORDER_SIZE

# Header: head counter, tail counter, capacity
HEADER_FORMAT = "<QQQ"
HEADER_SIZE = 64


class RingBuffer:
    """Single-producer, single-consumer ring buffer using a memory-mapped file."""

    def __init__(self, path, capacity=1024, create=True, record_size=ORDER_SIZE):
        if capacity < 1:
            raise ValueError("Capacity must be at least 1")

        if record_size < 1:
            raise ValueError("Record size must be at least 1")

        self.record_size = record_size

        if create:
            with open(path, "wb") as file:
                file.truncate(HEADER_SIZE + capacity * record_size)

        self._file = open(path, "r+b")
        self._mm = mmap.mmap(self._file.fileno(), 0)

        if create:
            struct.pack_into(
                HEADER_FORMAT, self._mm, 0, 0, 0, capacity
            )

        self.capacity = struct.unpack_from("<Q", self._mm, 16)[0]

        expected_size = HEADER_SIZE + self.capacity * self.record_size

        if len(self._mm) != expected_size:
            self._mm.close()
            self._file.close()
            raise ValueError(
                f"Buffer size mismatch: expected {expected_size} bytes"
            )

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
        """Read the next record without removing it."""
        tail = self._tail()

        if self._head() == tail:
            return None

        offset = HEADER_SIZE + (tail % self.capacity) * self.record_size

        return bytes(self._mm[offset:offset + self.record_size])

    def advance(self):
        """Remove the next record after it has been processed."""
        tail = self._tail()

        if self._head() == tail:
            return False

        struct.pack_into("<Q", self._mm, 8, tail + 1)

        return True

    def pop(self):
        """Read and remove the next record."""
        record = self.peek_view()

        if record is None:
            return None

        self.advance()

        return record

    def close(self):
        """Close the memory map and file safely."""
        if not self._mm.closed:
            self._mm.close()

        if not self._file.closed:
            self._file.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


if __name__ == "__main__":
    print("RingBuffer module loaded successfully.")