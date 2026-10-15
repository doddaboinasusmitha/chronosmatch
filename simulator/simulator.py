
import asyncio

from simulator.order_generator import generate_order
from ipc.ring_buffer import RingBuffer
from ipc.trade import TRADE_SIZE, unpack_trade
from ipc.stats import StatsBlock
from engine.order_book import OrderBook
from engine.matching_engine import MatchingEngine


async def run(count=1000):
    order_buffer = RingBuffer("orders.ring", capacity=100000)
    trade_buffer = RingBuffer(
        "trades.ring",
        capacity=100000,
        record_size=TRADE_SIZE,
    )
    stats = StatsBlock("stats.bin", create=True)

    try:
        engine = MatchingEngine(OrderBook(), trade_buffer, stats)

        sent = 0
        for _ in range(count):
            if order_buffer.push(generate_order()):
                sent += 1
            else:
                raise BufferError("Order ring buffer is full")

        processed = 0
        while not order_buffer.is_empty():
            order = order_buffer.pop()
            if order is not None:
                engine.process_order(order)
                processed += 1

        trade_count = 0
        while not trade_buffer.is_empty():
            record = trade_buffer.pop()
            if record is not None:
                trade = unpack_trade(record)
                trade_count += 1
                if trade_count <= 5:
                    print("Trade:", trade)

        snapshot = stats.snapshot()
        print("\n--- ChronosMatch Results ---")
        print("Orders generated:", sent)
        print("Orders processed:", processed)
        print("Trades produced:", trade_count)
        print("Orders in statistics:", snapshot["orders"])
        print("Best bid:", snapshot["best_bid"])
        print("Best ask:", snapshot["best_ask"])
        print("Last trade price:", snapshot["last_trade_price"])

    finally:
        order_buffer.close()
        trade_buffer.close()
        stats.close()


if __name__ == "__main__":
    asyncio.run(run())
