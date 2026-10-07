import struct

# One order record = 32 bytes, fixed size
# Order ID (8), Price in ticks (8), Quantity (4), Side (1: 0=Buy, 1=Sell), padding (3), Timestamp ns (8)
RECORD_FORMAT = "<QQIB3xQ"
RECORD_SIZE = struct.calcsize(RECORD_FORMAT)  # 32

BUY = 0
SELL = 1


def pack_order(order_id, price, quantity, side, timestamp_ns):
    return struct.pack(RECORD_FORMAT, order_id, price, quantity, side, timestamp_ns)


def unpack_order(data):
    return struct.unpack(RECORD_FORMAT, data)


if __name__ == "__main__":
    raw = pack_order(1, 10050, 100, BUY, 123456789)
    print(RECORD_SIZE, unpack_order(raw))
