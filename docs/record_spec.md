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

**Build status:** The Cython source was generated, but building the compiled extension requires Microsoft Visual C++ Build Tools 14.0 or later on Windows.

**Testing:** The existing Python test suite passed all 9 tests. The Cython extension itself has not yet been built and tested successfully.
