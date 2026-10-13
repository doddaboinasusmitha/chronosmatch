
from ipc.record import BUY, SELL, unpack_order


class OrderBook:
    def __init__(self):
        self.bids = {}
        self.asks = {}

    def add_order(self, data):
        """Add an order from a packed binary record."""
        order = unpack_order(data)

        price = order["price"]
        quantity = order["quantity"]
        side = order["side"]

        if quantity <= 0:
            raise ValueError("Order quantity must be positive")

        if side == BUY:
            book = self.bids
        elif side == SELL:
            book = self.asks
        else:
            raise ValueError("Invalid order side")

        book[price] = book.get(price, 0) + quantity

    def get_best_bid(self):
        """Return the highest buy price."""
        return max(self.bids) if self.bids else None

    def get_best_ask(self):
        """Return the lowest sell price."""
        return min(self.asks) if self.asks else None

    def get_snapshot(self):
        """Return bids and asks sorted by price."""
        return {
            "bids": sorted(self.bids.items(), reverse=True),
            "asks": sorted(self.asks.items()),
        }
