import sys
import time
from datetime import datetime as dt, timedelta
from typing import List, Union

import pandas as pd
import psycopg2
import simplejson as json
# from sqlalchemy import create_engine
from alpha_vantage.timeseries import TimeSeries
from psycopg2.sql import SQL, Identifier
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
    prebuffer: str
    box: dict
    postbuffer: str
    riskreward: int
    success: str
    stoploss: float
    level: float
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


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, dt):
            return obj.isoformat()
        return super().default(obj)


class HistoricalDataRepository:
    def update_historical_data(self, data, stock):
        def calculate_indicators(data):
            data["vwap"] = (
                data["1. open"]
                + data["2. high"]
                + data["3. low"]
                + data["4. close"]
            ) / 4
            data["ema009"] = data["4. close"].ewm(span=9, adjust=False).mean()
            data["ema021"] = data["4. close"].ewm(span=21, adjust=False).mean()
            data["ema200"] = (
                data["4. close"].ewm(span=200, adjust=False).mean()
            )
            return data

        data = calculate_indicators(data)

        # prevent sql injection
        allowed_table_name = ["QQQ", "TSLA", "SPY", "ES", "NQ"]
        if stock not in allowed_table_name:
            raise ValueError("Invalid Stock Name")
        else:
            table_name = stock.lower() + "_prices"
        try:
            with pool.connection() as conn:
                with conn.cursor() as db:
                    for date, row in data.iterrows():
                        try:
                            insert_query = """
                                INSERT INTO trading_data (timestamp, datetime, open, high, low, close, volume, vwap, ema009, ema021, ema200)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                ON CONFLICT (datetime) DO NOTHING
                                """
                            values = [
                                date.timestamp(),
                                date.to_pydatetime(),
                                row["1. open"],
                                row["2. high"],
                                row["3. low"],
                                row["4. close"],
                                row["5. volume"],
                                row["vwap"],
                                row["ema009"],
                                row["ema021"],
                                row["ema200"],
                            ]
                            db.execute(insert_query, values)
                        except Exception as e:
                            print(e)
                        try:
                            insert_price = f"""
                                INSERT INTO {table_name} (price)
                                VALUES (%s), (%s)
                                ON CONFLICT (price) DO NOTHING
                                """
                            values_price = [row["2. high"], row["3. low"]]
                            db.execute(insert_price, values_price)
                        except Exception as e:
                            print(e)
                    print("detail Historical data updated.")
                    return {"detail": "Historical data updated."}

        except Exception as e:
            print(e)
            return {
                "detail": "There was a problem interacting with the database."
            }

    def get_fraction_historical_data(
        self, fraction: int = 1
    ) -> HttpError | list[HistoricalDataPoint]:
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

    def get_range_historical_data(
        self, start, end
    ) -> HttpError | list[HistoricalDataPoint]:
        try:
            with pool.connection() as conn:
                with conn.cursor() as db:
                    result = db.execute(
                        f"""
                        SELECT *
                        FROM trading_data
                        WHERE datetime >= '{start}' AND
                        datetime <= '{end}';
                        """,
                    )
                    response = [
                        self.record_to_datapoint_out(record)
                        for record in result
                    ]
                    return response

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
            vwapf=record[8] or 0,
            ema009=record[9],
            ema021=record[10],
            ema200=record[11],
            tl01=record[12] or 0,
        )


class SignalService:
    def __init__(self):
        pass

    def create_strategy(self, data):
        self.levels_repo = LevelsRepository()
        self.threebar_repo = ThreeBarSignalRepository()
        self.trendline_repo = TrendlineSignalRepository()

    def get_strategy(self, stock) -> HttpError | list[StrategySignal]:
        allowed_table_name = ["QQQ", "TSLA", "SPY", "ES", "NQ"]
        if stock not in allowed_table_name:
            raise ValueError("Invalid Stock Name")
        else:
            table_name = stock.lower() + "_prices"
        try:
            with pool.connection() as conn:
                with conn.cursor() as db:
                    result = db.execute(
                        """
                        SELECT ss.*, td.*
                        FROM strategy_signal AS ss
                        JOIN trading_data AS td
                        ON td.datetime >= ss.prebuffer AND td.datetime <= ss.postbuffer
                        ORDER BY ss.timestart;
                        """
                    )
                    response = [
                        self.record_to_strat_out(record) for record in result
                    ]
                    return response
        except Exception as e:
            print(e)
            return {"detail": "There was a problem with pricing table"}

    def record_to_strat_out(self, record):
        return StrategySignal(
            prebuffer=str(record[0]),
            box={"timestart": record[1], "timeend": record[2]},
            postbuffer=str(record[3]),
            riskreward=record[4],
            success=record[5],
            stoploss=record[6],
            level=record[7],
            open=record[10],
            close=record[11],
            high=record[12],
            low=record[13],
            volume=record[14],
            vwap=record[15],
            vwapf=record[16] or 0,
            ema009=record[17],
            ema021=record[18],
            ema200=record[19],
            tl01=record[20] or 0,
        )

        # def use_threebar(self, data):
        #     return self.threebar_repo.use_threebar(data)

        # def use_trendline(self, data):
        #     return self.trendline_repo.use_trendline(data)

    #     def get(self):
    #         try:
    #             with pool.connection() as conn:
    #                 with conn.cursor() as db:
    #                     result = db.execute(
    #                         """
    # SELECT strategy_signal.timestart, strategy_signal.timeend, ema009, ema021, ema200, vwap, tl01, volume, strategy_signal.prebuffer, strategy_signal.postbuffer"""
    #                     )
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
        suc_trendline,
    ):
        first, last, rr, success = (
            min(first_threebar, first_trendline),
            max(last_threebar, last_trendline),
            100,
            "yes",
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
                        [first, last, rr, success],
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

    def data_to_three_bar(self, stock) -> list[ThreeBarSignal]:
        stock = stock
        try:
            with pool.connection() as conn:
                with conn.cursor() as db:
                    db.execute(
                        """
                        DELETE FROM strategy_signal
                        """
                    )
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
                    return self.three_bar(historical_data, stock)

        except Exception as e:
            print(e)
            return {
                "detail": "There was a problem reading QUERIES.data_to_three_bar from trading_data db."
            }

    def three_bar(self, candles, stock):
        print(candles[2])
        print(candles[1])
        candle2 = 0.5
        prev_high = 0
        prev_low = 0
        risk_to_reward = 2
        strat_implemented = 0
        strat_success = 0
        i = 2
        price_increment = 0.25  # increment for ES futures index
        # global prev_high, prev_low, strat_implemented, strat_success, risk_to_reward
        allowed_table_name = ["QQQ", "TSLA", "SPY", "ES", "NQ"]
        if stock not in allowed_table_name:
            raise ValueError("Invalid Stock Name")
        else:
            table_name = stock.lower() + "_prices"

        current = candles[i]
        second = candles[i - 1]
        first = candles[i - 2]
        while i <= len(candles) - 1:
            current = candles[i]
            second = candles[i - 1]
            first = candles[i - 2]

            if first["High"] > float(prev_high):
                prev_high = first["High"]
            if prev_low == 0:
                prev_low = first["Low"]
            elif first["Low"] < prev_low:
                prev_low = first["Low"]

            # calculating risk to reward based on candle size
            first_candle_height = first["Close"] - first["Low"]
            second_candle_height = second["Open"] - second["Low"]
            stop_loss = second["Low"]

            # actual algo here to check if pattern is correct
            if (
                current["Open"] < current["Close"]
                and second["Open"] > second["Close"]
                and first["Open"] < first["Close"]
                # criteria of second candle vs first
                # and second_candle_height <= first_candle_height * candle2
            ):
                strat_implemented += 1
                j = i + 1
                # price increment above pattern where we would like to enter a trade
                entry = second["Open"] + price_increment

                # using next candle to check for exit
                entry_candle = candles[j]
                # calculate risk to reward level needed
                level_needed = (
                    second_candle_height * risk_to_reward + second["Open"]
                )
                level = LevelsRepository.levels_to_signal(
                    table_name, level_needed
                )
                # run loop until either stop loss or prev high is equal to current candle price
                while (
                    entry_candle["Low"] > stop_loss
                    and entry_candle["High"] < prev_high
                    and j <= len(candles)
                ):
                    j += 1
                    entry_candle = candles[j]

                # pattern failed to work out from stop loss
                if entry_candle["Low"] <= stop_loss:
                    first_candle = first["datetime"]
                    last_candle = entry_candle["datetime"]
                    rr = 1
                    success_msg = "no"
                    self.record_to_signal_table(
                        first_candle,
                        last_candle,
                        rr,
                        success_msg,
                        stop_loss,
                        level,
                    )
                    i += j

                # pattern worked but risk to reward not enough
                elif (level - entry) / (entry - stop_loss) < risk_to_reward:
                    first_candle = first["datetime"]
                    last_candle = current["datetime"]
                    rr = 1
                    success_msg = "no rr"
                    self.record_to_signal_table(
                        first_candle,
                        last_candle,
                        rr,
                        success_msg,
                        stop_loss,
                        level,
                    )
                    i += 3

                # pattern worked and risk to reward is enough
                elif current["High"] >= level:
                    first_candle = first["datetime"]
                    last_candle = current["datetime"]
                    rr = 1
                    success_msg = "yes"
                    self.record_to_signal_table(
                        first_candle,
                        last_candle,
                        rr,
                        success_msg,
                        stop_loss,
                        level,
                    )
                    strat_success += 1
                    i += 3
            else:
                i += 1
        success_probability = 0.1
        # success_probability = strat_success / strat_implemented
        return first_candle, last_candle, success_probability, success_msg

    def record_to_signal_table(
        self, first_candle, last_candle, rr, success_msg, stop_loss, level
    ):
        timeframe = 5
        pre_buffer = first_candle - timedelta(minutes=timeframe * 10)
        post_buffer = last_candle + timedelta(minutes=timeframe * 10)
        try:
            with pool.connection() as conn:
                with conn.cursor() as db:
                    db.execute(
                        """
                        INSERT INTO strategy_signal (prebuffer, Timestart, Timeeend, postbuffer, riskreward, success, stoploss, level)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        [
                            pre_buffer,
                            first_candle,
                            last_candle,
                            post_buffer,
                            rr,
                            success_msg,
                            stop_loss,
                            level,
                        ],
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
            success=record[3],
            stoploss=record[4],
            level=record[5],
        )


class TrendlineSignalRepository:
    def data_to_trendline(self) -> list[TrendlineSignal]:
        try:
            with pool.connection() as conn:
                with conn.cursor() as db:
                    result = """
                        SELECT Datetimme, Open, High, Low, Close
                        FROM trading_data
                        ORDER BY Datetime ASC
                        """
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

        while i <= len(candles) - 1:

            def expected_trend(candles, price, operand, j):
                global i
                initial_candle = candles[j - 2][price]
                next_candle = candles[j - 1][price]
                signal_finished = False
                percent_slope = percent_slope2 = (
                    (next_candle - initial_candle) / initial_candle
                ) * 100
                expected_last_candle = next_candle + percent_slope
                count = 0

                while (
                    j <= len(candles) - 1 and count < 11
                ) or signal_finished == False:
                    last_candle = candles[j][price]
                    last_candle_close = candles[i]["Close"]

                    if eval(
                        f"{last_candle_close} {operand} {expected_last_candle}"
                    ):
                        signal_finished = True
                        return (
                            candles[i - 2]["Datetime"],
                            candles[j]["Datetime"],
                            100,
                            "Yes",
                        )
                    if last_candle == expected_last_candle:
                        j += 1
                    else:
                        expected_last_candle = (
                            (last_candle - initial_candle) / initial_candle
                        ) * 100 + percent_slope2
                        j += 1
                    count += 1
                i = i + count

            if candles[i - 2]["High"] >= candles[i - 1]["High"]:
                price = "High"
                operand = ">"
                first, last, rr, success = expected_trend(
                    candles, price, operand, i
                )

            elif candles[i - 2]["Low"] <= candles[i - 1]["Low"]:
                price = "Low"
                operand = "<"
                first, last, rr, success = expected_trend(
                    candles, price, operand, i
                )

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


class LevelsRepository:
    def data_to_levels(self, stock):
        allowed_table_name = ["QQQ", "TSLA", "SPY", "ES", "NQ"]
        if stock not in allowed_table_name:
            raise ValueError("Invalid Stock Name")
        else:
            table_name = stock.lower() + "_prices"

        # finds hourly high/low and creates level if high/low repeats
        try:
            with pool.connection() as conn:
                with conn.cursor() as db:
                    levels_query = f"""
                    WITH HourlyHighLow AS (
                        SELECT
                            DATE_TRUNC('hour', datetime) AS hour,
                            MAX(high) AS max_high,
                            MIN(low) AS min_low
                        FROM trading_data
                        GROUP BY hour
                    )
                    UPDATE {table_name}
                    SET
                        level01 = 1
                    WHERE
                        level01 = 0
                        AND (price IN (SELECT max_high FROM HourlyHighLow)
                        OR price IN (SELECT min_low FROM HourlyHighLow));
                    WITH HourlyHighLow AS (
                        SELECT
                            DATE_TRUNC('hour', datetime) AS hour,
                            MAX(high) AS max_high,
                            MIN(low) AS min_low
                        FROM trading_data
                        GROUP BY hour
                    )
                    UPDATE {table_name}
                    SET
                        level02 = 1
                    WHERE level01 = 1 AND level02 = 0
                        AND (price IN (SELECT max_high FROM HourlyHighLow)
                        OR price IN (SELECT min_low FROM HourlyHighLow));
                    """
                    db.execute(levels_query)
        except Exception as e:
            print(e)
            return {
                "detail": "There was a problem with levels query or database."
            }

    # find nearest levels
    def levels_to_signal(table_name, level_needed):
        try:
            with pool.connection() as conn:
                with conn.cursor() as db:
                    result = db.execute(
                        f"""
                        SELECT price FROM {table_name}
                        WHERE level02 > 0
                        AND price >= {level_needed}
                        ORDER BY price
                        """
                    )
                    level = result.fetchone()
                    level_float = float(level[0])
                    return level_float
        except Exception as e:
            print(e)
            return {
                "detail": "There was a problem reading data from stock prices table"
            }
