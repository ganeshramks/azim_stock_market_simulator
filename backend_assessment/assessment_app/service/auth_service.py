from sqlalchemy.orm import Session
from assessment_app.models.models import User
import bcrypt
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
import jwt
from fastapi import HTTPException
from typing import Dict
from assessment_app.middleware.auth_middleware import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, decode_access_token


class AuthService:

    @staticmethod
    def hash_password(plain_password: str) -> str:
        return bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

    @staticmethod
    def register_user(db: Session, email_id: str, full_name: str, password: str):
        existing_user = db.query(User).filter(User.email_id == email_id).first()
        if existing_user:
            raise ValueError("User with this email already exists")

        hashed_pwd = AuthService.hash_password(password)
        new_user = User(
            email_id=email_id,
            full_name=full_name,
            hashed_password=hashed_pwd,
            created_at=datetime.utcnow()
        )

        db.add(new_user)
        try:
            db.commit()
            db.refresh(new_user)
        except IntegrityError:
            db.rollback()
            raise ValueError("Failed to create user. Email might already exist.")
        
        return {
            "user_id": new_user.user_id,
            "email_id": new_user.email_id,
            "full_name": new_user.full_name,
            "created_at": new_user.created_at
        }

    @staticmethod
    def login_user(db: Session, email_id: str, password: str):
        user = db.query(User).filter(User.email_id == email_id).first()
        if not user:
            raise ValueError("Invalid credentials")

        if not AuthService.verify_password(password, user.hashed_password):
            raise ValueError("Invalid credentials")

        return {
            "user_id": user.user_id,
            "email_id": user.email_id,
            "full_name": user.full_name
        }
