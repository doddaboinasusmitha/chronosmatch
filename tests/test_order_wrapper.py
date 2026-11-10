import pytest

from ipc.order_wrapper import decode_order
from ipc.record import BUY, pack_order


def test_decode_order_valid_record():
    record = pack_order(1, 10050, 100, BUY, 123456789)

    result = decode_order(record)

    assert result == {
        "order_id": 1,
        "price": 10050,
        "quantity": 100,
        "side": BUY,
        "timestamp_ns": 123456789,
    }


def test_decode_order_invalid_length():
    with pytest.raises(ValueError):
        decode_order(b"invalid")
