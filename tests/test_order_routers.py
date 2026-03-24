from unittest.mock import AsyncMock, patch
from httpx import AsyncClient

async def test_create_order_200(client: AsyncClient, mock_order_repo, order_service, verify_user, fake_product, fake_order, mock_refresh):
    mock_order_repo.save.return_value = fake_order
    order_service.product_repo.get_by_id.return_value = fake_product
    order_service.db.refresh = mock_refresh
    response = await client.post('/orders', json={'info': 'test', 'items': [{'product_id': 1, 'quantity': 1}]})
    assert response.status_code == 200
async def test_create_order_404(client: AsyncClient, mock_order_repo, order_service, verify_user, fake_product, fake_order, mock_refresh):
    mock_order_repo.save.return_value = fake_order
    order_service.product_repo.get_by_id.return_value = None
    order_service.db.refresh = mock_refresh
    response = await client.post('/orders', json={'info': 'test', 'items': [{'product_id': 1, 'quantity': 1}]})
    assert response.status_code == 404
async def test_create_order_400(client: AsyncClient, mock_order_repo, order_service, verify_user, fake_product, fake_order, mock_refresh):
    mock_order_repo.save.return_value = fake_order
    order_service.product_repo.get_by_id.return_value = fake_product
    order_service.db.refresh = mock_refresh
    response = await client.post('/orders', json={'info': 'test', 'items': [{'product_id': 1, 'quantity': 500}]})
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