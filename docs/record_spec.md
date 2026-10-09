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
