import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from assessment_app.main import app
from assessment_app.models.models import User
from assessment_app.database import get_db_session
import bcrypt

client = TestClient(app)

def hash_password(plain_password: str) -> str:
    return bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def test_register_user(db_session: Session):
    response = client.post("/register_user", json={
        "email_id": "testuser@gmail.com",
        "full_name": "Test User",
        "password": "testpass123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "user_id" in data
    assert data["email_id"] == "testuser@gmail.com"

    # Cleanup
    user = db_session.query(User).filter_by(email_id="testuser@gmail.com").first()
    if user:
        db_session.delete(user)
        db_session.commit()


def test_login_user(db_session: Session):
    # Create test user first
    user = User(
        email_id="azim@gmail.com",
        hashed_password=hash_password("azim123"),
        full_name="Azim",
        created_at=datetime.now()
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    response = client.post("/login_user", json={
        "email_id": "azim@gmail.com",
        "password": "azim123"
    })
    print("test_login_user response:", response, response.json())
    # assert response.status_code == 200
    # data = response.json()
    # assert "access_token" in response.headers["set-cookie"]

    # # Cleanup
    # db_session.delete(user)
    # db_session.commit()
