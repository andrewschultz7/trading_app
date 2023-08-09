# import sqlite3, csv, os
# import json
# import requests
# import pandas as pd
# from sqlalchemy import create_engine
# from alpha_vantage.timeseries import TimeSeries

# API_key='1WIB48A9B3W11D8L'
# ts = TimeSeries(key=API_key, output_format='pandas')
# data = ts.get_intraday('QQQ', interval='5min', outputsize='full')
# response=json.loads(data)


# db_file = 'trading_data.db'
# vwap = 0.0
# vwapf = 0.0
# cumulative_volume = 0.0
# cumulative_traded_value = 0.0

# def calculate_ema(data, window):
#   ema = []
#   smoothing_factor = 2 / (window + 1)
#   ema.append(data[0])

#   return ema[-1] if len(ema) > 0 else 0

# def vwap_calculation(data):
#   for i, item in enumerate(data):
#     timestamp = item['timestamp']

#     datetime = item['datetime']
#     open = item['open']
#     high = item['high']
#     low = item['low']
#     close = item['close']
#     volume = item['volume']


#     if '09:30:00' <= datetime.split(' ')[1] <= '16:00:00':
#       traded_value = close * volume
#       cumulative_traded_value += traded_value
#       cumulative_volume += volume
#       vwap = cumulative_traded_value/cumulative_volume
#       vwapf = cumulative_traded_value/cumulative_volume # change here
#       close_values = [close for item in data[:i+1]]
#       ema009 = calculate_ema(close_values, 9)
#       ema021 = calculate_ema(close_values, 21)
#       ema200 = calculate_ema(close_values, 200)
#     else:
#       vwap = close
#       vwapf = close
#       ema009 = 0.0
#       ema021 = 0.0
#       ema200 = 0.0
#       tl01 = 0.0
#   return data




# def get_stock_data(function: str, symbol: str, interval: str, api_key: str) -> dict:
#   interval='5min'

#   url = f'https://www.alphavantage.co/query?function={function}&symbol={symbol}&interval={interval}&apikey={api_key}'

#   response = requests.get(url)
#   data = response.text
#   return json.loads(data)

# print(response)





# engine=create_engine(f'sqlite:///{db_file}')
# data.to_sql(name='trading_data', con=engine, if_exists='replace', index=False)
# conn = sqlite3.connect(db_file)
# cursor = conn.cursor()





# conn.commit()
# conn.close()
# print("OK")

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
