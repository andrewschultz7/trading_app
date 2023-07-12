import sqlite3, csv, os
import json
import requests

db_file = 'trading_data.db'
# cur_dir = os.path.dirname(os.path.abspath(__file__))
# db_file_path = os.path.join(cur_dir, db_file)

url = "https://eod-historical-data.p.rapidapi.com/intraday/spy.us"

querystring = {"interval":"1m","fmt":"json","from":"1677880341","to":"1688161941"}

headers = {
	"X-RapidAPI-Key": "4dc42ec080mshb6dfe849efda91dp19005djsne9933aa0ba36",
	"X-RapidAPI-Host": "eod-historical-data.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)

# print(response.json())

# CSVFILE = "sample2.csv"
# DBFILE = db_file_path
DBFILE = db_file

conn = sqlite3.connect(DBFILE)
cursor = conn.cursor()

with open('response.json', 'w') as f:
  f.write(response.text)
with open('response.json') as demo:
  data = json.load(demo)

for item in data:
  timestamp = item['timestamp']
  gmtoffset = item['gmtoffset']
  datetime = item['datetime']
  open = item['open']
  high = item['high']
  low = item['low']
  close = item['close']
  volume = item['volume']
  cursor.execute("INSERT INTO `trading_data` (`timestamp`, `gmtoffset`, `datetime`, `open`, `high`, `low`, `close`, `volume`) VALUES (?,?,?,?,?,?,?,?)", (timestamp, gmtoffset, datetime, open, high, low, close, volume))

# with open(CSVFILE) as demo:
#   reader = csv.reader(demo)
#   for row in reader:
#     cursor.execute("INSERT INTO `trading_data` (`timestamp`, `gmtoffset`, `datetime`, `open`, `high`, `low`, `close`, `volume`) VALUES (?,?,?,?,?,?,?,?)", row)



conn.commit()
conn.close()
print("OK")
