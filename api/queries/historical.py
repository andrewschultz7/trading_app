import sys, time
import pandas as pd
# from sqlalchemy import create_engine
from alpha_vantage.timeseries import TimeSeries

from datetime import datetime, timedelta
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

class TrendlineSignal(BaseModel):
    timestart: int
    timeend: int
    riskreward: int
    success: str

class StrategySignal(BaseModel):
    timestart: int
    timeend: int
    riskreward: int
    success: str
"""
level function
upon close, if candle high two candles back is higher than current candle close
    run query to find prior daily occurences

 """
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

class SignalService:
    def __init__(self):
        self.threebar_repo = ThreeBarSignalRepository()
        self.trendline_repo = TrendlineSignalRepository()

    def use_threebar(self, data):
        return self.threebar_repo.use_threebar(data)

    def use_trendline(self, data):
        return self.trendline_repo.use_trendline(data)

    # def signal_to_frontend(
#     self, fraction: int = 1
# ) -> Union[HttpError, List[HistoricalDataPoint]]:
#     try:
#         with pool.connection() as conn:
#             with conn.cursor() as db:
#                 result = db.execute(
#                     """
#                     SELECT *
#                     FROM trading_data as td
#                     WHERE ;
#                     """,
#                 )
#                 response = [
#                     self.record_to_datapoint_out(record)
#                     for record in result
#                 ]
#                 fraction_response = len(response) // fraction
#                 print(len(response[:fraction_response]))
#                 return response[:fraction_response]

#     except Exception as e:
#         print(e)
#         return {
#             "detail": "There was a problem interacting with the database."
#         }

    def record_to_strategy_signal(
            self,
            first_threebar,
            last_threebar,
            rr_threebar,
            suc_threebar,
            first_trendline,
            last_trendline,
            rr_trendline,
            suc_trendline
            ):
        first, last, rr, success = (
            min(first_threebar, first_trendline),
            max(last_threebar, last_trendline),
            100,
            "yes"
        )
        try:
            with pool.connection() as conn:
                with conn.cursor() as db:
                    result = db.execute(
                        """
                        INSERT INTO strategy_signal (Timestart, Timeend,
                        riskreward, success)
                        VALUES (%s, %s, %s, %s)
                        """,
                        [first, last, rr, success]
                    )
        except Exception as e:
            print(e)
            return {
                "detail": "There was a problem writing QUERIES.strategy_signal to db"
            }

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
                    self.record_to_signal_table(first_candle, last_candle, rr, stat_success)
                    i += 3

                elif (prev_high - entry) / (entry - sl) < r_r:
                    first_candle = first["datetime"]
                    last_candle = current["datetime"]
                    rr = 1
                    stat_success = "no rr"
                    self.record_to_signal_table(first_candle, last_candle, rr, stat_success)
                    i += 3

                elif current["High"] >= prev_high:
                    first_candle = first["datetime"]
                    last_candle = current["datetime"]
                    rr = 1
                    stat_success = "yes"
                    self.record_to_signal_table(first_candle, last_candle, rr, stat_success)
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

    def record_to_signal_table(self, first_candle, last_candle, rr, stat_success):
        timeframe = 5
        pre_buffer = first_candle - timedelta(minutes=timeframe*10)
        post_buffer = last_candle + timedelta(minutes=timeframe*10)
        print("PPPPPPPPPP buffer ", pre_buffer, first_candle, post_buffer, last_candle)
        try:
            with pool.connection() as conn:
                with conn.cursor() as db:
                    result = db.execute(
                        """
                        INSERT INTO strategy_signal (prebuffer, Timestart, Timeeend, postbuffer, riskreward, success)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """,
                        [pre_buffer, first_candle, last_candle, post_buffer, rr, stat_success]
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

class TrendlineSignalRepository:
    def data_to_trendline(self) -> List[TrendlineSignal]:
        try:
            with pool.connection() as conn:
                with conn.cursor() as db:
                    result = (
                        """
                        SELECT Datetimme, Open, High, Low, Close
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
                    return self.trendline(historical_data)
        except Exception as e:
            print(e)
            return {
                 "detail": "There was a problem reading QUERIES.data_to_trendline from trading_data db."
            }

    def trendline(self, candles):
        stop_loss = candles[1]["Low"]
        take_profit = 0.0
        global i
        i = 0
        slope1 = 0.0
        slope2 = 0.0
        candle_count = 0

        while i <= len(candles)-1:
            def expected_trend(candles, price, operand, j):
                global i
                initial_candle = candles[j-2][price]
                next_candle = candles[j-1][price]
                signal_finished = False
                percent_slope = percent_slope2 = (
                    ((next_candle - initial_candle) /
                    initial_candle) * 100
                )
                expected_last_candle = next_candle + percent_slope
                count = 0

                while (
                    (j <= len(candles) - 1 and
                    count < 11) or
                    signal_finished == False
                ):
                    last_candle = candles[j][price]
                    last_candle_close = candles[i]["Close"]

                    if eval(f"{last_candle_close} {operand} {expected_last_candle}"):
                        signal_finished = True
                        return candles[i-2]["Datetime"], candles[j]["Datetime"], 100, "Yes"
                    if last_candle == expected_last_candle:
                        j += 1
                    else:
                        expected_last_candle = (
                            ((last_candle - initial_candle) / initial_candle) * 100 +
                            percent_slope2
                        )
                        j += 1
                    count += 1
                i = i + count

            if candles[i-2]["High"] >= candles[i-1]["High"]:
                price = "High"
                operand = ">"
                first, last, rr, success = expected_trend(candles, price, operand, i)

            elif candles[i-2]["Low"] <= candles[i-1]["Low"]:
                price = "Low"
                operand = "<"
                first, last, rr, success = expected_trend(candles, price, operand, i)

            return first, last, rr, success





            # if initial_candle["High"] >= next_candle["High"]:
            #     self.slope_1_to_2 = (candle_count + 1) (next_candle["High"]/initial_candle["High"])
            #     expected_last_candle = next_candle["High"] * self.slope_1_to_2
            #     self.stop_loss = next_candle["Low"]

            # if (initial_candle["High"] >= last_candle["High"] and
            #     last_candle["Close"] > expected_last_candle
            # ):
            #     self.stop_loss = next_candle["Low"]
            #     return "find_exit_lvl"

            # elif (
            #     initial_candle["High"] >= last_candle["High"] and
            #     last_candle["Close"] <= expected_last_candle and
            #     last_candle["Open"] <= expected_last_candle
            # ):
            #     self.slope_1_to_3 = (candle_count + 2) / (initial_candle["High"]-last_candle["High"])

            # elif (
            #     last_candle["Open"] >= expected_last_candle and
            #     last_candle["Close"] > last_candle["Open"] and
            #     (
            #         (last_candle["High"]-last_candle["Close"])/
            #         (last_candle["High"]-last_candle["Low"])
            #     ) <= .25
            # ):



            # if initial_candle["High"] >= next_candle["High"]:
            #     slope1 = (initial_candle["High"]-next_candle["High"])/candle_count
            #     expected_last_candle =
            #     #descending
            # elif initial_candle["Low"] <= next_candle["Low"]:
            #     slope1 = (next_candle["Low"]-initial_candle["Low"])/candle_count
            #     #ascending

            # #confirm slope with third candle
            # if initial_candle["High"] >= last_candle["High"]:
            #     slope2 = (initial_candle["High"]-last_candle["High"])/candle_count
            #     if slope1 == slope2:
            #         trend = "ascending"
            # elif initial_candle["Low"] <= last_candle["Low"]:
            #     slope2 = (last_candle["Low"]-initial_candle["Low"])/candle_count
            #     if slope1 == slope2:
            #         trend = "descending"
            # else:
            #     trend = "no_trend"
