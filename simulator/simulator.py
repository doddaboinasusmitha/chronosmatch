import argparse
import asyncio

from ipc.ring_buffer import RingBuffer
from ipc.record import ORDER_SIZE
from ipc.trade import TRADE_SIZE, unpack_trade
from ipc.stats import StatsBlock
from ipc.journal import process_batch

from simulator.order_generator import OrderGenerator
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
    """Generate orders, run the matching engine, and report results."""

    if count < 0:
        raise ValueError("count must be non-negative")

    if rate < 0:
        raise ValueError("rate must be non-negative")

    order_buffer = None
    trade_buffer = None
    stats = None

    sent = 0
    processed = 0
    trade_count = 0

    try:
        # Create the order ring buffer.
        order_buffer = RingBuffer(
            ring,
            capacity=max(count, 1),
            record_size=ORDER_SIZE,
        )

        # Create the trade ring buffer.
        trade_buffer = RingBuffer(
            trade_ring,
            capacity=max(count, 1),
            record_size=TRADE_SIZE,
        )

        # Create statistics storage.
        stats = StatsBlock(stats_file, create=True)

        # Initialize matching engine.
        order_book = create_order_book()

        engine = MatchingEngine(
            order_book,
            trade_buffer,
            stats,
        )

        # Initialize deterministic order generator.
        generator = OrderGenerator(seed=seed)

        # Generate orders, write to ring, and process them.
        for _ in range(count):
            order = generator.generate_order()

            # Store the order in the order ring buffer.
            if not order_buffer.push(order):
                raise RuntimeError("Order buffer is full")

            sent += 1

            # Process the same order without removing it from the ring.
            engine.process_order(order)
            processed += 1

            if rate > 0:
                await asyncio.sleep(1 / rate)

        # Process trades produced by the matching engine.
        if journal_db is not None:
            trade_count = process_batch(
                trade_buffer,
                db_path=journal_db,
                batch_size=max(count, 1),
            )

            print("Trades saved to SQLite:", trade_count)

        else:
            while not trade_buffer.is_empty():
                record = trade_buffer.pop()

                if record is None:
                    break

                trade = unpack_trade(record)
                trade_count += 1

                if trade_count <= 5:
                    print("Trade:", trade)

        # Read final statistics.
        snapshot = stats.snapshot()

        print("\n--- ChronosMatch Results ---")
        print("orders written:", sent)
        print("Orders generated:", sent)
        print("Orders processed:", processed)
        print("Trades produced:", trade_count)
        print("Orders in statistics:", snapshot["orders"])
        print("Best bid:", snapshot["best_bid"])
        print("Best ask:", snapshot["best_ask"])
        print("Last trade price:", snapshot["last_trade_price"])

    finally:
        if order_buffer is not None:
            order_buffer.close()

        if trade_buffer is not None:
            trade_buffer.close()

        if stats is not None:
            stats.close()


def main():
    parser = argparse.ArgumentParser(
        description="ChronosMatch order-book simulator"
    )

    parser.add_argument("--count", type=int, default=1000)
    parser.add_argument("--rate", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--ring", default="orders.ring")
    parser.add_argument("--trade-ring", default="trades.ring")
    parser.add_argument("--stats-file", default="stats.bin")
    parser.add_argument("--journal-db", default=None)

    args = parser.parse_args()

    if args.count < 0:
        parser.error("--count must be non-negative")

    if args.rate < 0:
        parser.error("--rate must be non-negative")

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