from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse

from assessment_app.database import get_db_session
from assessment_app.service import trade_service
from assessment_app.models.schema import TradeCreate, TradeOut


router = APIRouter(prefix="/me/trade", tags=["Trade"])


@router.post("/place", response_model=TradeOut, status_code=status.HTTP_201_CREATED)
def place_trade(
    trade_data: TradeCreate,
    request: Request,
    db: Session = Depends(get_db_session)
):
    try:
    	user_id = getattr(request.state, "user_id", None)
    	trade = trade_service.place_trade(db, user_id, trade_data)
    	return trade
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})

