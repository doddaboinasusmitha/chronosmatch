
from engine.ledger import OrderLedger
import os

TEST_FILE = "test_orders.jsonl"

# Start with a clean test file.
if os.path.exists(TEST_FILE):
    os.remove(TEST_FILE)

# Save an order and close the ledger.
ledger = OrderLedger(TEST_FILE)
ledger.append_order({
    "order_id": 1,
    "price": 100,
    "quantity": 10,
    "side": 0,
    "timestamp_ns": 123456
})
ledger.close()

# Reopen the ledger and recover saved orders.
ledger = OrderLedger(TEST_FILE)
orders = ledger.recover_orders()
ledger.close()

assert len(orders) == 1
assert orders[0]["order_id"] == 1
assert orders[0]["price"] == 100

print("Recovered orders:", orders)
print("Ledger recovery test: PASSED")
