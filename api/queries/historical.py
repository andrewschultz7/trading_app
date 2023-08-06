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
    def update_historical_data(self, data: list):
        res = []

        # Initialize
        vwap = 0.0
        vwapf = 0.0
        cumulative_volume = 0.0
        cumulative_traded_value = 0.0

        for i, data_point in enumerate(data):
            timestamp = data_point["timestamp"]
            # gmtoffset = data_point["gmtoffset"]
            datetime = data_point["datetime"]
            open = data_point["open"]
            high = data_point["high"]
            low = data_point["low"]
            close = data_point["close"]
            volume = data_point["volume"]

            # need vwap for futures added
            if "09:30:00" <= datetime.split(" ")[1] <= "16:00:00":
                traded_value = close * volume
                cumulative_traded_value += traded_value
                cumulative_volume += volume
                vwap = cumulative_traded_value / cumulative_volume
                vwapf = cumulative_traded_value / cumulative_volume
                close_values = [close for data_point in data[: i + 1]]
                ema009 = self.calculate_ema(close_values, 9)
                ema021 = self.calculate_ema(close_values, 21)
                ema200 = self.calculate_ema(close_values, 200)
            else:
                vwap = 0.0
                vwapf = 0.0
                cumulative_volume = 0.0
                cumulative_traded_value = 0.0
                ema009 = 0.0
                ema021 = 0.0
                ema200 = 0.0
                tl01 = 0.0

            data_point_temp = [
                timestamp,
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
                tl01,
            ]

            stringified = ", ".join(
                list(map(lambda x: f"'{x}'", data_point_temp))
            )
            res.append(f"({stringified})")

        try:
            with pool.connection() as conn:
                with conn.cursor() as db:
                    result = db.execute(
                        f"""
                        INSERT INTO trading_data (
                        timestamp,
                        datetime,
                        open,
                        close,
                        high,
                        low,
                        volume,
                        vwap,
                        vwapf,
                        ema009,
                        ema021,
                        ema200,
                        tl01
                        )
                        VALUES
                        {",".join(res)};
                        """,
                    )
                    # response = [
                    #     self.record_to_datapoint_out(record)
                    #     for record in result
                    # ]

                    # return response[:fraction_response]
                    return {"detail": "Historical data updated."}

        except Exception as e:
            print(e)
            return {
                "detail": "There was a problem interacting with the database."
            }

    def calculate_ema(self, data, window):
        ema = []
        smoothing_factor = 2 / (window + 1)
        ema.append(data[0])

        return ema[-1] if len(ema) > 0 else 0

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
