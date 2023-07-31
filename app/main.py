from fastapi import Cookie,FastAPI, Request,Form,Response, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Annotated
from .users_repository import UserRepository, UserCreate
from .flowers_repository import  FlowersRepository
from .purchases_repository import PurchaseRepository, PurchaseCreate
import json
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from .database import Base, engine, SessionLocal
from sqlalchemy.orm import Session
from pydantic import BaseModel
Base.metadata.create_all(bind=engine)

class Item(BaseModel):
    item_id: int
    

oauth2_scheme = OAuth2PasswordBearer(tokenUrl = 'token')


def create_jwt(user_email: int)->str:
    body = {'user_email': user_email}
    token = jwt.encode(body, 'youngccamel', 'HS256')
    return token

def decode_jwt(token: str)->str:
    data = jwt.decode(token, 'youngccamel', 'HS256')
    return data['user_email']

app = FastAPI()
        
# template = templating.Jinja2Templates('templates')
users_repository = UserRepository()
flowers_repository = FlowersRepository()
purchases_repository = PurchaseRepository()

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close() 
  
class UserCreateRequest(BaseModel):
    email:str
    full_name: str
    password: str


@app.post('/signup')
def post_reg(input: UserCreateRequest, db: Session=Depends(get_db)):
    user = UserCreate(email = input.email, full_name=input.full_name,password = input.password)
    users_repository.save(db, user)
    return {f'successfully registered!'}

@app.post('/token')
def login(username: str = Form(), password: str = Form(), db:Session=Depends(get_db)):
    if users_repository.get_by_email(db,username) == None:
        raise HTTPException(status_code = 404, detail = '404 User Is Not Found')
    else:
        user = users_repository.get_by_email(db,username)
    if user.password != password:
        raise HTTPException(status_code = 403, detail = 'Forbidden')
    access_token = create_jwt(username)
    return {'access_token': access_token}

@app.get('/profile')
def profile(token: str = Depends(oauth2_scheme), db: Session=Depends(get_db)):
    user_email = decode_jwt(token)
    user = users_repository.get_by_email(db,user_email)
    return {f'Hello {user.full_name}! You are authenticated!'}

@app.get('/flowers')
def get_flowers(db:Session=Depends(get_db)):
    flowers = flowers_repository.get_all(db)
    return {'flowers': flowers}

class FlowerCreate(BaseModel):
    name: str
    count: int
    cost: int
    
@app.post('/flowers')
def add_flowers(flower: FlowerCreate, db:Session=Depends(get_db)):
    flowers_repository.save(db,flower)
    return {f'{flower.name} was added to the list!'}

@app.delete('/flowers/{flower_id}')
def delete_flower(flower_id: int, db:Session=Depends(get_db)):
    flowers_repository.delete(db, flower_id)
    return {f'flower was deleted!'}

class FlowerEdit(BaseModel):
    name: str
    count: int
    cost: int
    
@app.patch('/flowers/{flower_id}')
def patch_flower(flower_id: int, input: FlowerEdit, db:Session=Depends(get_db)):
    flowers_repository.update(flower_id, input, db)
    return {f'flower was edited!'}
    
    
    
@app.post('/cart/items')
def add_to_cart(item: Item, cart: str = Cookie(default = "[]"), db:Session=Depends(get_db)):
    response = JSONResponse({'message': 'item was added'})
    cart = json.loads(cart)
    if item.item_id > 0 and item.item_id <= len(flowers_repository.get_all(db)):
        cart.append(item.item_id)
        cart_json = json.dumps(cart)
        response.set_cookie('cart', cart_json)
    return response

@app.get('/cart/items')
def get_cart(cart: str = Cookie(default='[]'), db:Session=Depends(get_db)):
    if cart == None:
        return {f'cart is empty'}
    cart = json.loads(cart)
    flowers = flowers_repository.get_by_ids(db,cart)
    total_price = 0
    for flower in flowers:
        total_price+=int(flower.cost)
    return {'flowers': [flower.name for flower in flowers], 'total_price': total_price}


@app.post('/purchased')
def purchase(response: Response, token: str = Depends(oauth2_scheme), cart: str = Cookie(default = '[]'), db:Session=Depends(get_db)):
    cart = json.loads(cart)
    user_email = decode_jwt(token)
    user = users_repository.get_by_email(db,user_email)
    if user is None:
        raise HTTPException(detail = 'Permission denied', status_code = 403)
    for flower_id in cart:
        purchase = PurchaseCreate(user.id, flower_id)
        purchases_repository.save(db, purchase)
    response = JSONResponse({'message': 'purchased!'})
    response.delete_cookie('cart')
    return response
    
    
@app.get('/purchased')
def get_purchases(token: str = Depends(oauth2_scheme),db:Session=Depends(get_db)):
    user_email = decode_jwt(token)
    user = users_repository.get_by_email(db, user_email)
    purchases = purchases_repository.get_by_user_id(db, user.id)
    flowers = flowers_repository.get_by_ids(db, purchases)
    return JSONResponse({'flowers': [flower.name for flower in flowers]})