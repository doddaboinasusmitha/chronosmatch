
import pytest

from engine.metrics import calculate_latency_ns, latency_bucket_index


def test_calculates_latency():
    assert calculate_latency_ns(100, now_ns=175) == 75


def test_future_timestamp_is_ignored():
    assert calculate_latency_ns(200, now_ns=100) is None


def test_negative_timestamp_is_rejected():
    with pytest.raises(ValueError):
        calculate_latency_ns(-1, now_ns=100)


def test_base_two_bucket_boundaries():
    assert latency_bucket_index(0) == 0
    assert latency_bucket_index(1) == 0
    assert latency_bucket_index(2) == 1
    assert latency_bucket_index(3) == 1
    assert latency_bucket_index(4) == 2


def test_large_latency_uses_last_bucket():
    assert latency_bucket_index(2**64) == 63


def test_negative_latency_is_rejected():
    with pytest.raises(ValueError):
        latency_bucket_index(-1)
