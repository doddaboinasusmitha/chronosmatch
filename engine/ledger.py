
import json
import os


class OrderLedger:
    """Append-only order ledger with basic crash recovery."""

    def __init__(self, path):
        self.path = path
        self.file = open(path, "a+b")
        self.file.seek(0)

        # Discard an incomplete final line left by a crash.
        data = self.file.read()
        last_newline = data.rfind(b"\n")

        if data and last_newline != len(data) - 1:
            self.file.seek(last_newline + 1)
            self.file.truncate()

        self.file.seek(0, os.SEEK_END)

    def append_order(self, order):
        """Persist one order dictionary."""
        line = json.dumps(order, separators=(",", ":")).encode("utf-8")
        self.file.write(line + b"\n")
        self.file.flush()
        os.fsync(self.file.fileno())

    def recover_orders(self):
        """Return valid complete order records from the ledger."""
        self.file.flush()
        self.file.seek(0)
        orders = []

        for line in self.file:
            try:
                order = json.loads(line.decode("utf-8"))
                if isinstance(order, dict):
                    orders.append(order)
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue

        self.file.seek(0, os.SEEK_END)
        return orders

    def close(self):
        self.file.close()
