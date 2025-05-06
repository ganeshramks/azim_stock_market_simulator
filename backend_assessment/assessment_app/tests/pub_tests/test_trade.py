import pytest
import json
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from assessment_app.main import app
from assessment_app.models.models import *
from datetime import datetime
from assessment_app.tests.pub_tests.test_portfolio import *

from assessment_app.database import get_db_session

client = TestClient(app)


@pytest.fixture
def place_trade(db_session: Session, update_portfolio, get_access_token):
    updated_cash_balance, portfolio_data = update_portfolio
    portfolio_id = portfolio_data["id"]
    user, access_token = get_access_token
    
    request_headers = {"Cookie": str(access_token)}
    
    request_payload = {
        "stock_symbol": "ICICIBANK",
        "qty": 1,
        "side": "BUY",
        "portfolio_id": portfolio_id,
        "price": 1242.60,
        "execution_ts": "2025-07-18T00:00:00"
    }

    assert request_payload["qty"]*request_payload["price"] <= portfolio_data["cash_balance"]

    response = client.post(f"/me/trade/place", json=request_payload, headers=request_headers)
    assert response.status_code == 201
    trade_data = response.json()

    return portfolio_data, trade_data

def test_place_trade(db_session, place_trade):
    portfolio_data, trade_data = place_trade
    portfolio_id = portfolio_data["id"]

    assert trade_data["portfolio_id"] == portfolio_data["id"]
    assert trade_data["execution_ts"] >= portfolio_data["current_ts"]
    # assert trade_data["user_id"] == portfolio_data["user_id"]