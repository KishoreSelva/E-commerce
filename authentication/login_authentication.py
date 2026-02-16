from typing import Union
from datetime import datetime,timedelta,timezone
from jose import JWTError
import jwt
from fastapi.security import HTTPBasic,HTTPBearer,HTTPBasicCredentials
from fastapi import Depends,HTTPException,status
from schemas.schema import TokenData
from database.database import getdb
from sqlalchemy.orm import Session
from database.models import Customer
from hashing import verify_password
from config import settings


security = HTTPBasic()

token_auth_scheme = HTTPBearer()

EXPIRE_TIME = 120 #in mins

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str =  Depends(token_auth_scheme) , db: Session = Depends(getdb)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        return credentials_exception 
    user = db.query(Customer).filter(Customer.username == token_data.username).first()

    if user is None:
        raise credentials_exception
    return user

def authenticate_user(
    credentials: HTTPBasicCredentials = Depends(security),
    db: Session = Depends(getdb),
):
    email = credentials.username
    password = credentials.password
    user = db.query(
        Customer.id,
        Customer.email,
        Customer.username,
        Customer.password).filter(Customer.email == email).first()

    if user:
        if verify_password(password, user.password):
            return user
        else:
            message = "Invalid password"
    else:
        message = "Invalid email"
        
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=message)

