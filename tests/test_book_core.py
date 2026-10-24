import pytest

from engine.book_core import BookCore


def test_add_order_and_best_prices():
    book = BookCore(1000)
    book.add_order(0, 100, 5, 1)
    book.add_order(1, 110, 4, 2)

    assert book.best_bid() == 100
    assert book.best_ask() == 110
    assert book.quantity_at(0, 100) == 5
    assert book.quantity_at(1, 110) == 4


def test_fifo_matching_at_same_price():
    book = BookCore(1000)
    book.add_order(1, 100, 3, 11)
    book.add_order(1, 100, 5, 12)

    trades = book.add_order(0, 100, 4, 20)

    assert trades == [
        {
            "buy_order_id": 20,
            "sell_order_id": 11,
            "price": 100,
            "quantity": 3,
        },
        {
            "buy_order_id": 20,
            "sell_order_id": 12,
            "price": 100,
            "quantity": 1,
        },
    ]
    assert book.quantity_at(1, 100) == 4


def test_partial_fill_preserves_remaining_quantity():
    book = BookCore(1000)
    book.add_order(1, 100, 10, 11)

    trades = book.add_order(0, 100, 4, 20)

    assert len(trades) == 1
    assert trades[0]["quantity"] == 4
    assert book.quantity_at(1, 100) == 6


def test_non_crossing_orders_do_not_trade():
    book = BookCore(1000)
    book.add_order(1, 110, 5, 11)

    trades = book.add_order(0, 100, 3, 20)

    assert trades == []
    assert book.best_bid() == 100
    assert book.best_ask() == 110


def test_best_price_priority():
    book = BookCore(1000)
    book.add_order(1, 105, 2, 11)
    book.add_order(1, 100, 3, 12)

    trades = book.add_order(0, 110, 4, 20)

    assert [trade["sell_order_id"] for trade in trades] == [12, 11]
    assert [trade["price"] for trade in trades] == [100, 105]


@pytest.mark.parametrize(
    "side,price,quantity",
    [
        (2, 100, 1),
        (0, 0, 1),
        (0, 1001, 1),
        (0, 100, 0),
    ],
)
def test_invalid_orders_are_rejected(side, price, quantity):
    book = BookCore(1000)

    with pytest.raises(ValueError):
        book.add_order(side, price, quantity, 1)
