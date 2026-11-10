# ChronosMatch Dashboard

## Overview

The terminal dashboard reads engine statistics using the read-only StatsReader interface.

It displays:
- Best bid and best ask
- Market spread
- Orders processed and trades executed
- Orders per second
- P50 and P99 latency estimates
- Engine heartbeat status
- Latest trade

## Demo

The simulator invokes MatchingEngine directly and updates shared statistics.

Run the simulator with temporary output files, then launch the dashboard from the temporary demo directory with the repository on PYTHONPATH.

Press Q to exit the dashboard.

## Architecture note

The standalone engine loop is a separate consumer that attaches to existing shared-memory files. Do not start both processing paths for the same simulator demo.

## Data limitation

The statistics interface exposes aggregate market information, not individual order records. Live order-depth and whale-order displays are not claimed by this dashboard.
