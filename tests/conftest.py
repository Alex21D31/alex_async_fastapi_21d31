import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock
from httpx import AsyncClient, ASGITransport
from datetime import datetime, timezone
from main import app
from auth import verify_token
from dependencies import get_admin_service, get_user_service, get_order_service,get_product_service
from services.user_service import UserService
from services.product_service import ProductService
from services.order_service import OrderService
from services.admin_service import AdminService
from repositories.user_repo import UserRepository
from repositories.product_repo import ProductRepository
from repositories.order_repo import OrderRepository
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
def product_service(mock_product_repo):
    service = ProductService(mock_product_repo)
    app.dependency_overrides[get_product_service] = lambda: service
    yield service
    app.dependency_overrides.pop(get_product_service, None)

@pytest.fixture
def order_service(mock_order_repo, mock_product_repo):
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    service = OrderService(mock_order_repo, mock_product_repo, mock_db)
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
def admin_service(mock_user_repo,mock_order_repo):
    service = AdminService(mock_user_repo, mock_order_repo)
    app.dependency_overrides[get_admin_service] = lambda: service
    yield service
    app.dependency_overrides.pop(get_admin_service,None)

@pytest.fixture
def verify_user():
    app.dependency_overrides[verify_token] = lambda: {
        'sub' : '5',
        'email' : 'alex@.test',
        'token' : 'access',
        'role' : 'user'
    }
    yield
    app.dependency_overrides.pop(verify_token, None)

@pytest.fixture
def verify_admin():
    app.dependency_overrides[verify_token] = lambda: {
        'sub' : '5',
        'email' : 'alex@.test',
        'token' : 'access',
        'role' : 'admin'
    }
    yield
    app.dependency_overrides.pop(verify_token, None)

@pytest.fixture
def verify_creator():
    app.dependency_overrides[verify_token] = lambda: {
        'sub' : '5',
        'email' : 'alex@.test',
        'token' : 'access',
        'role' : 'creator'
    }
    yield
    app.dependency_overrides.pop(verify_token, None)

@pytest.fixture
def fake_user():
    user = MagicMock()
    user.id = 5
    user.name = 'Alex'
    user.email = 'alex@test.com'
    user.phone = '1231231230'
    user.role = 'user'
    user.created_at = datetime.now(timezone.utc)
    user.updated_at = None
    user.orders = []
    return user

@pytest.fixture
def fake_user_for_login():
    user = MagicMock()
    user.id = 5
    user.name = 'Alex'
    user.email = 'alex@test.com'
    user.phone = '1231231230'
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
    user.name = 'Alex'
    user.email = 'alex@test.com'
    user.phone = '1231231230'
    user.role = Role.banned
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
    product.quantity = 321
    product.price = 1313
    product.created_at = datetime.now(timezone.utc)
    product.updated_at = None
    return product

@pytest.fixture
def fake_order():
    order = MagicMock()
    order.id = 1
    order.info = 'test'
    order.status = 'pending'
    order.user_id = 5
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
        obj.user_id = fake_order.user_id
        obj.info = fake_order.info
        obj.items = fake_order.items
    return _refresh

@pytest.fixture
def fake_target_user():
    user = MagicMock()
    user.id = 10
    user.name = 'Target'
    user.email = 'target@test.com'
    user.phone = '9876543210'
    user.role = MagicMock()
    user.role.value = 'user'
    user.created_at = datetime.now(timezone.utc)
    user.updated_at = None
    user.orders = []
    return user