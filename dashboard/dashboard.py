import curses
import time
import random
from datetime import datetime


def get_market_data():
    """Temporary mock data provider.

    Replace this function with the confirmed ring-buffer
    data interface after coordinating with the team.
    """
    return {
        "available": True,
        "buy_orders": [
            {"price": 10002 + random.randint(-3,3), "quantity": 10, "order_id": "B101"},
            {"price": 10001 + random.randint(-3,3),"quantity": 15, "order_id": "B102"},
            {"price": 10000 + random.randint(-3,3),"quantity": 8, "order_id": "B103"},
        ],
        "sell_orders": [
            {"price": 10003 + random.randint(-3,3), "quantity": 12, "order_id": "S101"},
            {"price": 10004 + random.randint(-3,3), "quantity": 7, "order_id": "S102"},
            {"price": 10005 + random.randint(-3,3), "quantity": 20, "order_id": "S103"},
        ],
        "activity": [
            "BUY order B101 received",
            "SELL order S101 received",
            "Market data refreshed",
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


def draw_section(window, y, x, height, width, title):
    """Draw a bordered dashboard section."""
    if height < 3 or width < 4:
        return

    try:
        section = window.derwin(height, width, y, x)
        section.box()
        safe_addstr(section, 0, 2, f" {title} ")
    except curses.error:
        pass


def draw_order_book(stdscr, data, height, width):
    book_width = max(30, width * 2 // 3)
    book_width = min(book_width, width - 2)

    draw_section(stdscr, 1, 1, height - 2, book_width, "ORDER BOOK")

    safe_addstr(stdscr, 3, 3, "BUY ORDERS")
    safe_addstr(stdscr, 3, book_width // 2, "SELL ORDERS")

    safe_addstr(stdscr, 4, 3, "PRICE      QTY   ORDER ID")
    safe_addstr(stdscr, 4, book_width // 2, "PRICE      QTY   ORDER ID")

    rows = max(0, height - 8)

    for i, order in enumerate(data["buy_orders"][:rows]):
        safe_addstr(
            stdscr, 5 + i, 3,
            f'{order["price"]:<10} {order["quantity"]:<5} {order["order_id"]}'
        )

    for i, order in enumerate(data["sell_orders"][:rows]):
        safe_addstr(
            stdscr, 5 + i, book_width // 2,
            f'{order["price"]:<10} {order["quantity"]:<5} {order["order_id"]}'
        )


def draw_activity(stdscr, data, height, width):
    book_width = min(max(30, width * 2 // 3), width - 2)
    x = book_width + 1
    section_width = width - x - 1

    if section_width < 15:
        return

    draw_section(stdscr, 1, x, height - 2, section_width, "RECENT ACTIVITY")

    for i, message in enumerate(data["activity"][:height - 5]):
        safe_addstr(stdscr, 3 + i, x + 2, message)


def draw_status(stdscr, data, height, width):
    status = "DATA AVAILABLE" if data["available"] else "WAITING FOR DATA"
    safe_addstr(stdscr, height - 1, 2,
                f"System: RUNNING | Data: {status} | Updated: "
                f"{datetime.now().strftime('%H:%M:%S')} | Q: Quit")


def draw(stdscr):
    curses.curs_set(0)
    stdscr.timeout(500)

    while True:
        key = stdscr.getch()

        if key in (ord("q"), ord("Q"), 3):
            break

        # Redraw after a resize or the next refresh interval.
        height, width = stdscr.getmaxyx()
        stdscr.erase()

        safe_addstr(
            stdscr, 0, 2,
            "CHRONOSMATCH - TERMINAL DASHBOARD"
        )

        if height < 12 or width < 60:
            safe_addstr(stdscr, 3, 2,
                        "Terminal too small. Enlarge it to view the dashboard.")
            safe_addstr(stdscr, height - 1, 2, "Press Q to quit")
            stdscr.refresh()
            continue

        data = get_market_data()

        draw_order_book(stdscr, data, height - 2, width)
        draw_activity(stdscr, data, height - 2, width)
        draw_status(stdscr, data, height, width)

        stdscr.refresh()


if __name__ == "__main__":
    try:
        curses.wrapper(draw)
    except KeyboardInterrupt:
        pass