import random
import time

from ipc.record import BUY, SELL, pack_order

_order_id = 0


def generate_order():
    """Create one random Buy/Sell order as a 32-byte record."""
    global _order_id
    _order_id += 1
    side = random.choice([BUY, SELL])
    price = random.randint(9950, 10050)
    quantity = random.randint(1, 500)
    return pack_order(_order_id, price, quantity, side, time.time_ns())
