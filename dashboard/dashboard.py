"""ChronosMatch live market and engine statistics dashboard."""

import time
from datetime import datetime

try:
    import curses
except ImportError:
    curses = None

from ipc.stats import StatsReader


WHALE_ORDER_THRESHOLD = 1000
_previous_orders = None
_previous_sample_time = None


def percentile_latency_ns(buckets, percentile):
    """Estimate a latency percentile from 64 base-2 buckets."""
    if not 0 < percentile <= 100:
        raise ValueError("Invalid percentile")

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


def format_order(order):
    """Format an order and identify large quantities when available."""
    if isinstance(order, dict):
        quantity = order.get(
            "quantity", order.get("qty", order.get("size", 0))
        )
        try:
            if float(quantity) >= WHALE_ORDER_THRESHOLD:
                return f"[WHALE] {order}"
        except (TypeError, ValueError):
            pass

    return str(order)


def get_market_data(path="stats.bin"):
    """Read live engine statistics without modifying the stats file."""
    global _previous_orders, _previous_sample_time

    with StatsReader(path) as reader:
        stats = reader.snapshot()

    now = time.time()
    heartbeat = stats["heartbeat_ns"]
    age_ns = max(0, time.time_ns() - heartbeat) if heartbeat else None

    orders = stats["orders"]
    orders_per_second = 0.0

    if _previous_orders is not None and _previous_sample_time is not None:
        elapsed = now - _previous_sample_time
        if elapsed > 0:
            orders_per_second = max(
                0, orders - _previous_orders
            ) / elapsed

    _previous_orders = orders
    _previous_sample_time = now

    bid = stats["best_bid"]
    ask = stats["best_ask"]

    if age_ns is None:
        status = "NO HEARTBEAT"
    elif age_ns <= 5_000_000_000:
        status = "LIVE"
    else:
        status = "STALE"

    return {
        **stats,
        "available": age_ns is not None,
        "engine_status": status,
        "heartbeat_age_ns": age_ns,
        "spread": ask - bid if bid and ask else None,
        "orders_per_second": orders_per_second,
        "p50_latency_ns": percentile_latency_ns(
            stats["latency_buckets"], 50
        ),
        "p99_latency_ns": percentile_latency_ns(
            stats["latency_buckets"], 99
        ),
        "activity": [
            f"Orders processed: {orders}",
            f"Trades executed: {stats['trades']}",
            f"Latency samples: {sum(stats['latency_buckets'])}",
        ],
        "last_trade": (
            f"Last trade: {stats['last_trade_quantity']} "
            f"@ {stats['last_trade_price']}"
            if stats["last_trade_price"]
            else "Last trade: waiting for trade"
        ),
    }


def safe_addstr(window, y, x, text):
    """Print safely within terminal boundaries."""
    try:
        height, width = window.getmaxyx()
        if 0 <= y < height and 0 <= x < width - 1:
            window.addnstr(y, x, str(text), width - x - 1)
    except Exception:
        pass


def draw_order_book(window, data, height, width):
    """Display actual best bid, best ask and spread."""
    safe_addstr(window, 2, 2, "BEST BID")
    safe_addstr(window, 2, max(2, width // 2), "BEST ASK")

    bid = data["best_bid"]
    ask = data["best_ask"]

    safe_addstr(window, 3, 2, str(bid if bid else "No buy orders"))
    safe_addstr(
        window, 3, max(2, width // 2),
        str(ask if ask else "No sell orders")
    )

    spread = data["spread"]
    safe_addstr(
        window, 5, 2,
        f"Spread: {spread if spread is not None else 'N/A'}"
    )


def draw_activity(window, data, height, width):
    """Display live engine activity and latency metrics."""
    safe_addstr(window, 1, 2, "ENGINE ACTIVITY")

    activity = data.get("activity", []) + [
        f"Orders/sec: {data['orders_per_second']:.2f}",
        f"Latency p50: {data['p50_latency_ns'] or 'N/A'} ns",
        f"Latency p99: {data['p99_latency_ns'] or 'N/A'} ns",
    ]

    for index, message in enumerate(activity):
        y = 3 + index
        if y >= height - 1:
            break
        safe_addstr(window, y, 2, f"- {message}")


def draw_status(window, data, height, width):
    """Display engine status and latest trade."""
    safe_addstr(
        window, height - 3, 2,
        f"Status: {data['engine_status']}"
    )
    safe_addstr(
        window, height - 2, 2,
        f"Orders/sec: {data['orders_per_second']:.2f}"
    )
    safe_addstr(window, height - 1, 2, data["last_trade"])


def draw(stdscr):
    """Main dashboard loop. Press Q to quit."""
    curses.curs_set(0)
    stdscr.nodelay(True)

    while True:
        height, width = stdscr.getmaxyx()
        stdscr.erase()

        safe_addstr(stdscr, 0, 2, "CHRONOSMATCH - LIVE MARKET DASHBOARD")

        if height < 16 or width < 55:
            safe_addstr(
                stdscr, 2, 2,
                "Enlarge the terminal. Press Q to quit."
            )
        else:
            try:
                data = get_market_data()
            except (OSError, ValueError, KeyError) as exc:
                safe_addstr(
                    stdscr, 2, 2,
                    f"Waiting for valid stats.bin: {exc}"
                )
                data = None

            if data is not None:
                draw_order_book(stdscr, data, height // 2, width)

                activity_y = height // 2
                activity_height = max(3, height - activity_y - 5)

                try:
                    activity_window = stdscr.derwin(
                        activity_height, width, activity_y, 0
                    )
                    draw_activity(
                        activity_window, data, activity_height, width
                    )
                except curses.error:
                    pass

                safe_addstr(
                    stdscr, height - 4, 2,
                    f"Engine: {data['engine_status']}"
                )
                draw_status(stdscr, data, height, width)

        safe_addstr(
            stdscr, height - 1, max(2, width - 20),
            "Press Q to quit"
        )
        stdscr.refresh()

        key = stdscr.getch()
        if key in (ord("q"), ord("Q"), 3):
            break

        time.sleep(0.2)


if __name__ == "__main__":
    if curses is None:
        print("Install Windows terminal support: python -m pip install windows-curses")
    else:
        try:
            curses.wrapper(draw)
        except KeyboardInterrupt:
            pass
