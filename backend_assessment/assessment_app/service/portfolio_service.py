import datetime
from collections import defaultdict
from sqlalchemy.orm import Session
from assessment_app.repository import portfolio_repository, trade_repository
from assessment_app.models.schema import PortfolioCreate, PortfolioUpdate
from assessment_app.models.models import Portfolio, PortfolioStatus, TradeSide
from fastapi import HTTPException, status



# def get_or_create_portfolio(db: Session, user_id: int, portfolio_id: int):
# 	if portfolio_id:
# 		portfolio = portfolio_repository.get_portfolio_by_user_id_and_portfolio_id(db, user_id, portfolio_id)
# 	if portfolio:
# 		return portfolio
#     return portfolio_repository.create_portfolio(db, portfolio)

def create_portfolio(db: Session, user_id: int, portfolio: PortfolioCreate):
	# since we need empty holdings
	emptyPortfolio = Portfolio(user_id=user_id, current_ts=datetime.datetime.now(), status = "active")
	return portfolio_repository.create_portfolio(db, emptyPortfolio)

# def get_portfolio_by_user_id_and_portfolio_id(db: Session, user_id: int, portfolio_id: int):
# 	portfolio = portfolio_repository.get_portfolio_by_user_id_and_portfolio_id(db, user_id, portfolio_id)
# 	return portfolio


def get_portfolio_by_user_id_and_portfolio_id(db: Session, user_id: int, portfolio_id: int):
    portfolio = portfolio_repository.get_portfolio_by_user_id_and_portfolio_id(db, user_id, portfolio_id)
    if not portfolio:
        raise HTTPException(
        	status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio with ID {portfolio_id} not found for user {user_id}"
        )
    return portfolio


def update_portfolio(db: Session, portfolio_id: int, update_data: PortfolioUpdate) -> Portfolio:
    updated_portfolio = portfolio_repository.update_portfolio(db, portfolio_id, update_data)
    if not updated_portfolio:
        raise ValueError(f"Portfolio with id {portfolio_id} not found")
    return updated_portfolio

def calculate_net_worth(db: Session, user_id: int, portfolio_id: int):
    # Get active portfolio for the current user and given portfolio id
	portfolio_status = PortfolioStatus.ACTIVE
	portfolio = portfolio_repository.get_portfolio_by_user_id_and_portfolio_id_and_status(db, user_id, portfolio_id, portfolio_status)
	if not portfolio:
	    raise HTTPException(status_code=404, detail="No Portfolio found")
	
	trades = trade_repository.get_trades_up_to_timestamp(db, portfolio.id, portfolio.current_ts)

	stock_holdings = defaultdict(int)
	for trade in trades:
		if trade.side == TradeSide.BUY:
			stock_holdings[trade.stock_symbol] += trade.qty
		elif trade.side == TradeSide.SELL:
			stock_holdings[trade.stock_symbol] -= trade.qty

	holdings_value = 0.0
	for symbol, quantity in stock_holdings.items():
	    if quantity <= 0:
	        continue
	    # current_price = stock_repository.get_price_at(db, symbol, portfolio.current_ts)
	    current_price = 10
	    holdings_value += quantity * current_price

	return round(portfolio.cash_balance + holdings_value, 2)
