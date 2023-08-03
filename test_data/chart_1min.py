import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd

df = pd.read_csv(
    "sample2.csv",
    header=None,
    names=["Date", "Open", "High", "Low", "Close", "Volume"],
)
df["Date"] = pd.to_datetime(df["Date"])
df.set_index("Date", inplace=True)

mpf.plot(df, type="candle", title="Candlestick Chart", ylabel="Price")

plt.show()
