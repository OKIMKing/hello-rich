import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path

REPORT_DIR = Path('reports')
REPORT_DIR.mkdir(exist_ok=True)
OUT_HTML = REPORT_DIR / 'dashboard.html'

def load_series():
    nav_path = REPORT_DIR / 'backtest_nav.csv'
    if not nav_path.exists():
        raise FileNotFoundError('Run backtest.py first to generate backtest_nav.csv')
    nav = pd.read_csv(nav_path, index_col=0, parse_dates=True).iloc[:,0]
    # load benchmark if exists
    try:
        q = pd.read_csv('data/QQQ_price.csv', parse_dates=['Date']).set_index('Date')['Close'].sort_index()
        # normalize to nav start
        if nav.index[0] in q.index:
            qnorm = q / q.loc[nav.index[0]]
        else:
            q0 = q[:nav.index[0]].iloc[-1]
            qnorm = q / q0
        qnorm = qnorm.reindex(nav.index).ffill()
    except Exception:
        qnorm = None
    return nav, qnorm

def build_dashboard(nav, qnorm=None):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=nav.index, y=nav.values, mode='lines', name='Strategy NAV'))
    if qnorm is not None:
        fig.add_trace(go.Scatter(x=qnorm.index, y=qnorm.values, mode='lines', name='QQQ (norm)'))
    fig.update_layout(title='Cumulative NAV', xaxis_title='Date', yaxis_title='NAV')

    # annual returns bar
    yearly = nav.groupby(nav.index.year).apply(lambda x: x.iloc[-1]/x.iloc[0]-1)
    fig2 = px.bar(x=yearly.index.astype(str), y=yearly.values, labels={'x':'Year', 'y':'Return'}, title='Yearly Returns')

    # drawdown
    roll_max = nav.cummax()
    drawdown = (nav - roll_max) / roll_max
    fig3 = go.Figure(go.Scatter(x=drawdown.index, y=drawdown.values, mode='lines', name='Drawdown'))
    fig3.update_layout(title='Drawdown', xaxis_title='Date', yaxis_title='Drawdown')

    # compose into single html
    html = """<html><head><meta charset='utf-8'><title>Backtest Dashboard</title></head><body>"""
    html += '<h1>NASDAQ-100 Enhanced Strategy — Dashboard</h1>'
    html += fig.to_html(full_html=False, include_plotlyjs='cdn')
    html += '<hr>' + fig2.to_html(full_html=False, include_plotlyjs=False)
    html += '<hr>' + fig3.to_html(full_html=False, include_plotlyjs=False)
    html += '</body></html>'
    OUT_HTML.write_text(html, encoding='utf-8')
    print('✅ Dashboard saved to', OUT_HTML)

if __name__ == '__main__':
    nav, qnorm = load_series()
    build_dashboard(nav, qnorm)
