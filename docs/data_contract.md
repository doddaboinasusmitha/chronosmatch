# ChronosMatch Data Contract v1.1

## 1. Purpose

This document defines the data contract between ChronosMatch components. It specifies record formats, shared-memory communication, file responsibilities, and buffer handling rules.

## 2. Record Types

ChronosMatch uses two record types:

- **Order Record:** Fixed size of 32 bytes.
- **Trade Record:** Fixed size of 64 bytes.

Each record must follow its defined binary format to ensure consistent communication between components.

## 3. Order Record

- **Record size:** 32 bytes
- **Format:** `<QQIB3xQ`
- **Python module:** `ipc/record.py`

The order record contains order identifiers, price, quantity, side, and additional order data as defined by the existing record implementation.

## 4. Trade Record

- **Record size:** 64 bytes
- **Format:** `<QQIB3xQQQQ8x`
- **Python module:** `ipc/trade.py`

Trade records store trade-related information using the fixed 64-byte binary format. Packing and unpacking must follow the format defined in `ipc/trade.py`.

## 5. Ring Buffer Contract

- **Implementation:** `ipc/ring_buffer.py`
- The ring buffer supports configurable `record_size`.
- The default record size is 32 bytes for order records.
- A record size of 64 bytes can be used for trade records.
- Records must have the expected size before being written.
- The buffer must preserve FIFO (First In, First Out) ordering.
- A full buffer must reject new records rather than overwrite unread records.
- An empty buffer must not return a record.

## 6. File Responsibilities

| File | Responsibility |
|---|---|
| `ipc/record.py` | Order record format and pack/unpack functions |
| `ipc/trade.py` | Trade record format and pack/unpack functions |
| `ipc/ring_buffer.py` | Shared-memory ring buffer implementation |
| `docs/record_spec.md` | Record layout and field specifications |
| `docs/data_contract.md` | Data contract and communication rules |
| `tests/test_ring_buffer.py` | Ring buffer behavior tests |

## 7. Create vs. Attach Policy

- The component responsible for initializing the shared-memory region creates the buffer.
- Other components that need access to the same region attach to the existing shared-memory buffer.
- Components must use the same buffer layout, capacity, and record size.
- A component must not independently initialize or reset a buffer that is already in use by another component.

## 8. Full-Buffer Policy

When the ring buffer is full, a new record must not overwrite an unread record. The push operation must indicate failure so that the calling component can handle the situation.

## 9. Data Consistency

- All components must use the agreed record formats.
- Record sizes must remain fixed at