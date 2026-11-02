import argparse
import subprocess
import sys
import time


def run_benchmark(count, seed):
    command = [
        sys.executable,
        "-m",
        "simulator.simulator",
        "--count",
        str(count),
        "--rate",
        "0",
        "--seed",
        str(seed),
    ]

    print("\n--- ChronosMatch Benchmark ---")
    print(f"Orders requested: {count}")
    print(f"Random seed: {seed}")

    start_time = time.perf_counter()

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
    )

    end_time = time.perf_counter()

    elapsed = end_time - start_time

    if result.returncode != 0:
        print("\nBenchmark failed!")
        print(result.stderr)
        return

    throughput = count / elapsed if elapsed > 0 else 0

    print("\n--- Benchmark Results ---")
    print(f"Execution time: {elapsed:.4f} seconds")
    print(f"Orders processed: {count}")
    print(f"Throughput: {throughput:.2f} orders/second")

    print("\n--- Simulator Output ---")
    print(result.stdout)


def main():
    parser = argparse.ArgumentParser(
        description="ChronosMatch benchmark script"
    )

    parser.add_argument(
        "--count",
        type=int,
        default=100,
        help="Number of orders to process",
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed",
    )

    args = parser.parse_args()

    if args.count <= 0:
        parser.error("--count must be greater than 0")

    run_benchmark(args.count, args.seed)


if __name__ == "__main__":
    main()

    