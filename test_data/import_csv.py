import csv
import sqlite3

CSVFILE = "sample.csv"
DBFILE = "trading_data.db"

conn = sqlite3.connect(DBFILE)
cursor = conn.cursor()

with open(CSVFILE) as demo:
    reader = csv.reader(demo)
    for row in reader:
        cursor.execute(
            "INSERT INTO `trading_data` (`datetime`, `open`, `high`, `low`, `close`, `volume`) VALUES (?,?,?,?,?,?)",  # noqa
            row,
        )

conn.commit()
conn.close()
print("OK")
