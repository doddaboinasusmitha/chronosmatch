
from ipc.record import BUY, SELL, pack_order, unpack_order
from ipc.ring_buffer import RingBuffer

TOTAL_ORDERS = 10_000


def main():
    rb = RingBuffer("check.ring", capacity=100)
    sent = 0
    received = 0

    try:
        for i in range(1, TOTAL_ORDERS + 1):
            side = BUY if i % 2 else SELL
            data = pack_order(i, 10000 + i % 50, 10, side, i)

            while not rb.push(data):
                item = rb.pop()
                if item is None:
                    continue

                order = unpack_order(item)
                received += 1
                assert order["order_id"] == received, (
                    f"Order sequence error: expected {received}, "
                    f"got {order['order_id']}"
                )

            sent += 1

        while not rb.is_empty():
            item = rb.pop()
            if item is None:
                continue

            order = unpack_order(item)
            received += 1
            assert order["order_id"] == received, (
                f"Order sequence error: expected {received}, "
                f"got {order['order_id']}"
            )

        assert received == sent, (
            f"Order count mismatch: sent {sent}, received {received}"
        )

        print(f"Sent: {sent}")
        print(f"Received: {received}")
        print("Order sequence: correct")
        print("IPC audit: PASSED")

    finally:
        rb.close()


if __name__ == "__main__":
    main()
