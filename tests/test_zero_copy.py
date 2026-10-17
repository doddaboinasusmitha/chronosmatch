from ipc.ring_buffer import RingBuffer
from ipc.record import pack_order, BUY


def test_peek_view_returns_memoryview():
    rb = RingBuffer("test_zero_copy.ring", capacity=4)
    view = None

    try:
        record = pack_order(1, 100, 10, BUY, 123)
        assert rb.push(record)

        view = rb.peek_view()

        assert isinstance(view, memoryview)
        assert bytes(view) == record
        assert view.obj is rb._mm
        assert len(rb) == 1

    finally:
        if view is not None:
            view.release()
        rb.close()


def test_peek_view_matches_pop():
    rb = RingBuffer("test_zero_copy.ring", capacity=4)
    view = None

    try:
        record = pack_order(2, 200, 5, BUY, 456)
        assert rb.push(record)

        view = rb.peek_view()
        assert view is not None
        assert bytes(view) == record

        view.release()
        view = None

        assert rb.pop() == record

    finally:
        if view is not None:
            view.release()
        rb.close()


def test_advance_consumes_record():
    rb = RingBuffer("test_zero_copy.ring", capacity=4)
    view = None

    try:
        record = pack_order(3, 300, 8, BUY, 789)
        assert rb.push(record)

        view = rb.peek_view()
        assert view is not None
        assert bytes(view) == record

        view.release()
        view = None

        assert rb.advance() is True
        assert rb.is_empty()
        assert rb.peek_view() is None

    finally:
        if view is not None:
            view.release()
        rb.close()


def test_advance_returns_false_when_empty():
    rb = RingBuffer("test_zero_copy.ring", capacity=4)

    try:
        assert rb.advance() is False
        assert rb.is_empty()

    finally:
        rb.close()