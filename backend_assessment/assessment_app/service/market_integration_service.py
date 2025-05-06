import os
import pandas as pd
from datetime import datetime
from fastapi import HTTPException
from assessment_app.models.schema import TickData
from assessment_app.models.constants import DATA_FOLDER


def get_tick_data_for_stock(stock_symbol: str, current_ts: datetime) -> TickData:
    """
    Returns TickData with average of Open and Close for the stock at current_ts date.
    """
    print("Inside get_tick_data_for_stock", stock_symbol, current_ts)
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

    print("average_price:", average_price)

    return TickData(
        stock_symbol=stock_symbol.upper(),
        current_ts=datetime.combine(target_date, datetime.min.time()),
        price=average_price
    )


def get_range_data(stock_symbol: str, from_ts: datetime, to_ts: datetime) -> TickData:

    file_path = os.path.join(DATA_FOLDER, f"{stock_symbol.upper()}.csv")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Stock data file not found")

    df = pd.read_csv(file_path, parse_dates=["Date"])
    df = df[(df["Date"] >= from_ts) & (df["Date"] <= to_ts)]

    if df.empty:
        # raise ValueError(f"No data found for {stock_symbol} in the given date range.")
        raise HTTPException(status_code=404, detail="Data for the given date range not found")

    # Compute average of (Open + Close) for each row
    df["AvgPrice"] = (df["Open"] + df["Close"]) / 2

    # Compute mean price across range
    avg_price = df["AvgPrice"].mean()

    # Return using the `to_ts` as the current_ts reference
    return TickData(
        stock_symbol=stock_symbol,
        current_ts=to_ts,
        price=avg_price
    )