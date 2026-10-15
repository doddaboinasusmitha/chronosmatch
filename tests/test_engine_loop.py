
from engine.engine_loop import run_engine
from ipc.record import BUY, SELL, pack_order
from ipc.ring_buffer import RingBuffer
from ipc.stats import StatsBlock
from ipc.trade import TRADE_SIZE, unpack_trade


def test_engine_loop_processes_orders_and_publishes_trade(tmp_path):
    order_path = tmp_path / "orders.ring"
    trade_path = tmp_path / "trades.ring"
    stats_path = tmp_path / "stats.bin"

    orders = RingBuffer(str(order_path), capacity=8, create=True)
    trades = RingBuffer(
        str(trade_path),
        capacity=8,
        create=True,
        record_size=TRADE_SIZE,
    )
    stats = StatsBlock(str(stats_path), create=True)

    try:
        assert orders.push(pack_order(1, 10000, 10, BUY, 1))
        assert orders.push(pack_order(2, 9990, 5, SELL, 2))
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
        str(trade_path),
        create=False,
        record_size=TRADE_SIZE,
    )
    stats = StatsBlock(str(stats_path), create=False)

    try:
        record = trades.pop()
        assert record is not None

        trade = unpack_trade(record)
        assert trade["quantity"] == 5
        assert trade["trade_id"] == 1

        snapshot = stats.snapshot()
        assert snapshot["orders"] == 2
        assert snapshot["trades"] == 1
    finally:
        trades.close()
        stats.close()
