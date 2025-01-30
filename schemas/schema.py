from pydantic import BaseModel
from typing import Union

class CustomerCreate(BaseModel):
    email: str
    username: str
    password: str 


class Login(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None

class RequestLogin(BaseModel):
    email : str
    password : str

class CategoryCreate(BaseModel):
    
    name: str
    description: str

class ProductCreate(BaseModel):

    name : str
    description : str
    price : float
    category_id : int

class CartCreate(BaseModel):
    product_id: int
    quantity: int

class CartDisplay(BaseModel):
    id: int
    product_id: int
    quantity: int
    