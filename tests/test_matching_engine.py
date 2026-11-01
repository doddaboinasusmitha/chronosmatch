
from ipc.record import BUY, SELL, pack_order
from ipc.ring_buffer import RingBuffer
from ipc.trade import unpack_trade
from ipc.stats import StatsBlock
from engine.order_book import OrderBook
from engine.matching_engine import MatchingEngine


def test_matching_engine_publishes_trade_and_updates_stats(tmp_path):
    order_buffer = RingBuffer(
        str(tmp_path / "orders.ring"), capacity=8
    )
    trade_buffer = RingBuffer(
        str(tmp_path / "trades.ring"),
        capacity=8,
        record_size=64,
    )
    stats = StatsBlock(str(tmp_path / "stats.bin"), create=True)

    try:
        engine = MatchingEngine(OrderBook(), trade_buffer, stats)

        # First order rests in the book.
        sell = pack_order(2, 10050, 5, SELL, 100)
        engine.process_order(sell)

        # Second order crosses the resting ask and executes a trade.
        buy = pack_order(1, 10050, 5, BUY, 200)
        trades = engine.process_order(buy)

        assert len(trades) == 1
        assert trades[0].price == 10050
        assert trades[0].quantity == 5

        stored = trade_buffer.pop()
        result = unpack_trade(stored)

        assert result["price"] == 10050
        assert result["quantity"] == 5
        assert result["buyer_id"] == 1
        assert result["seller_id"] == 2

        snapshot = stats.snapshot()
        assert snapshot["orders"] == 2
        assert snapshot["trades"] == 1
        assert snapshot["last_trade_price"] == 10050
        assert snapshot["last_trade_quantity"] == 5
    finally:
        order_buffer.close()
        trade_buffer.close()
        stats.close()

