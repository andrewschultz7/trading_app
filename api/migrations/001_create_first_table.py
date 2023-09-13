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
        prebuffer TIMESTAMP,
        timestart TIMESTAMP,
        timeeend TIMESTAMP,
        postbuffer TIMESTAMP,
        riskreward INT,
        success TEXT
        );
        """,
        # "Down" SQL statement
        """
        DROP TABLE strategy_signal;
        """,
    ],
    [
        """
        CREATE TABLE tsla_prices (
        price DECIMAL(10,2),
        level01 INT DEFAULT 0,
        timestamp01 TIMESTAMP,
        level02 INT DEFAULT 0,
        timestamp02 TIMESTAMP
        )
        """,
        """
        DROP TABLE tsla_prices;
        """,
    ],
    [
        """
        CREATE TABLE es_prices (
        price DECIMAL(10,2),
        level01 INT DEFAULT 0,
        timestamp01 TIMESTAMP,
        level02 INT DEFAULT 0,
        timestamp02 TIMESTAMP
        )
        """,
        """
        DROP TABLE es_prices;
        """,
    ],
    [
        """
        CREATE TABLE nq_prices (
        price DECIMAL(10,2) UNIQUE,
        level01 INT DEFAULT 0,
        timestamp01 TIMESTAMP,
        level02 INT DEFAULT 0,
        timestamp02 TIMESTAMP
        )
        """,
        """
        DROP TABLE nq_prices;
        """,
    ],
]
# pg-admin_trading_data
# pg_trading_data
