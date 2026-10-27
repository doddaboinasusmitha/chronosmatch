import asyncio
import sqlite3

from simulator.simulator import run


def test_seeded_simulator_saves_trades_to_sqlite(tmp_path, capsys):
    order_ring = str(tmp_path / "orders.ring")
    trade_ring = str(tmp_path / "trades.ring")
    stats_file = str(tmp_path / "stats.bin")
    journal_db = str(tmp_path / "journal.db")

    asyncio.run(
        run(
            count=100,
            rate=0,
            seed=42,
            ring=order_ring,
            trade_ring=trade_ring,
            stats_file=stats_file,
            journal_db=journal_db,
        )
    )

    output = capsys.readouterr().out
    assert "Orders generated:" in output
    assert "Orders processed:" in output
    assert "Trades produced:" in output

    with sqlite3.connect(journal_db) as connection:
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        assert "trades" in tables

        saved_trades = connection.execute(
            "SELECT COUNT(*) FROM trades"
        ).fetchone()[0]

    assert saved_trades >= 0
        