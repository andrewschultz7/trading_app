import sys
from pathlib import Path

path = str(Path(Path(__file__).parent.absolute()).parent.absolute())
sys.path.insert(0, path)
from db_data.import_csv import import_csv

steps = [
    [
        # "Up" SQL statement
        """
        CREATE TABLE trading_data (
        timestamp BIGINT,
        datetime TIMESTAMP,
        open DECIMAL(10,2),
        close DECIMAL(10,2),
        high DECIMAL(10,2),
        low DECIMAL(10,2),
        volume INT,
        vwap DECIMAL(10,2),
        vwapf DECIMAL(10,2),
        ema009 DECIMAL(10,2),
        ema021 DECIMAL(10,2),
        ema200 DECIMAL(10,2),
        tl01 DECIMAL(10,2)
        );
        """,
        # "Down" SQL statement
        """
        DROP TABLE trading_data;
        """,
    ],
    [
        # "Up" SQL statement
        """
        CREATE TABLE strategy_signal (
        timestart TIMESTAMP,
        timeeend TIMESTAMP,
        riskreward INT,
        success TEXT
        );
        """,
        # "Down" SQL statement
        """
        DROP TABLE strategy_signal;
        """,
    ],
]
# pg-admin_trading_data
# pg_trading_data
