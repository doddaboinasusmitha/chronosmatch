import asyncio
import time

from ipc.ring_buffer import RingBuffer
from simulator.order_generator import generate_order


async def producer(rb, count, stats):
    for _ in range(count):
        while not rb.push(generate_order()):
            await asyncio.sleep(0)
        stats["sent"] += 1
        if stats["sent"] % 1000 == 0:
            await asyncio.sleep(0)
    stats["done"] = True


async def consumer(rb, stats):
    while not (stats["done"] and rb.is_empty()):
        if rb.pop() is None:
            await asyncio.sleep(0)
        else:
            stats["received"] += 1


async def run(count=200000):
    rb = RingBuffer("orders.ring", capacity=100000)
    stats = {"sent": 0, "received": 0, "done": False}
    start = time.perf_counter()

    await asyncio.gather(
        producer(rb, count, stats),
        consumer(rb, stats)
    )

    elapsed = time.perf_counter() - start
    print(
        f"sent {stats['sent']} received {stats['received']} "
        f"in {elapsed:.2f}s = {stats['sent'] / elapsed:,.0f} orders/sec"
    )
    rb.close()


if __name__ == "__main__":
    asyncio.run(run())