import asyncio

from ipc.ring_buffer import RingBuffer
from simulator.order_generator import generate_order


async def run(count=1000):
    rb = RingBuffer("orders.ring", capacity=100000)
    sent = 0
    for _ in range(count):
        if rb.push(generate_order()):
            sent += 1
        await asyncio.sleep(0)
    print("orders written:", sent)
    rb.close()


if __name__ == "__main__":
    asyncio.run(run())
