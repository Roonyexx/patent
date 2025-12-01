from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import os
from dotenv import load_dotenv
from jose import JWTError, jwt
import bcrypt
from pydantic import BaseModel

load_dotenv()


SECRET_KEY = os.getenv("SECRET_KEY", "oleg")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 600))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))


class TokenData(BaseModel):
    user_id: int
    username: str
    user_type: str  # employee или author
    position_name: Optional[str] = None
    employee_id: Optional[int] = None
    author_id: Optional[int] = None
    exp: Optional[datetime] = None


def hash_password(password: str) -> str:
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password_bytes, salt).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        password_bytes = plain_password.encode('utf-8')[:72]
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False


def create_access_token(
    user_id: int,
    username: str,
    user_type: str,
    position_name: Optional[str] = None,
    employee_id: Optional[int] = None,
    author_id: Optional[int] = None,
    expires_delta: Optional[timedelta] = None
) -> str:
    to_encode: Dict[str, Any] = {
        "user_id": user_id,
        "username": username,
        "user_type": user_type,
        "position_name": position_name,
        "employee_id": employee_id,
        "author_id": author_id,
    }
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(user_id: int, username: str) -> str:
    to_encode = {
        "user_id": user_id,
        "username": username,
        "type": "refresh"
    }
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[TokenData]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        username: str = payload.get("username")
        user_type: str = payload.get("user_type")
        position_name: Optional[str] = payload.get("position_name")
        employee_id: Optional[int] = payload.get("employee_id")
        author_id: Optional[int] = payload.get("author_id")
        exp = payload.get("exp")

        if user_id is None or username is None:
            return None

        return TokenData(
            user_id=user_id,
            username=username,
            user_type=user_type,
            position_name=position_name,
            employee_id=employee_id,
            author_id=author_id,
            exp=datetime.utcfromtimestamp(exp) if isinstance(exp, (int, float)) else exp
        )
    except JWTError:
        return None


def extract_token_from_header(authorization: Optional[str]) -> Optional[str]:
    if not authorization:
        return None
    
    parts = authorization.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return None
