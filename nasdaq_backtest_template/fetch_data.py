import pandas as pd
import yfinance as yf
import requests
import io

def fetch_nasdaq100_symbols():
    """
    获取当前纳斯达克100成分股，来源：Nasdaq 官方 CSV
    """
    url = "https://data.nasdaq.com/api/v3/datatables/NDAQ/NDX.csv"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200 and 'symbol' in r.text:
            df = pd.read_csv(io.StringIO(r.text))
            tickers = df['symbol'].dropna().unique().tolist()
            print(f"✅ 成功获取 {len(tickers)} 支纳斯达克100股票。")
            return tickers
    except Exception as e:
        print(f"⚠️ 获取官方CSV失败，使用备用列表: {e}")

    # 备用方案（静态名单）
    return [
        'AAPL', 'MSFT', 'GOOG', 'AMZN', 'NVDA', 'META', 'TSLA', 'PEP', 'COST', 'AVGO',
        'NFLX', 'ADBE', 'INTC', 'AMD', 'CSCO', 'TXN', 'QCOM', 'AMAT', 'INTU', 'PYPL'
    ]

def fetch_price_data(symbols, start_date, end_date):
    """
    从 Yahoo Finance 抓取历史股价
    """
    data = yf.download(symbols, start=start_date, end=end_date, group_by='ticker', auto_adjust=True)
    print(f"✅ 成功抓取 {len(symbols)} 支股票的历史数据。")
    return data
