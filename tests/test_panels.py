
from dashboard.panels import (
    calculate_orders_per_second,
    format_last_trade,
    engine_is_alive,
)


def test_orders_per_second():
    assert calculate_orders_per_second(100, 150, 5) == 10.0


def test_zero_elapsed_time():
    assert calculate_orders_per_second(100, 150, 0) == 0.0


def test_counter_reset():
    assert calculate_orders_per_second(150, 10, 2) == 0.0


def test_missing_last_trade():
    assert format_last_trade(None) == "Last trade: waiting for trade"


def test_format_last_trade():
    trade = {"side": "BUY", "quantity": 5, "price": 10025}
    assert format_last_trade(trade) == "Last trade: BUY 5 @ 10025"


def test_recent_heartbeat():
    assert engine_is_alive(9, 10) is True


def test_old_heartbeat():
    assert engine_is_alive(5, 10) is False
