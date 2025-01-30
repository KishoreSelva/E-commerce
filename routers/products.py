from fastapi import APIRouter,Depends,Request,HTTPException,status
from sqlalchemy.orm import Session
from database.database import getdb
from database.models import Product
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional


router = APIRouter(
    tags=["Products"]
)
templates = Jinja2Templates(directory="templates")

@router.get("/get_products", response_class=HTMLResponse)
def display_products(request: Request,category: Optional[int] = None, db: Session = Depends(getdb)):
    try:
        if category:
            products = db.query(Product).filter(Product.category_id==category).all()
        else:
            products = db.query(Product).all()
        return templates.TemplateResponse("product.html", {"request": request,"products": products,"category":category})
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="category not found"
        )

@router.get("/view_products",response_class=HTMLResponse)
def view_products(request: Request,product_id: int, db: Session = Depends(getdb)):
    try:
        products = db.query(Product).filter(Product.id == product_id).first()
        return templates.TemplateResponse("product_details.html", {"request": request,"products": products})
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    
