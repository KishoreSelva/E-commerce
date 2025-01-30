from fastapi import FastAPI,Depends,HTTPException,status,Request,Form
from database.database import engine,getdb
from database import models
from database.models import Customer
from routers import login,categories,products,cart
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse,HTMLResponse
from sqlalchemy.orm import Session
from hashing import get_hash_password
from datetime import datetime



app = FastAPI()
models.Base.metadata.create_all(bind=engine)

@app.get('/')
def root():
    return RedirectResponse(url='/register')

@app.get("/register", response_class=HTMLResponse)
def register_form(request: Request):
    try:
        return templates.TemplateResponse("register.html", {"request": request})
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An error occurred while registering the user"
        )
    
@app.post('/register')
def register_user(
    email: str = Form(),
    name: str = Form(),
    password: str = Form(),
    db: Session = Depends(getdb)
):
    try:
        user = db.query(Customer).filter(Customer.email == email).first()

        if user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists"
            )

        new_customer = Customer(
            email=email,
            username=name,
            password=get_hash_password(password),
            created_at=datetime.now()
        )

        db.add(new_customer)
        db.commit()
        db.refresh(new_customer)

        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while registering the user"
        )


templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(login.router)
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(cart.router)


