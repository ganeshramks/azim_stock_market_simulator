from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from assessment_app.models import schema
from assessment_app.service.auth_service import AuthService, create_access_token
from assessment_app.database import get_db_session



router = APIRouter()

@router.post("/register_user", response_model=schema.UserResponse)
def register_user(user: schema.RegisterUserRequest, db: Session = Depends(get_db_session)):
    try:
        created_user = AuthService.register_user(
            db=db,
            email_id=user.email_id,
            full_name=user.full_name,
            password=user.password
        )
        return created_user
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"Exception during registration: {e}")
        raise HTTPException(status_code=500, detail="Something went wrong during registration")


@router.post("/login_user", response_model=schema.UserLoginResponse)
def login_user(user: schema.LoginUserRequest, db: Session = Depends(get_db_session)):
    try:
        logged_in_user = AuthService.login_user(
            db=db,
            email_id=user.email_id,
            password=user.password
        )
        if logged_in_user["user_id"]:
            token_data = {
                "user_id": logged_in_user["user_id"],
                "email": logged_in_user["email_id"]
            }
            access_token = create_access_token(token_data)

            # Prepare the response JSON
            response_body = {
                "user_id": logged_in_user["user_id"],
                "email_id": logged_in_user["email_id"],
                "full_name": logged_in_user["full_name"]
            }

            # Create a JSONResponse directly
            response = JSONResponse(content=response_body)

            # Set cookie
            response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                secure=False,  # Set to True if running with HTTPS
                samesite="lax",
                max_age=1800,
                expires=1800,
            )

            return response
        else:
            raise HTTPException(status_code=400, detail="Invalid credentials")
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"Router Exception in login_user: {e}")
        raise HTTPException(status_code=500, detail="Something went wrong during login")
