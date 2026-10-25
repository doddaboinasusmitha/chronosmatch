from engine.order_book import OrderBook, Trade
from ipc.record import unpack_order

try:
    from engine.book_core import BookCore
except (ImportError, OSError):
    BookCore = None


class CythonOrderBook:
    """Adapt packed order records to the Cython matching core."""

    def __init__(self, max_price=100000):
        if BookCore is None:
            raise ImportError("Cython BookCore extension is unavailable")
        self._core = BookCore(max_price)

    def add_order(self, data):
        order = unpack_order(data)
        trades = self._core.add_order(
            order["side"],
            order["price"],
            order["quantity"],
            order["order_id"],
        )
        return [
            Trade(
                buy_order_id=trade["buy_order_id"],
                sell_order_id=trade["sell_order_id"],
                price=trade["price"],
                quantity=trade["quantity"],
            )
            for trade in trades
        ]

    def get_best_bid(self):
        return self._core.best_bid()

    def get_best_ask(self):
        return self._core.best_ask()


def create_order_book(prefer_cython=True):
    """Use Cython when available; otherwise use the Python implementation."""
    if prefer_cython and BookCore is not None:
        try:
            return CythonOrderBook()
        except (ImportError, OSError):
            pass
    return OrderBook()
