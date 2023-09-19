from typing import List, Union
import os
from alpha_vantage.timeseries import TimeSeries
from fastapi import APIRouter, Depends, HTTPException, status, Query
from queries.historical import (
    SignalService,
    HistoricalDataRepository,
    ThreeBarSignalRepository,
    HistoricalDataPoint,
    LevelsRepository,
    HttpError,
    SystemMessage,
    StrategySignal,
)

router = APIRouter()


@router.get("/populate_data", response_model=SystemMessage)
def get_historical_data(
    repo_updateddata: HistoricalDataRepository = Depends(),
    repo_threebar: ThreeBarSignalRepository = Depends(),
    repo_levels: LevelsRepository = Depends(),
):
    stock = "TSLA"
    intraday = get_updated_data(repo_updateddata, stock)
    levels = data_to_levels(repo_levels, stock)
    threebar = get_threebarsignal_data(repo_threebar, stock)
    message = {}
    message["detail"] = "test"
    return message


@router.get(
    "/strategy",
    response_model=List[StrategySignal] | SystemMessage,
)
def get_strategy_data(repo: SignalService = Depends()):
    stock = "TSLA"
    try:
        strategy_data = repo.get_strategy(stock)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to retrieve strategy data",
        )
    return strategy_data


@router.get(
    "/candles/retrieve",
    response_model=List[HistoricalDataPoint] | SystemMessage,
)
def get_strategy_data(
    start: str,
    end: str,
    repo: HistoricalDataRepository = Depends(),
):
    print("ZZZZZZZ", start, end)
    try:
        strategy_historical_data = repo.get_range_historical_data(start, end)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to retrieve strategy data.",
        )
    return strategy_historical_data


@router.get("/update_data", response_model=SystemMessage)
def get_updated_data(
    repo: HistoricalDataRepository = Depends(),
    stock: str = Query(..., title="Stock"),
):
    API_key = os.environ.get("ALPHAVANTAGEKEY")
    ts = TimeSeries(key=API_key, output_format="pandas")
    stock = stock
    print("GET UPDATED DATA")
    data, _ = ts.get_intraday(stock, interval="5min", outputsize="full")
    print("get updated data finished")
    return repo.update_historical_data(data, stock)


@router.get("/threebarsignal", response_model=SystemMessage)
def get_threebarsignal_data(
    repo: ThreeBarSignalRepository = Depends(),
    stock: str = Query(..., title="Stock"),
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
    message["detail"] = "test"
    print("get threebar finished")
    return message


@router.get("/levels", response_model=SystemMessage)
def data_to_levels(
    repo: LevelsRepository = Depends(), stock: str = Query(..., title="Stock")
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
    message["detail"] = "test"
    print("get levels finished")
    return message


@router.get("/threebarsignal", response_model=SystemMessage)
def get_threebarsignal_data(
    repo: ThreeBarSignalRepository = Depends(),
    stock: str = Query(..., title="Stock"),
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
    message["detail"] = "test"
    print("get threebar finished")
    return message


@router.get("/levels", response_model=SystemMessage)
def data_to_levels(
    repo: LevelsRepository = Depends(), stock: str = Query(..., title="Stock")
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
    message["detail"] = "test"
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
