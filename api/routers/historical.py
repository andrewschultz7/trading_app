from typing import List, Union
import os
import requests
import pandas as pd

from sqlalchemy import create_engine
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
    # Hit 3rd party API
    # get JSON response
    # parse JSON, appending vwap, vwapf, ema009, ema021, ema200, tl101
    # Then store data into database

    # url = "https://eod-historical-data.p.rapidapi.com/intraday/spy.us"

    # rapid_api_key = os.environ.get("RAPIDAPIKEY")
    # querystring = {"interval":"1m","fmt":"json","from":"1688510826","to":"1691189226"}
    # headers = {
    #     "X-RapidAPI-Key": rapid_api_key,
    #     "X-RapidAPI-Host": "eod-historical-data.p.rapidapi.com",
    # }
    # api_response = requests.get(url, headers=headers, params=querystring)
    # data = api_response.json()
    # response = repo.update_historical_data(data)
    # return response
    API_key = os.environ.get("ALPHAVANTAGEKEY")
    ts = TimeSeries(key=API_key, output_format='pandas')
    data, _ = ts.get_intraday('QQQ', interval='5min', outputsize='full')
    db_file = os.path.join(os.path.dirname(__file__), '..', 'trading_data.db')
    engine = create_engine(f'sqlite:///{db_file}')

    def calculate_indicators(data):
        data['vwap'] = (data['1. open'] + data['2. high'] + data['3. low'] + data['4. close']) / 4
        data['ema009'] = data['4. close'].ewm(span=9, adjust=False).mean()
        data['ema021'] = data['4. close'].ewm(span=21, adjust=False).mean()
        data['ema200'] = data['4. close'].ewm(span=200, adjust=False).mean()
        return data

    data = calculate_indicators(data)

    for date, row in data.iterrows():
        insert_query = """
            INSERT INTO trading_data (timestamp, datetime, open, high, low, close, volume, vwap, ema009, ema021, ema200)
            VALUES (?,?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        values = (
            str(date),str(date), row['1. open'], row['2. high'], row['3. low'], row['4. close'],
            row['5. volume'], row['vwap'], row['ema009'], row['ema021'], row['ema200']
        )
        cursor.execute(insert_query, values)



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
