from pydantic import BaseModel
from datetime import datetime
from models import Status
class BaseSchema(BaseModel):
    model_config = {'from_attributes': True}
class CreateUser(BaseModel):
    name : str
    phone : str
    email : str
    password : str
class CreateProduct(BaseModel):
    name : str
    description : str | None = None
    price : int
    quantity : int
class OutProduct(BaseSchema):
    id : int
    name : str
    description : str | None = None
    price : int
    quantity : int
    created_at : datetime
    updated_at: datetime | None = None
class OrderItemCreate(BaseModel):
    product_id : int
    quantity : int
class OutOrderItem(BaseSchema):
    product_id: int
    quantity: int
    product: OutProduct
class CreateOrder(BaseModel):
    info : str | None = None
    items : list[OrderItemCreate]
class OutOrder(BaseSchema):
    id : int
    info : str | None = None
    created_at : datetime
    updated_at: datetime | None = None
    status : str
    user_id : int
    items : list[OutOrderItem]
class OutUser(BaseSchema):
    id : int
    name : str
    phone : str
    email : str
    role : str
    created_at : datetime
    updated_at: datetime | None = None
    orders : list[OutOrder]
class UpdatePassword(BaseModel):
    old_password : str
    new_password : str
class UpdateUser(BaseModel):
    name : str | None = None
    phone : str | None = None
    email : str | None = None
class UpdateProduct(BaseModel):
    name : str | None = None
    description : str | None = None
    price : int | None = None
    quantity : int | None = None
class UpdateOrder(BaseModel):
    info : str | None = None
class UpdateStatus(BaseModel):
    status : Status
class UserLogin(BaseModel):
    email : str
    password : str