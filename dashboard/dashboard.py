"""ChronosMatch terminal market dashboard."""

import curses
import time
from datetime import datetime


def safe_addstr(window, y, x, text):
    """Print text safely without crashing at terminal boundaries."""
    try:
        height, width = window.getmaxyx()
        if 0 <= y < height and 0 <= x < width:
            available = max(0, width - x - 1)
            window.addnstr(y, x, str(text), available)
    except curses.error:
        pass


def get_market_data():
    """Return placeholder data until the live engine is connected."""
    return {
        "available": False,
        "buy_orders": [],
        "sell_orders": [],
        "orders_per_second": 0.0,
        "last_trade": "Last trade: waiting for trade",
        "engine_status": "NOT RESPONDING",
        "activity": [
            "Live market data is not connected",
            "Waiting for engine data interface",
        ],
    }


def draw_order_book(window, data, height, width):
    """Display buy and sell orders."""
    safe_addstr(window, 2, 2, "BUY ORDERS")
    safe_addstr(window, 2, max(2, width // 2), "SELL ORDERS")

    buy_orders = data.get("buy_orders", [])
    sell_orders = data.get("sell_orders", [])

    if not buy_orders:
        safe_addstr(window, 3, 2, "No buy orders yet")

    if not sell_orders:
        safe_addstr(
            window, 3, max(2, width // 2), "No sell orders yet"
        )

    for index, order in enumerate(buy_orders):
        y = 3 + index
        if y >= height - 1:
            break
        safe_addstr(window, y, 2, str(order))

    for index, order in enumerate(sell_orders):
        y = 3 + index
        if y >= height - 1:
            break
        safe_addstr(window, y, max(2, width // 2), str(order))


def draw_activity(window, data, height, width):
    """Display recent dashboard activity."""
    safe_addstr(window, 1, 2, "ACTIVITY")

    activity = data.get("activity", [])

    for index, message in enumerate(activity):
        y = 3 + index
        if y >= height - 1:
            break
        safe_addstr(window, y, 2, f"- {message}")


def draw_status(window, data, height, width):
    """Display connection status, metrics, and current time."""
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
        str(data.get("last_trade", "Last trade: waiting for trade")),
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
                stdscr, 2, 2, "Please enlarge the terminal window."
            )
        else:
            data = get_market_data()

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
                stdscr,
                height - 4,
                2,
                f"Engine: {data.get('engine_status', 'UNKNOWN')}",
            )
            draw_status(stdscr, data, height, width)

        safe_addstr(stdscr, height - 1, max(2, width - 20), "Press Q to quit")
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