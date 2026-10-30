
import argparse
import statistics
import time

from engine.book_adapter import create_order_book
from engine.order_book import OrderBook
from simulator.order_generator import OrderGenerator


def run_benchmark(count, seed):
    generator = OrderGenerator(seed=seed)
    book = create_order_book(prefer_cython=True)

    latencies = []
    start = time.perf_counter_ns()

    for _ in range(count):
        order = generator.generate_order()

        order_start = time.perf_counter_ns()
        book.add_order(order)
        order_end = time.perf_counter_ns()

        latencies.append(order_end - order_start)

    elapsed = time.perf_counter_ns() - start

    throughput = count / (elapsed / 1_000_000_000)
    ordered = sorted(latencies)
    p99 = ordered[min(len(ordered) - 1, int(len(ordered) * 0.99))]

    return {
        "orders": count,
        "seed": seed,
        "throughput": throughput,
        "p99_ns": p99,
        "elapsed_seconds": elapsed / 1_000_000_000,
        "engine": type(book).__name__,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    if args.count < 1:
        parser.error("--count must be positive")

    result = run_benchmark(args.count, args.seed)

    print("\nCHRONOSMATCH ENGINE BENCHMARK")
    print("-----------------------------")
    for key, value in result.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
