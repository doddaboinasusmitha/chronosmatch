import pytest

from ipc.record import BUY, pack_order, unpack_order
from ipc.ring_buffer import RingBuffer
from ipc.trade import TRADE_SIZE, pack_trade


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


def test_ring_buffer_supports_trade_record_size(tmp_path):
    path = tmp_path / "trade_ring.bin"
    ring = RingBuffer(
        str(path),
        capacity=4,
        record_size=TRADE_SIZE,
    )

    record = pack_trade(1, 10050, 100, 0, 123456789, 10, 20, 30)

    try:
        assert ring.push(record) is True
        assert ring.pop() == record
    finally:
        ring.close()


def test_peek_view_and_advance(tmp_path):
    ring = RingBuffer(str(tmp_path / "view_ring.bin"), capacity=4)
    view = None

    try:
        record = pack_order(1, 10050, 10, BUY, 123456789)
        assert ring.push(record) is True

        view = ring.peek_view()
        assert view is not None
        assert bytes(view) == record

        view.release()
        view = None

        assert ring.advance() is True
        assert ring.pop() is None
    finally:
        if view is not None:
            view.release()
        ring.close()


def test_attach_existing_buffer_preserves_records(tmp_path):
    path = str(tmp_path / "shared.ring")
    writer = RingBuffer(path, capacity=4)

    try:
        record = order(1)
        assert writer.push(record)

        reader = RingBuffer(
            path,
            capacity=4,
            create=False,
            record_size=32,
        )

        try:
            assert len(reader) == 1
            assert reader.pop() == record
            assert reader.is_empty()
        finally:
            reader.close()
    finally:
        writer.close()


def test_zero_capacity_rejected(tmp_path):
    with pytest.raises(ValueError, match="capacity must be positive"):
        RingBuffer(str(tmp_path / "zero.ring"), capacity=0)


def test_negative_capacity_rejected(tmp_path):
    with pytest.raises(ValueError, match="capacity must be positive"):
        RingBuffer(str(tmp_path / "negative.ring"), capacity=-1)


def test_zero_record_size_rejected(tmp_path):
    with pytest.raises(ValueError, match="record_size must be positive"):
        RingBuffer(
            str(tmp_path / "invalid.ring"),
            capacity=4,
            record_size=0,
        )


def test_attach_missing_file_times_out(tmp_path):
    path = str(tmp_path / "missing.ring")

    with pytest.raises(TimeoutError, match="Timed out waiting"):
        RingBuffer(
            path,
            create=False,
            timeout=0,
            retry_interval=0.01,
        )


def test_attach_rejects_zero_header_capacity(tmp_path):
    path = str(tmp_path / "invalid.ring")

    with open(path, "wb") as file:
        file.truncate(64)

    with pytest.raises(ValueError, match="header capacity must be positive"):
        RingBuffer(path, create=False, timeout=0)


def test_attach_rejects_file_size_mismatch(tmp_path):
    path = str(tmp_path / "wrong_size.ring")

    writer = RingBuffer(path, capacity=4, record_size=32)
    writer.close()

    with open(path, "r+b") as file:
        file.truncate(64 + 4 * 32 - 1)

    with pytest.raises(ValueError, match="file size mismatch"):
        RingBuffer(
            path,
            create=False,
            record_size=32,
            timeout=0,
        )
