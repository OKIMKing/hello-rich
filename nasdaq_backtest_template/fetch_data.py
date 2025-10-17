import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
from pathlib import Path

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

def fetch_nasdaq100_symbols():
    url = "https://en.wikipedia.org/wiki/Nasdaq-100"
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", {"id": "constituents"})
    tickers = [row.find_all("td")[1].text.strip() for row in table.find_all("tr")[1:]]
    pd.Series(tickers).to_csv(DATA_DIR / "nasdaq100_symbols.csv", index=False)
    print(f"✅ Saved {len(tickers)} tickers.")
    return tickers

def fetch_price_and_fundamentals(tickers):
    all_data = []
    for t in tickers:
        print(f"Fetching {t} ...")
        ticker = yf.Ticker(t)
        hist = ticker.history(start="2015-01-01")
        hist.to_csv(DATA_DIR / f"{t}_price.csv")

        info = ticker.info
        fundamentals = {
            "symbol": t,
            "trailingPE": info.get("trailingPE"),
            "revenue": info.get("totalRevenue"),
            "marketCap": info.get("marketCap"),
        }
        all_data.append(fundamentals)
    pd.DataFrame(all_data).to_csv(DATA_DIR / "fundamentals.csv", index=False)
    print("✅ Fundamentals saved.")

if __name__ == "__main__":
    tickers = fetch_nasdaq100_symbols()
    fetch_price_and_fundamentals(tickers)
