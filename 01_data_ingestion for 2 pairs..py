import pandas as pd
from datetime import datetime, timedelta
import dukascopy_python as dp
from dukascopy_python.instruments import INSTRUMENT_FX_MAJORS_EUR_USD, INSTRUMENT_FX_MAJORS_GBP_USD

def get_test_data():
    # Corrected Thesis: Commodity-linked neighboring economies
    pairs = {
        "EURUSD": INSTRUMENT_FX_MAJORS_EUR_USD,
        "GBPUSD": INSTRUMENT_FX_MAJORS_GBP_USD
    }
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=720)#xpanded to 1 year for statistically valid testing
    
    aligned_df = pd.DataFrame()
    
    print("Starting data download...")
    
    for sym, instrument in pairs.items():
        print(f"Fetching {sym} hourly data...")
        df = dp.fetch(
            instrument,
            dp.INTERVAL_HOUR_1,
            dp.OFFER_SIDE_BID,
            start_date,
            end_date
        )
        
        df.index = pd.to_datetime(df.index, utc=True)
        s_close = df['close'].rename(sym)
        
        if aligned_df.empty:
            aligned_df = pd.DataFrame(s_close)
        else:
            aligned_df = aligned_df.join(s_close, how='outer')
            
    print("Aligning timestamps and filling gaps...")
    aligned_df.ffill(inplace=True)
    aligned_df.dropna(inplace=True)
    
    return aligned_df

if __name__ == "__main__":
    try:
        df = get_test_data()
        df.to_csv("test_data.csv")
        print(f"\nSUCCESS! test_data.csv generated with {len(df)} rows.")
    except Exception as e:
        print(f"\nERROR: {e}")