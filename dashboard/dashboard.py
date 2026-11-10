"""ChronosMatch terminal market dashboard."""

import curses
import os
import time

from ipc.stats import StatsBlock


WHALE_ORDER_THRESHOLD = 1000

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATS_PATH = os.path.join(BASE_DIR, "stats.bin")

_previous_orders = None
_previous_time = None


def safe_addstr(window, y, x, text):
    """Print text safely without crashing at terminal boundaries."""
    try:
        height, width = window.getmaxyx()

        if 0 <= y < height and 0 <= x < width:
            available = max(0, width - x - 1)
            window.addnstr(y, x, str(text), available)

    except curses.error:
        pass


def format_order(order):
    """Format an order and highlight large whale orders."""
    if isinstance(order, dict):
        quantity = order.get(
            "quantity",
            order.get("qty", order.get("size", 0)),
        )

        try:
            if float(quantity) >= WHALE_ORDER_THRESHOLD:
                return f"[WHALE] {order}"
        except (TypeError, ValueError):
            pass

    return str(order)


def get_market_data():
    """Read market statistics from stats.bin."""
    global _previous_orders, _previous_time

    try:
        stats_block = StatsBlock(path=STATS_PATH, create=False)

        try:
            stats = stats_block.snapshot()
        finally:
            stats_block.close()

        current_time = time.time()
        current_orders = stats.get("orders", 0)

        orders_per_second = 0.0

        if _previous_orders is not None and _previous_time is not None:
            elapsed = current_time - _previous_time

            if elapsed > 0:
                orders_per_second = max(
                    0,
                    current_orders - _previous_orders,
                ) / elapsed

        _previous_orders = current_orders
        _previous_time = current_time

        heartbeat = stats.get("heartbeat_ns", 0)

        engine_alive = (
            heartbeat > 0
            and 0 <= time.time_ns() - heartbeat < 5_000_000_000
        )

        if not engine_alive:
            orders_per_second = 0.0

        last_price = stats.get("last_trade_price", 0)
        last_quantity = stats.get("last_trade_quantity", 0)

        if engine_alive and last_price:
            last_trade = f"Last trade: {last_quantity} @ {last_price}"
        else:
            last_trade = "Last trade: waiting for trade"

        activity = [
            f"Total orders: {current_orders}",
            f"Total trades: {stats.get('trades', 0)}",
            f"Best bid: {stats.get('best_bid', 0)}",
            f"Best ask: {stats.get('best_ask', 0)}",
        ]

        return {
            "available": engine_alive,
            "buy_orders": [],
            "sell_orders": [],
            "orders_per_second": orders_per_second,
            "last_trade": last_trade,
            "engine_status": (
                "RUNNING" if engine_alive else "NOT RESPONDING"
            ),
            "activity": activity,
        }

    except (OSError, ValueError, KeyError, TypeError) as error:
        return {
            "available": False,
            "buy_orders": [],
            "sell_orders": [],
            "orders_per_second": 0.0,
            "last_trade": "Last trade: waiting for trade",
            "engine_status": "NOT RESPONDING",
            "activity": [f"Statistics unavailable: {error}"],
        }


def draw_order_book(window, data, height, width):
    """Display available buy and sell orders."""
    safe_addstr(window, 2, 2, "BUY ORDERS")
    safe_addstr(window, 2, max(2, width // 2), "SELL ORDERS")

    buy_orders = data.get("buy_orders", [])
    sell_orders = data.get("sell_orders", [])

    if not buy_orders:
        safe_addstr(window, 3, 2, "Order details unavailable")

    if not sell_orders:
        safe_addstr(
            window,
            3,
            max(2, width // 2),
            "Order details unavailable",
        )

    for index, order in enumerate(buy_orders):
        y = 3 + index

        if y >= height - 1:
            break

        safe_addstr(window, y, 2, format_order(order))

    for index, order in enumerate(sell_orders):
        y = 3 + index

        if y >= height - 1:
            break

        safe_addstr(
            window,
            y,
            max(2, width // 2),
            format_order(order),
        )


def draw_activity(window, data, height, width):
    """Display recent market activity."""
    safe_addstr(window, 1, 2, "ACTIVITY")

    for index, message in enumerate(data.get("activity", [])):
        y = 3 + index

        if y >= height - 1:
            break

        safe_addstr(window, y, 2, f"- {message}")


def draw_status(window, data, height, width):
    """Display connection status and market statistics."""
    status = (
        "LIVE DATA CONNECTED"
        if data.get("available", False)
        else "WAITING FOR ENGINE DATA"
    )

    safe_addstr(window, height - 3, 2, f"Status: {status}")

    safe_addstr(
        window,
        height - 2,
        2,
        f"Orders/sec: {data.get('orders_per_second', 0.0):.2f}",
    )

    safe_addstr(
        window,
        height - 1,
        2,
        data.get("last_trade", "Last trade: waiting for trade"),
    )


def draw(stdscr):
    """Main dashboard loop. Press Q to quit."""
    curses.curs_set(0)
    stdscr.nodelay(True)

    while True:
        height, width = stdscr.getmaxyx()
        stdscr.erase()

        safe_addstr(stdscr, 0, 2, "ChronosMatch - Market Dashboard")

        if height < 16 or width < 50:
            safe_addstr(
                stdscr,
                2,
                2,
                "Please enlarge the terminal window.",
            )
        else:
            data = get_market_data()

            draw_order_book(stdscr, data, height // 2, width)

            activity_y = height // 2
            activity_height = max(3, height - activity_y - 5)

            try:
                activity_window = stdscr.derwin(
                    activity_height,
                    width,
                    activity_y,
                    0,
                )

                draw_activity(
                    activity_window,
                    data,
                    activity_height,
                    width,
                )
            except curses.error:
                pass

            safe_addstr(
                stdscr,
                height - 4,
                2,
                f"Engine: {data.get('engine_status', 'UNKNOWN')}",
            )

            draw_status(stdscr, data, height, width)

        safe_addstr(
            stdscr,
            height - 1,
            max(2, width - 20),
            "Press Q to quit",
        )

        stdscr.refresh()

        key = stdscr.getch()

        if key in (ord("q"), ord("Q")):
            break

        time.sleep(0.2)


if __name__ == "__main__":
    try:
        curses.wrapper(draw)
    except KeyboardInterrupt:
        pass