import sqlite3

connection = sqlite3.connect("trades.db")

tables = connection.execute(
    "SELECT name FROM sqlite_master WHERE type='table'"
).fetchall()

print("Tables:", tables)

for table in tables:
    name = table[0]
    count = connection.execute(
        f'SELECT COUNT(*) FROM "{name}"'
    ).fetchone()[0]

    print(f"{name}: {count} records")

connection.close()