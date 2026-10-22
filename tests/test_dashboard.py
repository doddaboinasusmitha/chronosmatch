from dashboard.dashboard import get_market_data


def test_market_data_structure():
    data = get_market_data()

    assert data["available"] is False
    assert "buy_orders" in data
    assert "sell_orders" in data
    assert "activity" in data


def test_market_data_orders_have_required_fields():
    data = get_market_data()

    for order in data["buy_orders"] + data["sell_orders"]:
        assert "price" in order
        assert "quantity" in order
        assert "order_id" in order


def test_dashboard_shows_engine_not_responding_without_live_data():
    data = get_market_data()

    assert data["available"] is False
    assert data["engine_status"] == "NOT RESPONDING"
    assert data["orders_per_second"] == 0.0
    assert data["last_trade"] == "Last trade: waiting for trade"