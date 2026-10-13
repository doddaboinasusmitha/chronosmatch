import random
import time

from ipc.record import BUY, SELL, pack_order


class OrderGenerator:
    """Generate repeatable orders using a seeded random walk."""

    def __init__(
        self,
        seed=None,
        start_price=10000,
        min_price=9950,
        max_price=10050,
    ):
        if min_price > max_price:
            raise ValueError("min_price cannot exceed max_price")

        if not min_price <= start_price <= max_price:
            raise ValueError(
                "start_price must be within the price range"
            )

        self.rng = random.Random(seed)
        self.order_id = 0
        self.price = start_price
        self.min_price = min_price
        self.max_price = max_price

    def generate_order(self):
        """Return one packed 32-byte order."""

        self.order_id += 1

        # Move the price gradually by -5 to +5.
        movement = self.rng.randint(-5, 5)

        self.price = max(
            self.min_price,
            min(self.max_price, self.price + movement),
        )

        side = self.rng.choice([BUY, SELL])
        quantity = self.rng.randint(1, 500)
        timestamp_ns = time.time_ns()

        return pack_order(
            self.order_id,
            self.price,
            quantity,
            side,
            timestamp_ns,
        )


# Preserve compatibility with simulator.py.
_default_generator = OrderGenerator()


def generate_order():
    """Generate one order using the default generator."""
    return _default_generator.generate_order()