
from dashboard.dashboard import get_market_data, percentile_latency_ns
from ipc.stats import StatsBlock


def test_market_data_structure():
    data = get_market_data()

    assert data["available"] is True
    assert "buy_orders" in data
    assert "sell_orders" in data
    assert "activity" in data


def test_market_data_orders_have_required_fields():
    data = get_market_data()

    for order in data["buy_orders"] + data["sell_orders"]:
        assert "price" in order
        assert "quantity" in order
        assert "order_id" in order


def test_latency_percentiles_from_histogram():
    buckets = [0] * 64
    buckets[0] = 2
    buckets[2] = 2

    assert percentile_latency_ns(buckets, 50) == 1
    assert percentile_latency_ns(buckets, 99) == 7
    assert percentile_latency_ns([0] * 64, 50) is None


def test_dashboard_reads_live_stats(tmp_path):
    path = tmp_path / "stats.bin"
    writer = StatsBlock(str(path), create=True)

    writer.update(
        orders=4,
        trades=1,
        best_bid=10000,
        best_ask=10020,
        last_trade_price=10020,
        last_trade_quantity=3,
    )
    writer.increment_latency_bucket(2)
    writer.close()

    data = get_market_data(str(path))

    assert data["orders"] == 4
    assert data["trades"] == 1
    assert data["best_bid"] == 10000
    assert data["best_ask"] == 10020
    assert data["spread"] == 20
    assert data["last_trade_price"] == 10020
    assert data["p50_latency_ns"] == 7
    assert data["p99_latency_ns"] == 7
