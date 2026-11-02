ChronosMatch Usage Guide

Overview

ChronosMatch is a zero-copy high-frequency trading engine designed to process buy and sell orders using a shared-memory ring buffer.

This guide explains how to set up, test, and run the project.

1. Open the Project

Open the ChronosMatch repository in Visual Studio Code.

Open the terminal and navigate to the project root directory.

2. Set Up the Environment

Create a Python virtual environment:

python -m venv .venv

Activate the environment:

.\.venv\Scripts\Activate.ps1

Install the required dependencies:

python -m pip install -r requirements.txt

3. Run the Tests

Run the following command to check whether the project is working correctly:

python -m pytest -v

The tests check different components, including the ring buffer and simulator.

4. Run the Benchmark

Run the benchmark script:

python benchmarks/benchmark_simulator.py --count 100

The benchmark generates and processes 100 orders and displays the resulting trade and market statistics.

5. Dashboard

Refer to "dashboard/README.md" for instructions on running the market dashboard.

The dashboard displays market information such as order book details, activity, and engine status.

6. Troubleshooting

- If Python is not recognized, check that Python is installed and added to PATH.
- If dependencies fail to install, check your internet connection and Python version.
- If tests fail, review the error messages in the terminal.
- If the dashboard does not start, refer to "dashboard/README.md".

Important Note

A complete live demonstration requires the simulator, matching engine, shared statistics, and dashboard to be integrated and running.

Refer to "docs/setup.md" for additional setup instructions.