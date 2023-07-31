from datetime import datetime
from typing import List, Union

from pydantic import BaseModel
from queries.pool import pool


class HttpError(BaseModel):
    detail: str


class HistoricalDataPoint(BaseModel):
    timestamp: int
    gmtoffset: int
    datetime: str
    open: float
    high: float
    low: float
    close: float
    volume: int


class HistoricalDataRepository:
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
                "message": "There was a problem interacting with the database."
            }

    def record_to_datapoint_out(self, record):
        data_datetime_str = str(record[0])
        data_datetime_obj = datetime.strptime(
            data_datetime_str, "%Y-%m-%d %H:%M:%S"
        )
        data_timestamp = datetime.timestamp(data_datetime_obj)

        return HistoricalDataPoint(
            timestamp=data_timestamp,
            gmtoffset=0,
            datetime=data_datetime_str,
            open=record[1],
            close=record[2],
            high=record[3],
            low=record[4],
            volume=record[5],
        )
