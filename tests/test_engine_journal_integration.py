import sqlite3

from engine.engine_loop import run_engine
from ipc.journal import process_batch
from ipc.record import BUY, SELL, pack_order
from ipc.ring_buffer import RingBuffer
from ipc.stats import StatsBlock
from ipc.trade import TRADE_SIZE


def test_engine_loop_trade_is_saved_to_sqlite(tmp_path):
    order_path = tmp_path / "orders.ring"
    trade_path = tmp_path / "trades.ring"
    stats_path = tmp_path / "stats.bin"
    db_path = tmp_path / "journal.db"

    orders = RingBuffer(str(order_path), capacity=8)
    trades = RingBuffer(
        str(trade_path), capacity=8, record_size=TRADE_SIZE
    )
    stats = StatsBlock(str(stats_path), create=True)

    try:
        assert orders.push(pack_order(2, 10050, 5, SELL, 100))
        assert orders.push(pack_order(1, 10050, 5, BUY, 200))
    finally:
        orders.close()
        trades.close()
        stats.close()

    processed = run_engine(
        order_ring=str(order_path),
        trade_ring=str(trade_path),
        stats_file=str(stats_path),
        idle_timeout=0.02,
        poll_interval=0.001,
    )
    assert processed == 2

    trades = RingBuffer(
        str(trade_path), create=False, record_size=TRADE_SIZE
    )

    try:
        saved = process_batch(trades, str(db_path), batch_size=10)
        assert saved == 1
    finally:
        trades.close()

    with sqlite3.connect(db_path) as connection:
        rows = connection.execute(
            "SELECT order_id, price, quantity, side, trade_id, "
            "buyer_id, seller_id FROM trades"
        ).fetchall()

    assert len(rows) == 1
    assert rows[0] == (1, 10050, 5, BUY, 1, 1, 2)
