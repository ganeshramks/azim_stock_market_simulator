import pandas as pd
from datetime import datetime
import os
from fastapi import HTTPException
from collections import defaultdict
from sqlalchemy.orm import Session
from assessment_app.models.constants import DATA_FOLDER
from assessment_app.models.models import TradeSide, PortfolioStatus
from assessment_app.repository import trade_repository, portfolio_repository
from assessment_app.service import market_integration_service


def compute_cagr(initial_value: float, final_value: float, start_date: datetime, end_date: datetime) -> float:
    years = (end_date - start_date).days / 365.25
    if initial_value <= 0 or years <= 0:
        return 0.0
    cagr = ((final_value / initial_value) ** (1 / years)) - 1
    return round(cagr * 100, 2)  # return as percentage


def get_stock_cagr(stock_symbol: str, start_ts: datetime, end_ts: datetime) -> float:
    print("Inside get_stock_cagr: ", stock_symbol, start_ts, end_ts)
    
    file_path = os.path.join(DATA_FOLDER, f"{stock_symbol.upper()}.csv")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Stock data file not found")

    df = pd.read_csv(file_path, parse_dates=["Date"])
    df = df.sort_values(by="Date")

    df_range = df[(df["Date"] >= start_ts) & (df["Date"] <= end_ts)]

    if df_range.empty:
        raise ValueError("No data found in the given date range.")

    start_row = df_range.iloc[0]
    end_row = df_range.iloc[-1]

    # Use average of Open and Close prices
    initial_value = (start_row["Open"] + start_row["Close"]) / 2
    final_value = (end_row["Open"] + end_row["Close"]) / 2

    stock_cagr = compute_cagr(initial_value, final_value, start_ts, end_ts)

    print("stock_cagr:", stock_cagr)

    return stock_cagr


def estimate_portfolio_cagr(user_id: int, db: Session, start_ts: datetime, end_ts: datetime) -> float:
    
    portfolio_status = PortfolioStatus.ACTIVE
    portfolio = portfolio_repository.get_portfolio_by_user_id_and_portfolio_status(db, user_id, portfolio_status)
    if not portfolio:
        raise HTTPException(status_code=404, detail="No Portfolio found")

    trades = trade_repository.get_trades_by_portfolio_id(db, portfolio.id)
    print(portfolio.id, trades)

    holdings = defaultdict(int)
    for trade in trades:
        if trade.execution_ts > end_ts:
            continue
        if trade.side == TradeSide.BUY:
            holdings[trade.stock_symbol] += trade.qty
        elif trade.side == TradeSide.SELL:
            holdings[trade.stock_symbol] -= trade.qty

    value_start = 0.0
    value_end = 0.0

    print(holdings.items())

    for symbol, qty in holdings.items():
        if qty <= 0:
            continue
        try:
            tick_start = market_integration_service.get_tick_data_for_stock(symbol, start_ts)
            tick_end = market_integration_service.get_tick_data_for_stock(symbol, end_ts)
        except FileNotFoundError:
            continue

        value_start += tick_start.price * qty
        value_end += tick_end.price * qty
        print("value_start:", value_start, "value_end:", value_end)

    # Add cash balance if it existed at start time
    value_start += portfolio.cash_balance
    value_end += portfolio.cash_balance

    print("value_start:", value_start, "value_end:", value_end)

    return compute_cagr(value_start, value_end, start_ts, end_ts)

