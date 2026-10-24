import pytest
import os
import sqlite3
import tempfile
from contextlib import closing

from ipc.journal import process_batch
from ipc.ring_buffer import RingBuffer
from ipc.trade import TRADE_SIZE, pack_trade


def test_process_batch_saves_trades():
    with tempfile.TemporaryDirectory() as folder:
        ring_path = os.path.join(folder, "trades.ring")
        db_path = os.path.join(folder, "journal.db")
        ring = RingBuffer(ring_path, capacity=10, record_size=TRADE_SIZE)

        try:
            for trade_id in (1, 2, 3):
                record = pack_trade(
                    trade_id, 1000, 2, 0, 123456,
                    trade_id, 10, 20
                )
                assert ring.push(record)

            first = process_batch(ring, db_path, batch_size=2)
            second = process_batch(ring, db_path, batch_size=2)

            with closing(sqlite3.connect(db_path)) as connection:
                count = connection.execute(
                    "SELECT COUNT(*) FROM trades"
                ).fetchone()[0]

            assert first == 2
            assert second == 1
            assert count == 3
        finally:
            ring.close()

def test_duplicate_trade_id_is_ignored():
    with tempfile.TemporaryDirectory() as folder:
        ring_path = os.path.join(folder, "trades.ring")
        db_path = os.path.join(folder, "journal.db")
        ring = RingBuffer(ring_path, capacity=10, record_size=TRADE_SIZE)

        try:
            for _ in range(2):
                record = pack_trade(
                    1, 1000, 2, 0, 123456,
                    99, 10, 20
                )
                assert ring.push(record)

            processed = process_batch(ring, db_path, batch_size=10)

            with closing(sqlite3.connect(db_path)) as connection:
                count = connection.execute(
                    "SELECT COUNT(*) FROM trades WHERE trade_id = 99"
                ).fetchone()[0]

            assert processed == 2
            assert count == 1
        finally:
            ring.close()

def test_restart_does_not_duplicate_saved_trades():
    with tempfile.TemporaryDirectory() as folder:
        ring_path = os.path.join(folder, "trades.ring")
        db_path = os.path.join(folder, "journal.db")

        ring = RingBuffer(ring_path, capacity=10, record_size=TRADE_SIZE)

        try:
            record = pack_trade(1, 1000, 2, 0, 123456, 99, 10, 20)
            assert ring.push(record)
            assert process_batch(ring, db_path, batch_size=10) == 1
        finally:
            ring.close()

        # Simulate the same trade appearing again after restart.
        restarted_ring = RingBuffer(
            ring_path, capacity=10, record_size=TRADE_SIZE
        )
        try:
            record = pack_trade(1, 1000, 2, 0, 123456, 99, 10, 20)
            assert restarted_ring.push(record)
            assert process_batch(restarted_ring, db_path, batch_size=10) == 1
        finally:
            restarted_ring.close()

        with closing(sqlite3.connect(db_path)) as connection:
            count = connection.execute(
                "SELECT COUNT(*) FROM trades WHERE trade_id = 99"
            ).fetchone()[0]

        assert count == 1

def test_database_failure_does_not_lose_trade():
    with tempfile.TemporaryDirectory() as folder:
        ring_path = os.path.join(folder, "trades.ring")
        ring = RingBuffer(ring_path, capacity=10, record_size=TRADE_SIZE)

        try:
            record = pack_trade(1, 1000, 2, 0, 123456, 99, 10, 20)
            assert ring.push(record)

            with pytest.raises(sqlite3.OperationalError):
                process_batch(ring, folder, batch_size=10)

            assert len(ring) == 1
        finally:
            ring.close()
