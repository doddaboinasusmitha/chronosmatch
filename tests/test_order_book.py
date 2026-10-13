
from engine.order_book import OrderBook
from ipc.record import pack_order, BUY, SELL


def test_add_buy_and_sell_orders():
    book = OrderBook()

    book.add_order(pack_order(1, 10050, 10, BUY, 123))
    book.add_order(pack_order(2, 10100, 5, SELL, 124))

    assert book.get_best_bid() == 10050
    assert book.get_best_ask() == 10100


def test_orders_at_same_price_are_aggregated():
    book = OrderBook()

    book.add_order(pack_order(1, 10050, 10, BUY, 123))
    book.add_order(pack_order(2, 10050, 5, BUY, 124))

    assert book.get_snapshot()["bids"] == [(10050, 15)]


def test_best_prices_are_selected_correctly():
    book = OrderBook()

    book.add_order(pack_order(1, 10000, 10, BUY, 123))
    book.add_order(pack_order(2, 10100, 5, BUY, 124))
    book.add_order(pack_order(3, 10200, 8, SELL, 125))
    book.add_order(pack_order(4, 10150, 4, SELL, 126))

    assert book.get_best_bid() == 10100
    assert book.get_best_ask() == 10150


def test_empty_order_book():
    book = OrderBook()

    assert book.get_best_bid() is None
    assert book.get_best_ask() is None
    assert book.get_snapshot() == {"bids": [], "asks": []}
