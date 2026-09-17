import pandas as pd
import statsmodels.tsa.stattools as ts
import itertools

def find_cointegrated_pairs(dataframe):
    # Get all column names (the 8 tickers)
    assets = dataframe.columns
    
    # Generate all unique combinations of pairs (28 total combinations)
    pairs = list(itertools.combinations(assets, 2))
    
    cointegrated_results = []
    
    print(f"Testing {len(pairs)} unique combinations for cointegration...")
    
    for pair in pairs:
        asset1 = pair[0]
        asset2 = pair[1]
        
        # Extract the price series for both assets
        series1 = dataframe[asset1]
        series2 = dataframe[asset2]
        
        # Run the Engle-Granger Cointegration Test
        # It returns a tuple: (t-statistic, p-value, critical_values)
        try:
            coint_test = ts.coint(series1, series2)
            p_value = coint_test[1]
            
            # A p-value < 0.05 means we reject the null hypothesis (meaning they ARE cointegrated)
            if p_value < 0.05:
                cointegrated_results.append({
                    'Pair': f"{asset1} - {asset2}",
                    'P-Value': round(p_value, 4),
                    'Significance': 'High (<0.01)' if p_value < 0.01 else 'Medium (<0.05)'
                })
        except Exception as e:
            print(f"Error testing {asset1} and {asset2}: {e}")
            
    # Convert results to a DataFrame and sort by the strongest statistical edge (lowest p-value)
    results_df = pd.DataFrame(cointegrated_results)
    
    if not results_df.empty:
        results_df = results_df.sort_values(by='P-Value', ascending=True).reset_index(drop=True)
        print("\n--- STATISTICALLY COINTEGRATED PAIRS FOUND ---")
        print(results_df.to_string())
    else:
        print("\nNo statistically significant pairs found in this timeframe.")
        
    return results_df

# --- HOW TO RUN IT ---
if __name__ == "__main__":
    try:
        df = pd.read_csv("aligned_forex_portfolio.csv", index_col=0, parse_dates=True)
        trdable_pairs = find_cointegrated_pairs(df)
    except FileNotFoundError:
        print("ERROR: aligned_forex_portfolio.csv not found. Please run get_data.py first to fetch and align the data.")
    # Run the screener
        tradable_pairs = find_cointegrated_pairs(df)