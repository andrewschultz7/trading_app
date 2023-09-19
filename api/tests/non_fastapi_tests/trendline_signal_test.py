import sys, os
import unittest

# project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
# sys.path.append(project_root)

# from trading_app.api.queries.historical import TrendlineSignalRepository
# from queries.historical import TrendlineSignalRepository

import mplfinance as mpf
import pandas as pd

all_candles = [
    {'High': 100, 'Low': 85, 'Open': 97, 'Close': 87, 'Datetime': '2023-08-04 10:00'},
    {'High': 95, 'Low': 79, 'Open': 92, 'Close': 81, 'Datetime': '2023-08-04 10:05'},
    {'High': 92, 'Low': 78, 'Open': 91, 'Close': 81, 'Datetime': '2023-08-04 10:10'},
    {'High': 88, 'Low': 74, 'Open': 86, 'Close': 76, 'Datetime': '2023-08-04 10:15'},
    {'High': 83, 'Low': 68, 'Open': 80, 'Close': 70, 'Datetime': '2023-08-04 10:20'},
    {'High': 81, 'Low': 64, 'Open': 78, 'Close': 66, 'Datetime': '2023-08-04 10:25'},
    {'High': 85, 'Low': 58, 'Open': 70, 'Close': 81, 'Datetime': '2023-08-04 10:30'}, #signal
    {'High': 73, 'Low': 72, 'Open': 72, 'Close': 100, 'Datetime': '2023-08-04 10:35'},
    {'High': 111, 'Low': 96, 'Open': 101, 'Close': 110, 'Datetime': '2023-08-04 10:40'},
    {'High': 110, 'Low': 98, 'Open': 110, 'Close': 95, 'Datetime': '2023-08-04 10:45'},
    {'High': 100, 'Low': 97, 'Open': 96, 'Close': 100, 'Datetime': '2023-08-04 10:50'},
    {'High': 99, 'Low': 68, 'Open': 99, 'Close': 71, 'Datetime': '2023-08-04 10:55'},
    {'High': 81, 'Low': 64, 'Open': 78, 'Close': 66, 'Datetime': '2023-08-04 11:00'},
    {'High': 83, 'Low': 68, 'Open': 80, 'Close': 70, 'Datetime': '2023-08-04 11:05'},
    {'High': 88, 'Low': 74, 'Open': 86, 'Close': 76, 'Datetime': '2023-08-04 11:10'},
    {'High': 92, 'Low': 78, 'Open': 91, 'Close': 81, 'Datetime': '2023-08-04 11:15'},
    {'High': 95, 'Low': 79, 'Open': 92, 'Close': 81, 'Datetime': '2023-08-04 11:20'},
    {'High': 100, 'Low': 85, 'Open': 97, 'Close': 87, 'Datetime': '2023-08-04 11:25'},
    {'High': 90, 'Low': 76, 'Open': 86, 'Close': 78, 'Datetime': '2023-08-04 11:30'}, #signal
    {'High': 79, 'Low': 64, 'Open': 77, 'Close': 64, 'Datetime': '2023-08-04 11:35'},
    {'High': 68, 'Low': 51, 'Open': 63, 'Close': 60, 'Datetime': '2023-08-04 11:40'},
    {'High': 71, 'Low': 68, 'Open': 60, 'Close': 77, 'Datetime': '2023-08-04 11:45'}
]


class TestTrendlineFunction(unittest.TestCase):
    def trendline(self, candles):
        stop_loss = candles[1]["Low"]
        take_profit = 0.0
        global current_candle
        current_candle = 2
        slope1 = 0.0
        slope2 = 0.0
        candle_count = 0
        result = []

        while current_candle <= len(candles)-1:
            def expected_trend(candles, candle_price, less_greater, j):
                global current_candle
                initial_candle = [candles[j-2][candle_price], candles[j-2]["Datetime"]] #starts first candle for signal
                # initial_candle = candles[j-2][candle_price]
                next_candle = candles[j-1][candle_price] # candle_price will be either High or Low
                signal_finished = False
                percent_slope = percent_slope2 = (
                    ((next_candle - initial_candle[0]) /
                    initial_candle[0]) * 100
                )
                expected_last_candle = next_candle + percent_slope
                count = 0
                while (
                    count < 11 and
                    (j <= len(candles) - 1 or
                    signal_finished == False)
                ): #count < 11 placeholder
                    print("JJJJJJJJJJJJJJJJ ", j, count, current_candle)
                    last_candle = candles[j][candle_price]#last candle for signal, dynamic
                    last_candle_close = candles[j]["Close"]
                    if eval(f"{last_candle_close} {less_greater} {expected_last_candle}"):
                        signal_finished = True
                        current_candle += count
                        return initial_candle[1], candles[j]["Datetime"], 100, "Yes"
                    # else:
                    #     expected_last_candle = (
                    #         ((last_candle - initial_candle) / initial_candle) * 100 +
                    #         percent_slope2
                    #     )
                    j += 1
                    count += 1
                    print(current_candle)
                print(i)
                current_candle += count

            if candles[current_candle-2]["High"] >= candles[current_candle-1]["High"]:
                candle_price = "High"
                less_greater = ">"
                first, last, risk_reward, success = expected_trend(candles, candle_price, less_greater, current_candle)

            elif candles[current_candle-2]["Low"] <= candles[current_candle-1]["Low"]:
                candle_price = "Low"
                less_greater = "<"
                first, last, risk_reward, success = expected_trend(candles, candle_price, less_greater, current_candle)

            if result is None:
                result = []
            else:
                result.append([first, last])


        return result

    def test_trendline_postive_cases(self):
        candles = all_candles
        placeholder = None
        result = self.trendline(candles)

        expected_first = all_candles[0]["Datetime"]
        expected_breakout = all_candles[7]["Datetime"]

        self.assertEqual(result[0][0], expected_first)
        self.assertEqual(result[0][1], expected_breakout)

    def test_trendline_negative_cases(self):
        pass



class Visualization_of_data:
    def __init__(self, candles):
        self.candles = candles
        self.date = [candle["Datetime"] for candle in candles]
        self.high = [candle["High"] for candle in candles]
        self.low = [candle["Low"] for candle in candles]
        self.open = [candle["Open"] for candle in candles]
        self.close = [candle["Close"] for candle in candles]

    def visualize(self):
        df = self.get_dataframe()
        mpf.plot(df, type='candle', style='charles', title="Candlestick Chart - Descending Channel")

    def get_dataframe(self):
        data = {
            "Open": self.open,
            "High": self.high,
            "Low": self.low,
            "Close": self.close
        }
        df = pd.DataFrame(data, index=pd.to_datetime(self.date))
        return df


visualizer = Visualization_of_data(all_candles)
visualizer.visualize()

if __name__ == '__main__':
    unittest.main()
