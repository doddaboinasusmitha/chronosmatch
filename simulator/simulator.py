import argparse
import asyncio

from ipc.journal import process_batch
from ipc.record import ORDER_SIZE
from ipc.ring_buffer import RingBuffer
from ipc.stats import StatsBlock
from ipc.trade import TRADE_SIZE, unpack_trade
from simulator.order_generator import OrderGenerator
from engine.matching_engine import MatchingEngine
from engine.order_book import OrderBook


async def run(
    count=1000,
    rate=1000,
    seed=None,
    ring="orders.ring",
    trade_ring="trades.ring",
    stats_file="stats.bin",
    journal_db=None,
):
    """Generate orders, run the engine, and optionally save trades."""
    if count < 0:
        raise ValueError("count must be non-negative")

    if rate < 0:
        raise ValueError("rate must be non-negative")

    order_buffer = None
    trade_buffer = None
    stats = None

    try:
        capacity = max(count, 1)

        order_buffer = RingBuffer(
            ring,
            capacity=capacity,
            record_size=ORDER_SIZE,
        )

        trade_buffer = RingBuffer(
            trade_ring,
            capacity=capacity,
            record_size=TRADE_SIZE,
        )

        stats = StatsBlock(stats_file, create=True)

        order_book = OrderBook()
        engine = MatchingEngine(order_book, trade_buffer, stats)
        generator = OrderGenerator(seed=seed)

        sent = 0
        processed = 0

        loop = asyncio.get_running_loop()
        start_time = loop.time()
        interval = 1.0 / rate if rate > 0 else 0.0

        for index in range(count):
            order = generator.generate_order()

            if not order_buffer.push(order):
                raise RuntimeError("Order ring buffer is full")

            sent += 1

            # Process the generated order directly. Keep the order in the
            # ring buffer so it remains available for later inspection.
            engine.process_order(order)
            processed += 1

            if interval:
                target_time = start_time + (index + 1) * interval
                delay = target_time - loop.time()

                if delay > 0:
                    await asyncio.sleep(delay)

        if journal_db is not None:
            saved_count = process_batch(
                trade_buffer,
                db_path=journal_db,
                batch_size=max(count, 1),
            )
            print(f"Trades saved to SQLite: {saved_count}")
        else:
            displayed = 0

            while not trade_buffer.is_empty():
                trade_data = trade_buffer.pop()
                trade = unpack_trade(trade_data)

                if displayed < 5:
                    print("Trade:", trade)

                displayed += 1

        snapshot = stats.snapshot()

        print(f"orders written: {sent}")
        print(f"Orders generated: {sent}")
        print(f"Orders processed: {processed}")
        print(f"Trades produced: {snapshot['trades']}")
        print(f"Orders in statistics: {snapshot['orders']}")
        print(f"Best bid: {snapshot['best_bid']}")
        print(f"Best ask: {snapshot['best_ask']}")
        print(f"Last trade price: {snapshot['last_trade_price']}")

    finally:
        if order_buffer is not None:
            order_buffer.close()

        if trade_buffer is not None:
            trade_buffer.close()

        if stats is not None:
            stats.close()


def main():
    parser = argparse.ArgumentParser(
        description="Run the ChronosMatch trading simulator"
    )
    parser.add_argument("--count", type=int, default=1000)
    parser.add_argument("--rate", type=float, default=1000)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--ring", default="orders.ring")
    parser.add_argument("--trade-ring", default="trades.ring")
    parser.add_argument("--stats-file", default="stats.bin")
    parser.add_argument("--journal-db", default=None)

    args = parser.parse_args()

    asyncio.run(
        run(
            count=args.count,
            rate=args.rate,
            seed=args.seed,
            ring=args.ring,
            trade_ring=args.trade_ring,
            stats_file=args.stats_file,
            journal_db=args.journal_db,
        )
    )


if __name__ == "__main__":
    main()
