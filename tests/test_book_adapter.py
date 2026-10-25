from engine.book_adapter import (
    BookCore,
    CythonOrderBook,
    create_order_book,
)
from engine.order_book import OrderBook
from ipc.record import BUY, SELL, pack_order


def test_factory_uses_cython_when_available():
    book = create_order_book()
    if BookCore is not None:
        assert isinstance(book, CythonOrderBook)
    else:
        assert isinstance(book, OrderBook)


def test_cython_adapter_matches_python_trade_results():
    if BookCore is None:
        return

    python_book = OrderBook()
    cython_book = CythonOrderBook()

    orders = [
        pack_order(1, 10000, 3, SELL, 100),
        pack_order(2, 10005, 5, SELL, 101),
        pack_order(3, 10005, 6, BUY, 102),
        pack_order(4, 9995, 2, BUY, 103),
    ]

    python_trades = []
    cython_trades = []

    for order in orders:
        python_trades.extend(python_book.add_order(order))
        cython_trades.extend(cython_book.add_order(order))

    assert cython_trades == python_trades
    assert cython_book.get_best_bid() == python_book.get_best_bid()
    assert cython_book.get_best_ask() == python_book.get_best_ask()


def test_factory_can_force_python_fallback():
    assert isinstance(create_order_book(prefer_cython=False), OrderBook)


def test_cython_adapter_rejects_invalid_orders():
    if BookCore is None:
        return

    import pytest

    book = CythonOrderBook()
    with pytest.raises(ValueError):
        book.add_order(pack_order(1, 0, 1, BUY, 100))
