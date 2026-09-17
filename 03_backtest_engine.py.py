import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt

def generate_trading_signals(series1: pd.Series, series2: pd.Series, window: int = 100) -> pd.DataFrame:
    """
    Calculates the OLS hedge ratio and tracks trading state to prevent signal spam.
    Enters on 2.0 std deviations, exits on reversion to 0.0.
    """
    print("Calculating Hedge Ratio via OLS Regression...")

    model = sm.OLS(series1, series2).fit()
    hedge_ratio = model.params.iloc[0]

    spread = series1 - (hedge_ratio * series2)
    rolling_mean = spread.rolling(window=window).mean()
    rolling_std = spread.rolling(window=window).std()
    z_score = (spread - rolling_mean) / rolling_std

    signals_df = pd.DataFrame(index=series1.index)
    signals_df['Asset1_Price'] = series1
    signals_df['Asset2_Price'] = series2
    signals_df['Spread'] = spread
    signals_df['Z_Score'] = z_score
    signals_df['Signal'] = 'HOLD'

    # --- STATE MACHINE LOGIC ---
    current_position = 0

    for i in range(len(signals_df)):
        z = signals_df['Z_Score'].iloc[i]

        if pd.isna(z):
            continue

        if current_position == 0:
            if z < -2.0:
                signals_df.iloc[i, signals_df.columns.get_loc('Signal')] = 'BUY SPREAD'
                current_position = 1
            elif z > 2.0:
                signals_df.iloc[i, signals_df.columns.get_loc('Signal')] = 'SELL SPREAD'
                current_position = -1

        elif current_position == 1:
            if z >= 0.0:
                signals_df.iloc[i, signals_df.columns.get_loc('Signal')] = 'EXIT LONG'
                current_position = 0

        elif current_position == -1:
            if z <= 0.0:
                signals_df.iloc[i, signals_df.columns.get_loc('Signal')] = 'EXIT SHORT'
                current_position = 0

    return signals_df

def calculate_backtest_pnl(signals_df: pd.DataFrame, transaction_cost: float = 0.0002) -> pd.DataFrame:
    """
    Simulates the actual Profit & Loss of the state machine.
    transaction_cost represents the bid/ask spread and slippage penalty per trade.
    """
    print("Calculating Backtest PNL...")
    
    signals_df['Position'] = 0 
    signals_df['Trade_PNL'] = 0.0
    
    current_position = 0
    entry_spread = 0.0
    
    for i in range(len(signals_df)):
        signal = signals_df['Signal'].iloc[i]
        current_spread = signals_df['Spread'].iloc[i]
        
        signals_df.iloc[i, signals_df.columns.get_loc('Position')] = current_position
        
        if signal == 'BUY SPREAD':
            current_position = 1
            entry_spread = current_spread
            signals_df.iloc[i, signals_df.columns.get_loc('Position')] = current_position
            
        elif signal == 'SELL SPREAD':
            current_position = -1
            entry_spread = current_spread
            signals_df.iloc[i, signals_df.columns.get_loc('Position')] = current_position
            
        elif 'EXIT' in signal:
            if current_position == 1:
                gross_pnl = current_spread - entry_spread
            elif current_position == -1:
                gross_pnl = entry_spread - current_spread
            else:
                gross_pnl = 0
                
            net_pnl = gross_pnl - (transaction_cost * 2)
            signals_df.iloc[i, signals_df.columns.get_loc('Trade_PNL')] = net_pnl
            
            current_position = 0
            entry_spread = 0.0
            signals_df.iloc[i, signals_df.columns.get_loc('Position')] = current_position
            
    signals_df['Cumulative_PNL'] = signals_df['Trade_PNL'].cumsum()
    
    closed_trades = signals_df[signals_df['Trade_PNL'] != 0]
    total_trades = len(closed_trades)
    winning_trades = len(closed_trades[closed_trades['Trade_PNL'] > 0])
    total_pnl = signals_df['Cumulative_PNL'].iloc[-1]
    
    print("\n--- BACKTEST RESULTS (NET OF FEES) ---")
    print(f"Total Trades Executed: {total_trades}")
    if total_trades > 0:
        win_rate = (winning_trades / total_trades) * 100
        print(f"Win Rate: {win_rate:.2f}%")
        print(f"Net Profit (Spread Points): {total_pnl:.6f}")
        print(f"Average Profit Per Trade: {(total_pnl / total_trades):.6f}")
    else:
        print("No trades closed during this period.")
        
    return signals_df

def plot_zscore_signals(signals_df: pd.DataFrame, pair_name: str = "Asset 1 vs Asset 2"):
    """
    Plots the rolling Z-Score, entry bands, and clean entry/exit markers.
    """
    print(f"Generating performance visualization for {pair_name}...")
    plot_df = signals_df.dropna().copy()

    plt.figure(figsize=(14, 7))

    plt.plot(plot_df.index, plot_df['Z_Score'], label="Rolling Z-Score", color='blue', linewidth=1.2)
    plt.axhline(2.0, color='red', linestyle='--', linewidth=1.5, label='Sell Threshold (+2.0)')
    plt.axhline(-2.0, color='green', linestyle='--', linewidth=1.5, label='Buy Threshold (-2.0)')
    plt.axhline(0.0, color='grey', linestyle=':', linewidth=1.5, label='Mean (0.0)')

    buy_signals = plot_df[plot_df['Signal'] == 'BUY SPREAD']
    sell_signals = plot_df[plot_df['Signal'] == 'SELL SPREAD']
    exit_signals = plot_df[plot_df['Signal'].str.contains('EXIT')]

    plt.scatter(buy_signals.index, buy_signals['Z_Score'], marker='^', color='green', s=120, label='Enter Long', zorder=5)
    plt.scatter(sell_signals.index, sell_signals['Z_Score'], marker='v', color='red', s=120, label='Enter Short', zorder=5)
    plt.scatter(exit_signals.index, exit_signals['Z_Score'], marker='x', color='black', s=120, label='Exit Position (Mean Reversion)', zorder=5)

    plt.title(f"Statistical Arbitrage: Mean Reversion Trade Signals ({pair_name})", fontsize=16, fontweight='bold', pad=15)
    plt.xlabel("Date", fontsize=12, fontweight='bold')
    plt.ylabel("Z-Score (Standard Deviations)", fontsize=12, fontweight='bold')
    plt.legend(loc='upper left', frameon=True, shadow=True)
    plt.grid(True, linestyle='--', alpha=0.4)
    plt.tight_layout()

    filename = "zscore_signals_chart.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"SUCCESS: Clean chart saved as {filename}")
    plt.show()

if __name__ == "__main__":
    try:
        df = pd.read_csv("test_data.csv", index_col=0, parse_dates=True)
        signals = generate_trading_signals(df['EURUSD'], df['GBPUSD'])
        signals = calculate_backtest_pnl(signals, transaction_cost=0.0002)
        plot_zscore_signals(signals, "EUR/USD vs GBP/USD")
    except FileNotFoundError:
        print("ERROR: test_data.csv not found. Run form.py first.")
    except KeyError as e:
        print(f"ERROR: Missing column in dataset. {e}")