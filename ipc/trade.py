
import struct

# Fixed 64-byte binary trade record
TRADE_FORMAT = "<QQIB3xQQQQ8x"
TRADE_SIZE = struct.calcsize(TRADE_FORMAT)


def pack_trade(order_id, price, quantity, side, timestamp_ns,
               trade_id, buyer_id, seller_id):
    """Convert trade fields into a fixed 64-byte binary record."""
    return struct.pack(
        TRADE_FORMAT,
        order_id,
        price,
        quantity,
        side,
        timestamp_ns,
        trade_id,
        buyer_id,
        seller_id,
    )


def unpack_trade(data):
    """Convert a 64-byte binary record back into trade fields."""
    if len(data) != TRADE_SIZE:
        raise ValueError(
            f"Expected {TRADE_SIZE} bytes, got {len(data)} bytes"
        )

    (
        order_id,
        price,
        quantity,
        side,
        timestamp_ns,
        trade_id,
        buyer_id,
        seller_id,
    ) = struct.unpack(TRADE_FORMAT, data)

    return {
        "order_id": order_id,
        "price": price,
        "quantity": quantity,
        "side": side,
        "timestamp_ns": timestamp_ns,
        "trade_id": trade_id,
        "buyer_id": buyer_id,
        "seller_id": seller_id,
    }
