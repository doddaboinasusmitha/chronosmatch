import sqlite3
from contextlib import closing

from ipc.trade import unpack_trade


DEFAULT_DB_PATH = "trades.db"


def initialize_database(db_path=DEFAULT_DB_PATH):
    """Create the trade journal table if it does not already exist."""

    with closing(sqlite3.connect(db_path)) as connection:
        connection.execute(
            """
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
            """
        )

        connection.commit()


def process_batch(
    ring,
    db_path=DEFAULT_DB_PATH,
    batch_size=100,
):
    """
    Process a batch of trades from the ring buffer and save them to SQLite.

    Trades are removed from the ring buffer only after the database
    transaction has been committed successfully.
    """

    if batch_size < 1:
        raise ValueError("batch_size must be at least 1")

    if ring.is_empty():
        return 0

    initialize_database(db_path)

    processed = 0

    with closing(sqlite3.connect(db_path)) as connection:

        while processed < batch_size:

            # Read the next trade without removing it from the ring.
            view = ring.peek_view()

            if view is None:
                break

            # peek_view returns bytes, so there is no view.release().
            trade = unpack_trade(view)

            # Insert the trade into the SQLite journal.
            connection.execute(
                """
                INSERT OR IGNORE INTO trades (
                    trade_id,
                    order_id,
                    price,
                    quantity,
                    side,
                    timestamp_ns,
                    buyer_id,
                    seller_id
                ) VALUES (
                    :trade_id,
                    :order_id,
                    :price,
                    :quantity,
                    :side,
                    :timestamp_ns,
                    :buyer_id,
                    :seller_id
                )
                """,
                trade,
            )

            # Commit the database transaction first.
            connection.commit()

            # Remove the trade from the ring buffer after committing.
            if not ring.advance():
                raise RuntimeError(
                    "Trade disappeared before consumption"
                )

            processed += 1

    return processed


if __name__ == "__main__":
    initialize_database()
    print("Trade journal initialized successfully.")