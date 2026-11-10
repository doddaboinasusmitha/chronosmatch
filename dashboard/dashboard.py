"""ChronosMatch live market and engine statistics dashboard."""

import curses
import os
import time

from ipc.stats import StatsBlock


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATS_PATH = os.path.join(BASE_DIR, "stats.bin")

WHALE_ORDER_THRESHOLD = 1000
_previous_orders = None
_previous_sample_time = None


def percentile_latency_ns(buckets, percentile):
    """Estimate a latency percentile from base-2 buckets."""
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
    """Identify large orders when quantity is available."""
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


def get_market_data():
    """Read market statistics from stats.bin."""
    global _previous_orders, _previous_sample_time

    stats_block = StatsBlock(path=STATS_PATH, create=False)

    try:
        stats = stats_block.snapshot()
    finally:
        stats_block.close()

    now = time.time()
    orders = stats.get("orders", 0)
    heartbeat = stats.get("heartbeat_ns", 0)

    orders_per_second = 0.0

    if _previous_orders is not None and _previous_sample_time is not None:
        elapsed = now - _previous_sample_time
        if elapsed > 0:
            orders_per_second = max(
                0, orders - _previous_orders
            ) / elapsed

    _previous_orders = orders
    _previous_sample_time = now

    age_ns = max(0, time.time_ns() - heartbeat) if heartbeat else None

    engine_alive = (
        age_ns is not None and age_ns < 5_000_000_000
    )

    if not engine_alive:
        orders_per_second = 0.0

    bid = stats.get("best_bid", 0)
    ask = stats.get("best_ask", 0)
    last_price = stats.get("last_trade_price", 0)
    last_quantity = stats.get("last_trade_quantity", 0)

    buckets = stats.get("latency_buckets", [])

    if age_ns is None:
        status = "NO HEARTBEAT"
    elif engine_alive:
        status = "LIVE"
    else:
        status = "STALE"

    return {
        **stats,
        "available": engine_alive,
        "engine_status": status,
        "heartbeat_age_ns": age_ns,
        "spread": ask - bid if bid and ask else None,
        "orders_per_second": orders_per_second,
        "p50_latency_ns": percentile_latency_ns(buckets, 50),
        "p99_latency_ns": percentile_latency_ns(buckets, 99),
        "activity": [
            f"Orders processed: {orders}",
            f"Trades executed: {stats.get('trades', 0)}",
            f"Latency samples: {sum(buckets)}",
        ],
        "last_trade": (
            f"Last trade: {last_quantity} @ {last_price}"
            if engine_alive and last_price
            else "Last trade: waiting for trade"
        ),
    }


def safe_addstr(window, y, x, text):
    """Print safely within terminal boundaries."""
    try:
        height, width = window.getmaxyx()
        if 0 <= y < height and 0 <= x < width - 1:
            window.addnstr(y, x, str(text), width - x - 1)
    except curses.error:
        pass


def draw_order_book(window, data, height, width):
    """Display best bid, best ask and spread."""
    safe_addstr(window, 2, 2, "BEST BID")
    safe_addstr(window, 2, max(2, width // 2), "BEST ASK")

    bid = data.get("best_bid", 0)
    ask = data.get("best_ask", 0)

    safe_addstr(window, 3, 2, str(bid if bid else "No buy orders"))
    safe_addstr(
        window, 3, max(2, width // 2),
        str(ask if ask else "No sell orders")
    )

    spread = data.get("spread")
    safe_addstr(
        window, 5, 2,
        f"Spread: {spread if spread is not None else 'N/A'}"
    )


def draw_activity(window, data, height, width):
    """Display engine activity and latency metrics."""
    safe_addstr(window, 1, 2, "ENGINE ACTIVITY")

    activity = data.get("activity", []) + [
        f"Orders/sec: {data.get('orders_per_second', 0):.2f}",
        f"Latency p50: {data.get('p50_latency_ns') or 'N/A'} ns",
        f"Latency p99: {data.get('p99_latency_ns') or 'N/A'} ns",
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
        f"Status: {data.get('engine_status', 'UNKNOWN')}"
    )
    safe_addstr(
        window, height - 2, 2,
        f"Orders/sec: {data.get('orders_per_second', 0):.2f}"
    )
    safe_addstr(
        window, height - 1, 2,
        data.get("last_trade", "Last trade: waiting for trade")
    )


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

                draw_order_book(stdscr, data, height // 2, width)

                activity_y = height // 2
                activity_height = max(3, height - activity_y - 5)

                activity_window = stdscr.derwin(
                    activity_height, width, activity_y, 0
                )

                draw_activity(
                    activity_window, data, activity_height, width
                )

                safe_addstr(
                    stdscr, height - 4, 2,
                    f"Engine: {data['engine_status']}"
                )

                draw_status(stdscr, data, height, width)

            except (OSError, ValueError, KeyError, TypeError) as error:
                safe_addstr(
                    stdscr, 2, 2,
                    f"Waiting for valid stats.bin: {error}"
                )

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
    try:
        curses.wrapper(draw)
    except KeyboardInterrupt:
        pass


  