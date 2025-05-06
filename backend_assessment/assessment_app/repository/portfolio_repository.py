from sqlalchemy.orm import Session
from assessment_app.models.models import Portfolio
from assessment_app.models.schema import PortfolioUpdate


def get_portfolio_by_user_id(db: Session, user_id: int):
    return db.query(Portfolio).filter(Portfolio.user_id == user_id).first()

def get_portfolio_by_user_id_and_portfolio_status(db: Session, user_id: int, portfolio_status: str):
    return db.query(Portfolio).filter(Portfolio.user_id == user_id).filter(Portfolio.status == portfolio_status).first()

def get_portfolio_by_user_id_and_portfolio_id(db: Session, user_id: int, portfolio_id: int):
	return db.query(Portfolio).filter(Portfolio.user_id == user_id).filter(Portfolio.id == portfolio_id).first()

def get_portfolio_by_user_id_and_portfolio_id_and_status(db: Session, user_id: int, portfolio_id: int, portfolio_status: str):
	return db.query(Portfolio).filter(Portfolio.user_id == user_id).filter(Portfolio.id == portfolio_id).filter(Portfolio.status == portfolio_status).first()


def create_portfolio(db: Session, portfolio: Portfolio):
    # portfolio = Portfolio(user_id=user_id)
    db.add(portfolio)
    db.commit()
    db.refresh(portfolio)
    return portfolio


def update_portfolio(db: Session, portfolio_id: int, update_data: PortfolioUpdate) -> Portfolio:
	print("inside update_portfolio", " db type:", type(db), "update_data type", type(update_data), "portfolio_id type", type(portfolio_id))
	portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
	if not portfolio:
		return None  # Or raise an exception as appropriate

	for key, value in update_data.dict(exclude_unset=True).items():
		setattr(portfolio, key, value)
	
	db.commit()
	db.refresh(portfolio)
	return portfolio

def direct_update_portfolio(db: Session, portfolio: Portfolio):
	print("inside direct_update_portfolio", " db type:", type(db), "portfolio type", type(portfolio))
	db.add(portfolio)
	db.commit()
	db.refresh(portfolio)
	return portfolio