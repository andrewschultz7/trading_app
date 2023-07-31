import sqlite3

DBFILE = "trading_data.db"

candle2 = 0.5
prev_high = 0
prev_low = 0
r_r = 2
strat_implemented = 0
strat_success = 0


def key_levels(candles):
    global prev_high, prev_low, strat_implemented, strat_success, r_r

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
            print(
                "Prev High ",
                prev_high,
                " Prev Low ",
                prev_low,
                " strat ",
                current["datetime"],
            )

            strat_implemented += 1

            j = i + 1
            entry = second["Open"] + 0.25
            current = candles[j]
            while (
                current["Low"] > sl
                and current["High"] < prev_high
                and j <= len(candles) - 1
            ):
                current = candles[j]
                j += 1

            if current["Low"] <= sl:
                f = first["datetime"]
                l = current["datetime"]
                rr = 1
                s = "no"
                cursor.execute(
                    "INSERT INTO `three_barsignal` (`Timestart`, `Timeeend`, `riskreward`, `success`) VALUES (?,?,?,?)",
                    (f, l, rr, s),
                )
                print("loss at ", current["Low"], current["datetime"])
            elif (prev_high - entry) / (entry - sl) < r_r:
                f = first["datetime"]
                l = current["datetime"]
                rr = 1
                s = "no rr"
                cursor.execute(
                    "INSERT INTO `three_barsignal` (`Timestart`, `Timeeend`, `riskreward`, `success`) VALUES (?,?,?,?)",
                    (f, l, rr, s),
                )
                print(
                    "Risk to reward not satisfied.  ",
                    " high minus entry: ",
                    prev_high - entry,
                    " Entry minues sl: ",
                    entry - sl,
                    " Current r:r ",
                    (prev_high - entry) / (entry - sl),
                )
            elif current["High"] >= prev_high:
                f = first["datetime"]
                l = current["datetime"]
                rr = 1
                s = "yes"
                cursor.execute(
                    "INSERT INTO `three_barsignal` (`Timestart`, `Timeeend`, `riskreward`, `success`) VALUES (?,?,?,?)",
                    (f, l, rr, s),
                )
                print(
                    "win at ",
                    current["High"],
                    " r to r ",
                    (prev_high - entry) / (entry - sl),
                    current["datetime"],
                )
                strat_success += 1
    print(
        "SSSSSSSSSS  Strategy success probability: ",
        strat_success / strat_implemented,
    )
    conn.commit()


conn = sqlite3.connect(DBFILE)
cursor = conn.cursor()
cursor.execute(
    "SELECT DISTINCT Datetime, Open, High, Low, Close FROM trading_data"
)
historical_data = []
for row in cursor.fetchall():
    datetime, open, high, low, close = row
    candle = {
        "datetime": datetime,
        "Open": float(open),
        "High": float(high),
        "Close": float(close),
        "Low": float(low),
    }
    historical_data.append(candle)

key_levels(historical_data)

conn.close()
