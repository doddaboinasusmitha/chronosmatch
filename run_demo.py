"""ChronosMatch integrated demo launcher."""

import subprocess
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


def run_command(command, description):
    """Run a project command and report its result."""
    print(f"\n{description}", flush=True)

    result = subprocess.run(
        command,
        cwd=BASE_DIR,
        check=False,
    )

    if result.returncode != 0:
        print(f"\nERROR: {description} failed.")
        return False

    return True


def main():
    print("=" * 55)
    print("             CHRONOSMATCH FINAL DEMO")
    print("=" * 55)

    # Step 1: Run simulator and save trades to SQLite.
    simulator_command = [
        sys.executable,
        "-m",
        "simulator.simulator",
        "--count", "100",
        "--seed", "42",
        "--journal-db", str(BASE_DIR / "trades.db"),
    ]

    success = run_command(
        simulator_command,
        "STEP 1: Starting simulator and matching engine...",
    )

    if not success:
        return

    print("\nSimulator and matching engine completed.")
    print("Trade journal database: trades.db")

    # Step 2: Start the market dashboard.
    dashboard_command = [
        sys.executable,
        "-m",
        "dashboard.dashboard",
    ]

    success = run_command(
        dashboard_command,
        "STEP 2: Starting ChronosMatch market dashboard...",
    )

    if not success:
        return

    print("\n" + "=" * 55)
    print("          CHRONOSMATCH DEMO FINISHED")
    print("=" * 55)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nDemo interrupted by user.")

   