from fastapi.testclient import TestClient
import sys, time, os
import pandas as pd
from alpha_vantage.timeseries import TimeSeries
from datetime import datetime, timedelta
from typing import List, Union
from pydantic import BaseModel

root_directory = os.path.abspath(os.path.join(__file__, "..", ".."))
sys.path.insert(0, root_directory)
from main import app
from queries.pool import pool


client = TestClient(app)

class TestThreeBarFunction():
    def data_to_three_bar(self):
        try:
            with pool.connection() as conn:
                with conn.cursor() as db:
                    result = db.execute(
                        """
                        SELECT Datetime, Open, High, Low, Close
                        FROM trading_data
                        ORDER BY Datetime ASC
                        """
                    )
                    rows = result.fetchall()
                    historical_data = []
                    file_path = "asignal_output.json"
                    for row in rows:
                        datetime, open, high, low, close = row
                        candle = {
                            "datetime": datetime,
                            "Open": float(open),
                            "High": float(high),
                            "Close": float(close),
                            "Low": float(low),
                        }
                        historical_data.append(candle)
                        print("AAAAAA ", historical_data)
                    return self.three_bar(historical_data)

        except Exception as e:
            print(e)
            return {
                "detail": "There was a problem reading QUERIES.data_to_three_bar from trading_data db."
            }
        # file_path = "signal_output.txt"
        # historical_data = []
        # with open(file_path, "r") as file:
        #         for line in file:
        #             line = line.strip()
        #             match = re.search(r'\((\d+), (\d+), (\d+), (\d+), (\d+)\)', line)
        #             year, month, day, hour, minute = map(int, match.groups())
        #             datetime_obj = (datetime(year, month, day, hour, minute))
        #             formatted_datetime = datetime_obj.strftime('%Y-%m-%d %H:%M:%S')
        #             pattern = r"'datetime': datetime\.datetime\((\d+), (\d+), (\d+), (\d+), (\d+)\),"
        #             split_pattern = re.search(pattern, line)
        #             matched_pattern = split_pattern.group()
        #             remaining = line.split(matched_pattern, 1)
        #             remaining = f"'datetime': {datetime_obj}, {remaining[1:]}"
        #             print("DDDDDDD ", remaining)
        #             remaining = remaining.strip()
        #             new_dt = (ast.literal_eval(remaining))
        #             print("Pattern ", new_dt)
                    # print("2nd ", remaining)
                    # new_dict = {'datetime':formatted_datetime}
                    # print("dict ", new_dict)
                    # print("ast ", new_dt)
                    # new_dict.update(new_dt)
                    # historical_data.append(new_dict)
                    # print(historical_data)
        # return self.three_bar(historical_data)

    def three_bar(self, candles):
        candle2 = 0.5
        prev_high = 0
        prev_low = 0
        r_r = 2
        strat_implemented = 0
        strat_success = 0
        i = 2
        # global prev_high, prev_low, strat_implemented, strat_success, r_r

        while i <= len(candles)-1:
            current = candles[i]
            second = candles[i - 1]
            first = candles[i - 2]

            if i <150:
                print(f"{i} First {first['datetime']} Second {current['datetime']}")

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
                    first_candle = first["datetime"]
                    last_candle = current["datetime"]
                    rr = 1
                    stat_success = "no"
                    print(first_candle, last_candle, rr, stat_success)
                    i += 3

                elif (prev_high - entry) / (entry - sl) < r_r:
                    first_candle = first["datetime"]
                    last_candle = current["datetime"]
                    rr = 1
                    stat_success = "no rr"
                    print(first_candle, last_candle, rr, stat_success)
                    i += 3

                elif current["High"] >= prev_high:
                    first_candle = first["datetime"]
                    last_candle = current["datetime"]
                    rr = 1
                    stat_success = "yes"
                    print(first_candle, last_candle, rr, stat_success)
                    strat_success += 1
                    i += 3
            else:
                i += 1

        success_probability = strat_success / strat_implemented
        print(
            "SSSSSSSSSS  Strategy success probability: ",
            success_probability
        )
        return first_candle, last_candle, success_probability, stat_success

    def test_three_bar_cases(self):
        result = self.data_to_three_bar()

# if __name__ == '__main__':
#     unittest.main()
