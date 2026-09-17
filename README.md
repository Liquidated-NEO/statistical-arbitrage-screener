# Statistical Cointegration Screener

A quantitative research tool for finding potentially mean-reverting relationships between **Forex and Precious Metals**.

The project takes historical market data from Dukascopy, aligns different instruments into a common time series, tests them for cointegration using the **Engle-Granger test**, and then builds statistically weighted spreads using **OLS regression**.

Once a potentially cointegrated relationship is found, the system tracks the spread using a **rolling Z-Score** and generates systematic entry and exit signals when the spread moves significantly away from, and then back toward, its historical mean.

The main idea is simple:

> Find assets that have historically moved together in a stable long-term relationship, measure how far that relationship has deviated, and look for potential mean-reversion opportunities.

---

## How It Works

The project follows a three-step research process:

```text
Historical Data
      │
      ▼
Data Alignment
      │
      ▼
Cointegration Screening
      │
      ▼
OLS Hedge Ratio
      │
      ▼
Spread Construction
      │
      ▼
Rolling Z-Score
      │
      ▼
Trading Signals
```

Each stage has a specific purpose and is kept separate so the research process is easier to inspect and modify.

---

# 1. Data Ingestion

The first step is collecting historical price data from **Dukascopy**.

The system downloads multi-year historical data for the instruments being tested and uses **bid prices** as the primary price series.

Using a consistent price source is important when comparing multiple instruments. Bid prices also help avoid introducing unnecessary noise from changes in the bid-ask spread.

The data is then passed to the alignment stage.

---

# 2. Time-Series Alignment

Different markets and instruments don't always have observations at exactly the same timestamps.

Before running any statistical tests, the data needs to be put onto a common time axis.

The alignment process:

* Converts timestamps into a proper `datetime` index.
* Resamples the data to **hourly intervals**.
* Combines the instruments into a common matrix.
* Uses an outer join so that missing market observations aren't silently discarded.
* Preserves the underlying gaps in the data for further handling.

The resulting structure looks roughly like this:

```text
                 EURUSD    GBPUSD    XAUUSD    XAGUSD
2026-01-01 09:00    ...       ...       ...       ...
2026-01-01 10:00    ...       ...       ...       ...
2026-01-01 11:00    ...       ...       ...       ...
...
```

Proper timestamp alignment is critical. If the series are incorrectly synchronized, the statistical relationship can be distorted and may introduce look-ahead or synchronization bias.

---

# 3. Cointegration Screening

Once the data has been aligned, the system tests combinations of instruments using the **Engle-Granger two-step cointegration test**.

The goal isn't simply to find assets that are correlated.

Correlation tells us that two assets have tended to move together.

Cointegration asks a different question:

> Is there a combination of these two non-stationary price series that has historically behaved like a stationary series?

For a pair of assets, the relationship can be represented as:

$$
Y_t = \alpha + \beta X_t + \epsilon_t
$$

The resulting residual is:

$$
\epsilon_t = Y_t - \alpha - \beta X_t
$$

The residual is then tested for stationarity.

The current screening threshold is:

```text
p-value < 0.05
```

Pairs that pass this test are kept as candidates for the next stage.

### Why Cointegration Instead of Correlation?

A high correlation doesn't necessarily mean that a spread will revert.

Two assets can remain highly correlated while gradually drifting apart.

Cointegration is useful for statistical-arbitrage research because it specifically looks for a more stable long-term relationship.

That said, a significant cointegration test is **not proof that the relationship will continue to work in the future**.

---

# 4. OLS Hedge Ratio

After identifying a potentially cointegrated pair, the system estimates its hedge ratio using **Ordinary Least Squares (OLS)** regression.

The basic spread is:

$$
Spread_t = Y_t - \beta X_t
$$

where:

* \(Y_t\) is the dependent asset.
* \(X_t\) is the independent asset.
* \(\beta\) is the estimated hedge ratio.

This is preferable to simply subtracting one price from another.

For example, assuming:

```text
Spread = Asset A - Asset B
```

implicitly assumes a **1:1 relationship**.

That's usually an arbitrary assumption.

OLS instead estimates how much of one instrument is required to hedge the other based on the historical relationship between them.

This gives us a more meaningful statistical spread.

---

# 5. Rolling Z-Score

Once the spread has been constructed, the system measures how far it has moved from its recent historical mean.

This is done using a rolling Z-Score:

$$
Z_t =
\frac{Spread_t - \mu_t}
{\sigma_t}
$$

where:

* \(Spread_t\) = current spread
* \(\mu_t\) = rolling mean
* \(\sigma_t\) = rolling standard deviation

A Z-Score of `+2`, for example, means that the spread is approximately two standard deviations above its rolling mean.

A Z-Score of `-2` means that it is approximately two standard deviations below it.

---

# 6. Trading Signals

The signal engine uses a simple state-machine approach.

The purpose of the state machine is to avoid repeatedly entering the same trade while the spread remains outside the entry threshold.

### Entry Conditions

| Z-Score  | Signal          |
| -------- | --------------- |
| `< -2.0` | Buy the spread  |
| `> +2.0` | Sell the spread |

Conceptually:

```text
Z-Score < -2
      │
      ▼
Long Spread
```

```text
Z-Score > +2
      │
      ▼
Short Spread
```

### Exit Condition

The position is closed when the Z-Score returns to the mean:

```text
Z-Score → 0
      │
      ▼
Exit Position
```

The basic strategy therefore follows:

```text
Large negative deviation
          ↓
     Long spread
          ↓
     Mean reversion
          ↓
        Exit
```

and:

```text
Large positive deviation
          ↓
     Short spread
          ↓
     Mean reversion
          ↓
        Exit
```

---

# Complete Workflow

Putting everything together:

```text
┌──────────────────────────┐
│ Dukascopy Historical Data│
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│ Timestamp Normalization  │
│ + Hourly Resampling      │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│ Engle-Granger Test       │
│ p-value < 0.05           │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│ OLS Regression           │
│ Estimate Hedge Ratio     │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│ Construct Spread         │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│ Rolling Z-Score          │
└────────────┬─────────────┘
             │
       ┌─────┴─────┐
       ▼           ▼
    Z < -2       Z > +2
       │           │
       ▼           ▼
 Long Spread   Short Spread
       │           │
       └─────┬─────┘
             ▼
       Z-Score → 0
             │
             ▼
           Exit
```

---

# Installation

Install the required Python packages:

```bash
pip install dukascopy-python pandas statsmodels matplotlib
```

### Dependencies

| Package            | Used For                                     |
| ------------------ | -------------------------------------------- |
| `dukascopy-python` | Downloading historical market data           |
| `pandas`           | Data manipulation and time-series processing |
| `statsmodels`      | Engle-Granger testing and OLS regression     |
| `matplotlib`       | Charts and statistical visualizations        |

---

# Running the Project

The scripts are intended to be run in the following order.

## Step 1 — Download and Prepare Data

```bash
python Form.py
```

This downloads the historical data, processes it, and creates the aligned hourly dataset.

---

## Step 2 — Screen for Cointegration

```bash
python Engle-Granger.py
```

This tests the available instrument combinations and identifies relationships that satisfy the configured cointegration criteria.

Current threshold:

```text
p-value < 0.05
```

---

## Step 3 — Generate Trading Signals

```bash
python signal_generate_2.py
```

This performs the final analysis:

* Calculates the OLS regression.
* Estimates the hedge ratio.
* Builds the spread.
* Calculates the rolling Z-Score.
* Runs the signal state machine.
* Generates entry and exit signals.
* Produces visual analytics.

---

# Current Strategy Parameters

| Parameter               | Current Value |
| ----------------------- | ------------: |
| Cointegration threshold |    `p < 0.05` |
| Long entry              |    `Z < -2.0` |
| Short entry             |    `Z > +2.0` |
| Exit                    |     `Z → 0.0` |
| Data frequency          |      `1 hour` |

These are the current research parameters and shouldn't be assumed to be optimal.

---

# Why This Approach?

The project combines several statistical techniques rather than relying on a single indicator.

**Cointegration** is used to find potentially stable relationships.

**OLS regression** determines how the instruments should be weighted against each other.

**The spread** represents the deviation between the two instruments after accounting for their estimated relationship.

**The Z-Score** standardizes that deviation so extreme moves can be compared across different pairs.

The result is a systematic framework for researching statistical-arbitrage opportunities rather than simply looking for assets that appear visually correlated.

---

# Important Limitations

There are several things to keep in mind before treating a statistically significant pair as a trading opportunity.

### Statistical significance is not profitability

A pair passing the Engle-Granger test doesn't guarantee that trading it will make money.

Real-world performance can be affected by:

* Transaction costs
* Bid-ask spreads
* Slippage
* Execution latency
* Market impact
* Liquidity
* Structural breaks
* Changes in market regimes
* Parameter instability

### Multiple testing matters

If hundreds or thousands of combinations are tested, some pairs will inevitably produce a `p < 0.05` result purely by chance.

This is a major issue for automated cointegration screeners.

A robust research process should therefore consider:

* Multiple-hypothesis testing
* False-discovery control
* Out-of-sample validation
* Walk-forward testing
* Parameter sensitivity
* Stability of the hedge ratio
* Stability of the cointegration relationship

### Historical relationships can break

Cointegration is not permanent.

A relationship that existed for several years can disappear because of changes in:

* Monetary policy
* Market structure
* Commodity fundamentals
* Currency regimes
* Liquidity
* Volatility
* Macroeconomic conditions

The screener should therefore be treated as a **research and candidate-generation system**, not as a guarantee of persistent alpha.

---

# Research Objective

The purpose of this project is to build a systematic pipeline for discovering and evaluating potential statistical-arbitrage relationships.

The workflow is:

1. **Collect** historical market data.
2. **Align** asynchronous time series.
3. **Screen** instruments for cointegration.
4. **Estimate** the hedge ratio.
5. **Construct** the spread.
6. **Measure** deviations using the Z-Score.
7. **Generate** systematic signals.
8. **Evaluate** the relationship through further research and validation.

The end goal is not simply to find pairs with a low p-value. The real objective is to determine whether those relationships are **stable, economically meaningful, and robust out of sample**.

---

## Disclaimer

This project is intended for **quantitative research and educational purposes**.

A statistically significant historical relationship does not guarantee future performance. Before using the strategy with real capital, it should be subjected to realistic backtesting, transaction-cost modeling, out-of-sample testing, walk-forward analysis, and appropriate risk management.

