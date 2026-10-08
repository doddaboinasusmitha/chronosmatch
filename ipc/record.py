import struct

# Fixed 32-byte binary order record:
# Order ID (8), Price in ticks (8), Quantity (4), Side (1), padding (3), Timestamp ns (8)
ORDER_FORMAT = "<QQIB3xQ"
ORDER_SIZE = struct.calcsize(ORDER_FORMAT)  # 32

BUY = 0
SELL = 1


def pack_order(order_id, price, quantity, side, timestamp_ns):
    """Convert an order into a fixed 32-byte binary record."""
    return struct.pack(ORDER_FORMAT, order_id, price, quantity, side, timestamp_ns)


def unpack_order(data):
    """Convert a 32-byte binary record back into order fields."""
    if len(data) != ORDER_SIZE:
        raise ValueError(f"Expected {ORDER_SIZE} bytes, got {len(data)} bytes")

    order_id, price, quantity, side, timestamp_ns = struct.unpack(ORDER_FORMAT, data)
    return {
        "order_id": order_id,
        "price": price,
        "quantity": quantity,
        "side": side,
        "timestamp_ns": timestamp_ns,
    }


if __name__ == "__main__":
    raw = pack_order(1, 10050, 100, BUY, 123456789)
    print("Order format:", ORDER_FORMAT)
    print("Order size:", ORDER_SIZE)
    print(unpack_order(raw))