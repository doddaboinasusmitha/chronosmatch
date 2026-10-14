from simulator.order_generator import OrderGenerator
from ipc.record import unpack_order, BUY, SELL


def test_same_seed_generates_same_orders():
    first = OrderGenerator(seed=42)
    second = OrderGenerator(seed=42)

    for _ in range(20):
        order1 = unpack_order(first.generate_order())
        order2 = unpack_order(second.generate_order())

        # Timestamps change, so compare the other fields.
        assert order1["order_id"] == order2["order_id"]
        assert order1["price"] == order2["price"]
        assert order1["quantity"] == order2["quantity"]
        assert order1["side"] == order2["side"]


def test_price_and_quantity_stay_in_range():
    generator = OrderGenerator(seed=42)

    for _ in range(1000):
        order = unpack_order(generator.generate_order())

        assert len(generator.generate_order.__name__) > 0
        assert 9950 <= order["price"] <= 10050
        assert 1 <= order["quantity"] <= 500
        assert order["side"] in (BUY, SELL)