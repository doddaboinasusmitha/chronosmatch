import asyncio

from ipc.record import unpack_order
from ipc.ring_buffer import RingBuffer
from simulator.simulator import run


def test_simulator_writes_requested_orders(tmp_path, capsys):
    ring_file = tmp_path / "orders.ring"

    asyncio.run(
        run(
            count=5,
            rate=0,
            seed=42,
            ring=str(ring_file),
        )
    )

    output = capsys.readouterr().out
    assert "orders written: 5" in output
    assert ring_file.exists()

    rb = RingBuffer(str(ring_file), capacity=100000, create=False)
    try:
        assert len(rb) == 5

        orders = [unpack_order(rb.pop()) for _ in range(5)]
        assert all(order is not None for order in orders)
        assert rb.is_empty()
    finally:
        rb.close()