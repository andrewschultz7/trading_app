import sys, time
import pandas as pd
# from sqlalchemy import create_engine
from alpha_vantage.timeseries import TimeSeries

from datetime import datetime
from typing import List, Union

from pydantic import BaseModel
from queries.pool import pool


class HttpError(BaseModel):
    detail: str


class SystemMessage(BaseModel):
    detail: str


class HistoricalDataPoint(BaseModel):
    timestamp: int
    datetime: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    vwap: float
    vwapf: float
    ema009: float
    ema021: float
    ema200: float
    tl01: float

class ThreeBarSignal(BaseModel):
    timestart: int
    timeend: int
    riskreward: int
    success: str

class HistoricalDataRepository:
    def update_historical_data(self, data):
        def calculate_indicators(data):
            data['vwap'] = (data['1. open'] + data['2. high'] + data['3. low'] + data['4. close']) / 4
            data['ema009'] = data['4. close'].ewm(span=9, adjust=False).mean()
            data['ema021'] = data['4. close'].ewm(span=21, adjust=False).mean()
            data['ema200'] = data['4. close'].ewm(span=200, adjust=False).mean()
            return data

        data = calculate_indicators(data)

        try:
            with pool.connection() as conn:
                with conn.cursor() as db:
                    for date, row in data.iterrows():
                        insert_query = """
                            INSERT INTO trading_data (timestamp, datetime, open, high, low, close, volume, vwap, ema009, ema021, ema200)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
                        values = [
                            date.timestamp(), date.to_pydatetime(), row['1. open'], row['2. high'], row['3. low'], row['4. close'],
                            row['5. volume'], row['vwap'], row['ema009'], row['ema021'], row['ema200']
                        ]
                        db.execute(
                            insert_query, values
                        )

                    return {"detail": "Historical data updated."}

        except Exception as e:
            print(e)
            return {
                "detail": "There was a problem interacting with the database."
            }


    def get_fraction_historical_data(
        self, fraction: int = 1
    ) -> Union[HttpError, List[HistoricalDataPoint]]:
        try:
            with pool.connection() as conn:
                with conn.cursor() as db:
                    result = db.execute(
                        """
                        SELECT *
                        FROM trading_data;
                        """,
                    )
                    response = [
                        self.record_to_datapoint_out(record)
                        for record in result
                    ]
                    fraction_response = len(response) // fraction
                    print(len(response[:fraction_response]))
                    return response[:fraction_response]

        except Exception as e:
            print(e)
            return {
                "detail": "There was a problem interacting with the database."
            }

    def record_to_datapoint_out(self, record):
        data_datetime_str = str(record[1])
        # data_datetime_obj = datetime.strptime(
        #     data_datetime_str, "%Y-%m-%d %H:%M:%S"
        # )
        # data_timestamp = datetime.timestamp(data_datetime_obj)

        return HistoricalDataPoint(
            timestamp=record[0],
            datetime=data_datetime_str,
            open=record[2],
            close=record[3],
            high=record[4],
            low=record[5],
            volume=record[6],
            vwap=record[7],
            vwapf=record[8],
            ema009=record[9],
            ema021=record[10],
            ema200=record[11],
            tl01=record[12],
        )

class ThreeBarSignalRepository:
    def pause_for_user(self):
        user_choice = input("Do you want to continue? (y/n): ")
        time.sleep(5)
        if user_choice == "y":
            print("Exiting the program.")
            sys.exit()
        else:
            pass

    def data_to_three_bar(self) -> List[ThreeBarSignal]:
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
                    return self.three_bar(historical_data)

        except Exception as e:
            print(e)
            return {
                "detail": "There was a problem reading QUERIES.data_to_three_bar from trading_data db."
            }

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
                # print(
                #     "Prev High ",
                #     prev_high,
                #     " Prev Low ",
                #     prev_low,
                #     " strat ",
                #     current["datetime"],
                # )

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
                    self.record_to_signal_table(f, l, rr, s)
                    i += 3

                elif (prev_high - entry) / (entry - sl) < r_r:
                    f = first["datetime"]
                    l = current["datetime"]
                    rr = 1
                    s = "no rr"
                    self.record_to_signal_table(f, l, rr, s)
                    i += 3

                elif current["High"] >= prev_high:
                    f = first["datetime"]
                    l = current["datetime"]
                    rr = 1
                    s = "yes"
                    self.record_to_signal_table(f, l, rr, s)
                    strat_success += 1
                    i += 3
            else:
                i += 1

        success_probability = strat_success / strat_implemented
        print(
            "SSSSSSSSSS  Strategy success probability: ",
            success_probability
        )
        return success_probability

    def record_to_signal_table(self, f, l, rr, s):
        try:
            with pool.connection() as conn:
                with conn.cursor() as db:
                    result = db.execute(
                        """
                        INSERT INTO strategy_signal (Timestart, Timeeend, riskreward, success)
                        VALUES (%s, %s, %s, %s)
                        """,
                        [f, l, rr, s]
                    )

        except Exception as e:
            print(e)
            return {
                "detail": "There was a problem writing to strategy_signal db."
            }

    def record_to_datapoint_out(self, record):
        return ThreeBarSignal(
            timestart=record[0],
            timeend=record[1],
            riskreward=record[2],
            success=record[3]
        )
