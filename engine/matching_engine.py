
import time

from engine.metrics import calculate_latency_ns, latency_bucket_index
from engine.order_book import OrderBook
from ipc.record import BUY, SELL, unpack_order
from ipc.trade import pack_trade, TRADE_SIZE


class MatchingEngine:
    """Connect the order book to the trade ring buffer and statistics."""

    def __init__(self, order_book, trade_buffer, stats):
        self.order_book = order_book
        self.trade_buffer = trade_buffer
        self.stats = stats
        self.trade_id = 0

    def process_order(self, order_data):
        """Match one packed order and publish its resulting trades."""
        order_count = self.stats.snapshot()["orders"] + 1

        order = unpack_order(order_data)
        latency_ns = calculate_latency_ns(order["timestamp_ns"])

        if latency_ns is not None:
            bucket_index = latency_bucket_index(latency_ns)
            self.stats.increment_latency_bucket(bucket_index)

        trades = self.order_book.add_order(order_data)

        for trade in trades:
            self.trade_id += 1
            timestamp_ns = time.time_ns()

            # Use the buyer ID as the record's order_id and BUY as side.
            record = pack_trade(
                trade.buy_order_id,
                trade.price,
                trade.quantity,
                BUY,
                timestamp_ns,
                self.trade_id,
                trade.buy_order_id,
                trade.sell_order_id,
            )

            if not self.trade_buffer.push(record):
                raise BufferError("Trade ring buffer is full")

            self.stats.update(
                trades=self.stats.snapshot()["trades"] + 1,
                last_trade_price=trade.price,
                last_trade_quantity=trade.quantity,
            )

        best_bid = self.order_book.get_best_bid()
        best_ask = self.order_book.get_best_ask()

        self.stats.update(
            orders=order_count,
            best_bid=best_bid or 0,
            best_ask=best_ask or 0,
            heartbeat_ns=time.time_ns(),
        )

        return trades
