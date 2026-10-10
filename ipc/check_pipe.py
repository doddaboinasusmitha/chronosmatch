from ipc.record import BUY, SELL, pack_order, unpack_order
from ipc.ring_buffer import RingBuffer

rb = RingBuffer("check.ring", capacity=100)
sent = received = 0

for i in range(1, 10001):
    side = BUY if i % 2 else SELL
    while not rb.push(pack_order(i, 10000 + i % 50, 10, side, i)):
        order = unpack_order(rb.pop())
        assert order["order_id"] == received + 1
        received += 1
    sent += 1

while not rb.is_empty():
    order = unpack_order(rb.pop())
    assert order["order_id"] == received + 1
    received += 1

print("sent:", sent, "received:", received, "in order:", sent == received)
rb.close()
