
import mmap
import os
import struct
import time

# Stats block layout: fixed-size header + 64 latency buckets
MAGIC = b"CHST"
VERSION = 1
LATENCY_BUCKETS = 64

# magic, version, trades, orders, best bid, best ask,
# last trade price, last trade quantity, heartbeat_ns
HEADER_FORMAT = "<4sIQQQQQQQ"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
BUCKET_FORMAT = "<" + ("Q" * LATENCY_BUCKETS)
BUCKET_SIZE = struct.calcsize(BUCKET_FORMAT)
STATS_SIZE = HEADER_SIZE + BUCKET_SIZE


class StatsBlock:
    """Shared stats file. The engine should be the only writer."""

    def __init__(self, path="stats.bin", create=False):
        self.path = path
        flags = os.O_RDWR | (os.O_CREAT if create else 0)

        if create:
            fd = os.open(path, flags, 0o600)
            try:
                os.ftruncate(fd, STATS_SIZE)
                self._file = os.fdopen(fd, "r+b")
            except Exception:
                os.close(fd)
                raise
        else:
            self._file = open(path, "r+b")
            if os.path.getsize(path) != STATS_SIZE:
                self._file.close()
                raise ValueError("Invalid stats.bin file size")

        self._mm = mmap.mmap(self._file.fileno(), STATS_SIZE)

        if create:
            self._write_header(
                trades=0,
                orders=0,
                best_bid=0,
                best_ask=0,
                last_trade_price=0,
                last_trade_quantity=0,
                heartbeat_ns=time.time_ns(),
            )
            self._write_buckets([0] * LATENCY_BUCKETS)
        else:
            values = self._read_header()
            if values[0] != MAGIC or values[1] != VERSION:
                self.close()
                raise ValueError("Invalid stats.bin magic or version")

    def _write_header(
        self, trades, orders, best_bid, best_ask,
        last_trade_price, last_trade_quantity, heartbeat_ns
    ):
        self._mm[:HEADER_SIZE] = struct.pack(
            HEADER_FORMAT,
            MAGIC,
            VERSION,
            trades,
            orders,
            best_bid,
            best_ask,
            last_trade_price,
            last_trade_quantity,
            heartbeat_ns,
        )

    def _read_header(self):
        return struct.unpack(HEADER_FORMAT, self._mm[:HEADER_SIZE])

    def _write_buckets(self, buckets):
        if len(buckets) != LATENCY_BUCKETS:
            raise ValueError("Expected 64 latency buckets")
        self._mm[HEADER_SIZE:] = struct.pack(BUCKET_FORMAT, *buckets)

    def snapshot(self):
        (
            magic, version, trades, orders, best_bid, best_ask,
            last_trade_price, last_trade_quantity, heartbeat_ns
        ) = self._read_header()

        buckets = struct.unpack(BUCKET_FORMAT, self._mm[HEADER_SIZE:])

        return {
            "version": version,
            "trades": trades,
            "orders": orders,
            "best_bid": best_bid,
            "best_ask": best_ask,
            "last_trade_price": last_trade_price,
            "last_trade_quantity": last_trade_quantity,
            "heartbeat_ns": heartbeat_ns,
            "latency_buckets": list(buckets),
        }

    def update(
        self, *, trades=None, orders=None, best_bid=None, best_ask=None,
        last_trade_price=None, last_trade_quantity=None, heartbeat_ns=None
    ):
        current = self._read_header()
        values = list(current[2:])

        updates = [
            trades, orders, best_bid, best_ask,
            last_trade_price, last_trade_quantity, heartbeat_ns
        ]

        for index, value in enumerate(updates):
            if value is not None:
                values[index] = value

        self._write_header(*values)

    def increment_latency_bucket(self, bucket_index):
        if not 0 <= bucket_index < LATENCY_BUCKETS:
            raise ValueError("bucket_index must be between 0 and 63")

        buckets = list(
            struct.unpack(BUCKET_FORMAT, self._mm[HEADER_SIZE:])
        )
        buckets[bucket_index] += 1
        self._write_buckets(buckets)

    def heartbeat(self):
        self.update(heartbeat_ns=time.time_ns())

    def close(self):
        if getattr(self, "_mm", None) is not None:
            self._mm.close()
            self._mm = None
        if getattr(self, "_file", None) is not None:
            self._file.close()
            self._file = None


class StatsReader:
    """Read shared engine statistics without modifying the file."""

    def __init__(self, path="stats.bin"):
        if os.path.getsize(path) != STATS_SIZE:
            raise ValueError("Invalid stats.bin file size")

        self.path = path
        self._file = open(path, "rb")
        try:
            self._mm = mmap.mmap(
                self._file.fileno(),
                STATS_SIZE,
                access=mmap.ACCESS_READ,
            )

            values = struct.unpack(
                HEADER_FORMAT, self._mm[:HEADER_SIZE]
            )
            if values[0] != MAGIC or values[1] != VERSION:
                raise ValueError("Invalid stats.bin magic or version")
        except Exception:
            if hasattr(self, "_mm"):
                self._mm.close()
            self._file.close()
            raise

    def snapshot(self):
        values = struct.unpack(
            HEADER_FORMAT, self._mm[:HEADER_SIZE]
        )
        buckets = struct.unpack(
            BUCKET_FORMAT, self._mm[HEADER_SIZE:]
        )

        return {
            "version": values[1],
            "trades": values[2],
            "orders": values[3],
            "best_bid": values[4],
            "best_ask": values[5],
            "last_trade_price": values[6],
            "last_trade_quantity": values[7],
            "heartbeat_ns": values[8],
            "latency_buckets": list(buckets),
        }

    def close(self):
        self._mm.close()
        self._file.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

