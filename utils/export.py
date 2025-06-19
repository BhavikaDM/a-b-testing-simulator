# utils/export.py

import pandas as pd
import io

def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')
