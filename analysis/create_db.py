import csv
import sqlite3
import os

DBFILE = "trading_data.db"
SQLFILE = "create_1m.sql"

cur_dir = os.path.dirname(os.path.abspath(__file__))
sql_file_path = os.path.join(cur_dir, SQLFILE)

if os.path.exists(DBFILE):
    print("Database file exists. Removing the file...")
    os.remove(DBFILE)

conn = sqlite3.connect(DBFILE)
cursor = conn.cursor()


cursor.execute("DROP TABLE IF EXISTS trading_data")


with open(sql_file_path) as f:
    cursor.executescript(f.read())

conn.commit()
conn.close()

print("Database created!")


# import csv
# import sqlite3, os


# DBFILE = "trading_data.db"
# SQLFILE = "create_1m.sql"

# cur_dir = os.path.dirname(os.path.abspath(__file__))
# sql_file_path = os.path.join(cur_dir, SQLFILE)

# if os.path.exists(DBFILE):
#     print("exists")
#     os.remove(DBFILE)


# conn = sqlite3.connect(DBFILE)
# cursor = conn.cursor()
# cursor.execute("DROP TABLE IF EXISTS trading_data")

# with open(sql_file_path) as f:
#   conn.executescript(f.read())
# conn.commit()
# conn.close()
# print("Database created!")
