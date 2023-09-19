from typing import List, Union
import os
import requests
import pandas as pd

from alpha_vantage.timeseries import TimeSeries

from fastapi import APIRouter, Depends, HTTPException, status, Query
from queries.historical import (
    HistoricalDataPoint,
    SignalService,
    ThreeBarSignal,
    HistoricalDataRepository,
    ThreeBarSignalRepository,
    LevelsRepository,
    HttpError,
    SystemMessage,
)

router = APIRouter()

@router.get("/populate_data", response_model=SystemMessage)
def get_historical_data(
    repo_updateddata: HistoricalDataRepository = Depends(),
    repo_threebar: ThreeBarSignalRepository = Depends(),
    repo_levels: LevelsRepository = Depends()
    ):
    stock = 'TSLA'
    intraday = get_updated_data(repo_updateddata, stock)
    levels = data_to_levels(repo_levels, stock)
    threebar = get_threebarsignal_data(repo_threebar, stock)
    return intraday, threebar, levels

@router.get("/strategy", response_model=SystemMessage)
def get_strategy_data(repo: SignalService = Depends()):
    stock = 'TSLA'
    try:
        strategy_data = repo.get_strategy(stock)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to retrieve strategy data"
        )
    print(strategy_data, stock)
    return strategy_data, stock

# @router.get("/signal", response_model=SystemMessage)
# async def signal_data_to_output(signal_data: dict):
#     signal_service = SignalService()
#     first_threebar, last_threebar, rr_threebar, suc_threebar = signal_service.use_threebar(signal_data)
#     first_trendline, last_trendline, rr_trendline, suc_trendline = signal_service.use_trendline(signal_data)

#     signal_service.record_to_strategy_signal(
#         first_threebar,
#         last_threebar,
#         rr_threebar,
#         suc_threebar,
#         first_trendline,
#         last_trendline,
#         rr_trendline,
#         suc_trendline
#         )

@router.get("/update_data", response_model=SystemMessage)
def get_updated_data(
    repo: HistoricalDataRepository = Depends(),
    stock: str = Query(..., title="Stock")):
    API_key = os.environ.get("ALPHAVANTAGEKEY")
    ts = TimeSeries(key=API_key, output_format='pandas')
    # stock = 'TSLA'
    stock = stock
    print("GET UPDATED DATA")
    data, _ = ts.get_intraday(stock, interval='5min', outputsize='full')
    print("get updated data finished")
    return repo.update_historical_data(data, stock)



@router.get("/threebarsignal", response_model=SystemMessage)
def get_threebarsignal_data(
    repo: ThreeBarSignalRepository = Depends(),
    stock: str = Query(..., title="Stock")
    ):
    print("THREE BAR SIGNAL")
    stock = stock
    try:
        threebarsignal_data = repo.data_to_three_bar(stock)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to retrieve test threebarsignal data.",
        )
    message = {}
    message['detail'] = "test"
    print("get threebar finished")
    return message

@router.get("/levels", response_model=SystemMessage)
def data_to_levels(
    repo: LevelsRepository = Depends(),
    stock: str = Query(..., title="Stock")
    ):
    print("Data to Levels")
    stock = stock
    try:
        levels_data = repo.data_to_levels(stock)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to retrieve test levels data.",
        )
    message = {}
    message['detail'] = "test"
    print("get levels finished")
    return message

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
