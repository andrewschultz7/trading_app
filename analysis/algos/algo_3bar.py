import sqlite3, json, os

current_directory = os.path.dirname(os.path.abspath(__file__))
db_file_path = os.path.join(current_directory, "..", "trading_data.db")

DBFILE = db_file_path

candle2 = 0.5
prev_high = 0
prev_low = 0
r_r = 2
strat_implemented = 0
strat_success = 0


def three_bar(candles):
    global prev_high, prev_low, strat_implemented, strat_success, r_r

    data_signal = []


    for i in range(2, len(candles)):
        current = candles[i]
        second = candles[i - 1]
        first = candles[i - 2]

        if first["High"] > float(prev_high):
            prev_high = first["High"]
        if prev_low == 0:
            prev_low = first["Low"]
        elif first["Low"] < prev_low:
            prev_low = first["Low"]

        f1 = first["Close"] - first["Low"]
        s1 = second["Open"] - second["Low"]
        sl = second["Low"]

        if (
            current["Open"] < current["Close"]
            and second["Open"] > second["Close"]
            and first["Open"] < first["Close"]
            and
            # criteria of second candle vs first
            s1 <= f1 * candle2

        ):

            strat_implemented += 1

            j = i+1
            entry = second["Open"]  + .25
            current = candles[j]
            while current["Low"] > sl and current["High"] < prev_high and j<=len(candles)-1:
                current = candles[j]
                j += 1

            if current["Low"] <= sl:
                f = first['datetime']
                l = current['datetime']
                rr = 1
                s = 'no'
                cursor.execute("INSERT INTO `three_barsignal` (`Timestart`, `Timeeend`, `riskreward`, `success`) VALUES (?,?,?,?)", (f, l, rr, s))
            elif (prev_high-entry)/(entry-sl) < r_r:
                f = first['datetime']
                l = current['datetime']
                rr = 1
                s = 'no rr'
                cursor.execute("INSERT INTO `three_barsignal` (`Timestart`, `Timeeend`, `riskreward`, `success`) VALUES (?,?,?,?)", (f, l, rr, s))
            elif current["High"] >= prev_high:
                f = first['datetime']
                l = current['datetime']
                rr = 1
                s = 'yes'
                cursor.execute("INSERT INTO `three_barsignal` (`Timestart`, `Timeeend`, `riskreward`, `success`) VALUES (?,?,?,?)", (f, l, rr, s))
                strat_success += 1
            data_for_signal = {
                "Timestart": f,
                "Timeeend": l,
                "riskreward": rr,
                "success": s
            }
            data_signal.append(data_for_signal)


    print("SSSSSSSSSS  Strategy success probability: ", strat_success/strat_implemented)

    conn.commit()


conn = sqlite3.connect(DBFILE)
cursor = conn.cursor()
cursor.execute("SELECT DISTINCT Datetime, Open, High, Low, Close FROM trading_data")
historical_data = []
for row in cursor.fetchall():
    datetime, open_p, high, low, close = row
    candle = {
        "datetime": datetime,
        "Open": float(open_p),
        "High": float(high),
        "Close": float(close),
        "Low": float(low),
    }
    historical_data.append(candle)

three_bar(historical_data)

conn.close()
