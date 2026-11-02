import asyncio
import sqlite3

from ipc.record import unpack_order
from ipc.ring_buffer import RingBuffer
from simulator.simulator import run


def test_simulator_writes_requested_orders(tmp_path, capsys):
    ring_file = tmp_path / "orders.ring"
    trade_file = tmp_path / "trades.ring"
    stats_file = tmp_path / "stats.bin"

    asyncio.run(
        run(
            count=5,
            rate=0,
            seed=42,
            ring=str(ring_file),
            trade_ring=str(trade_file),
            stats_file=str(stats_file),
        )
    )

    output = capsys.readouterr().out

    assert "orders written: 5" in output
    assert "Orders generated: 5" in output
    assert "Orders processed: 5" in output
    assert ring_file.exists()

    rb = RingBuffer(
        str(ring_file),
        capacity=100000,
        create=False,
    )

    try:
        assert len(rb) == 5

        orders = [
            unpack_order(rb.pop())
            for _ in range(5)
        ]

        assert all(order is not None for order in orders)
        assert rb.is_empty()

    finally:
        rb.close()


def test_simulator_saves_trades_to_sqlite(tmp_path, capsys):
    ring_file = tmp_path / "orders.ring"
    trade_file = tmp_path / "trades.ring"
    stats_file = tmp_path / "stats.bin"
    database_file = tmp_path / "journal.db"

    asyncio.run(
        run(
            count=1000,
            rate=0,
            seed=42,
            ring=str(ring_file),
            trade_ring=str(trade_file),
            stats_file=str(stats_file),
            journal_db=str(database_file),
        )
    )

    output = capsys.readouterr().out

    assert "Orders generated: 1000" in output
    assert "Orders processed: 1000" in output

    with sqlite3.connect(database_file) as connection:
        trade_count = connection.execute(
            "SELECT COUNT(*) FROM trades"
        ).fetchone()[0]

    assert trade_count > 0
    assert f"Trades saved to SQLite: {trade_count}" in output
