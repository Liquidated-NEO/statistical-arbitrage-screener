Statistical Cointegration Screener
This repository implements an automated statistical arbitrage pipeline for Forex and Precious Metals. It ingests asynchronous historical data from Dukascopy, normalizes the time-series matrix, and runs Engle-Granger tests to identify historically stationary spreads. The tool programmatically filters out spurious correlations to isolate statistically significant, mean-reverting trading pairs.

Pipeline Architecture
The system is built on a fault-tolerant, 4-stage quantitative pipeline:

Data Ingestion: Fetches multi-year historical data via the Dukascopy API, strictly limiting to bid prices to prevent spread-widening noise.

Matrix Alignment: Forces explicit datetime indexing, resamples to hourly intervals, and outer-joins asynchronous data to prevent look-ahead bias and drop missing market gaps.

Statistical Screening: Iterates through portfolio combinations using the statsmodels Engle-Granger two-step cointegration test to mathematically prove stationarity (p-value < 0.05).

OLS Regression: Calculates the hedge ratio via Ordinary Least Squares regression to dynamically weight the spread, avoiding the mathematical flaws of 1:1 nominal subtraction.

Signal Generation (Rolling Z-Score)
The system utilizes a state machine to track the rolling Z-Score of the OLS-weighted spread, preventing signal spam during extended deviations. Trades are executed mechanically:

Entry Triggers: The system buys the spread when the Z-score drops below -2.0 and sells the spread when it spikes above +2.0.

Exit Triggers: The system exits all active positions the moment the Z-score reverts to the historical mean (0.0).

Installation & Execution
Install dependencies: pip install dukascopy-python pandas statsmodels matplotlib

Step 1 (Ingest Data): Run python Form.py to fetch historical hourly data and generate the aligned dataset.

Step 2 (Find Edge): Run python Engle-Granger.py to test the portfolio for statistical cointegration.

Step 3 (Generate Signals): Run python signal_generate_2.py to calculate OLS regression, trigger the state machine, and render the visual analytics.
