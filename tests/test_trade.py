
import pytest

from ipc.trade import pack_trade, unpack_trade


def sample_trade():
    return {
        "order_id": 1001,
        "price": 25000,
        "quantity": 10,
        "side": 0,
        "timestamp_ns": 123456789,
        "trade_id": 2001,
        "buyer_id": 3001,
        "seller_id": 3002,
    }


def test_trade_record_size_is_64_bytes():
    packed = pack_trade(**sample_trade())
    assert len(packed) == 64


def test_trade_pack_unpack_round_trip():
    trade = sample_trade()
    packed = pack_trade(**trade)
    unpacked = unpack_trade(packed)
    assert unpacked == trade


def test_unpack_trade_wrong_length_raises_value_error():
    with pytest.raises(ValueError):
        unpack_trade(b"too short")

