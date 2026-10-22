
"""Latency calculation helpers for ChronosMatch."""

import time

from ipc.stats import LATENCY_BUCKETS


def calculate_latency_ns(timestamp_ns, now_ns=None):
    """Return order latency in nanoseconds, or None for a future timestamp."""
    if not isinstance(timestamp_ns, int) or timestamp_ns < 0:
        raise ValueError("timestamp_ns must be a non-negative integer")

    if now_ns is None:
        now_ns = time.time_ns()

    if not isinstance(now_ns, int) or now_ns < 0:
        raise ValueError("now_ns must be a non-negative integer")

    if timestamp_ns > now_ns:
        return None

    return now_ns - timestamp_ns


def latency_bucket_index(latency_ns):
    """Map latency to a base-2 bucket index from 0 to 63."""
    if not isinstance(latency_ns, int) or latency_ns < 0:
        raise ValueError("latency_ns must be a non-negative integer")

    if latency_ns <= 1:
        return 0

    return min(latency_ns.bit_length() - 1, LATENCY_BUCKETS - 1)
