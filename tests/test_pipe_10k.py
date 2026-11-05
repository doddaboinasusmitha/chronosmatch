from ipc.record import BUY, SELL, pack_order, unpack_order
from ipc.ring_buffer import RingBuffer

TOTAL_ORDERS = 10_000


def test_pipe_10k_orders(tmp_path):
    ring_path = tmp_path / "check.ring"
    rb = RingBuffer(str(ring_path), capacity=100)

    sent = 0
    received = 0

    try:
        for i in range(1, TOTAL_ORDERS + 1):
            side = BUY if i % 2 else SELL
            data = pack_order(i, 10000 + i % 50, 10, side, i)

            while not rb.push(data):
                item = rb.pop()
                if item is not None:
                    order = unpack_order(item)
                    received += 1
                    assert order["order_id"] == received

            sent += 1

        while not rb.is_empty():
            item = rb.pop()
            if item is not None:
                order = unpack_order(item)
                received += 1
                assert order["order_id"] == received

        assert sent == TOTAL_ORDERS
        assert received == sent

    finally:
        rb.close()