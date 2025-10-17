import requests
from bs4 import BeautifulSoup

def fetch_nasdaq100_symbols():
    url = "https://en.wikipedia.org/wiki/Nasdaq-100"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    table = soup.find("table")
    if table is None:
        print("⚠️ 无法从网页抓取NASDAQ100列表，改用备用名单。")
        return ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "NFLX", "PEP", "AVGO"]
    tickers = [row.find_all("td")[1].text.strip() for row in table.find_all("tr")[1:]]
    return tickers

if __name__ == "__main__":
    symbols = fetch_nasdaq100_symbols()
    print(f"共获取 {len(symbols)} 支股票")
