import pandas as pd
from pathlib import Path
from src.core.state import SalesState


def data_loader_node(state: SalesState) -> dict:
    #1.读取csv文件
    csv_path = Path(__file__).parent.parent.parent / "data"/ "raw" / "sales.csv"
    df = pd.read_csv(csv_path)
    #2.限定读取内容
    return {
        "columns": df.columns.tolist(),
        "data_sample": df.head(5).to_string()
    }
