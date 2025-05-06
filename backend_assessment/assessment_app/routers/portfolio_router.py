from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from assessment_app.database import get_db_session
from assessment_app.service import portfolio_service
from assessment_app.models.schema import PortfolioCreate, PortfolioOut, PortfolioUpdate

router = APIRouter(prefix="/me/portfolio", tags=["Portfolio"])

# @router.get("/")
# def get_portfolio(request: Request, db: Session = Depends(get_db)):
#     user_id = request.state.user_id
#     if not user_id:
#         raise HTTPException(status_code=401, detail="Unauthorized")
#     portfolio = portfolio_service.get_or_create_portfolio(db, user_id)
#     return {
#         "user_id": portfolio.user_id,
#         "cash_balance": portfolio.cash_balance,
#         "current_ts": portfolio.current_ts,
#         "id": portfolio.id,
#     }


@router.post("/", response_model=PortfolioOut, status_code=status.HTTP_201_CREATED)
def create_portfolio(portfolio_request: PortfolioCreate, request: Request, db: Session = Depends(get_db_session)):
    print("Inside create_portfolio router")
    """
    Create a new portfolio and initialise with funds with empty holdings.
    """
    try:
        user_id = getattr(request.state, "user_id", None)
        newPortfolio = portfolio_service.create_portfolio(db, user_id, portfolio_request)
        return newPortfolio
    except Exception as e:
        print(f"caught Exception: {e}")
        return JSONResponse(status_code=500, content={"detail": str(e)})

    pass



@router.get("/{portfolio_id}", response_model=PortfolioOut, status_code=status.HTTP_200_OK)
async def get_portfolio_by_id(
    portfolio_id: str,
    request: Request,
    db: Session = Depends(get_db_session)
):
    """
    Get specified portfolio for the current user.
    """
    user_id = getattr(request.state, "user_id", None)
    return portfolio_service.get_portfolio_by_user_id_and_portfolio_id(
        db, user_id, int(portfolio_id)
    )

@router.put("/{portfolio_id}", response_model=PortfolioOut)
async def update_portfolio(
    portfolio_id: int,
    update_data: PortfolioUpdate,
    request: Request,
    db: Session = Depends(get_db_session)
):
    user_id = getattr(request.state, "user_id", None)
    try:
        existing_portfolio = portfolio_service.get_portfolio_by_user_id_and_portfolio_id(db, user_id, portfolio_id)
        if not existing_portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")

        updated_portfolio = portfolio_service.update_portfolio(db, portfolio_id, update_data)
        return updated_portfolio

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# @router.delete("/portfolio/{portfolio_id}", response_model=PortfolioOut) -> this is already handled
# async def get_portfolio_by_id(
#     portfolio_id: str,
#     request: Request,
#     db: Session = Depends(get_db_session)
# ):
#     """
#     Delete the specified portfolio for the current user.
#     """
#     pass


@router.get("/{portfolio_id}/net-worth")
async def get_net_worth(portfolio_id: str, request: Request, db: Session = Depends(get_db_session)):
    """
    Get net-worth from portfolio (holdings value and cash) at current_ts field in portfolio.

    To compute the net worth of a portfolio at current_ts, we’ll combine:
    1. Cash balance (from the cash_balance field in Portfolio)
    2. Holdings value = sum of (stock_price at current_ts × quantity held) for each stock.
    """

    user_id = getattr(request.state, "user_id", None)
    net_worth = portfolio_service.calculate_net_worth(db, user_id, portfolio_id)

    return {"net_worth": net_worth}

    pass