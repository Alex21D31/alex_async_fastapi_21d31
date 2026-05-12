from pydantic import BaseModel, computed_field
from datetime import datetime
from models import Status
class BaseSchema(BaseModel):
    model_config = {'from_attributes': True}
class CreateUser(BaseModel):
    username : str
    email : str
    password : str
class CreateProduct(BaseModel):
    name : str
    description : str | None = None
    category : str
class OutProduct(BaseSchema):
    name : str
    description : str | None = None
    category : str
    created_at : datetime
class OrderItemCreate(BaseModel):
    product_name : str
    quantity : int
class OutOrderItem(BaseSchema):
    product_name: str
    quantity: int
    product: OutProduct
class CreateOrder(BaseModel):
    info : str | None = None
    items : list[OrderItemCreate]
class OutOrder(BaseSchema):
    info : str | None = None
    created_at : datetime
    status : str
    owner_name : str
    items : list[OutOrderItem]
class OutUser(BaseSchema):
    username : str
    email : str
    role : str
    created_at : datetime
class UpdatePassword(BaseModel):
    old_password : str
    new_password : str
class UpdateUser(BaseModel):
    username : str | None = None
    email : str | None = None
class UpdateProduct(BaseModel):
    name : str | None = None
    description : str | None = None
class UpdateOrder(BaseModel):
    info : str | None = None
class UpdateStatus(BaseModel):
    status : Status
class UserLogin(BaseModel):
    email : str
    password : str
class CreateCategory(BaseModel):
    name : str
    description : str | None = None
class OutCategory(BaseSchema):
    name : str
    description : str | None = None
class CreateShop(BaseModel):
    name : str
    description : str | None = None
class OutShop(BaseSchema):
    name : str
    is_verified : bool
    created_at : datetime
    @computed_field
    @property
    def seller_name(self) -> str:
        return self.seller.username
class UpdateShop(BaseModel):
    name : str | None = None
    description : str | None = None
class CreateShopProduct(BaseModel):
    product_name : str
    shop_name : str
    quantity : int
    price : int
    category_name : str
class OutShopProduct(BaseSchema):
    quantity : int
    price : int
    @computed_field
    @property
    def product_name(self) -> str:
        return self.product.name
    @computed_field
    @property
    def shop_name(self) -> str:
        return self.shop.name
    @computed_field
    @property
    def category_name(self) -> str:
        return self.category.name
class UpdateShopProduct(BaseModel):
    quantity : int
    price : int
class CreateSellerApplication(BaseModel):
    text : str
class OutSellerApplication(BaseSchema):
    text: str
    status: str
    created_at: datetime
    @computed_field
    @property
    def user_name(self) -> str:
        return self.user.username
    @computed_field
    @property
    def reviewer_name(self) -> str | None:
        return self.reviewer.username if self.reviewer else None
class OutModerationRequest(BaseSchema):
    status: str
    created_at: datetime
    @computed_field
    @property
    def shop_name(self) -> str:
        return self.shop.name
    @computed_field
    @property
    def reviewer_name(self) -> str | None:
        return self.reviewer.username if self.reviewer else None