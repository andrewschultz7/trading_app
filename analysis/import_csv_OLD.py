import sqlite3, csv, os
import json
import requests
import pandas as pd
from sqlalchemy import create_engine
from alpha_vantage.timeseries import TimeSeries

API_key='1WIB48A9B3W11D8L'
ts = TimeSeries(key=API_key, output_format='pandas')
data = ts.get_intraday('QQQ', interval='5min', outputsize='full')
response=json.loads(data)

db_file = 'trading_data.db'
# cur_dir = os.path.dirname(os.path.abspath(__file__))
# db_file_path = os.path.join(cur_dir, db_file)
def get_stock_data(function: str, symbol: str, interval: str, api_key: str) -> dict:
  interval='5min'

  url = f'https://www.alphavantage.co/query?function={function}&symbol={symbol}&interval={interval}&apikey={api_key}'

  response = requests.get(url)
  data = response.text
  return json.loads(data)

# url = "https://eod-historical-data.p.rapidapi.com/intraday/spy.us"
# querystring = {"interval":"1m","fmt":"json","from":"1677880341","to":"1688161941"}
# querystring = {"interval":"5min","fmt":"json","from":"1677880341","to":"1688161941"}

# headers = {
# 	"X-RapidAPI-Key": "4dc42ec080mshb6dfe849efda91dp19005djsne9933aa0ba36",
# 	"X-RapidAPI-Host": "eod-historical-data.p.rapidapi.com"
# }
# function=TIME_SERIES_INTRADAY
# symbol=QQQ


# response = requests.get(url, headers=headers, params=querystring)

print(response)

vwap = 0.0
vwapf = 0.0
cumulative_volume = 0.0
cumulative_traded_value = 0.0

def calculate_ema(data, window):
  ema = []
  smoothing_factor = 2 / (window + 1)
  ema.append(data[0])

  return ema[-1] if len(ema) > 0 else 0

# CSVFILE = "sample2.csv"
# DBFILE = db_file_path
# DBFILE = db_file
engine=create_engine(f'sqlite:///{db_file}')
conn = sqlite3.connect(db_file)
cursor = conn.cursor()



# with open('response.json', 'w') as f:
#   f.write(response.text)
# with open('response.json') as demo:
#   data = json.load(demo)

for i, item in enumerate(data):
  timestamp = item['timestamp']
  gmtoffset = item['gmtoffset']
  datetime = item['datetime']
  open = item['open']
  high = item['high']
  low = item['low']
  close = item['close']
  volume = item['volume']

  # need vwap for futures added
  if '09:30:00' <= datetime.split(' ')[1] <= '16:00:00':
    traded_value = close * volume
    cumulative_traded_value += traded_value
    cumulative_volume += volume
    vwap = cumulative_traded_value/cumulative_volume
    vwapf = cumulative_traded_value/cumulative_volume # change here
    close_values = [close for item in data[:i+1]]
    ema009 = calculate_ema(close_values, 9)
    ema021 = calculate_ema(close_values, 21)
    ema200 = calculate_ema(close_values, 200)
  else:
    vwap = close
    vwapf = close
    ema009 = 0.0
    ema021 = 0.0
    ema200 = 0.0
    tl01 = 0.0

  cursor.execute(
    """
    INSERT INTO `trading_data`
      (timestamp
      , gmtoffset
      , datetime
      , open
      , high
      , low
      , close
      , volume
      , vwap
      , vwapf
      , ema009
      , ema021
      , ema200,
      tl01)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """,
    (
      timestamp,
      gmtoffset,
      datetime,
      open,
      high,
      low,
      close,
      volume,
      vwap,
      vwapf,
      ema009,
      ema021,
      ema200,
      tl01,)
  ),

  cursor.execute(
      """
      INSERT INTO `trading_data`
        (kl)
      VALUES (%s)
      """
      (
        timestamp,
        gmtoffset,
        datetime,
        open,
        high,
        low,
        close,
        volume,
        vwap,
        vwapf,
        ema009,
        ema021,
        ema200,
        tl01,)
    )

# for item in tf:
#   def combine(array):
#     candle = {}
#     high = []
#     low = []
#     volume = 0

#     for item in array:
#         high.append(item['high'])
#         low.append(item['low'])
#         volume += item['volume']

#     candle['datetime'] = array[0]['datetime']
#     candle['open'] = array[0]['open']
#     candle['high'] = max(high)
#     candle['low'] = min(low)
#     candle['close'] = array[-1]['close']
#     candle['volume'] = volume

#     return candle



conn.commit()
conn.close()
print("OK")
