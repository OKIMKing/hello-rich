# 纳斯达克100增强策略（NASDAQ-100 Enhanced Strategy）

自动抓取真实行情与财务数据，从 2015 年至今回测增强型多因子策略。

## 使用方法

```bash
# 安装依赖
pip install -r requirements.txt

# 抓取数据
python fetch_data.py

# 运行回测
python backtest.py

# 生成报告
python build_ppt.py
```

生成的报告保存在 `reports/` 文件夹中。
