ChronosMatch



Zero-Copy High-Frequency Trading Engine



ChronosMatch is a high-frequency trading engine project designed to process buy and sell orders using a shared-memory ring buffer. It demonstrates order processing, matching, trade recording, statistics, and market dashboard concepts.



Features



\- Shared-memory ring buffer for order transfer

\- Order simulator for generating buy and sell orders

\- Matching engine for processing orders

\- Trade recording and statistics

\- Market dashboard for displaying order book information

\- Automated tests

\- Benchmark simulator



Architecture



The main components of ChronosMatch include:



1\. Order Simulator

2\. Shared Memory Ring Buffer

3\. Matching Engine

4\. Trade Execution

5\. Trade Database

6\. Statistics

7\. Market Dashboard



Refer to "docs/architecture.md" (docs/architecture.md) for the architecture diagram and component details.



Project Structure



chronosmatch/

├── benchmarks/

├── dashboard/

├── docs/

├── engine/

├── ipc/

├── simulator/

├── tests/

├── requirements.txt

└── README.md



Requirements



\- Python

\- Git

\- Visual Studio Code (recommended)



Setup



Clone the repository and navigate to its root directory.



Create a virtual environment:



python -m venv .venv



Activate it:



.\\.venv\\Scripts\\Activate.ps1



Install dependencies:



python -m pip install -r requirements.txt



Run Tests



Run the automated tests:



python -m pytest -v



The tests verify components such as the ring buffer and simulator.



Run Benchmark



Run the benchmark simulator:



python benchmarks/benchmark\_simulator.py --count 100



Benchmark Results



In a benchmark run with 100 orders:



Metric| Result

Orders generated| 100

Orders processed| 100

Trades produced| 77

Orders in statistics| 100

Best bid| 10026

Best ask| 10034

Last trade price| 10026



See "docs/benchmark\_results.md" (docs/benchmark\_results.md) for more details.



Dashboard



Refer to "dashboard/README.md" (dashboard/README.md) for dashboard instructions.



A complete live demonstration requires the simulator, matching engine, shared statistics, and dashboard to be integrated and running.



Documentation



\- "Setup Guide" (docs/setup.md)

\- "Usage Guide" (docs/usage\_guide.md)

\- "Architecture" (docs/architecture.md)

\- "Benchmark Results" (docs/benchmark\_results.md)



Project Status



ChronosMatch is a project demonstrating trading engine components, order processing, benchmarking, and dashboard functionality. Refer to the module documentation for implementation details and usage instructions.



License



See the repository license file, if available.
