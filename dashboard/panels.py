
"""Helper functions for ChronosMatch dashboard metrics."""


def calculate_orders_per_second(previous_count, current_count, elapsed_seconds):
    """Calculate order throughput from two counter readings."""
    if elapsed_seconds <= 0:
        return 0.0

    difference = max(0, current_count - previous_count)
    return difference / elapsed_seconds


def format_last_trade(trade):
    """Format the latest trade for dashboard display."""
    if not trade:
        return "Last trade: waiting for trade"

    side = str(trade.get("side", "UNKNOWN")).upper()
    price = trade.get("price", "N/A")
    quantity = trade.get("quantity", "N/A")

    return f"Last trade: {side} {quantity} @ {price}"


def engine_is_alive(heartbeat_time, now, timeout_seconds=2):
    """Return True when a heartbeat timestamp is recent."""
    if heartbeat_time is None or heartbeat_time <= 0:
        return False

    age = now - heartbeat_time
    return 0 <= age <= timeout_seconds


def build_metrics(
    previous_count,
    current_count,
    elapsed_seconds,
    last_trade,
    heartbeat_time,
    now,
):
    """Combine values into a dictionary for the dashboard."""
    return {
        "orders_per_second": calculate_orders_per_second(
            previous_count, current_count, elapsed_seconds
        ),
        "last_trade": format_last_trade(last_trade),
        "engine_status": (
            "ALIVE"
            if engine_is_alive(heartbeat_time, now)
            else "NOT RESPONDING"
        ),
    }