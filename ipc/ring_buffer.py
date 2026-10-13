
import mmap
import struct

from ipc.record import ORDER_SIZE

HEADER_FORMAT = "<QQQ"
HEADER_SIZE = 64


class RingBuffer:
    """Single-producer, single-consumer ring buffer."""

    def __init__(self, path, capacity=1024, create=True, record_size=ORDER_SIZE):
        if record_size <= 0:
            raise ValueError("record_size must be positive")

        self.record_size = record_size

        if create:
            with open(path, "wb") as f:
                f.truncate(HEADER_SIZE + capacity * self.record_size)

        self._file = open(path, "r+b")
        self._mm = mmap.mmap(self._file.fileno(), 0)

        if create:
            struct.pack_into(HEADER_FORMAT, self._mm, 0, 0, 0, capacity)

        self.capacity = struct.unpack_from("<Q", self._mm, 16)[0]

        expected_size = HEADER_SIZE + self.capacity * self.record_size
        if len(self._mm) != expected_size:
            self._mm.close()
            self._file.close()
            raise ValueError("Ring buffer file size does not match record_size")

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
        if len(record) != self.record_size:
            raise ValueError(
                f"Expected {self.record_size} bytes, got {len(record)} bytes"
            )

        head = self._head()
        if head - self._tail() >= self.capacity:
            return False

        offset = HEADER_SIZE + (head % self.capacity) * self.record_size
        self._mm[offset:offset + self.record_size] = record
        struct.pack_into("<Q", self._mm, 0, head + 1)
        return True

    def pop(self):
        tail = self._tail()
        if self._head() == tail:
            return None

        offset = HEADER_SIZE + (tail % self.capacity) * self.record_size
        record = bytes(self._mm[offset:offset + self.record_size])
        struct.pack_into("<Q", self._mm, 8, tail + 1)
        return record

    def close(self):
        self._mm.close()
        self._file.close()


if __name__ == "__main__":
    from ipc.record import BUY, SELL, pack_order, unpack_order

    rb = RingBuffer("demo.ring", capacity=4)

    for i in range(1, 5):
        print("push", i, rb.push(pack_order(i, 10000 + i, 10, BUY, i)))

    print("push when full:", rb.push(pack_order(5, 10005, 10, SELL, 5)))
    print("pop:", unpack_order(rb.pop()))
    print("pop:", unpack_order(rb.pop()))
    print("push after wrap:", rb.push(pack_order(6, 10006, 10, SELL, 6)))
    print("items in buffer:", len(rb))

    rb.close()
