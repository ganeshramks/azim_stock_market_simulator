import uuid

from datetime import datetime
from typing import List
import enum

from pydantic import BaseModel

from assessment_app.models.constants import TradeType

from assessment_app.database import Base
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    email_id = Column(String(255), unique=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False)

    portfolios = relationship("Portfolio", back_populates="user", lazy='selectin')


# Enum for trade side
class TradeSide(enum.Enum):
    BUY = "buy"
    SELL = "sell"

class PortfolioStatus(enum.Enum):
    ACTIVE = "active"
    DELETED = "deleted"



class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    cash_balance = Column(Float, default=0.0)  # NEW
    current_ts = Column(DateTime, default=datetime.utcnow)  # NEW
    status = Column(Enum(PortfolioStatus), nullable=False)

    user = relationship("User", back_populates="portfolios")
    trades = relationship("Trade", back_populates="portfolio")


class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    stock_symbol = Column(String(10), nullable=False)
    qty = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    side = Column(Enum(TradeSide), nullable=False)
    execution_ts = Column(DateTime, nullable=False)

    portfolio = relationship("Portfolio", back_populates="trades")


class StockPrice(Base):
    __tablename__ = "stock_prices"

    id = Column(Integer, primary_key=True, index=True)
    stock_symbol = Column(String(10), index=True, nullable=False)
    price = Column(Float, nullable=False)
    timestamp = Column(DateTime, index=True, nullable=False)

