from dashboard.dashboard import get_market_data


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