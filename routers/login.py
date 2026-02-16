from fastapi import APIRouter,Depends,HTTPException,status,Request,Form
from sqlalchemy.orm import Session
from database.database import getdb
from database.models import Customer
from datetime import timedelta
from hashing import verify_password
from constants import constant
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from authentication.login_authentication import create_access_token
from fastapi.responses import JSONResponse


router = APIRouter(
    tags=["Authentication"]
)

templates = Jinja2Templates(directory="templates")

@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    try:
        return templates.TemplateResponse("login.html", {"request": request})
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An error occurred while login"
        )

@router.post('/login')
def login(
    email: str = Form(),
    password: str = Form(),
    db: Session = Depends(getdb)
):
    try:
        user = db.query(Customer).filter(Customer.email == email).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid email"
            )

        if not verify_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Incorrect password"
            )
        access_token_expires = timedelta(minutes=constant.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username,"user_id":user.id}, expires_delta=access_token_expires
        )

        response = JSONResponse(content={"user_id":user.id,"user_name":user.username, "token": access_token})
        return response

        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while logging in"
        )
    

