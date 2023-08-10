from typing import List, Union
import os
import requests
import pandas as pd

# from sqlalchemy import create_engine
from alpha_vantage.timeseries import TimeSeries

from fastapi import APIRouter, Depends, HTTPException, status
from queries.historical import (
    HistoricalDataPoint,
    HistoricalDataRepository,
    HttpError,
    SystemMessage,
)

router = APIRouter()


@router.get("/update_data", response_model=SystemMessage)
def get_updated_data(repo: HistoricalDataRepository = Depends()):
    API_key = os.environ.get("ALPHAVANTAGEKEY")
    ts = TimeSeries(key=API_key, output_format='pandas')
    data, _ = ts.get_intraday('QQQ', interval='5min', outputsize='full')
    return repo.update_historical_data(data)






@router.get(
    "/historical/{fraction}",
    # response_model=Union[List[HistoricalDataPoint], HttpError],
)
def get_test_historical_data(
    fraction: int,
    repo: HistoricalDataRepository = Depends(),
):
    if fraction < 1 or not isinstance(fraction, int):
        fraction = 1
    try:
        test_historical_data = repo.get_fraction_historical_data(fraction)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to retrieve test historical data.",
        )
    return test_historical_data
