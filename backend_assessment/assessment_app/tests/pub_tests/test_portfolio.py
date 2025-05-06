import pytest
import json
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from assessment_app.main import app
from assessment_app.models.models import *
from datetime import datetime
from assessment_app.tests.pub_tests.test_user_mgmt import hash_password

from assessment_app.database import get_db_session

client = TestClient(app)

user_password = "loginpass"

@pytest.fixture
def create_test_user(db_session: Session):
    user = User(email_id="loginuser@gmail.com", hashed_password= hash_password(user_password), full_name="Test User", created_at=datetime.now())
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user

@pytest.fixture
def get_access_token(db_session: Session, create_test_user):
    user = create_test_user
    response = client.post("/login_user", json={
        "email_id": user.email_id,
        "password": user_password
    })
    assert response.status_code == 200
    assert "access_token" in response.headers["set-cookie"]
    access_token = response.headers["set-cookie"]
    print("access_token: ", access_token)
    return user, access_token


@pytest.fixture
def create_portfolio(db_session: Session, get_access_token):
    _, access_token = get_access_token
    request_headers = {"Cookie": str(access_token)}
    request_payload = {"cash_balance": 120}

    response = client.post(f"/me/portfolio/", json=request_payload, headers=request_headers)
    assert response.status_code == 201
    data = response.json()

    return data

@pytest.fixture
def update_portfolio(db_session: Session, create_portfolio, get_access_token):
    input_data = create_portfolio
    portfolio_id = input_data["id"]
    updated_cash_balance = 1500.00
    _, access_token = get_access_token
    request_headers = {"Cookie": str(access_token)}
    request_payload = {"cash_balance": updated_cash_balance, "status": "active"}

    response = client.put(f"/me/portfolio/{portfolio_id}", json=request_payload, headers=request_headers)
    assert response.status_code == 200
    data = response.json()

    return updated_cash_balance, data


def test_create_portfolio(db_session: Session, create_portfolio, get_access_token):
    user, _ = get_access_token
    data = create_portfolio
    assert "id" in data
    assert data["cash_balance"] == 0.0 #portfolio should always be created with zero balance
    assert data["status"] == "active"
    assert data["user_id"] == user.user_id


def test_update_portfolio_cash_balance(db_session, update_portfolio):
    updated_cash_balance, input_data = update_portfolio
    portfolio_id = input_data["id"]
    assert "id" in input_data
    assert input_data["id"] == portfolio_id
    assert input_data["cash_balance"] == updated_cash_balance

def test_get_portfolio_net_worth(db_session, update_portfolio, get_access_token):
    updated_cash_balance, input_data = update_portfolio
    portfolio_id = input_data["id"]
    user, access_token = get_access_token
    request_headers = {"Cookie": str(access_token)}

    response = client.get(f"/me/portfolio/{portfolio_id}/net-worth", headers=request_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["net_worth"] >= updated_cash_balance

def test_get_portfolio(db_session, update_portfolio, get_access_token):
    updated_cash_balance, input_data = update_portfolio
    portfolio_id = input_data["id"]
    user, access_token = get_access_token
    request_headers = {"Cookie": str(access_token)}

    response = client.get(f"/me/portfolio/{portfolio_id}", headers=request_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] >= portfolio_id
    assert data["user_id"] == user.user_id
    assert data["cash_balance"] == updated_cash_balance
    assert data["status"] == input_data["status"]
