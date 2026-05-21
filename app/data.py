"""
Dataset Loading Utilities
"""
import pandas as pd

def load_dataset(data_path):
    try:
        if data_path.endswith('.zip'):
            df = pd.read_csv(data_path, compression='zip')
        else:
            df = pd.read_csv(data_path)
        return df
    except Exception as e:
        print(f"Error loading dataset: {str(e)}")
        return None
