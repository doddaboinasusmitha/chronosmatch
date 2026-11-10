
from ipc.record import ORDER_SIZE, unpack_order

def decode_order(bytes data):
    """Decode one existing 32-byte ChronosMatch order record."""
    if len(data) != ORDER_SIZE:
        raise ValueError(
            f"Expected {ORDER_SIZE} bytes, got {len(data)} bytes"
        )
    return unpack_order(data)
