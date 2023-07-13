import pandas
import sqlite3

DBFILE = "trading_data.db"

day = day_of_signal

params = {
    'start_time': f'{day} 09:30:00',
    'end_time': f'{day} 16:00:00'
}

query = """
    SELECT Close, Volume, Timestamp
    FROM trading_data
    WHERE timestamp >= %(start_time)s
    AND timestamp <= %(end_time)s;
    """
