from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime
from assessment_app.models.models import PortfolioStatus


class RegisterUserRequest(BaseModel):
    email_id: str
    full_name: str
    password: str

class LoginUserRequest(BaseModel):
    email_id: str
    password: str

class UserResponse(BaseModel):
    user_id: int
    email_id: str
    full_name: str
    created_at: datetime

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),  # 👈 important fix
        }

class UserLoginResponse(BaseModel):
    user_id: int
    email_id: str
    full_name: str

    class Config:
        orm_mode = True


class TradeCreate(BaseModel):
    stock_symbol: str = Field(..., example="AAPL")
    qty: int = Field(..., gt=0, example=10)
    side: Literal["BUY", "SELL"] = Field(..., example="BUY")
    portfolio_id: int = Field(..., gt=0, example=10)
    price: float = Field(..., gt=0.0, example=10.01)
    execution_ts: datetime = Field(..., example="2024-04-29T00:00:00")


class TradeOut(BaseModel):
    id: int
    portfolio_id: int
    stock_symbol: str
    qty: int
    price: float
    side: str
    execution_ts: datetime

    class Config:
        orm_mode = True


class PortfolioCreate(BaseModel):
    cash_balance: float
    # current_ts: datetime #this can be calculated dynamically in BE

class PortfolioOut(BaseModel):
    id: int
    user_id: int
    cash_balance: float
    current_ts: datetime
    status: str

class PortfolioUpdate(BaseModel):
    cash_balance: Optional[float]
    # current_ts: Optional[datetime]
    status: Optional[PortfolioStatus]



class TickData(BaseModel):
    stock_symbol: str = Field(..., example="HDFCBANK")
    current_ts: datetime = Field(..., example="2024-04-29T00:00:00")
    price: float = Field(..., example=1500.75)

    class Config:
        orm_mode = True

class TickDataRequest(BaseModel):
    stock_symbol: str = Field(..., example="AAPL")
    current_ts: datetime = Field(..., example="2024-04-29T00:00:00")

class TickDataRangeRequest(BaseModel):
    stock_symbol: str = Field(..., example="AAPL")
    from_ts: datetime = Field(..., example="2024-04-29T00:00:00")
    to_ts: datetime = Field(..., example="2024-04-29T00:00:00")


