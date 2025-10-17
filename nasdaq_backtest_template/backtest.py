from pathlib import Path
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from pathlib import Path

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

def backtest():
    fundamentals = pd.read_csv(DATA_DIR / "fundamentals.csv")
    prices = {}
    for sym in fundamentals["symbol"]:
        path = DATA_DIR / f"{sym}_price.csv"
        if path.exists():
            df = pd.read_csv(path, parse_dates=["Date"])
            df["symbol"] = sym
            prices[sym] = df
    if not prices:
        print("⚠️ No price data found.")
        return
    df_all = pd.concat(prices.values())

    # quarterly prices
    df_all["quarter"] = df_all["Date"].dt.to_period("Q")
    q_prices = df_all.groupby(["quarter", "symbol"])["Close"].last().unstack()

    # momentum score (12m change)
    momentum = q_prices.pct_change(4)
    pe_rank = fundamentals.set_index("symbol")["trailingPE"].rank(ascending=True)
    score = momentum.iloc[-1].rank(ascending=False) + pe_rank.reindex(momentum.columns)
    top20 = score.nsmallest(20).index.tolist()

    portfolio = q_prices[top20]
    returns = portfolio.pct_change().mean(axis=1)
    nav = (1 + returns.fillna(0)).cumprod()
    nav.to_csv(REPORT_DIR / "backtest_nav.csv")

    print("✅ Backtest complete.")
    return nav

if __name__ == "__main__":
    backtest()
