
"""Standalone reference loop for the ChronosMatch matching engine."""

import argparse
import time

from engine.matching_engine import MatchingEngine
from engine.book_adapter import create_order_book
from ipc.ring_buffer import RingBuffer
from ipc.stats import StatsBlock
from ipc.trade import TRADE_SIZE


def run_engine(
    order_ring="orders.ring",
    trade_ring="trades.ring",
    stats_file="stats.bin",
    idle_timeout=1.0,
    poll_interval=0.001,
):
    """Attach to existing shared files and process available orders."""
    if idle_timeout <= 0 or poll_interval <= 0:
        raise ValueError("Timeout and poll interval must be positive")

    # Attach only: never truncate or recreate shared files.
    orders = RingBuffer(order_ring, create=False)
    trades = None
    stats = None

    try:
        trades = RingBuffer(
            trade_ring,
            create=False,
            record_size=TRADE_SIZE,
        )
        stats = StatsBlock(stats_file, create=False)

        engine = MatchingEngine(create_order_book(), trades, stats)
        processed = 0
        last_activity = time.monotonic()

        while time.monotonic() - last_activity < idle_timeout:
            order_record = orders.pop()

            if order_record is None:
                time.sleep(poll_interval)
                continue

            engine.process_order(order_record)
            processed += 1
            last_activity = time.monotonic()

        print(f"Orders processed by engine: {processed}")
        return processed

    finally:
        orders.close()
        if trades is not None:
            trades.close()
        if stats is not None:
            stats.close()


def main():
    parser = argparse.ArgumentParser(
        description="Run the ChronosMatch reference matching engine"
    )
    parser.add_argument("--orders", default="orders.ring")
    parser.add_argument("--trades", default="trades.ring")
    parser.add_argument("--stats", default="stats.bin")
    parser.add_argument("--idle-timeout", type=float, default=1.0)
    parser.add_argument("--poll-interval", type=float, default=0.001)
    args = parser.parse_args()

    run_engine(
        order_ring=args.orders,
        trade_ring=args.trades,
        stats_file=args.stats,
        idle_timeout=args.idle_timeout,
        poll_interval=args.poll_interval,
    )


if __name__ == "__main__":
    main()
