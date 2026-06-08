from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient

async def test_create_order_200(client: AsyncClient, mock_order_repo, order_service, verify_user, fake_user, fake_order):
    fake_shop = MagicMock()
    fake_shop.id = 1
    fake_shop_product = MagicMock()
    fake_shop_product.quantity = 100
    fake_shop_product.price = 500
    order_service.shop_repo.get_by_shop_name = AsyncMock(return_value=fake_shop)
    order_service.user_repo.get_by_id = AsyncMock(return_value=fake_user)
    order_service.shop_product_repo.get_one_product_for_seller_by_name = AsyncMock(return_value=fake_shop_product)
    mock_result = MagicMock()
    mock_result.scalar_one.return_value = fake_order
    order_service.db.execute = AsyncMock(return_value=mock_result)
    response = await client.post('/orders', json={'shop_name': 'test_shop', 'info': 'test', 'items': [{'product_name': 'test_prod', 'quantity': 1}]})
    assert response.status_code == 200
async def test_create_order_404(client: AsyncClient, mock_order_repo, order_service, verify_user):
    order_service.shop_repo.get_by_shop_name = AsyncMock(return_value=None)
    response = await client.post('/orders', json={'shop_name': 'unknown', 'info': 'test', 'items': [{'product_name': 'test_prod', 'quantity': 1}]})
    assert response.status_code == 404
async def test_create_order_400(client: AsyncClient, mock_order_repo, order_service, verify_user, fake_user):
    fake_shop = MagicMock()
    fake_shop.id = 1
    order_service.shop_repo.get_by_shop_name = AsyncMock(return_value=fake_shop)
    order_service.user_repo.get_by_id = AsyncMock(return_value=fake_user)
    order_service.shop_product_repo.get_one_product_for_seller_by_name = AsyncMock(return_value=None)
    response = await client.post('/orders', json={'shop_name': 'test_shop', 'info': 'test', 'items': [{'product_name': 'missing', 'quantity': 1}]})
    assert response.status_code == 400

async def test_get_my_orders_200(client: AsyncClient, order_service, mock_order_repo, verify_user, fake_order):
    mock_order_repo.get_all_orders_by_user.return_value = [fake_order]
    response = await client.get('/orders')
    assert response.status_code == 200
async def test_get_my_orders_401(client: AsyncClient, order_service, mock_order_repo, fake_order):
    mock_order_repo.get_all_orders_by_user.return_value = [fake_order]
    response = await client.get('/orders')
    assert response.status_code == 401

async def test_get_one_order_200(client: AsyncClient, order_service, mock_order_repo, verify_user, fake_order):
    mock_order_repo.get_by_id_for_user.return_value = fake_order
    response = await client.get('/orders/5')
    assert response.status_code == 200
async def test_get_one_order_401(client: AsyncClient, order_service, mock_order_repo, fake_order):
    mock_order_repo.get_by_id_for_user.return_value = fake_order
    response = await client.get('/orders/5')
    assert response.status_code == 401
async def test_get_one_order_404(client: AsyncClient, order_service, mock_order_repo, verify_user, fake_order):
    mock_order_repo.get_by_id_for_user.return_value = None
    response = await client.get('/orders/5')
    assert response.status_code == 404

async def test_update_order_200(client: AsyncClient, order_service, mock_order_repo, verify_user, fake_order):
    mock_order_repo.update.return_value = fake_order
    response = await client.patch('/orders/5', json={'info' : 'dhahda'})
    assert response.status_code == 200
async def test_update_order_401(client: AsyncClient, order_service, mock_order_repo, fake_order):
    mock_order_repo.update.return_value = fake_order
    response = await client.patch('/orders/5', json={'info' : 'dhahda'})
    assert response.status_code == 401
async def test_update_order_404(client: AsyncClient, order_service, mock_order_repo, verify_user, fake_order):
    mock_order_repo.get_by_id.return_value = None
    response = await client.patch('/orders/5', json={'info' : 'dhahda'})
    assert response.status_code == 404

async def test_update_status_200(client: AsyncClient, order_service, mock_order_repo, verify_admin, fake_order):
    mock_order_repo.update.return_value = fake_order
    response = await client.patch('/orders/status/5?new_status=cancelled')
    assert response.status_code == 200
async def test_update_status_403(client: AsyncClient, order_service, mock_order_repo,verify_user, fake_order):
    mock_order_repo.update.return_value = fake_order
    response = await client.patch('/orders/status/5?new_status=cancelled')
    assert response.status_code == 403
async def test_update_status_404(client: AsyncClient, order_service, mock_order_repo, verify_admin, fake_order):
    mock_order_repo.get_by_id.return_value = None
    response = await client.patch('/orders/status/5?new_status=cancelled')
    assert response.status_code == 404
async def test_update_status_401(client: AsyncClient, order_service, mock_order_repo, fake_order):
    mock_order_repo.update.return_value = fake_order
    response = await client.patch('/orders/status/5?new_status=cancelled')
    assert response.status_code == 401

async def test_delete_order_200(client: AsyncClient, order_service, mock_order_repo, verify_admin, fake_order):
    mock_order_repo.get_by_id.return_value = fake_order
    response = await client.delete('/orders/5')
    assert response.status_code == 200
async def test_delete_order_403(client: AsyncClient, order_service, mock_order_repo, verify_user, fake_order):
    mock_order_repo.get_by_id.return_value = fake_order
    response = await client.delete('/orders/5')
    assert response.status_code == 403
async def test_delete_order_401(client: AsyncClient, order_service, mock_order_repo,  fake_order):
    mock_order_repo.get_by_id.return_value = fake_order
    response = await client.delete('/orders/5')
    assert response.status_code == 401
async def test_delete_order_404(client: AsyncClient, order_service, mock_order_repo, verify_admin, fake_order):
    mock_order_repo.get_by_id.return_value = None
    response = await client.delete('/orders/5')
    assert response.status_code == 404