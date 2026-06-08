from unittest.mock import patch, AsyncMock
from httpx import AsyncClient

# --- seller application ---

async def test_create_apply_200(client: AsyncClient, verify_user, seller_application_service, mock_apply_repo, mock_user_repo, fake_user, fake_application):
    mock_user_repo.get_by_id.return_value = fake_user
    mock_apply_repo.get_by_username.return_value = None
    mock_apply_repo.save.return_value = fake_application
    response = await client.post('/sellers/apply', json={'text': 'I want to be a seller'})
    assert response.status_code == 200

async def test_create_apply_409(client: AsyncClient, verify_user, seller_application_service, mock_apply_repo, mock_user_repo, fake_user, fake_application):
    fake_application.reviewed_by = None
    mock_user_repo.get_by_id.return_value = fake_user
    mock_apply_repo.get_by_username.return_value = fake_application
    response = await client.post('/sellers/apply', json={'text': 'I want to be a seller'})
    assert response.status_code == 409

async def test_create_apply_401(client: AsyncClient, seller_application_service):
    response = await client.post('/sellers/apply', json={'text': 'I want to be a seller'})
    assert response.status_code == 401

async def test_get_apply_status_200(client: AsyncClient, verify_user, seller_application_service, mock_apply_repo, mock_user_repo, fake_user, fake_application):
    mock_user_repo.get_by_id.return_value = fake_user
    mock_apply_repo.get_by_username.return_value = fake_application
    response = await client.get('/sellers/apply/status')
    assert response.status_code == 200

async def test_get_apply_status_401(client: AsyncClient, seller_application_service):
    response = await client.get('/sellers/apply/status')
    assert response.status_code == 401

# --- shop ---

async def test_create_shop_200(client: AsyncClient, verify_seller, shop_service, mock_shop_repo, fake_shop):
    mock_shop_repo.get_by_shop_name.return_value = None
    mock_shop_repo.get_by_seller_id.return_value = None
    mock_shop_repo.save_shop.return_value = fake_shop
    response = await client.post('/sellers/shop', json={'name': 'test_shop', 'description': 'test description'})
    assert response.status_code == 200

async def test_create_shop_409_name(client: AsyncClient, verify_seller, shop_service, mock_shop_repo, fake_shop):
    mock_shop_repo.get_by_shop_name.return_value = fake_shop
    response = await client.post('/sellers/shop', json={'name': 'test_shop', 'description': 'test description'})
    assert response.status_code == 409

async def test_create_shop_409_already_has(client: AsyncClient, verify_seller, shop_service, mock_shop_repo, fake_shop):
    mock_shop_repo.get_by_shop_name.return_value = None
    mock_shop_repo.get_by_seller_id.return_value = fake_shop
    response = await client.post('/sellers/shop', json={'name': 'test_shop', 'description': 'test description'})
    assert response.status_code == 409

async def test_create_shop_403(client: AsyncClient, verify_user, shop_service, mock_shop_repo):
    response = await client.post('/sellers/shop', json={'name': 'test_shop', 'description': 'test description'})
    assert response.status_code == 403

async def test_create_shop_401(client: AsyncClient, shop_service, mock_shop_repo):
    response = await client.post('/sellers/shop', json={'name': 'test_shop', 'description': 'test description'})
    assert response.status_code == 401

async def test_get_my_shop_200(client: AsyncClient, verify_seller, shop_service, mock_shop_repo, fake_shop):
    mock_shop_repo.get_by_seller_id.return_value = fake_shop
    response = await client.get('/sellers/shop')
    assert response.status_code == 200

async def test_get_my_shop_404(client: AsyncClient, verify_seller, shop_service, mock_shop_repo):
    mock_shop_repo.get_by_seller_id.return_value = None
    response = await client.get('/sellers/shop')
    assert response.status_code == 404

async def test_get_my_shop_403(client: AsyncClient, verify_user, shop_service):
    response = await client.get('/sellers/shop')
    assert response.status_code == 403

async def test_get_my_shop_401(client: AsyncClient, shop_service):
    response = await client.get('/sellers/shop')
    assert response.status_code == 401

async def test_update_shop_200(client: AsyncClient, verify_seller, shop_service, mock_shop_repo, mock_user_repo, fake_user, fake_shop):
    mock_user_repo.get_by_id.return_value = fake_user
    mock_shop_repo.get_by_seller_id.return_value = fake_shop
    mock_shop_repo.update_shop.return_value = fake_shop
    with patch('services.shop_service.verify_password', return_value=True):
        response = await client.patch('/sellers/shop', json={'name': 'new_name'}, headers={'x-password': 'pass'})
    assert response.status_code == 200

async def test_update_shop_403_password(client: AsyncClient, verify_seller, shop_service, mock_shop_repo, mock_user_repo, fake_user):
    mock_user_repo.get_by_id.return_value = fake_user
    with patch('services.shop_service.verify_password', return_value=False):
        response = await client.patch('/sellers/shop', json={'name': 'new_name'}, headers={'x-password': 'wrong'})
    assert response.status_code == 403

async def test_update_shop_403_role(client: AsyncClient, verify_user, shop_service):
    response = await client.patch('/sellers/shop', json={'name': 'new_name'}, headers={'x-password': 'pass'})
    assert response.status_code == 403

async def test_update_shop_401(client: AsyncClient, shop_service):
    response = await client.patch('/sellers/shop', json={'name': 'new_name'}, headers={'x-password': 'pass'})
    assert response.status_code == 401

async def test_delete_shop_200(client: AsyncClient, verify_seller, shop_service, mock_shop_repo, mock_user_repo, fake_user, fake_shop):
    mock_user_repo.get_by_id.return_value = fake_user
    mock_shop_repo.get_by_seller_id.return_value = fake_shop
    with patch('services.shop_service.verify_password', return_value=True):
        response = await client.delete('/sellers/shop', headers={'x-password': 'pass'})
    assert response.status_code == 200

async def test_delete_shop_403_password(client: AsyncClient, verify_seller, shop_service, mock_user_repo, fake_user):
    mock_user_repo.get_by_id.return_value = fake_user
    with patch('services.shop_service.verify_password', return_value=False):
        response = await client.delete('/sellers/shop', headers={'x-password': 'wrong'})
    assert response.status_code == 403

async def test_delete_shop_403_role(client: AsyncClient, verify_user, shop_service):
    response = await client.delete('/sellers/shop', headers={'x-password': 'pass'})
    assert response.status_code == 403

async def test_delete_shop_401(client: AsyncClient, shop_service):
    response = await client.delete('/sellers/shop', headers={'x-password': 'pass'})
    assert response.status_code == 401

# --- moderation ---

async def test_submit_for_moderation_200(client: AsyncClient, verify_seller, moderation_service, mock_moder_repo, mock_shop_repo, fake_shop, fake_moderation):
    mock_shop_repo.get_by_seller_id.return_value = fake_shop
    mock_moder_repo.get_by_shop_id.return_value = None
    mock_moder_repo.create_request.return_value = fake_moderation
    response = await client.post('/sellers/shop/submit')
    assert response.status_code == 200

async def test_submit_for_moderation_409(client: AsyncClient, verify_seller, moderation_service, mock_moder_repo, mock_shop_repo, fake_shop, fake_moderation):
    mock_shop_repo.get_by_seller_id.return_value = fake_shop
    mock_moder_repo.get_by_shop_id.return_value = fake_moderation
    response = await client.post('/sellers/shop/submit')
    assert response.status_code == 409

async def test_submit_for_moderation_403(client: AsyncClient, verify_user, moderation_service):
    response = await client.post('/sellers/shop/submit')
    assert response.status_code == 403

async def test_submit_for_moderation_401(client: AsyncClient, moderation_service):
    response = await client.post('/sellers/shop/submit')
    assert response.status_code == 401

async def test_check_moder_status_200(client: AsyncClient, verify_seller, moderation_service, mock_moder_repo, mock_shop_repo, fake_shop, fake_moderation):
    mock_shop_repo.get_by_seller_id.return_value = fake_shop
    mock_moder_repo.get_by_shop_id.return_value = fake_moderation
    response = await client.get('/sellers/shop/moderation-status')
    assert response.status_code == 200

async def test_check_moder_status_403(client: AsyncClient, verify_user, moderation_service):
    response = await client.get('/sellers/shop/moderation-status')
    assert response.status_code == 403

async def test_check_moder_status_401(client: AsyncClient, moderation_service):
    response = await client.get('/sellers/shop/moderation-status')
    assert response.status_code == 401
