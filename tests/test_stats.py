
from ipc.stats import StatsBlock, STATS_SIZE, LATENCY_BUCKETS


def test_stats_block_initializes_and_has_64_latency_buckets(tmp_path):
    path = tmp_path / "stats.bin"

    stats = StatsBlock(path=str(path), create=True)
    try:
        snapshot = stats.snapshot()

        assert path.stat().st_size == STATS_SIZE
        assert snapshot["trades"] == 0
        assert snapshot["orders"] == 0
        assert len(snapshot["latency_buckets"]) == LATENCY_BUCKETS
        assert all(value == 0 for value in snapshot["latency_buckets"])
    finally:
        stats.close()


def test_stats_update_and_heartbeat(tmp_path):
    path = tmp_path / "stats.bin"

    stats = StatsBlock(path=str(path), create=True)
    try:
        stats.update(
            trades=5,
            orders=10,
            best_bid=100,
            best_ask=105,
            last_trade_price=102,
            last_trade_quantity=3,
        )

        snapshot = stats.snapshot()
        assert snapshot["trades"] == 5
        assert snapshot["orders"] == 10
        assert snapshot["best_bid"] == 100
        assert snapshot["best_ask"] == 105
        assert snapshot["last_trade_price"] == 102
        assert snapshot["last_trade_quantity"] == 3

        old_heartbeat = snapshot["heartbeat_ns"]
        stats.heartbeat()
        assert stats.snapshot()["heartbeat_ns"] >= old_heartbeat
    finally:
        stats.close()


def test_increment_latency_bucket(tmp_path):
    path = tmp_path / "stats.bin"

    stats = StatsBlock(path=str(path), create=True)
    try:
        stats.increment_latency_bucket(0)
        stats.increment_latency_bucket(63)

        buckets = stats.snapshot()["latency_buckets"]
        assert buckets[0] == 1
        assert buckets[63] == 1
    finally:
        stats.close()


def test_invalid_latency_bucket_raises_value_error(tmp_path):
    path = tmp_path / "stats.bin"

    stats = StatsBlock(path=str(path), create=True)
    try:
        import pytest

        with pytest.raises(ValueError):
            stats.increment_latency_bucket(64)
    finally:
        stats.close()


def test_writer_and_reader_share_stats(tmp_path):
    path = tmp_path / "stats.bin"

    writer = StatsBlock(path=str(path), create=True)
    reader = None

    try:
        writer.update(trades=7, orders=12)

        reader = StatsBlock(path=str(path), create=False)
        snapshot = reader.snapshot()

        assert snapshot["trades"] == 7
        assert snapshot["orders"] == 12
    finally:
        if reader is not None:
            reader.close()
        writer.close()
