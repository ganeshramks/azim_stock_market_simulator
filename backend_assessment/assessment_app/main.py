from fastapi import FastAPI
from assessment_app.middleware.auth_middleware import AuthMiddleware
from assessment_app.routers.user_mgmt import router as user_mgmt_router
from assessment_app.routers import trade_router
from assessment_app.routers import portfolio_router
from assessment_app.routers import market_integration_router
from assessment_app.routers import analysis_router

# from assessment_app.routers.strategy import router as strategy_router
# from assessment_app.routers.market_integration import router as market_router
# from assessment_app.routers.analysis import router as analysis_router
# from assessment_app.routers.backtest import router as backtest_router
from assessment_app.routers import me_routes


app = FastAPI()

# Add the AuthMiddleware
app.add_middleware(AuthMiddleware)


app.include_router(user_mgmt_router, prefix="", tags=["user_mgmt"])
app.include_router(trade_router.router)
app.include_router(portfolio_router.router)
app.include_router(market_integration_router.router)
app.include_router(analysis_router.router)

# app.include_router(strategy_router, prefix="", tags=["strategy"])
# app.include_router(market_router, prefix="", tags=["market_data"])
# app.include_router(analysis_router, prefix="", tags=["analysis"])
# app.include_router(backtest_router, prefix="", tags=["backtest"])
# comment
app.include_router(me_routes.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Stock Simulator"}
