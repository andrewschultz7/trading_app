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
