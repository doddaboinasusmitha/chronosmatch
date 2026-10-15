import argparse
import asyncio

from ipc.ring_buffer import RingBuffer
from simulator.order_generator import OrderGenerator


async def run(count=1000, rate=1000, seed=None, ring="orders.ring"):
    rb = RingBuffer(ring, capacity=100000)
    generator = OrderGenerator(seed=seed)
    sent = 0

    try:
        interval = 1 / rate if rate > 0 else 0
        start_time = asyncio.get_running_loop().time()

        for i in range(count):
            order = generator.generate_order()

            if rb.push(order):
                sent += 1

            if interval > 0:
                target_time = start_time + (i + 1) * interval
                delay = target_time - asyncio.get_running_loop().time()

                if delay > 0:
                    await asyncio.sleep(delay)
            else:
                await asyncio.sleep(0)

        print("orders written:", sent)

    finally:
        rb.close()


def main():
    parser = argparse.ArgumentParser(
        description="ChronosMatch order simulator"
    )

    parser.add_argument(
        "--count",
        type=int,
        default=1000,
        help="number of orders to generate"
    )

    parser.add_argument(
        "--rate",
        type=float,
        default=1000,
        help="target orders per second"
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="random seed for reproducible orders"
    )

    parser.add_argument(
        "--ring",
        default="orders.ring",
        help="ring buffer file path"
    )

    args = parser.parse_args()

    if args.count < 0:
        parser.error("--count must be zero or greater")

    if args.rate < 0:
        parser.error("--rate cannot be negative")

    asyncio.run(
        run(
            count=args.count,
            rate=args.rate,
            seed=args.seed,
            ring=args.ring
        )
    )


if __name__ == "__main__":
    main()
