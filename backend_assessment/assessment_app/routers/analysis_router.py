from datetime import datetime

from fastapi import Depends, APIRouter, Query, HTTPException, Request
from sqlalchemy.orm import Session

from assessment_app.models.constants import StockSymbols
from assessment_app.service import analysis_service
from assessment_app.database import get_db_session

router = APIRouter()


@router.get("/analysis/estimate_returns/stock", response_model=float)
async def get_stock_analysis(stock_symbol: str, start_ts: datetime = Query(..., description="Start timestamp"),end_ts: datetime = Query(..., description="End timestamp")
) -> float:
    """
    Estimate returns for given stock based on stock prices between the given timestamps.
    Use compute_cagr method.
    Example:
        200% CAGR would mean your returned value would be 200 for the duration.
        5% CAGR would mean your returned value would be 5 for the duration.
    """
    try:
        return analysis_service.get_stock_cagr(stock_symbol, start_ts, end_ts)
    except (FileNotFoundError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/me/analysis/estimate_returns/portfolio")
async def estimate_portfolio_returns(start_ts: datetime, end_ts: datetime, request: Request, db: Session = Depends(get_db_session)):
    """
    Estimate returns for the current portfolio based on stock prices between the given timestamps.
    Use compute_cagr method.
    Example:
        100% CAGR would mean your returned value would be 2.0 for the duration
        5% CAGR would mean your returned value would be 1.05 for the duration
    """
    user_id = getattr(request.state, "user_id", None)
    cagr = analysis_service.estimate_portfolio_cagr(user_id, db, start_ts, end_ts)
    print("cagr:", cagr)
    return {"cagr_multiplier": cagr}