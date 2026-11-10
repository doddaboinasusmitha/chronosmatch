# Order Record Specification
Fixed size: 32 bytes. Format string: "<QQIB3xQ" (little-endian, no alignment padding)

| Field        | Type   | Size | Byte offset |
| ------------ | ------ | ---- | ----------- |
| order_id     | uint64 | 8    | 0 to 7      |
| price        | uint64 | 8    | 8 to 15     |
| quantity     | uint32 | 4    | 16 to 19    |
| side         | uint8  | 1    | 20          |
| padding      | -      | 3    | 21 to 23    |
| timestamp_ns | uint64 | 8    | 24 to 31    |

Side: 0 = BUY, 1 = SELL

## Cython Order Wrapper

The Cython wrapper is located at `ipc/order_wrapper.pyx`.

It accepts an existing order record in bytes format and checks that its length matches the 32-byte order record specification. It then uses the existing Python `unpack_order` function to decode the record.

The build configuration is provided in the root-level `setup.py` file.

**Build status:** The Cython order wrapper imports successfully in the current environment. The compiled extension build process has not been independently verified in this update.

**Testing:** The full Python test suite passed all 45 tests. Two dedicated order-wrapper tests passed, covering valid 32-byte record decoding and invalid-length handling.

## Trade Record Specification

Fixed size: 64 bytes. Format string: "<QQIB3xQQQQ8x" (little-endian, no alignment padding).

| Field       | Type   | Size | Byte offset |
|-------------|--------|------|-------------|
| order_id    | uint64 | 8    | 0 to 7      |
| price       | uint64 | 8    | 8 to 15     |
| quantity    | uint32 | 4    | 16 to 19    |
| side        | uint8  | 1    | 20           |
| padding     | -      | 3    | 21 to 23    |
| timestamp_ns| uint64 | 8    | 24 to 31    |
| trade_id    | uint64 | 8    | 32 to 39    |
| buyer_id    | uint64 | 8    | 40 to 47    |
| seller_id   | uint64 | 8    | 48 to 55    |
| padding     | -      | 8    | 56 to 63    |

Side: 0 = BUY, 1 = SELL

The trade record is implemented in `ipc/trade.py`.
`pack_trade()` encodes the fields into a fixed 64-byte record.
`unpack_trade()` decodes the record and raises `ValueError` if the input length is not 64 bytes.
