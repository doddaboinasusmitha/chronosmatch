import pytest

from ipc.record import ORDER_SIZE, BUY, SELL, pack_order, unpack_order


def test_record_size_is_32_bytes():
    assert ORDER_SIZE == 32


def test_pack_unpack_roundtrip():
    raw = pack_order(1, 10050, 100, BUY, 123456789)
    assert len(raw) == 32
    assert unpack_order(raw) == {
        "order_id": 1, "price": 10050, "quantity": 100,
        "side": BUY, "timestamp_ns": 123456789,
    }


def test_sell_side_is_kept():
    raw = pack_order(2, 9990, 5, SELL, 42)
    assert unpack_order(raw)["side"] == SELL


def test_wrong_length_raises_error():
    with pytest.raises(ValueError):
        unpack_order(b"short")
