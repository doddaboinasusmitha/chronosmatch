
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


def test_peek_view_is_zero_copy_and_does_not_consume(rb):
    record = order(1)
    assert rb.push(record)

    view = rb.peek_view()

    assert isinstance(view, memoryview)
    assert bytes(view) == record
    assert len(rb) == 1

    view.release()

    popped = rb.pop()
    assert popped == record
    assert rb.is_empty()


def test_advance_consumes_record_without_copying(tmp_path):
    from ipc.ring_buffer import RingBuffer
    from ipc.record import pack_order, BUY

    rb = RingBuffer(str(tmp_path / "test.ring"), capacity=4)
    try:
        record = pack_order(1, 100, 10, BUY, 123)
        assert rb.push(record)

        view = rb.peek_view()
        assert view is not None
        assert bytes(view) == record

        assert rb.advance() is True
        assert rb.is_empty()
        assert rb.peek_view() is None

        del view
    finally:
        rb.close()


def test_advance_returns_false_when_empty(tmp_path):
    from ipc.ring_buffer import RingBuffer

    rb = RingBuffer(str(tmp_path / "test.ring"), capacity=4)
    try:
        assert rb.advance() is False
        assert rb.is_empty()
    finally:
        rb.close()
