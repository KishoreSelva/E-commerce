from fastapi import APIRouter,Depends,status,HTTPException,Request
from sqlalchemy.orm import Session
from typing import List
from database.database import getdb
from database.models import Category,Product
from schemas.schema import CategoryCreate
from datetime import datetime
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from authentication.login_authentication import authenticate_user,get_current_user

router = APIRouter(
    tags=["Categories"]
)

templates = Jinja2Templates(directory="templates")

@router.get("/get_categories",response_class=HTMLResponse)
async def display_category(request: Request, new_user = Depends(authenticate_user), db: Session = Depends(getdb)):
    try:
        categories = db.query(Category).all()
        return templates.TemplateResponse("category.html", {"request": request,"categories": categories,"user":new_user})
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"An error occured while fetching the Categories"}
        )

@router.post('/create_category')
def create_category(payload: CategoryCreate, db: Session = Depends(getdb)):
    
    try:
        user = db.query(Category).filter(Category.name == payload.name).first()

        if user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Category already exists"
            )

        new_category = Category(
            name = payload.name,
            description = payload.description,
            created_at=datetime.now()
        )
        
        db.add(new_category)
        db.commit()
        db.refresh(new_category)

        return RedirectResponse(url="/get_products", status_code=status.HTTP_303_SEE_OTHER)
    
    
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while create a category"
        )

@router.put('/update_category')
def update_category(payload: CategoryCreate, db:Session = Depends(getdb)):
    try:
        category = db.query(Category).filter(Category.name == payload.name).first()

        if not category:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Category not exists add the category by creating category"
            )

        category.name = payload.name,
        category.description = payload.description,
        category.updated_at = datetime.now()

        db.commit()
        db.refresh(category)

        return {"message": "update successful"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while category updateing"
        )
    
@router.delete('/delete_category')
def delete_category(category_name: str, db: Session = Depends(getdb)):
    try:
        category = db.query(Category).filter(Category.name == category_name).first()
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="category not exist"
            )

        category.is_active = False
        category.updated_at = datetime.now()

        db.commit()
        db.refresh(category)

        return {"message": "Delete successful"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while category delete"
        )