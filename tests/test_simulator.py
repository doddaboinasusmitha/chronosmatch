
import asyncio
import sqlite3

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

    assert ring_file.exists()
    assert "Orders generated: 5" in output
    assert "Orders processed: 5" in output


def test_simulator_saves_trades_to_sqlite(tmp_path, capsys):
    order_file = tmp_path / "orders.ring"
    trade_file = tmp_path / "trades.ring"
    stats_file = tmp_path / "stats.bin"
    database_file = tmp_path / "journal.db"

    asyncio.run(
        run(
            count=1000,
            rate=0,
            seed=42,
            ring=str(order_file),
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

        saved_count = connection.execute(
            "SELECT COUNT(*) FROM trades WHERE trade_id IS NOT NULL"
        ).fetchone()[0]

        assert saved_count == trade_count

    assert f"Trades saved to SQLite: {trade_count}" in output
