ChronosMatch Architecture

Overview

ChronosMatch is a zero-copy high-frequency trading engine. It uses a shared-memory ring buffer to transfer orders between the simulator and matching engine.

System Architecture

flowchart TD
    A[Order Simulator] --> B[Shared Memory Ring Buffer]
    B --> C[Matching Engine]
    C --> D[Order Matching]
    D --> E[Trade Execution]
    E --> F[Trade Database]
    C --> G[Statistics]
    G --> H[Market Dashboard]
    F --> H

Components

1. Order Simulator

Generates buy and sell orders for testing the matching engine.

2. Shared Memory Ring Buffer

Transfers orders between the simulator and matching engine. It avoids unnecessary data copying.

3. Matching Engine

Receives orders and processes them according to the matching logic.

4. Order Matching

Matches compatible buy and sell orders based on price and order rules.

5. Trade Execution

Creates trade records when orders are successfully matched.

6. Trade Database

Stores trade information for later review and analysis.

7. Statistics

Collects engine performance metrics such as orders processed and orders per second.

8. Market Dashboard

Displays order book information, activity, engine status, and performance metrics.

Data Flow

1. The simulator generates orders.
2. Orders are placed into the shared memory ring buffer.
3. The matching engine reads and processes the orders.
4. Compatible buy and sell orders are matched.
5. Executed trades are recorded in the database.
6. Statistics are collected and displayed on the dashboard.

Summary

ChronosMatch uses a modular architecture in which the simulator, ring buffer, matching engine, trade database, statistics, and dashboard work together to process and display market orders.