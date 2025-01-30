from sqlalchemy import (
    Integer,
    Float,
    Boolean,
    Column,
    String,
    UniqueConstraint,
    ForeignKey,
    DateTime,
    Enum,
    TIMESTAMP,
    Double, 
    VARCHAR,
    
)
from database.database import Base
from sqlalchemy.orm import relationship
from database.db_enum import PaymentMethod,StatusEnum,OrderStatus
import uuid

class ParentBase(Base):
    __abstract__ = True
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    is_active = Column(Boolean, default=True)
    
class Customer(ParentBase):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True,nullable=False)
    username = Column(String, unique=True, nullable=False)
    password = Column(String)

    order_history = relationship("Order_history",back_populates="customers")
    customer_cart = relationship("Cart", back_populates="customer")

class Category(ParentBase):

    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True)
    description = Column(String)
    covers = Column(String)
    
    products = relationship("Product", back_populates="categories")

class Product(ParentBase):

    __tablename__ = "products"

    category_id = Column(Integer, ForeignKey("categories.id"))
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    description = Column(String)
    cover = Column(String)
    price = Column(Double)
    
    categories = relationship("Category", back_populates="products")
    orders = relationship("Order",back_populates="product")
    carts = relationship("Cart", back_populates="product_cart")
    order_hist_prod = relationship("Order_history", back_populates="prod_hist_order")

class Order(ParentBase):

    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer,ForeignKey("products.id"))
    quantity = Column(Integer)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    product = relationship("Product", back_populates="orders")
    order_hist = relationship("Order_history", back_populates="order")
    order_checking = relationship("Checkout", back_populates="check_order")

class Order_history(ParentBase):

    __tablename__ = "order_history"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("customers.id"))
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    payment_id = Column(Integer, ForeignKey("payment_history.id"))
    total = Column(Integer)
    price = Column(Float)
    
    customers = relationship("Customer", back_populates="order_history")
    order = relationship("Order", back_populates="order_hist")
    payment = relationship("Payment_history", back_populates="payment_id_order")
    prod_hist_order = relationship("Product", back_populates="order_hist_prod")
    
class Payment_history(ParentBase):

    __tablename__ = "payment_history"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer)
    amount = Column(Double,nullable=False)
    status = Column(Enum(StatusEnum), nullable=False, default=StatusEnum.pending)
    payment_method = Column(Enum(PaymentMethod), nullable=False)

    payment_id_order = relationship("Order_history", back_populates="payment")

class Cart(ParentBase):

    __tablename__ = 'carts'
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    cover = Column(String)
    customer = relationship("Customer", back_populates="customer_cart")
    product_cart = relationship('Product', back_populates="carts")
    checkouts = relationship("Checkout", back_populates="cart")


class Checkout(ParentBase):

    __tablename__ = "checkout"
    id = Column(Integer, primary_key=True, autoincrement=True)
    cart_id = Column(Integer, ForeignKey('carts.id'))
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    zipcode = Column(Integer, nullable=False)
    phonenumber = Column(String, nullable=False)
    email = Column(String, nullable=False)
    total_price = Column(Integer)
    order_id = Column(Integer, ForeignKey('orders.id'))
    cart = relationship("Cart", back_populates="checkouts")
    check_order = relationship("Order", back_populates="order_checking")