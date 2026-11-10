from collections import defaultdict


class BookCore:
    """Pure-Python fallback for the Cython matching engine."""

    def __init__(self, max_price=100000):
        if not isinstance(max_price, int) or max_price < 1 or max_price >= 2147483647:
            raise ValueError(
                "max_price must be between 1 and INT_MAX - 1"
            )

        self.max_price = max_price
        self.bids = defaultdict(list)
        self.asks = defaultdict(list)

    def add_order(self, side, price, quantity, order_id=0):
        if side not in (0, 1):
            raise ValueError("side must be BUY (0) or SELL (1)")
        if price < 1 or price > self.max_price:
            raise ValueError("price is outside the supported range")
        if quantity <= 0:
            raise ValueError("quantity must be positive")

        opposite = self.asks if side == 0 else self.bids
        own = self.bids if side == 0 else self.asks

        remaining = quantity
        trades = []

        while remaining > 0 and opposite:
            best_price = min(opposite) if side == 0 else max(opposite)

            if side == 0 and best_price > price:
                break
            if side == 1 and best_price < price:
                break

            resting = opposite[best_price][0]
            fill_quantity = min(remaining, resting["quantity"])

            if side == 0:
                buy_id, sell_id = order_id, resting["order_id"]
            else:
                buy_id, sell_id = resting["order_id"], order_id

            trades.append({
                "buy_order_id": buy_id,
                "sell_order_id": sell_id,
                "price": best_price,
                "quantity": fill_quantity,
            })

            remaining -= fill_quantity
            resting["quantity"] -= fill_quantity

            if resting["quantity"] == 0:
                opposite[best_price].pop(0)

                if not opposite[best_price]:
                    del opposite[best_price]

        if remaining > 0:
            own[price].append({
                "order_id": order_id,
                "quantity": remaining,
            })

        return trades

    def best_bid(self):
        return max(self.bids) if self.bids else None

    def best_ask(self):
        return min(self.asks) if self.asks else None

    def quantity_at(self, side, price):
        if side not in (0, 1):
            raise ValueError("side must be BUY (0) or SELL (1)")
        if price < 1 or price > self.max_price:
            raise ValueError("price is outside the supported range")

        book = self.bids if side == 0 else self.asks

        return sum(
            order["quantity"] for order in book.get(price, [])
        )
