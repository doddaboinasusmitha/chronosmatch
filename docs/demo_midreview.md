ChronosMatch — Mid Review Demo Script

1. Introduction

Hello everyone. This is our ChronosMatch project, a Python-based market simulation and matching-system project.

The goal is to demonstrate the project structure, order data handling, simulation components, dashboard, and automated tests.

2. Project Structure

First, I will show the main project folders:

- "ipc/" — inter-process communication and order record handling.
- "simulator/" — order generator and simulation components.
- "engine/" — matching-engine components.
- "dashboard/" — dashboard interface and display helpers.
- "tests/" — automated tests.
- "docs/" — project documentation.

3. Order Data and Testing

Next, I will explain how the project defines and handles order records and uses a ring buffer.

I will show the relevant code and the tests that check record handling, buffer behaviour, and dashboard metric helper functions.

4. Dashboard Demonstration

Next, I will demonstrate the dashboard interface and explain how it displays market information.

I will also explain the dashboard metric helpers, including orders-per-second calculation, last-trade formatting, and engine heartbeat status.

These helpers have automated tests. Live metric values should only be demonstrated if the dashboard is connected to the corresponding running engine or shared statistics data.

5. Automated Tests

I will run the project's automated tests from the repository root and show the results.

The tests help us check that the implemented components behave as expected.

6. Conclusion

This mid-review demonstrates our current project structure, implemented components, dashboard work, and testing approach.

Further integration and end-to-end verification will be demonstrated as those components become available.

Thank you.