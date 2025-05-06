import os
import pandas as pd
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime
from assessment_app.models.models import Trade, TradeSide, PortfolioStatus
from assessment_app.models.schema import TradeCreate, PortfolioUpdate
from assessment_app.repository import trade_repository, portfolio_repository
from assessment_app.models.constants import DATA_FOLDER


DATA_FOLDER = "assessment_app/data"

def place_trade(db: Session, user_id: int, trade_data: TradeCreate):

    '''
        Only if trade.price is within Open and Close price of that stock on the execution timestamp, then trade should be successful.
        Trade.price must be average of Open and Close price of that stock on the execution timestamp.
        Also, update the portfolio and trade history with the trade details and adjust cash and networth appropriately.
        On every trade, current_ts of portfolio also becomes today.
        One cannot place trade in date (Trade.execution_ts) older than portfolio.current_ts
    '''
    
    try:
        print("Inside place_trade trade_data:", trade_data, "db type:", type(db))

        file_path = os.path.join(DATA_FOLDER, f"{trade_data.stock_symbol.upper()}.csv")
        if not os.path.exists(file_path):
           raise HTTPException(status_code=404, detail="Stock data file not found")

        df = pd.read_csv(file_path, parse_dates=["Date"])

        tick_row = df[df["Date"] == trade_data.execution_ts]

        if tick_row.empty:
            raise HTTPException(status_code=400, detail="No market data available for the given execution timestamp")

        row = tick_row.iloc[0]
        open_price, close_price = row["Open"], row["Close"]
        expected_price = round((open_price + close_price) / 2, 2)

        # Validation
        if not (min(open_price, close_price) <= trade_data.price <= max(open_price, close_price)):
            raise HTTPException(status_code=400, detail="Trade price out of bounds for Open/Close")

        if round(trade_data.price, 2) != expected_price:
            raise HTTPException(status_code=400, detail="Trade price must equal average of Open and Close")

        portfolio_id_req = int(trade_data.portfolio_id)
        # Get an active portfolio for the current user and given portfolio id
        portfolio_status = PortfolioStatus.ACTIVE
        portfolio = portfolio_repository.get_portfolio_by_user_id_and_portfolio_id_and_status(db, user_id, portfolio_id_req, portfolio_status)
        if not portfolio:
            raise HTTPException(status_code=404, detail="No Portfolio found")

        if trade_data.execution_ts < portfolio.current_ts:
            raise HTTPException(status_code=400, detail="Cannot place trade with older execution timestamp than portfolio")

        
        trade_amount = trade_data.qty * trade_data.price

        # Check cash balance for BUY
        if trade_data.side.lower() == TradeSide.BUY.value and portfolio.cash_balance < trade_amount:
            print("Insufficient balance")
            raise HTTPException(status_code=400, detail="Insufficient balance")

        # Checks for trade sell
        # Verify quantity held ≥ quantity being sold.
        if trade_data.side.lower() == TradeSide.SELL.value:
            total_bought = trade_repository.get_trade_qty(db, portfolio_id_req, trade_data.stock_symbol, TradeSide.BUY)
            total_sold = trade_repository.get_trade_qty(db, portfolio_id_req, trade_data.stock_symbol, TradeSide.SELL)

            net_qty = total_bought - total_sold

            if net_qty < trade_data.qty:
                err_msg = "Insufficient holdings to sell" + str(net_qty)
                print("Place Trade error: ", err_msg)
                raise ValueError(err_msg)

        # Adjust portfolio balance
        if trade_data.side.lower() == TradeSide.BUY.value:
            portfolio.cash_balance -= trade_amount
        else:  # SELL
            portfolio.cash_balance += trade_amount

        trade = Trade(
            portfolio_id=portfolio.id,
            stock_symbol=trade_data.stock_symbol,
            qty=trade_data.qty,
            price=trade_data.price,
            side=trade_data.side,
            execution_ts=datetime.utcnow(),
        )

        portfolio.current_ts=datetime.utcnow()
        
        # Save updates
        # the create trade and update portfolio should be in a single db txn
        db.add(trade)
        db.add(portfolio)
        db.commit()  # commit both changes
        db.refresh(trade)
        return trade
    except Exception as e:
        print(f"Exception in creating trade: {e}")
        db.rollback()
        raise e  # re-raise to handle further up
        return None

