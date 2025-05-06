from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from jose import jwt, JWTError, ExpiredSignatureError
from datetime import datetime, timedelta
from typing import Dict


SECRET_KEY = "azim_secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 300

def create_access_token(data: Dict) -> str:
    """
    Creates a JWT access token.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        print(f"Error encoding JWT: {str(e)}")
        raise HTTPException(status_code=500, detail="Error creating access token")


def decode_access_token(token: str) -> Dict:
    """
    Decodes a JWT access token.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/me"):
            try:
                cookie_header = request.headers.get("cookie")
                access_token = None

                if cookie_header:
                    for item in cookie_header.split(';'):
                        key, sep, value = item.strip().partition('=')
                        if key == "access_token":
                            access_token = value
                            break

                if not access_token:
                    return JSONResponse(
                        status_code=401,
                        content={"detail": "Unauthorized: Missing access token"}
                    )

                payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
                print("AuthMiddleware: payload:", payload)
                exp = payload.get("exp")
                if not exp or datetime.utcfromtimestamp(exp) < datetime.utcnow():
                    return JSONResponse(
                        status_code=401,
                        content={"detail": "Unauthorized: Token expired"}
                    )

                request.state.user_id = payload.get("user_id")
                request.state.email_id = payload.get("email_id")

            except jwt.ExpiredSignatureError:
                return JSONResponse(status_code=401, content={"detail": "Token expired"})
            except JWTError:
                return JSONResponse(status_code=401, content={"detail": "Invalid token"})
            except Exception as e:
                return JSONResponse(status_code=500, content={"detail": f"Middleware error: {str(e)}"})

        response = await call_next(request)
        return response
