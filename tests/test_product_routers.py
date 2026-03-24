from unittest.mock import AsyncMock, patch
from httpx import AsyncClient

async def test_get_all_prod(client : AsyncClient, mock_product_repo, product_service, fake_product):
    mock_product_repo.get_all.return_value = [fake_product]
    response = await client.get('/products')
    assert response.status_code == 200

async def test_get_prod_by_id_200(client : AsyncClient, mock_product_repo, product_service, fake_product):
    mock_product_repo.get_by_id.return_value = fake_product
    response = await client.get('/products/5')
    assert response.status_code == 200
async def test_get_prod_by_id_404(client : AsyncClient, mock_product_repo, product_service, fake_product):
    mock_product_repo.get_by_id.return_value = None
    response = await client.get('/products/5')
    assert response.status_code == 404

async def test_create_product_200(client : AsyncClient, mock_product_repo,verify_admin, product_service, fake_product):
    mock_product_repo.get_by_name.return_value = None
    mock_product_repo.save.return_value = fake_product
    response = await client.post('/products', json={'name' : 'apple', 'description' : 'dadad', 'price' : 123131, 'quantity' : 414})
    assert response.status_code == 200
async def test_create_product_403(client : AsyncClient, mock_product_repo,verify_user, product_service, fake_product):
    mock_product_repo.get_by_name.return_value = None
    response = await client.post('/products', json={'name' : 'apple', 'description' : 'dadad', 'price' : 123131, 'quantity' : 414})
    assert response.status_code == 403
async def test_create_product_409(client : AsyncClient, mock_product_repo,verify_admin, product_service, fake_product):
    mock_product_repo.get_by_name.return_value = fake_product
    response = await client.post('/products', json={'name' : 'apple', 'description' : 'dadad', 'price' : 123131, 'quantity' : 414})
    assert response.status_code == 409

async def test_patch_product_200(client : AsyncClient, mock_product_repo,verify_admin, product_service, fake_product):
        mock_product_repo.update.return_value = fake_product
        reponse = await client.patch('/products/5', json={'name' : 'apple', 'description' : 'dada', 'price' : 1313, 'quantity' : 11})
        assert reponse.status_code == 200
async def test_patch_product_403(client : AsyncClient, mock_product_repo,verify_user, product_service, fake_product):
        mock_product_repo.update.return_value = fake_product
        reponse = await client.patch('/products/5', json={'name' : 'apple', 'description' : 'dada', 'price' : 1313, 'quantity' : 11})
        assert reponse.status_code == 403
async def test_patch_product_404(client : AsyncClient, mock_product_repo,verify_admin, product_service, fake_product):
        mock_product_repo.get_by_id.return_value = None
        reponse = await client.patch('/products/5', json={'name' : 'apple', 'description' : 'dada', 'price' : 1313, 'quantity' : 11})
        assert reponse.status_code == 404

async def test_delete_product_200(client : AsyncClient, mock_product_repo,verify_admin, product_service, fake_product):
    mock_product_repo.get_by_id.return_value = fake_product
    response = await client.delete('/products/5')
    assert response.status_code == 200
async def test_delete_product_403(client : AsyncClient, mock_product_repo,verify_user, product_service, fake_product):
    mock_product_repo.get_by_id.return_value = fake_product
    response = await client.delete('/products/5')
    assert response.status_code == 403
async def test_delete_product_404(client : AsyncClient, mock_product_repo,verify_admin, product_service, fake_product):
    mock_product_repo.get_by_id.return_value = None
    response = await client.delete('/products/5')
    assert response.status_code == 404