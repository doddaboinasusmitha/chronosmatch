
"""Read-only ChronosMatch statistics dashboard."""

import time
from datetime import datetime

try:
    import curses
except ImportError:
    curses = None

from ipc.stats import StatsReader


def percentile_latency_ns(buckets, percentile):
    """Estimate a latency percentile from the 64 base-2 buckets."""
    if not 0 < percentile <= 100:
        raise ValueError("percentile must be greater than 0 and at most 100")

    total = sum(buckets)
    if total == 0:
        return None

    target = max(1, (total * percentile + 99) // 100)
    cumulative = 0

    for index, count in enumerate(buckets):
        cumulative += count
        if cumulative >= target:
            return (1 << (index + 1)) - 1

    return None


def get_market_data(path="stats.bin"):
    """Read a snapshot without modifying the engine's stats file."""
    with StatsReader(path) as reader:
        stats = reader.snapshot()

    bid = stats["best_bid"]
    ask = stats["best_ask"]
    heartbeat = stats["heartbeat_ns"]
    age_ns = max(0, time.time_ns() - heartbeat) if heartbeat else None

    return {
        **stats,
        "spread": ask - bid if bid and ask else None,
        "p50_latency_ns": percentile_latency_ns(
            stats["latency_buckets"], 50
        ),
        "p99_latency_ns": percentile_latency_ns(
            stats["latency_buckets"], 99
        ),
        "heartbeat_age_ns": age_ns,
    }


def safe_addstr(window, y, x, text):
    """Avoid writing beyond the visible terminal area."""
    height, width = window.getmaxyx()
    if 0 <= y < height and 0 <= x < width - 1:
        try:
            window.addnstr(y, x, str(text), width - x - 1)
        except curses.error:
            pass


def draw(stdscr):
    curses.curs_set(0)
    stdscr.timeout(500)

    while True:
        key = stdscr.getch()
        if key in (ord("q"), ord("Q"), 3):
            break

        stdscr.erase()
        height, width = stdscr.getmaxyx()
        safe_addstr(stdscr, 0, 2, "CHRONOSMATCH - LIVE ENGINE STATS")

        if height < 12 or width < 55:
            safe_addstr(
                stdscr, 3, 2,
                "Enlarge the terminal. Press Q to quit."
            )
            stdscr.refresh()
            continue

        try:
            data = get_market_data()
        except (OSError, ValueError) as exc:
            safe_addstr(stdscr, 3, 2, f"Waiting for valid stats.bin: {exc}")
            safe_addstr(stdscr, height - 1, 2, "Press Q to quit")
            stdscr.refresh()
            continue

        age = data["heartbeat_age_ns"]
        status = (
            "NO HEARTBEAT" if age is None
            else "LIVE" if age < 5_000_000_000
            else "STALE"
        )

        spread = data["spread"]
        p50 = data["p50_latency_ns"]
        p99 = data["p99_latency_ns"]

        lines = [
            f"System: {status}",
            f"Orders processed: {data['orders']}",
            f"Trades executed:  {data['trades']}",
            f"Best bid:         {data['best_bid'] or 'N/A'}",
            f"Best ask:         {data['best_ask'] or 'N/A'}",
            f"Spread:           {spread if spread is not None else 'N/A'}",
            f"Last trade price: {data['last_trade_price'] or 'N/A'}",
            f"Last trade qty:   {data['last_trade_quantity']}",
            f"Latency p50:      {p50 if p50 is not None else 'N/A'} ns",
            f"Latency p99:      {p99 if p99 is not None else 'N/A'} ns",
            f"Latency samples:  {sum(data['latency_buckets'])}",
            f"Updated:          {datetime.now().strftime('%H:%M:%S')}",
            "Press Q to quit",
        ]

        for index, line in enumerate(lines, start=2):
            safe_addstr(stdscr, index, 2, line)

        stdscr.refresh()


if __name__ == "__main__":
    if curses is None:
        print(
            "Terminal dashboard needs curses support. "
            "On Windows, install it with: python -m pip install windows-curses"
        )
    else:
        try:
            curses.wrapper(draw)
        except KeyboardInterrupt:
            pass
