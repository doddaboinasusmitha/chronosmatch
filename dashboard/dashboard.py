import curses
import random
import time


def draw(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)

    while True:
        key = stdscr.getch()
        if key in (ord("q"), ord("Q")):
            break

        best_bid = 10000 + random.randint(-3, 3)
        best_ask = best_bid + random.randint(1, 4)

        stdscr.erase()
        stdscr.addstr(0, 0, "ChronosMatch - Top of Book (press q to quit)")
        stdscr.addstr(2, 0, f"Best Bid: {best_bid}")
        stdscr.addstr(3, 0, f"Best Ask: {best_ask}")
        stdscr.addstr(4, 0, f"Spread: {best_ask - best_bid}")
        stdscr.refresh()

        time.sleep(0.2)


if __name__ == "__main__":
    curses.wrapper(draw)
