Statistical Arbitrage & Cointegration Screener.
Most retail traders lose money trying to trade basic price correlation. Two assets can move in the same direction for a month and then permanently drift apart, wiping out a trading account.

This project was built to test a real mathematical edge: Statistical Cointegration.

Instead of trading on gut feeling, this Python pipeline ingests raw market data, mathematically proves whether a mean-reverting relationship exists, and simulates the actual net profit of trading that spread.

The Pipeline
This is a 3-stage, fault-tolerant system built for Forex and Precious Metals:

Data Ingestion (01_data_ingestion.py): Pulls multi-year historical bid data directly from the Dukascopy API. It forces explicit datetime indexing and outer-joins asynchronous time-series data to eliminate look-ahead bias and handle missing market gaps.

Statistical Screener (02_statistical_screener.py): Iterates through portfolio combinations and runs the statsmodels Engle-Granger two-step test. It aggressively filters out spurious correlations and only flags pairs mathematically proven to be stationary (p-value < 0.05).

Backtest Engine (03_backtest_engine.py): Calculates the hedge ratio via Ordinary Least Squares (OLS) regression. It tracks the rolling Z-Score of the spread and executes a state machine to generate mechanical buy/sell signals without spamming orders.

The Reality Check: Net PNL vs. Gross PNL
A strategy that looks highly profitable on paper will often bleed money in live markets due to broker fees.

This backtester explicitly deducts simulated transaction costs (spread + slippage) from every single round-trip execution. To overcome this friction, the state machine requires a severe Z-Score deviation (+/- 2.5 standard deviations) before deploying capital. This ensures the gross profit per trade is actually large enough to survive real-world execution costs.

How to Run It
Install dependencies:
```Powershell
Bash
pip install dukascopy-python pandas statsmodels matplotlib
Execute the pipeline in order:
```
```
Run
python 01_data_ingestion.py to download and align the dataset.
```
```
Run
 python 02_statistical_screener.py to mathematically prove the edge.
```
```
Run
 python 03_backtest_engine.py to calculate OLS regression, simulate net profit, and render the visual analytics.
```
