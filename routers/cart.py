from fastapi import APIRouter,Depends,HTTPException,Request,Form,status
from sqlalchemy.orm import Session
from database.database import getdb
from database.models import Cart,Customer,Product,Order,Checkout,Order_history,Payment_history
from datetime import datetime
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from authentication.login_authentication import authenticate_user
from datetime import datetime
from database.db_enum import OrderStatus,StatusEnum,PaymentMethod

router = APIRouter(
    tags=["Cart"]
)
templates = Jinja2Templates(directory="templates")


@router.post("/add_to_cart")
def add_to_cart(
    product_id: int = Form(...),
    quantity: int = Form(...),
    db: Session = Depends(getdb),
    current_user: Customer = Depends(authenticate_user)
):
    try:
        product = db.query(Product).filter(Product.id == product_id).first()

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        cart_item = db.query(Cart).filter(Cart.customer_id == current_user.id, Cart.product_id == product_id).first()
        if cart_item:
            if not cart_item.is_active:
                cart_item.is_active = True
                cart_item.quantity = quantity
            else:
                # If the item is already active, just update the quantity
                cart_item.quantity += quantity
        else:
            cart_item = Cart(customer_id=current_user.id, product_id=product_id, quantity=quantity, created_at = datetime.now())
            db.add(cart_item)
        
        db.commit()
        db.refresh(cart_item)
        return RedirectResponse(url="/cart", status_code=302)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"An error occured while adding products to the cart"}
        )

@router.get("/cart")
def view_cart(request: Request, db: Session = Depends(getdb), current_user: Customer = Depends(authenticate_user)):

    try:
        cart_items = db.query(Cart).filter(Cart.customer_id == current_user.id,Cart.is_active==True).all()
        total_price = sum(item.quantity * item.product_cart.price for item in cart_items)
        return templates.TemplateResponse("cart.html", {"request": request, "cart_items": cart_items, "total_price": total_price})
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"Can't fetch the cart items because of invalid user"}
        )

@router.post("/update_cart_item")
def update_cart_item(
    cart_id: int = Form(...),
    quantity: int = Form(...),
    db: Session = Depends(getdb),
    current_user: Customer = Depends(authenticate_user)
):
    try:
        cart_item = db.query(Cart).filter(Cart.id == cart_id, Cart.customer_id == current_user.id).first()
        if not cart_item:
            raise HTTPException(status_code=404, detail="Cart item not found")
        
        if quantity <= 0:
            db.delete(cart_item)
        else:
            cart_item.quantity = quantity
            cart_item.updated_at = datetime.now()
        
        db.commit()
        return RedirectResponse(url="/cart", status_code=302)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"Can't fetch the cart items because of invalid user"}
        )

@router.post("/remove_cart_item")
def remove_cart_item(
    cart_id: int = Form(...),
    db: Session = Depends(getdb),
    current_user: Customer = Depends(authenticate_user)
):
    try:
        cart_item = db.query(Cart).filter(Cart.id == cart_id, Cart.customer_id == current_user.id).first()
        if not cart_item:
            raise HTTPException(status_code=404, detail="Cart item not found")
        
        db.delete(cart_item)
        db.commit()
        return RedirectResponse(url="/cart", status_code=302)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"Can't fetch the cart items because of invalid user id"}
        )


@router.get("/checkout", response_class=HTMLResponse)
def get_checkout(request: Request, db: Session = Depends(getdb), current_user: Customer = Depends(authenticate_user)):
    try:
        cart_items = db.query(Cart).filter(Cart.customer_id == current_user.id,Cart.is_active==True).all()
        total_price = sum(item.quantity * item.product_cart.price for item in cart_items)
        return templates.TemplateResponse("checkout.html", {"request": request, "cart_items": cart_items, "total_price": total_price})
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"Can't fetch the cart items because of invalid user id"}
        )

#nee to check
@router.post("/submit_order")
def submit_order(
    request: Request,
    name: str = Form(...),
    address: str = Form(...),
    city: str = Form(...),
    state: str = Form(...),
    zipcode: str = Form(...),
    phone: str = Form(...),
    email: str = Form(...),
    payment_method: str = Form(...),
    db: Session = Depends(getdb),
    current_user: Customer = Depends(authenticate_user)
):
    try:
        cart_items = db.query(Cart).filter(Cart.customer_id == current_user.id).all()
        total_quantity = sum(item.quantity for item in cart_items)
        total_price = sum(item.quantity * item.product_cart.price for item in cart_items)
        if not cart_items:
            raise HTTPException(status_code=400, detail="Cart is empty")
        
        for item in cart_items:
            order = Order(
                product_id=item.product_id,
                quantity=total_quantity,
                status=OrderStatus.PENDING,
                created_at=datetime.now()
            )
            db.add(order)
            db.commit()
            db.refresh(order)
            # db.query(Cart).filter(Cart.customer_id == current_user.id).update({"is_active": False})
            item.is_active = False
            db.commit()


        try:
            payment_history = Payment_history(
                order_id=order.id,
                amount=total_price,
                status=StatusEnum.pending,
                payment_method=PaymentMethod[payment_method.upper()],
                created_at=datetime.now()
            )
            db.add(payment_history)
            db.commit()
            db.refresh(payment_history)

        except KeyError as e:
            raise HTTPException(status_code=400, detail=f"Invalid payment method: {e}")
        
        for item in cart_items:
            order_history = Order_history(
                user_id=current_user.id,
                order_id=order.id,
                product_id=item.product_id,
                quantity=total_quantity,
                payment_id=payment_history.id,
                total=total_quantity,
                price=total_price,
                created_at=datetime.now()
            )
            db.add(order_history)
            db.commit()
            db.refresh(order_history)

        # Create a new order
        checkout = Checkout(
            cart_id=cart_items[0].id,
            name=name,
            address=address,
            city=city,
            state=state,
            zipcode=zipcode,
            phonenumber = phone,
            email = email,
            total_price=sum(item.quantity * item.product_cart.price for item in cart_items),
            order_id=order.id,
            created_at=datetime.now()
        )
        db.add(checkout)
        db.commit()
        db.refresh(checkout)


        if payment_method == "cash":
            payment_history.status = StatusEnum.pending
        else:
            payment_history.status = StatusEnum.completed

        db.commit()
        
        order_details = {
            "order_id": order.id,
            "order_status": order.status.value,
            "total_quantity": total_quantity,
            "total_price": total_price,
            "payment_method": payment_method.replace("_", " ").title(),
            "message": "Your order has been placed successfully!"
        }

        payment_details = {
            "payment_status": payment_history.status.value
        }

        return templates.TemplateResponse("order.html", {"request": request, "order_details": order_details,"checkout_details":checkout, "payment_details":payment_details})
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"An error occured while submit the order"}
        )

@router.get("/your_order")
def view_order(request: Request, db: Session = Depends(getdb), current_user: Customer = Depends(authenticate_user)):
    
    try:
        cart_items = db.query(Cart).filter(Cart.customer_id == current_user.id).all()
        total_price = sum(item.quantity * item.product_cart.price for item in cart_items)
        order_status = "completed"
        return templates.TemplateResponse("create_order.html", {"request": request, "cart_items": cart_items, "total_price": total_price,"order_status":order_status})
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"Invalid User"}
        )