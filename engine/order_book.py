
from dataclasses import dataclass

from ipc.record import BUY, SELL, unpack_order


@dataclass
class Trade:
    buy_order_id: int
    sell_order_id: int
    price: int
    quantity: int


class OrderBook:
    def __init__(self):
        self.bids = {}
        self.asks = {}

    def add_order(self, data):
        """Add an order and match it against existing orders."""
        order = unpack_order(data)

        if order["quantity"] <= 0:
            raise ValueError("Order quantity must be positive")

        if order["price"] <= 0:
            raise ValueError("Order price must be positive")

        if order["side"] not in (BUY, SELL):
            raise ValueError("Invalid order side")

        return self.match(order)

    def match(self, order):
        """Match an incoming order using price-time priority."""
        trades = []
        is_buy = order["side"] == BUY

        opposite_book = self.asks if is_buy else self.bids

        while order["quantity"] > 0 and opposite_book:
            best_price = (
                min(opposite_book) if is_buy
                else max(opposite_book)
            )

            # Stop when the best opposite price does not cross.
            if is_buy and best_price > order["price"]:
                break

            if not is_buy and best_price < order["price"]:
                break

            resting_orders = opposite_book[best_price]
            resting = resting_orders[0]

            fill_quantity = min(
                order["quantity"],
                resting["quantity"]
            )

            if is_buy:
                buy_id = order["order_id"]
                sell_id = resting["order_id"]
            else:
                buy_id = resting["order_id"]
                sell_id = order["order_id"]

            # Execute at the resting order's price.
            trades.append(
                Trade(
                    buy_order_id=buy_id,
                    sell_order_id=sell_id,
                    price=best_price,
                    quantity=fill_quantity,
                )
            )

            order["quantity"] -= fill_quantity
            resting["quantity"] -= fill_quantity

            # Remove a resting order only when fully filled.
            if resting["quantity"] == 0:
                resting_orders.pop(0)

            if not resting_orders:
                del opposite_book[best_price]

        # Keep any unfilled quantity in the book.
        if order["quantity"] > 0:
            own_book = self.bids if is_buy else self.asks
            price = order["price"]

            if price not in own_book:
                own_book[price] = []

            own_book[price].append(order)

        return trades

    def get_best_bid(self):
        """Return the highest buy price."""
        return max(self.bids) if self.bids else None

    def get_best_ask(self):
        """Return the lowest sell price."""
        return min(self.asks) if self.asks else None

    def get_snapshot(self):
        """Return price levels with their remaining quantities."""
        return {
            "bids": [
                (price, sum(o["quantity"] for o in orders))
                for price, orders in sorted(
                    self.bids.items(), reverse=True
                )
            ],
            "asks": [
                (price, sum(o["quantity"] for o in orders))
                for price, orders in sorted(self.asks.items())
            ],
        }
