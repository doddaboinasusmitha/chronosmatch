
import pytest

from ipc.stats import STATS_SIZE, StatsBlock, StatsReader


def test_stats_reader_reads_engine_statistics(tmp_path):
    path = tmp_path / "stats.bin"
    writer = StatsBlock(str(path), create=True)

    writer.update(
        orders=10,
        trades=3,
        best_bid=10000,
        best_ask=10020,
        last_trade_price=10010,
        last_trade_quantity=5,
        heartbeat_ns=123456,
    )
    writer.increment_latency_bucket(4)
    writer.close()

    with StatsReader(str(path)) as reader:
        snapshot = reader.snapshot()

    assert snapshot["orders"] == 10
    assert snapshot["trades"] == 3
    assert snapshot["best_bid"] == 10000
    assert snapshot["best_ask"] == 10020
    assert snapshot["last_trade_price"] == 10010
    assert snapshot["last_trade_quantity"] == 5
    assert snapshot["heartbeat_ns"] == 123456
    assert len(snapshot["latency_buckets"]) == 64
    assert snapshot["latency_buckets"][4] == 1


def test_stats_reader_rejects_wrong_file_size(tmp_path):
    path = tmp_path / "stats.bin"
    path.write_bytes(b"invalid")

    with pytest.raises(ValueError, match="file size"):
        StatsReader(str(path))


def test_stats_reader_rejects_invalid_header(tmp_path):
    path = tmp_path / "stats.bin"
    path.write_bytes(bytes(STATS_SIZE))

    with pytest.raises(ValueError, match="magic or version"):
        StatsReader(str(path))
