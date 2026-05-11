from database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import func, Enum, ForeignKey, Index
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
    __table_args__ = (
        Index('ix_user_username', 'username', postgresql_using='hash'),
        )
    id : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username : Mapped[str] = mapped_column(unique=True)
    email : Mapped[str] = mapped_column(unique=True)
    password : Mapped[str]
    role : Mapped[str] = mapped_column(Enum(Role), default=Role.user)
    created_at : Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at : Mapped[datetime | None] = mapped_column(onupdate=func.now())
    orders : Mapped[list['Order']] = relationship('Order', back_populates='user',lazy='selectin')
class Product(Base):
    __tablename__ = 'products'
    __table_args__ =(
        Index('ix_product_name', 'name', postgresql_using='hash'),
        )
    id : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name : Mapped[str] = mapped_column(unique=True)
    description : Mapped[str | None]
    category : Mapped[str] = mapped_column(ForeignKey('categories.name'))
    created_at : Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at : Mapped[datetime | None] = mapped_column(onupdate=func.now())
    items : Mapped[list['OrderItem']] = relationship('OrderItem', back_populates='product', cascade='all, delete-orphan')
class Order(Base):
    __tablename__ = 'orders'
    id : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    info : Mapped[str | None]
    created_at : Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at : Mapped[datetime | None] = mapped_column(onupdate=func.now())
    status : Mapped[str] = mapped_column(Enum(Status), default=Status.pending)
    owner_name : Mapped[str] = mapped_column(ForeignKey('users.username'))
    task_id : Mapped[str | None]
    task_stage : Mapped[str] = mapped_column(Enum(TaskStage),default=TaskStage.pending)
    user : Mapped['User'] = relationship('User', back_populates='orders')
    items : Mapped[list['OrderItem']] = relationship('OrderItem', back_populates='order',cascade='all, delete-orphan', lazy='selectin')
class OrderItem(Base):
    __tablename__ = 'orderitems'
    id : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id : Mapped[int] = mapped_column(ForeignKey('orders.id'))
    product_name : Mapped[str] = mapped_column(ForeignKey('products.name'))
    shop_product_id : Mapped[int | None] = mapped_column(ForeignKey('shopproducts.id'))
    quantity : Mapped[int]
    order : Mapped['Order'] = relationship('Order', back_populates='items')
    product : Mapped['Product'] = relationship('Product', back_populates='items',lazy='selectin')
class Category(Base):
    __tablename__ = 'categories'
    id : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name : Mapped[str] = mapped_column(unique=True)
    description : Mapped[str | None]
class Shop(Base):
    __tablename__ =  'shops'
    __table_args__ = (
        Index('ix_shop_name', 'name', postgresql_using='hash'),
    )
    id : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name : Mapped[str] = mapped_column(unique=True)
    description : Mapped[str | None]
    seller_id : Mapped[int] = mapped_column(ForeignKey('users.id'))
    seller : Mapped['User'] = relationship('User', lazy='selectin')
    is_verified : Mapped[bool] = mapped_column(default=False)
    created_at : Mapped[datetime] = mapped_column(server_default=func.now())
class ShopProduct(Base):
    __tablename__ = 'shopproducts'
    id : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    quantity : Mapped[int]
    price : Mapped[int]
    shop_id : Mapped[int] = mapped_column(ForeignKey('shops.id'))
    product_id : Mapped[int] = mapped_column(ForeignKey('products.id'))
    category_id : Mapped[int] = mapped_column(ForeignKey('categories.id'))
    shop : Mapped['Shop'] = relationship('Shop', lazy='selectin')
    product : Mapped['Product'] = relationship('Product', lazy='selectin')
    category : Mapped['Category'] = relationship('Category', lazy='selectin')
class SellerApplication(Base):
    __tablename__ = 'sellerapplications'
    id : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    text : Mapped[str]
    status : Mapped[str] = mapped_column(Enum(ApplicationStatus),default=ApplicationStatus.pending)
    created_at : Mapped[datetime] = mapped_column(server_default=func.now())
    user_id : Mapped[int] = mapped_column(ForeignKey('users.id'))
    reviewed_by : Mapped[int | None] = mapped_column(ForeignKey('users.id'), default=None)
    user : Mapped['User'] = relationship('User', foreign_keys=[user_id], lazy='selectin')
    reviewer : Mapped['User | None'] = relationship('User', foreign_keys=[reviewed_by], lazy='selectin')
class ModerationRequest(Base):
    __tablename__ = 'mod_requests'
    id : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    status : Mapped[str] = mapped_column(Enum(ApplicationStatus), default=ApplicationStatus.pending)
    created_at : Mapped[datetime] = mapped_column(server_default=func.now())
    shop_id : Mapped[int] = mapped_column(ForeignKey('shops.id'))
    reviewed_by : Mapped[int | None] = mapped_column(ForeignKey('users.id'), default=None)
    shop : Mapped['Shop'] = relationship('Shop', lazy='selectin')
    reviewer : Mapped['User | None'] = relationship('User', lazy='selectin')
