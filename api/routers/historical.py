from typing import List, Union
import os
import requests

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
    # Hit 3rd party API
    # get JSON response
    # parse JSON, appending vwap, vwapf, ema009, ema021, ema200, tl101
    # Then store data into database

    url = "https://eod-historical-data.p.rapidapi.com/intraday/spy.us"

    rapid_api_key = os.environ.get("RAPIDAPIKEY")
    querystring = {"interval":"1m","fmt":"json","from":"1688510826","to":"1691189226"}
    headers = {
        "X-RapidAPI-Key": rapid_api_key,
        "X-RapidAPI-Host": "eod-historical-data.p.rapidapi.com",
    }
    api_response = requests.get(url, headers=headers, params=querystring)
    data = api_response.json()
    response = repo.update_historical_data(data)
    return response


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
