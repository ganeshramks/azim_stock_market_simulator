from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from assessment_app.models.models import Trade, Portfolio, StockPrice


def update_portfolio_balance(db: Session, portfolio: Portfolio, new_balance: float):
    portfolio.cash_balance = new_balance
    db.commit()
    db.refresh(portfolio)

def create_trade(db: Session, trade: Trade):
	print("Inside create_trade")
	db.add(trade)
	db.commit()
	db.refresh(trade)
	return trade

def get_trade_qty(db: Session, portfolio_id: int, stock_symbol: str, tradeSide: str):
	qty = db.query(func.sum(Trade.qty)).filter_by(
	    portfolio_id=portfolio_id,
	    stock_symbol=stock_symbol,
	    side=tradeSide
	).scalar() or 0
	return qty



def get_trades_up_to_timestamp(db: Session, portfolio_id: int, execution_ts: datetime):
	print("Insdie get_trades_up_to_timestamp")
	return (
		db.query(Trade)
		.filter(
			Trade.portfolio_id == portfolio_id,
			Trade.execution_ts <= execution_ts
		).all()
	)


def get_trades_by_portfolio_id(db: Session, portfolio_id: int):
	print("Insdie get_trades_by_portfolio_id")
	return (
		db.query(Trade)
		.filter(
			Trade.portfolio_id == portfolio_id
		).all()
	)
