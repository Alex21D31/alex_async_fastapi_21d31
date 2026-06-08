import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient, ASGITransport
from datetime import datetime, timezone
from main import app
from auth import verify_token
from dependencies import (
    get_admin_service, get_user_service, get_category_service, get_shop_service,
    get_seller_application_serivce, get_moderation_service, get_order_service,
    get_product_service, get_shop_prod_service
)
from services.user_service import UserService
from services.category_service import CategoryService
from services.shop_service import ShopService
from services.seller_application_service import SellerApplicationService
from services.moderation_service import ModerationService
from services.product_service import ProductService
from services.order_service import OrderService
from services.admin_service import AdminService
from services.shop_prod_service import ShopProductService
from services.redis_service import redis_service
from kafka_utils.producer import get_producer
from repositories.user_repo import UserRepository
from repositories.product_repo import ProductRepository
from repositories.order_repo import OrderRepository
from repositories.shop_prod_repo import ShopProductRepository
from repositories.shop_repo import ShopRepository
from repositories.category_repo import CategoryRepository
from repositories.seller_applic_repo import SellerApplicationRepository
from repositories.moderation_repo import ModerationRepository
from models import Role


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as cli:
        yield cli

@pytest.fixture
def mock_user_repo():
    return AsyncMock(UserRepository)

@pytest.fixture
def mock_product_repo():
    return AsyncMock(ProductRepository)

@pytest.fixture
def mock_order_repo():
    return AsyncMock(OrderRepository)

@pytest.fixture
def mock_cate_repo():
    return AsyncMock(CategoryRepository)

@pytest.fixture
def mock_apply_repo():
    return AsyncMock(SellerApplicationRepository)

@pytest.fixture
def mock_shop_repo():
    return AsyncMock(ShopRepository)

@pytest.fixture
def mock_moder_repo():
    return AsyncMock(ModerationRepository)

@pytest.fixture
def mock_shop_prod_repo():
    return AsyncMock(ShopProductRepository)

@pytest.fixture
def mock_redis_service():
    mock = AsyncMock()
    mock.get_categories_with_redis = AsyncMock(return_value=None)
    mock.set_categorites_with_redis = AsyncMock()
    mock.clear_redis_key = AsyncMock()
    mock.get_products_for_shop_with_redis = AsyncMock(return_value=None)
    mock.set_products_for_shop_with_redis = AsyncMock()
    return mock

# --- services ---

@pytest.fixture
def product_service(mock_product_repo):
    service = ProductService(mock_product_repo)
    app.dependency_overrides[get_product_service] = lambda: service
    yield service
    app.dependency_overrides.pop(get_product_service, None)

@pytest.fixture
def order_service(mock_order_repo, mock_product_repo, mock_user_repo):
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    mock_db.flush = AsyncMock()
    mock_db.commit = AsyncMock()
    mock_db.rollback = AsyncMock()
    mock_shop_product_repo = AsyncMock(ShopProductRepository)
    mock_shop_repo = AsyncMock(ShopRepository)
    service = OrderService(mock_product_repo, mock_user_repo, mock_order_repo, mock_shop_product_repo, mock_shop_repo, mock_db)
    service.db = mock_db
    app.dependency_overrides[get_order_service] = lambda: service
    yield service
    app.dependency_overrides.pop(get_order_service, None)

@pytest.fixture
def user_service(mock_user_repo):
    service = UserService(mock_user_repo)
    app.dependency_overrides[get_user_service] = lambda: service
    yield service
    app.dependency_overrides.pop(get_user_service, None)

@pytest.fixture
def admin_service(mock_user_repo, mock_order_repo):
    service = AdminService(mock_user_repo, mock_order_repo)
    app.dependency_overrides[get_admin_service] = lambda: service
    yield service
    app.dependency_overrides.pop(get_admin_service, None)

@pytest.fixture
def category_service(mock_cate_repo, mock_redis_service):
    service = CategoryService(mock_cate_repo, mock_redis_service)
    app.dependency_overrides[get_category_service] = lambda: service
    yield service
    app.dependency_overrides.pop(get_category_service, None)

@pytest.fixture
def shop_service(mock_shop_repo, mock_user_repo):
    service = ShopService(mock_shop_repo, mock_user_repo)
    app.dependency_overrides[get_shop_service] = lambda: service
    yield service
    app.dependency_overrides.pop(get_shop_service, None)

@pytest.fixture
def seller_application_service(mock_apply_repo, mock_user_repo):
    service = SellerApplicationService(mock_apply_repo, mock_user_repo)
    app.dependency_overrides[get_seller_application_serivce] = lambda: service
    yield service
    app.dependency_overrides.pop(get_seller_application_serivce, None)

@pytest.fixture
def moderation_service(mock_moder_repo, mock_shop_repo):
    service = ModerationService(mock_moder_repo, mock_shop_repo)
    app.dependency_overrides[get_moderation_service] = lambda: service
    yield service
    app.dependency_overrides.pop(get_moderation_service, None)

@pytest.fixture
def shop_prod_service(mock_shop_prod_repo, mock_shop_repo, mock_product_repo, mock_cate_repo, mock_redis_service):
    service = ShopProductService(mock_cate_repo, mock_shop_prod_repo, mock_shop_repo, mock_product_repo, mock_redis_service)
    app.dependency_overrides[get_shop_prod_service] = lambda: service
    yield service
    app.dependency_overrides.pop(get_shop_prod_service, None)

# --- verify fixtures ---

@pytest.fixture
def verify_user():
    app.dependency_overrides[verify_token] = lambda: {'sub': '5', 'email': 'alex@.test', 'token': 'access', 'role': 'user'}
    yield
    app.dependency_overrides.pop(verify_token, None)

@pytest.fixture
def verify_admin():
    app.dependency_overrides[verify_token] = lambda: {'sub': '5', 'email': 'alex@.test', 'token': 'access', 'role': 'admin'}
    yield
    app.dependency_overrides.pop(verify_token, None)

@pytest.fixture
def verify_creator():
    app.dependency_overrides[verify_token] = lambda: {'sub': '5', 'email': 'alex@.test', 'token': 'access', 'role': 'creator'}
    yield
    app.dependency_overrides.pop(verify_token, None)

@pytest.fixture
def verify_seller():
    app.dependency_overrides[verify_token] = lambda: {'sub': '5', 'email': 'alex@.test', 'token': 'access', 'role': 'seller'}
    yield
    app.dependency_overrides.pop(verify_token, None)

# --- fake objects ---

@pytest.fixture
def fake_user():
    user = MagicMock()
    user.id = 5
    user.username = 'Alex'
    user.email = 'alex@test.com'
    user.role = 'user'
    user.created_at = datetime.now(timezone.utc)
    user.updated_at = None
    user.orders = []
    return user

@pytest.fixture
def fake_user_for_login():
    user = MagicMock()
    user.id = 5
    user.username = 'Alex'
    user.email = 'alex@test.com'
    user.role = MagicMock()
    user.role.value = 'user'
    user.created_at = datetime.now(timezone.utc)
    user.updated_at = None
    user.orders = []
    return user

@pytest.fixture
def fake_user_banned():
    user = MagicMock()
    user.id = 5
    user.username = 'Alex'
    user.email = 'alex@test.com'
    user.role = Role.banned
    user.created_at = datetime.now(timezone.utc)
    user.updated_at = None
    user.orders = []
    return user

@pytest.fixture
def fake_target_user():
    user = MagicMock()
    user.id = 10
    user.username = 'Target'
    user.email = 'target@test.com'
    user.role = MagicMock()
    user.role.value = 'user'
    user.created_at = datetime.now(timezone.utc)
    user.updated_at = None
    user.orders = []
    return user

@pytest.fixture
def fake_product():
    product = MagicMock()
    product.id = 5
    product.name = 'test_prod'
    product.description = 'desc'
    product.category = 'Electronics'
    product.created_at = datetime.now(timezone.utc)
    product.updated_at = None
    return product

@pytest.fixture
def fake_category():
    cat = MagicMock()
    cat.name = 'Electronics'
    cat.description = 'Electronic goods'
    return cat

@pytest.fixture
def fake_order():
    order = MagicMock()
    order.id = 1
    order.info = 'test'
    order.status = 'pending'
    order.owner_name = 'Alex'
    order.created_at = datetime.now(timezone.utc)
    order.updated_at = None
    order.items = []
    return order

@pytest.fixture
def mock_refresh(fake_order):
    async def _refresh(obj):
        obj.id = fake_order.id
        obj.created_at = fake_order.created_at
        obj.status = fake_order.status
        obj.owner_name = fake_order.owner_name
        obj.info = fake_order.info
        obj.items = fake_order.items
    return _refresh

@pytest.fixture
def fake_shop(fake_user):
    shop = MagicMock()
    shop.id = 1
    shop.name = 'test_shop'
    shop.description = 'test description'
    shop.is_verified = False
    shop.created_at = datetime.now(timezone.utc)
    shop.seller_id = 5
    shop.seller = fake_user
    shop.products = []
    shop.orders = []
    return shop

@pytest.fixture
def fake_shop_product(fake_product, fake_shop, fake_category):
    sp = MagicMock()
    sp.id = 1
    sp.quantity = 10
    sp.price = 500
    sp.shop_id = 1
    sp.product_id = 5
    sp.product = fake_product
    sp.shop = fake_shop
    sp.category = fake_category
    return sp

@pytest.fixture
def fake_application(fake_user):
    application = MagicMock()
    application.id = 1
    application.text = 'I want to be a seller'
    application.status = 'pending'
    application.created_at = datetime.now(timezone.utc)
    application.user_id = 5
    application.reviewed_by = None
    application.user = fake_user
    application.reviewer = None
    return application

@pytest.fixture
def fake_moderation(fake_shop):
    mod = MagicMock()
    mod.id = 1
    mod.status = 'pending'
    mod.created_at = datetime.now(timezone.utc)
    mod.shop_id = 1
    mod.reviewed_by = None
    mod.shop = fake_shop
    mod.reviewer = None
    return mod

# --- autouse ---

@pytest_asyncio.fixture(autouse=True)
async def mock_redis():
    mock_client = AsyncMock()
    mock_client.sismember = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(return_value=None)
    mock_client.zremrangebyscore = AsyncMock()
    mock_client.zadd = AsyncMock()
    mock_client.zcard = AsyncMock(return_value=0)
    mock_client.sadd = AsyncMock()
    mock_client.expireat = AsyncMock()
    with patch.object(redis_service, 'redis_client', mock_client):
        yield mock_client

@pytest.fixture(autouse=True)
def mock_celery_task():
    with patch('services.user_service.send_welcome_email') as mock:
        mock.delay = MagicMock()
        yield mock

@pytest.fixture(autouse=True)
def mock_kafka_producer():
    mock_producer = AsyncMock()
    app.state.producer = mock_producer
    app.dependency_overrides[get_producer] = lambda: mock_producer
    yield mock_producer
    app.dependency_overrides.pop(get_producer, None)

@pytest.fixture(autouse=True)
def mock_send_order_event():
    with patch('services.order_service.send_order_event') as mock:
        mock.return_value = AsyncMock()
        yield mock
