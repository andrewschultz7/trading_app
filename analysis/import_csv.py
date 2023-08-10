import sqlite3, os, sys
import pandas as pd
from sqlalchemy import create_engine
from alpha_vantage.timeseries import TimeSeries

API_key = '1WIB48A9B3W11D8L'
ts = TimeSeries(key=API_key, output_format='pandas')
data, _ = ts.get_intraday('QQQ', interval='5min', outputsize='full')

db_file = os.path.join(os.path.dirname(__file__), '..', 'trading_data.db')

engine = create_engine(f'sqlite:///{db_file}')

conn = sqlite3.connect(db_file)
cursor = conn.cursor()

def calculate_indicators(data):
    data['vwap'] = (data['1. open'] + data['2. high'] + data['3. low'] + data['4. close']) / 4
    data['ema009'] = data['4. close'].ewm(span=9, adjust=False).mean()
    data['ema021'] = data['4. close'].ewm(span=21, adjust=False).mean()
    data['ema200'] = data['4. close'].ewm(span=200, adjust=False).mean()
    return data


data = calculate_indicators(data)

for date, row in data.iterrows():
    insert_query = """
        INSERT INTO trading_data (timestamp, datetime, open, high, low, close, volume, vwap, ema009, ema021, ema200)
        VALUES (?,?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    values = (
        str(date),str(date), row['1. open'], row['2. high'], row['3. low'], row['4. close'],
        row['5. volume'], row['vwap'], row['ema009'], row['ema021'], row['ema200']
    )
    cursor.execute(insert_query, values)


conn.commit()
conn.close()
print("OK")
