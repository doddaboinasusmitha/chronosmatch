
from ipc.record import BUY, SELL, unpack_order
from simulator.order_generator import generate_order


def test_generated_order_has_valid_format():
    record = generate_order()

    assert isinstance(record, bytes)
    assert len(record) == 32

    order = unpack_order(record)
    assert order["order_id"] > 0
    assert order["price"] > 0
    assert 1 <= order["quantity"] <= 500
    assert order["side"] in (BUY, SELL)
    assert order["timestamp_ns"] > 0


def test_generated_orders_have_increasing_ids():
    first = unpack_order(generate_order())
    second = unpack_order(generate_order())

    assert second["order_id"] > first["order_id"]


import asyncio

from ipc.ring_buffer import RingBuffer
from simulator.simulator import producer, consumer


def test_simulator_producer_consumer_flow(tmp_path):
    async def run_test():
        rb = RingBuffer(str(tmp_path / "orders.ring"), capacity=8)
        stats = {
            "sent": 0,
            "received": 0,
            "done": False,
            "latencies_ns": [],
        }

        try:
            await asyncio.gather(
                producer(rb, 20, stats),
                consumer(rb, stats),
            )

            assert stats["sent"] == 20
            assert stats["received"] == 20
            assert rb.is_empty()
        finally:
            rb.close()

    asyncio.run(run_test())
