# import csv
import os
import sqlite3

DBFILE = "trading_data.db"
SQLFILE = "trading_data.sql"

if os.path.exists(DBFILE):
    os.remove(DBFILE)

conn = sqlite3.connect(DBFILE)
with open(SQLFILE) as f:
    conn.executescript(f.read())
conn.commit()
conn.close()
print("Database created!")
