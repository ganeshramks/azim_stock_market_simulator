import os
import pandas as pd
from datetime import datetime
from fastapi import HTTPException
from assessment_app.models.schema import TickData

DATA_FOLDER = "../data"


def get_tick_data_for_stock(stock_symbol: str, current_ts: datetime) -> TickData:
    """
    Returns TickData with average of Open and Close for the stock at current_ts date.
    """
    file_path = os.path.join(DATA_FOLDER, f"{stock_symbol.upper()}.csv")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Stock data file not found")

    df = pd.read_csv(file_path, parse_dates=["Date"])

    # Normalize the datetime to just date
    target_date = current_ts.date()
    row = df[df["Date"].dt.date == target_date]

    if row.empty:
        raise HTTPException(status_code=404, detail="Data for the given date not found")

    row = row.iloc[0]
    average_price = (row["Open"] + row["Close"]) / 2

    return TickData(
        stock_symbol=stock_symbol.upper(),
        timestamp=datetime.combine(target_date, datetime.min.time()),
        price=average_price
    )
