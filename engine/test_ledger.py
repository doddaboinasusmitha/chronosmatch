
from engine.ledger import OrderLedger


def test_ledger_recovers_saved_orders(tmp_path):
    test_file = tmp_path / "test_orders.jsonl"

    ledger = OrderLedger(str(test_file))
    try:
        ledger.append_order({
            "order_id": 1,
            "price": 100,
            "quantity": 10,
            "side": 0,
            "timestamp_ns": 123456,
        })
    finally:
        ledger.close()

    ledger = OrderLedger(str(test_file))
    try:
        orders = ledger.recover_orders()

        assert len(orders) == 1
        assert orders[0]["order_id"] == 1
        assert orders[0]["price"] == 100
        assert orders[0]["quantity"] == 10
    finally:
        ledger.close()


def test_ledger_discards_incomplete_final_line(tmp_path):
    test_file = tmp_path / "test_orders.jsonl"

    test_file.write_bytes(
        b'{"order_id":1,"price":100}\n'
        b'{"order_id":2'
    )

    ledger = OrderLedger(str(test_file))
    try:
        orders = ledger.recover_orders()

        assert len(orders) == 1
        assert orders[0]["order_id"] == 1
    finally:
        ledger.close()
