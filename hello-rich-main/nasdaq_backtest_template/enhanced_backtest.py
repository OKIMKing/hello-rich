import pandas as pd, numpy as np
from pathlib import Path
from datetime import datetime

DATA_DIR = Path("data")
REPORT_DIR = Path("reports")
REPORT_DIR.mkdir(exist_ok=True)

def load_nav():
    nav_path = REPORT_DIR / "backtest_nav.csv"
    if not nav_path.exists():
        raise FileNotFoundError("backtest_nav.csv not found. Run backtest.py first.")
    nav = pd.read_csv(nav_path, index_col=0, parse_dates=True).iloc[:,0]
    return nav

def load_prices():
    # load QQQ price if available in data folder
    qqq_path = DATA_DIR / "QQQ_price.csv"
    if qqq_path.exists():
        q = pd.read_csv(qqq_path, parse_dates=["Date"]).set_index('Date')["Close"].sort_index()
        return q
    return None

def performance_metrics(ts):
    # ts: pandas Series NAV indexed by date
    returns = ts.pct_change().dropna()
    total_return = ts.iloc[-1]/ts.iloc[0]-1
    days = (ts.index[-1] - ts.index[0]).days
    ann_return = (1+total_return)**(365.0/days)-1 if days>0 else 0.0
    ann_vol = returns.std() * (252**0.5)
    sharpe = (returns.mean()*252) / (returns.std()*(252**0.5) + 1e-9)
    roll_max = ts.cummax()
    drawdown = (ts - roll_max) / roll_max
    max_dd = drawdown.min()
    return {
        "total_return": total_return,
        "annualized_return": ann_return,
        "annualized_vol": ann_vol,
        "sharpe": sharpe,
        "max_drawdown": max_dd
    }

def yearly_returns(ts):
    yrs = ts.groupby(ts.index.year).apply(lambda x: x.iloc[-1]/x.iloc[0]-1)
    return yrs

def run_enhanced():
    nav = load_nav()
    metrics = performance_metrics(nav)
    yrs = yearly_returns(nav)
    qqq = load_prices()
    comp = None
    if qqq is not None:
        # align QQQ to nav dates by normalizing to 1 at nav start date
        qqq = qqq.ffill()
        if nav.index[0] in qqq.index:
            qqq_norm = qqq / qqq.loc[nav.index[0]]
        else:
            q0 = qqq[:nav.index[0]].iloc[-1]
            qqq_norm = qqq / q0
        qqq_nav = qqq_norm.reindex(nav.index).ffill()
        comp = qqq_nav
        comp_metrics = performance_metrics(qqq_nav)
    else:
        comp_metrics = None

    # save metrics and yearly returns
    pd.Series(metrics).to_csv(REPORT_DIR / "metrics_strategy.csv")
    if comp_metrics is not None:
        pd.Series(comp_metrics).to_csv(REPORT_DIR / "metrics_benchmark.csv")
    yrs.to_csv(REPORT_DIR / "yearly_returns_strategy.csv", header=["return"]) 
    if comp is not None:
        yearly_q = comp.groupby(comp.index.year).apply(lambda x: x.iloc[-1]/x.iloc[0]-1)
        yearly_q.to_csv(REPORT_DIR / "yearly_returns_benchmark.csv", header=["return"])
    print('✅ Enhanced metrics saved to reports/')

if __name__ == "__main__":
    run_enhanced()
