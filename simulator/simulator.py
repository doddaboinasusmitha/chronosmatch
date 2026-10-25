
import argparse
import asyncio

from ipc.ring_buffer import RingBuffer
from simulator.order_generator import OrderGenerator
from ipc.trade import TRADE_SIZE, unpack_trade
from ipc.stats import StatsBlock
from ipc.journal import process_batch
from engine.book_adapter import create_order_book
from engine.matching_engine import MatchingEngine


async def run(
    count=1000,
    rate=1000,
    seed=None,
    ring="orders.ring",
    trade_ring="trades.ring",
    stats_file="stats.bin",
    journal_db=None,
):
    if count < 0:
        raise ValueError("count must be zero or greater")
    if rate < 0:
        raise ValueError("rate cannot be negative")

    order_buffer = RingBuffer(ring, capacity=100000)
    trade_buffer = None
    stats = None

    try:
        generator = OrderGenerator(seed=seed)

        trade_buffer = RingBuffer(
            trade_ring,
            capacity=100000,
            record_size=TRADE_SIZE,
        )
        stats = StatsBlock(stats_file, create=True)

        engine = MatchingEngine(
            create_order_book(),
            trade_buffer,
            stats,
        )

        sent = 0
        interval = 1 / rate if rate > 0 else 0
        loop = asyncio.get_running_loop()
        start_time = loop.time()

        for i in range(count):
            order = generator.generate_order()

            if order_buffer.push(order):
                sent += 1
            else:
                raise BufferError("Order ring buffer is full")

            if interval > 0:
                target_time = start_time + (i + 1) * interval
                delay = target_time - loop.time()
                if delay > 0:
                    await asyncio.sleep(delay)
            else:
                await asyncio.sleep(0)

        processed = 0
        while not order_buffer.is_empty():
            order = order_buffer.pop()
            if order is not None:
                engine.process_order(order)
                processed += 1

        trade_count = 0

        if journal_db is not None:
            trade_count = process_batch(
                trade_buffer,
                db_path=journal_db,
                batch_size=100000,
            )
            print("Trades saved to SQLite:", trade_count)
        else:
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

        if trade_buffer is not None:
            trade_buffer.close()

        if stats is not None:
            stats.close()


def main():
    parser = argparse.ArgumentParser(
        description="ChronosMatch order simulator"
    )
    parser.add_argument("--count", type=int, default=1000)
    parser.add_argument("--rate", type=float, default=1000)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--ring", default="orders.ring")
    parser.add_argument("--trade-ring", default="trades.ring")
    parser.add_argument("--stats-file", default="stats.bin")
    parser.add_argument(
        "--journal-db",
        default=None,
        help="Optional SQLite database path for saving trades",
    )

    args = parser.parse_args()

    if args.count < 0:
        parser.error("--count must be zero or greater")

    if args.rate < 0:
        parser.error("--rate cannot be negative")

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
