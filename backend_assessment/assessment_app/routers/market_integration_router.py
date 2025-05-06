from datetime import datetime

from fastapi import APIRouter, Depends, Request

from assessment_app.models.models import Trade
from assessment_app.models.schema import TickData, TickDataRequest, TickDataRangeRequest
from assessment_app.service import market_integration_service

router = APIRouter()


@router.post("/market/data/tick", response_model=TickData)
async def get_market_data_tick(
    tickDataRequest: TickDataRequest
    # stock_symbol: str,
    # current_ts: datetime
) -> TickData:
    """
    Get data for stocks for a given datetime from `data` folder.
    Please note consider price value in TickData to be average of open and close price column value for the timestamp from the data file.
    """
    return market_integration_service.get_tick_data_for_stock(tickDataRequest.stock_symbol, tickDataRequest.current_ts)



@router.post("/market/data/range", response_model=TickData)
async def get_market_data_range(tickDataRangeRequest: TickDataRangeRequest) -> TickData:
    """
    Get data for stocks for a given datetime from `data` folder.
    Please note consider price value in TickData to be average of open and close price column value for the timestamp from the data file.
    """
    return market_integration_service.get_range_data(tickDataRangeRequest.stock_symbol, tickDataRangeRequest.from_ts, tickDataRangeRequest.to_ts)


# @router.post("/market/trade", response_model=Trade)
# async def trade_stock(trade: Trade, current_user_id: str = Depends(get_current_user)) -> Trade:
#     """
#     Only if trade.price is within Open and Close price of that stock on the execution timestamp, then trade should be successful.
#     Trade.price must be average of Open and Close price of that stock on the execution timestamp.
#     Also, update the portfolio and trade history with the trade details and adjust cash and networth appropriately.
#     On every trade, current_ts of portfolio also becomes today.
#     One cannot place trade in date (Trade.execution_ts) older than portfolio.current_ts
#     """
#     pass
