# chronosmatch
Zero Copy High Frequency Trading Engine

## Ring Buffer Layout
- File: memory-mapped with `mmap`, header of 64 bytes, then fixed 32-byte order records.
- Header: head counter (bytes 0-7), tail counter (bytes 8-15), capacity (bytes 16-23).
- Slot index = counter % capacity. Full when head - tail == capacity, empty when head == tail.
- Producer writes at head, consumer reads at tail. No serialization (no pickle/JSON).
