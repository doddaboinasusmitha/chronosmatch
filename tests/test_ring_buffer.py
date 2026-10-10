import pytest

from ipc.record import BUY, pack_order, unpack_order
from ipc.ring_buffer import RingBuffer


@pytest.fixture
def rb(tmp_path):
    buf = RingBuffer(str(tmp_path / "test.ring"), capacity=4)
    yield buf
    buf.close()


def order(i):
    return pack_order(i, 10000 + i, 10, BUY, i)


def test_empty_at_start(rb):
    assert rb.is_empty()
    assert rb.pop() is None


def test_write_then_read(rb):
    assert rb.push(order(1))
    assert unpack_order(rb.pop())["order_id"] == 1


def test_full_buffer_rejects_push(rb):
    for i in range(1, 5):
        assert rb.push(order(i))
    assert rb.is_full()
    assert rb.push(order(5)) is False


def test_wrap_around_keeps_order(rb):
    for i in range(1, 5):
        rb.push(order(i))
    rb.pop()
    rb.pop()
    rb.push(order(5))
    rb.push(order(6))
    ids = []
    while not rb.is_empty():
        ids.append(unpack_order(rb.pop())["order_id"])
    assert ids == [3, 4, 5, 6]


def test_wrong_size_record_rejected(rb):
    with pytest.raises(ValueError):
        rb.push(b"short")
