import pandas as pd
from datetime import datetime
import time

import dukascopy_python as dp
# Import the exact instrument constants required by the API
from dukascopy_python.instruments import (
    INSTRUMENT_FX_MAJORS_EUR_USD,
    INSTRUMENT_FX_MAJORS_GBP_USD,
    INSTRUMENT_FX_MAJORS_USD_JPY,
    INSTRUMENT_FX_MAJORS_AUD_USD,
    INSTRUMENT_FX_MAJORS_USD_CAD,
    INSTRUMENT_FX_MAJORS_USD_CHF,
    INSTRUMENT_FX_MAJORS_NZD_USD,
    INSTRUMENT_FX_METALS_XAU_USD,
    INSTRUMENT_FX_METALS_XAG_USD
)

def fetch_and_align_portfolio():
    # 1. Define the 8 pairs mapped to Dukascopy's exact constants
    target_pairs = {
        "EURUSD": INSTRUMENT_FX_MAJORS_EUR_USD,
        "GBPUSD": INSTRUMENT_FX_MAJORS_GBP_USD,
        "USDJPY": INSTRUMENT_FX_MAJORS_USD_JPY,
        "AUDUSD": INSTRUMENT_FX_MAJORS_AUD_USD,
        "USDCAD": INSTRUMENT_FX_MAJORS_USD_CAD,
        "USDCHF": INSTRUMENT_FX_MAJORS_USD_CHF,
        "NZDUSD": INSTRUMENT_FX_MAJORS_NZD_USD,
        "XAUUSD": INSTRUMENT_FX_METALS_XAU_USD,
        "XAGUSD": INSTRUMENT_FX_METALS_XAG_USD
    }

    # Set your historical lookback window 
    start_date = datetime(2021, 1, 1)
    end_date = datetime(2026,8,8)
    
    aligned_df = pd.DataFrame()
    
    print("Starting Dukascopy data pipeline for 8 pairs...")
    
    for sym, instrument in target_pairs.items():
        print(f"Fetching {sym}...")
        
        try:
            # 2. Fetch the hourly data (Bid price)
            df_asset = dp.fetch(
                instrument,
                dp.INTERVAL_HOUR_1,
                dp.OFFER_SIDE_BID,
                start_date,
                end_date
            )
            
            # 3. Clean and standardize the index to UTC
            df_asset.index = pd.to_datetime(df_asset.index, utc=True)
            
            # We only need the 'close' price for statistical cointegration tests
            s_close = df_asset['close'].rename(sym)
            
            # 4. Merge into the master DataFrame
            if aligned_df.empty:
                aligned_df = pd.DataFrame(s_close)
            else:
                # Outer join aligns timestamps perfectly
                aligned_df = aligned_df.join(s_close, how='outer')
                
        except Exception as e:
            # This prevents a single network timeout from crashing the whole script
            print(f"FAILED to fetch {sym}: {e}")
            print("Skipping to next pair...")
            
        # Hardcode a brief pause so Dukascopy doesn't ban your IP for spamming
        time.sleep(2)
            
    # 5. Handle missing data globally after the loop finishes
    print("Forward-filling missing market gaps...")
    aligned_df.ffill(inplace=True)
    aligned_df.dropna(inplace=True) # Drop leading NaNs if start dates differ
    
    print(f"Pipeline complete. Final matrix shape: {aligned_df.shape}")
    return aligned_df

if __name__ == "__main__":
    portfolio_matrix = fetch_and_align_portfolio()
    
    # Save the pristine dataset to disk
    portfolio_matrix.to_csv("aligned_forex_portfolio.csv")
    print("Data saved to aligned_forex_portfolio.csv. Ready for Statsmodels.")