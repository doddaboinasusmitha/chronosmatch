import pytest

from ipc.trade import TRADE_SIZE, pack_trade, unpack_trade


def test_trade_record_size():
    record = pack_trade(1, 10050, 100, 0, 123456789, 10, 20, 30)

    assert len(record) == 64
    assert TRADE_SIZE == 64


def test_trade_round_trip():
    record = pack_trade(1, 10050, 100, 0, 123456789, 10, 20, 30)

    result = unpack_trade(record)

    assert result == {
        "order_id": 1,
        "price": 10050,
        "quantity": 100,
        "side": 0,
        "timestamp_ns": 123456789,
        "trade_id": 10,
        "buyer_id": 20,
        "seller_id": 30,
    }


def test_trade_wrong_length():
    with pytest.raises(ValueError):
        unpack_trade(b"abc")
