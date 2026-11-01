import random

import pytest

from engine.book_adapter import BookCore, CythonOrderBook
from engine.order_book import OrderBook
from ipc.record import BUY, SELL, pack_order


ORDER_COUNT = 100_000
RANDOM_SEED = 20261025
MIN_PRICE = 50
MAX_PRICE = 150
CYTHON_MAX_PRICE = 200
SNAPSHOT_INTERVAL = 1000


def assert_book_state_matches(python_book, cython_book, observed_prices):
    """Compare all observed price levels in both order books."""
    python_snapshot = python_book.get_snapshot()

    expected_bids = dict(python_snapshot["bids"])
    expected_asks = dict(python_snapshot["asks"])

    for price in observed_prices:
        cython_bid_quantity = cython_book._core.quantity_at(BUY, price)
        cython_ask_quantity = cython_book._core.quantity_at(SELL, price)

        assert cython_bid_quantity == expected_bids.get(price, 0), (
            f"Bid quantity mismatch at price {price}"
        )

        assert cython_ask_quantity == expected_asks.get(price, 0), (
            f"Ask quantity mismatch at price {price}"
        )

    assert cython_book.get_best_bid() == python_book.get_best_bid()
    assert cython_book.get_best_ask() == python_book.get_best_ask()


@pytest.mark.skipif(
    BookCore is None,
    reason="Cython BookCore extension is unavailable",
)
def test_python_cython_parity_for_100000_seeded_orders():
    """Verify Python and Cython matching results for 100,000 orders."""
    rng = random.Random(RANDOM_SEED)

    python_book = OrderBook()
    cython_book = CythonOrderBook(max_price=CYTHON_MAX_PRICE)

    observed_prices = set()

    for order_id in range(1, ORDER_COUNT + 1):
        side = rng.choice((BUY, SELL))
        price = rng.randint(MIN_PRICE, MAX_PRICE)
        quantity = rng.randint(1, 500)

        order_data = pack_order(
            order_id,
            price,
            quantity,
            side,
            order_id,
        )

        observed_prices.add(price)

        python_trades = python_book.add_order(order_data)
        cython_trades = cython_book.add_order(order_data)

        assert cython_trades == python_trades, (
            f"Trade mismatch at order {order_id}: "
            f"Python={python_trades}, Cython={cython_trades}"
        )

        assert cython_book.get_best_bid() == python_book.get_best_bid(), (
            f"Best bid mismatch at order {order_id}"
        )

        assert cython_book.get_best_ask() == python_book.get_best_ask(), (
            f"Best ask mismatch at order {order_id}"
        )

        if order_id % SNAPSHOT_INTERVAL == 0:
            assert_book_state_matches(
                python_book,
                cython_book,
                observed_prices,
            )

    assert_book_state_matches(
        python_book,
        cython_book,
        observed_prices,
    )
