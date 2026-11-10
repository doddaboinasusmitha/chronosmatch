ChronosMatch – Zero-Copy High-Frequency Trading Engine

1. Project Overview

ChronosMatch is a Python-based high-frequency trading simulation system designed to demonstrate efficient order processing, matching, shared-memory communication, and real-time market monitoring.

The project uses a memory-mapped ring buffer to transfer order data between components efficiently, reducing unnecessary data copying.

2. Key Features

- Order Simulation: Generates buy and sell orders for testing.
- Zero-Copy Communication: Uses a memory-mapped ring buffer for efficient data transfer.
- Matching Engine: Processes orders and matches compatible buy and sell orders.
- Order Book: Maintains buy and sell order information.
- Trade Execution: Generates trade records when orders are matched.
- SQLite Database: Stores executed trade information.
- Dashboard: Displays market information and engine status.
- Performance Testing: Includes benchmarks and automated tests.

3. System Architecture

       Order Simulator
              |
              v
     Shared Memory Ring Buffer
              |
              v
       Matching Engine
              |
              v
         Order Book
              |
              v
       Trade Execution
              |
        +-----+------+
        |            |
        v            v
   SQLite DB     Statistics
                     |
                     v
                  Dashboard

4. Technologies Used

- Python
- Cython (optional acceleration)
- Memory-mapped files
- SQLite
- Curses dashboard
- Pytest
- Git and GitHub

5. Project Structure

chronosmatch/
│
├── engine/
│   ├── matching_engine.py
│   ├── order_book.py
│   ├── ledger.py
│   ├── metrics.py
│   └── convert_report.py
│
├── ipc/
│   └── Ring buffer implementation
│
├── simulator/
│   └── Order generation
│
├── dashboard/
│   ├── dashboard.py
│   └── panels.py
│
├── tests/
│   └── Automated test files
│
├── docs/
│   ├── architecture.md
│   ├── benchmark_results.md
│   ├── project_report.md
│   ├── project_report.pdf
│   └── submission_checklist.md
│
├── run_demo.py
├── requirements.txt
└── README.md

6. Installation

Clone the repository:

git clone https://github.com/doddaboinasusmitha/chronosmatch.git

Move into the project directory:

cd chronosmatch

Create a virtual environment:

python -m venv venv

Activate it on Windows:

.\venv\Scripts\Activate.ps1

Install the dependencies:

python -m pip install -r requirements.txt

7. Running the Project

Run the integrated demonstration:

python run_demo.py

The demonstration executes the order simulation, matching engine, trade processing, database storage, and dashboard.

Press "Q" to exit the dashboard.

8. Running Automated Tests

Execute the test suite:

python -m pytest -v

The project test suite has previously completed successfully with 100 tests passed.

9. Database Verification

To check the SQLite trade database, run:

python check_db.py

The verification script displays the database tables and their record counts.

10. Project Documentation

Additional documentation is available in the "docs/" directory, including:

- System architecture
- Ring buffer design
- Data contract and record specification
- Benchmark results
- Setup and usage guide
- Final project report
- Final review video script
- Submission checklist

11. Conclusion

ChronosMatch demonstrates how order simulation, efficient shared-memory communication, matching algorithms, trade execution, database storage, and dashboard monitoring can be integrated into a high-frequency trading simulation system.

The project provides practical experience in Python development, system integration, performance testing, and software collaboration.

---

Project: ChronosMatch
Repository: https://github.com/doddaboinasusmitha/chronosmatch
Branch: sushmitha-ba