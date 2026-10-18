import asyncio

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