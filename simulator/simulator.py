
import asyncio
import time
from statistics import mean

from ipc.ring_buffer import RingBuffer
from ipc.record import unpack_order
from simulator.order_generator import generate_order


async def producer(rb, count, stats):
    for _ in range(count):
        order = generate_order()

        while not rb.push(order):
            await asyncio.sleep(0)

        stats["sent"] += 1

        if stats["sent"] % 1000 == 0:
            await asyncio.sleep(0)

    stats["done"] = True


async def consumer(rb, stats):
    while not (stats["done"] and rb.is_empty()):
        data = rb.pop()

        if data is None:
            await asyncio.sleep(0)
            continue

        order = unpack_order(data)
        latency_ns = time.time_ns() - order["timestamp_ns"]

        stats["received"] += 1
        stats["latencies_ns"].append(max(0, latency_ns))


async def run(count=200000):
    rb = RingBuffer("orders.ring", capacity=100000)
    stats = {
        "sent": 0,
        "received": 0,
        "done": False,
        "latencies_ns": [],
    }

    start = time.perf_counter()

    try:
        await asyncio.gather(
            producer(rb, count, stats),
            consumer(rb, stats),
        )
    finally:
        rb.close()

    elapsed = time.perf_counter() - start
    received = stats["received"]

    print(f"Sent: {stats['sent']}")
    print(f"Received: {received}")
    print(f"Elapsed: {elapsed:.2f} seconds")

    if elapsed > 0:
        print(f"Throughput: {received / elapsed:,.0f} orders/sec")

    if stats["latencies_ns"]:
        latencies_us = [
            value / 1000 for value in stats["latencies_ns"]
        ]
        print(f"Average latency: {mean(latencies_us):.2f} microseconds")
        print(f"Maximum latency: {max(latencies_us):.2f} microseconds")


if __name__ == "__main__":
    asyncio.run(run())
