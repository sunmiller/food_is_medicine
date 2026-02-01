import pandas as pd
from pathlib import Path

def load_dataframe():
    # Get the directory where this script is located
    current_dir = Path(__file__).parent
    csv_path = current_dir / "pred_food.csv"
    df = pd.read_csv(csv_path)
    return df

df = load_dataframe()
