from database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import func, Enum, ForeignKey
from datetime import datetime
import enum
class Role(enum.Enum):
    user = 'user'
    admin = 'admin'
    creator = 'creator'
    banned = 'banned'
    seller = 'seller'
class Status(enum.Enum):
    pending = 'pending'
    delivered = 'delivered'
    cancelled = 'cancelled'
class TaskStage (enum.Enum):
    pending = 'pending'
    processing = 'processing'
    shipping = 'shipping'
    delivered = 'delivered'
class ApplicationStatus(enum.Enum):
    pending = 'pending'
    approved = 'approved'
    rejected = 'rejected'
class User(Base):
    __tablename__ = 'users'
    id : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name : Mapped[str] = mapped_column(nullable=False,unique=True)
    phone : Mapped[str] = mapped_column(nullable=False,unique=True)
    email : Mapped[str] = mapped_column(nullable=False,unique=True)
    password : Mapped[str] = mapped_column(nullable=False)
    role : Mapped[str] = mapped_column(Enum(Role), default=Role.user)
    created_at : Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at : Mapped[datetime] = mapped_column(nullable=True,onupdate=func.now())
    orders : Mapped[list['Order']] = relationship('Order', back_populates='user',lazy='selectin')
class Product(Base):
    __tablename__ = 'products'
    id : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name : Mapped[str] = mapped_column(nullable=False,unique=True)
    description : Mapped[str | None]
    price : Mapped[int] = mapped_column(nullable=False)
    quantity : Mapped[int] = mapped_column(nullable=False)
    category_id : Mapped[int | None] = mapped_column(ForeignKey('categories.id'), nullable=True)
    created_at : Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at : Mapped[datetime] = mapped_column(nullable=True,onupdate=func.now())
    items : Mapped[list['OrderItem']] = relationship('OrderItem', back_populates='product', cascade='all, delete-orphan')
class Order(Base):
    __tablename__ = 'orders'
    id : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    info : Mapped[str | None]
    created_at : Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at : Mapped[datetime] = mapped_column(nullable=True,onupdate=func.now())
    status : Mapped[str] = mapped_column(Enum(Status), default=Status.pending)
    user_id : Mapped[int] = mapped_column(ForeignKey('users.id'))
    task_id : Mapped[str | None] = mapped_column(nullable=True)
    task_stage : Mapped[str] = mapped_column(Enum(TaskStage),default=TaskStage.pending)
    user : Mapped['User'] = relationship('User', back_populates='orders')
    items : Mapped[list['OrderItem']] = relationship('OrderItem', back_populates='order',cascade='all, delete-orphan', lazy='selectin')
class OrderItem(Base):
    __tablename__ = 'orderitems'
    id : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id : Mapped[int] = mapped_column(ForeignKey('orders.id'))
    product_id : Mapped[int] = mapped_column(ForeignKey('products.id'))
    quantity : Mapped[int]
    order : Mapped['Order'] = relationship('Order', back_populates='items')
    product : Mapped['Product'] = relationship('Product', back_populates='items',lazy='selectin')

class Category(Base):
    __tablename__ = 'categories'
    id : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name : Mapped[str] = mapped_column(nullable=False, unique=True)
    description : Mapped[str | None] = mapped_column(nullable=True)
class Shop(Base):
    __tablename__ =  'shops'
    id : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name : Mapped[str] = mapped_column(nullable=False, unique=True)
    description : Mapped[str | None] = mapped_column(nullable=True)
    seller_id : Mapped[int] = mapped_column(ForeignKey('users.id'))
    is_verified : Mapped[bool] = mapped_column(default=False)
    created_at : Mapped[datetime] = mapped_column(server_default=func.now())
class ShopProduct(Base):
    __tablename__ = 'shopproducts'
    id : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    quantity : Mapped[int] = mapped_column(nullable=False)
    price : Mapped[int] = mapped_column(nullable=False)
    shop_id : Mapped[int] = mapped_column(ForeignKey('shops.id'))
    product_id : Mapped[int] = mapped_column(ForeignKey('products.id'))
    category_id : Mapped[int] = mapped_column(ForeignKey('categories.id'))
class SellerApplication(Base):
    __tablename__ = 'sellerapplications'
    id : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    text : Mapped[str | None] = mapped_column(nullable=True)
    status : Mapped[str] = mapped_column(Enum(ApplicationStatus),default=ApplicationStatus.pending)
    created_at : Mapped[datetime] = mapped_column(server_default=func.now())
    user_id : Mapped[int] = mapped_column(ForeignKey('users.id'))
    reviewed_by : Mapped[int | None] = mapped_column(ForeignKey('users.id'), nullable=True, default=None)

 