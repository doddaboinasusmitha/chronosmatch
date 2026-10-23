import sqlite3
from contextlib import closing

from ipc.ring_buffer import RingBuffer
from ipc.trade import TRADE_SIZE, unpack_trade

DEFAULT_DB_PATH = "journal.db"
DEFAULT_BATCH_SIZE = 100

def initialize_database(db_path=DEFAULT_DB_PATH):
    """Create the trade journal table if it does not already exist."""
    with closing(sqlite3.connect(db_path)) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                trade_id INTEGER PRIMARY KEY,
                order_id INTEGER NOT NULL,
                price INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                side INTEGER NOT NULL,
                timestamp_ns INTEGER NOT NULL,
                buyer_id INTEGER NOT NULL,
                seller_id INTEGER NOT NULL
            )
        """)

def process_batch(ring, db_path=DEFAULT_DB_PATH, batch_size=DEFAULT_BATCH_SIZE):
    """Read a batch of trades from the ring and save them to SQLite."""
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")

    batch = []

    for _ in range(batch_size):
        record = ring.pop()
        if record is None:
            break
        batch.append(unpack_trade(record))

    if not batch:
        return 0

    initialize_database(db_path)

    with closing(sqlite3.connect(db_path)) as connection:
        connection.executemany("""
            INSERT OR IGNORE INTO trades (
                trade_id, order_id, price, quantity, side,
                timestamp_ns, buyer_id, seller_id
            ) VALUES (
                :trade_id, :order_id, :price, :quantity, :side,
                :timestamp_ns, :buyer_id, :seller_id
            )
        """, batch)
        connection.commit()
    return len(batch)

def run_journal(
    ring_path="trades.ring",
    db_path=DEFAULT_DB_PATH,
    batch_size=DEFAULT_BATCH_SIZE,
    max_batches=None,
):
    """Attach to an existing trade ring and journal batches until empty."""
    initialize_database(db_path)

    ring = RingBuffer(
        ring_path,
        create=False,
        record_size=TRADE_SIZE,
    )

    total_saved = 0
    batches_processed = 0

    try:
        while max_batches is None or batches_processed < max_batches:
            count = process_batch(ring, db_path, batch_size)
            if count == 0:
                break

            total_saved += count
            batches_processed += 1
    finally:
        ring.close()

    return total_saved


