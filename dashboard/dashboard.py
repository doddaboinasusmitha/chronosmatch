import curses
import time
from datetime import datetime


def get_market_data():
    """Return safe dashboard data until the live engine interface is connected."""
    return {
        "available": False,
        "buy_orders": [],
        "sell_orders": [],
        "activity": [
            "Live market data is not connected",
            "Waiting for engine data interface",
        ],
    }


def safe_addstr(window, y, x, text):
    """Write text safely within the terminal window."""
    height, width = window.getmaxyx()

    if 0 <= y < height and 0 <= x < width - 1:
        try:
            window.addnstr(y, x, str(text), width - x - 1)
        except curses.error:
            pass


def draw_section(window, y, x, width, title):
    """Draw a section heading and underline."""
    safe_addstr(window, y, x, title)
    safe_addstr(window, y + 1, x, "-" * max(0, width - 2))


def draw_order_book(window, data, height, width):
    """Display buy and sell orders."""
    half_width = max(1, width // 2)

    draw_section(window, 1, 2, half_width, "BUY ORDERS")
    draw_section(window, 1, half_width + 2, half_width, "SELL ORDERS")

    safe_addstr(window, 3, 2, "PRICE       QTY     ORDER ID")
    safe_addstr(
        window, 3, half_width + 2, "PRICE       QTY     ORDER ID"
    )

    buy_orders = data.get("buy_orders", [])
    sell_orders = data.get("sell_orders", [])

    if not buy_orders:
        safe_addstr(window, 4, 2, "No live buy orders")

    if not sell_orders:
        safe_addstr(window, 4, half_width + 2, "No live sell orders")

    for index, order in enumerate(buy_orders):
        y = 4 + index
        if y >= height - 1:
            break

        safe_addstr(
            window,
            y,
            2,
            f"{order.get('price', '-')}   "
            f"{order.get('quantity', '-')}   "
            f"{order.get('order_id', '-')}",
        )

    for index, order in enumerate(sell_orders):
        y = 4 + index
        if y >= height - 1:
            break

        safe_addstr(
            window,
            y,
            half_width + 2,
            f"{order.get('price', '-')}   "
            f"{order.get('quantity', '-')}   "
            f"{order.get('order_id', '-')}",
        )


def draw_activity(window, data, height, width):
    """Display recent activity messages."""
    draw_section(window, 1, 2, width - 4, "ACTIVITY")

    activity = data.get("activity", [])

    if not activity:
        safe_addstr(window, 3, 2, "No recent activity")

    for index, message in enumerate(activity):
        y = 3 + index
        if y >= height - 1:
            break
        safe_addstr(window, y, 2, f"- {message}")


def draw_status(window, data, height, width):
    """Display connection status and current time."""
    status = (
        "LIVE DATA CONNECTED"
        if data.get("available", False)
        else "WAITING FOR ENGINE DATA"
    )

    safe_addstr(window, height - 2, 2, f"Status: {status}")
    safe_addstr(
        window,
        height - 2,
        max(2, width - 28),
        datetime.now().strftime("%H:%M:%S"),
    )


def draw(stdscr):
    """Main terminal dashboard loop. Press Q to quit."""
    curses.curs_set(0)
    stdscr.nodelay(True)

    while True:
        height, width = stdscr.getmaxyx()
        stdscr.erase()

        safe_addstr(
            stdscr,
            0,
            2,
            "ChronosMatch - Market Dashboard",
        )

        data = get_market_data()

        if height >= 12 and width >= 50:
            draw_order_book(
                stdscr,
                data,
                height - 5,
                width,
            )

            activity_y = max(7, height // 2)
            activity_window = stdscr.derwin(
                max(3, height - activity_y - 3),
                width,
                activity_y,
                0,
            )
            draw_activity(
                activity_window,
                data,
                height - activity_y - 3,
                width,
            )

            draw_status(stdscr, data, height, width)
        else:
            safe_addstr(
                stdscr,
                2,
                2,
                "Please enlarge the terminal window.",
            )

        safe_addstr(
            stdscr,
            height - 1,
            2,
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