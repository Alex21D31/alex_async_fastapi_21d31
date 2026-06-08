from unittest.mock import AsyncMock
from httpx import AsyncClient

# --- GET /sellers/shop/products/{prod_name} ---

async def test_get_one_product_200(client: AsyncClient, verify_seller, shop_prod_service, mock_shop_repo, mock_shop_prod_repo, fake_shop, fake_shop_product):
    mock_shop_repo.get_by_seller_id.return_value = fake_shop
    mock_shop_prod_repo.get_one_product_for_seller_by_name.return_value = fake_shop_product
    response = await client.get('/sellers/shop/products/test_prod')
    assert response.status_code == 200

async def test_get_one_product_404(client: AsyncClient, verify_seller, shop_prod_service, mock_shop_repo, mock_shop_prod_repo, fake_shop):
    mock_shop_repo.get_by_seller_id.return_value = fake_shop
    mock_shop_prod_repo.get_one_product_for_seller_by_name.return_value = None
    response = await client.get('/sellers/shop/products/test_prod')
    assert response.status_code == 404

async def test_get_one_product_403(client: AsyncClient, verify_user, shop_prod_service):
    response = await client.get('/sellers/shop/products/test_prod')
    assert response.status_code == 403

async def test_get_one_product_401(client: AsyncClient, shop_prod_service):
    response = await client.get('/sellers/shop/products/test_prod')
    assert response.status_code == 401

async def test_get_all_products_403(client: AsyncClient, verify_user, shop_prod_service):
    response = await client.get('/sellers/shop/products')
    assert response.status_code == 403

async def test_get_all_products_401(client: AsyncClient, shop_prod_service):
    response = await client.get('/sellers/shop/products')
    assert response.status_code == 401

async def test_add_product_200_new(client: AsyncClient, verify_seller, shop_prod_service, mock_shop_repo, mock_shop_prod_repo, mock_product_repo, mock_cate_repo, fake_shop, fake_shop_product, fake_product, fake_category):
    mock_shop_repo.get_by_seller_id.return_value = fake_shop
    mock_shop_prod_repo.get_one_product_for_seller_by_name.return_value = None
    mock_product_repo.get_by_name.return_value = fake_product
    mock_cate_repo.get_by_name.return_value = fake_category
    mock_shop_prod_repo.save.return_value = fake_shop_product
    response = await client.post('/sellers/shop/products', json={
        'product_name': 'test_prod', 'shop_name': 'test_shop',
        'quantity': 5, 'price': 500, 'category_name': 'Electronics'
    })
    assert response.status_code == 200

async def test_add_product_200_existing(client: AsyncClient, verify_seller, shop_prod_service, mock_shop_repo, mock_shop_prod_repo, fake_shop, fake_shop_product):
    mock_shop_repo.get_by_seller_id.return_value = fake_shop
    mock_shop_prod_repo.get_one_product_for_seller_by_name.return_value = fake_shop_product
    mock_shop_prod_repo.update.return_value = fake_shop_product
    response = await client.post('/sellers/shop/products', json={
        'product_name': 'test_prod', 'shop_name': 'test_shop',
        'quantity': 5, 'price': 500, 'category_name': 'Electronics'
    })
    assert response.status_code == 200

async def test_add_product_400_quantity(client: AsyncClient, verify_seller, shop_prod_service, mock_shop_repo, fake_shop):
    mock_shop_repo.get_by_seller_id.return_value = fake_shop
    response = await client.post('/sellers/shop/products', json={
        'product_name': 'test_prod', 'shop_name': 'test_shop',
        'quantity': 201, 'price': 500, 'category_name': 'Electronics'
    })
    assert response.status_code == 400

async def test_add_product_403_wrong_shop(client: AsyncClient, verify_seller, shop_prod_service, mock_shop_repo, fake_shop):
    mock_shop_repo.get_by_seller_id.return_value = fake_shop
    response = await client.post('/sellers/shop/products', json={
        'product_name': 'test_prod', 'shop_name': 'other_shop',
        'quantity': 5, 'price': 500, 'category_name': 'Electronics'
    })
    assert response.status_code == 403

async def test_add_product_404_not_in_catalog(client: AsyncClient, verify_seller, shop_prod_service, mock_shop_repo, mock_shop_prod_repo, mock_product_repo, fake_shop):
    mock_shop_repo.get_by_seller_id.return_value = fake_shop
    mock_shop_prod_repo.get_one_product_for_seller_by_name.return_value = None
    mock_product_repo.get_by_name.return_value = None
    response = await client.post('/sellers/shop/products', json={
        'product_name': 'unknown', 'shop_name': 'test_shop',
        'quantity': 5, 'price': 500, 'category_name': 'Electronics'
    })
    assert response.status_code == 404

async def test_add_product_403_role(client: AsyncClient, verify_user, shop_prod_service):
    response = await client.post('/sellers/shop/products', json={
        'product_name': 'test_prod', 'shop_name': 'test_shop',
        'quantity': 5, 'price': 500, 'category_name': 'Electronics'
    })
    assert response.status_code == 403

async def test_update_product_200(client: AsyncClient, verify_seller, shop_prod_service, mock_shop_repo, mock_shop_prod_repo, fake_shop, fake_shop_product):
    mock_shop_repo.get_by_seller_id.return_value = fake_shop
    mock_shop_prod_repo.get_one_product_for_seller_by_name.return_value = fake_shop_product
    mock_shop_prod_repo.update.return_value = fake_shop_product
    response = await client.patch('/sellers/shop/products/test_prod', json={'quantity': 20, 'price': 600})
    assert response.status_code == 200

async def test_update_product_404(client: AsyncClient, verify_seller, shop_prod_service, mock_shop_repo, mock_shop_prod_repo, fake_shop):
    mock_shop_repo.get_by_seller_id.return_value = fake_shop
    mock_shop_prod_repo.get_one_product_for_seller_by_name.return_value = None
    response = await client.patch('/sellers/shop/products/test_prod', json={'quantity': 20, 'price': 600})
    assert response.status_code == 404

async def test_update_product_403(client: AsyncClient, verify_user, shop_prod_service):
    response = await client.patch('/sellers/shop/products/test_prod', json={'quantity': 20, 'price': 600})
    assert response.status_code == 403

async def test_update_product_401(client: AsyncClient, shop_prod_service):
    response = await client.patch('/sellers/shop/products/test_prod', json={'quantity': 20, 'price': 600})
    assert response.status_code == 401

async def test_delete_product_404(client: AsyncClient, verify_seller, shop_prod_service, mock_shop_repo, mock_shop_prod_repo, fake_shop):
    mock_shop_repo.get_by_seller_id.return_value = fake_shop
    mock_shop_prod_repo.get_one_product_for_seller_by_name.return_value = None
    response = await client.delete('/sellers/shop/products/test_prod')
    assert response.status_code == 404

async def test_delete_product_403(client: AsyncClient, verify_user, shop_prod_service):
    response = await client.delete('/sellers/shop/products/test_prod')
    assert response.status_code == 403

async def test_delete_product_401(client: AsyncClient, shop_prod_service):
    response = await client.delete('/sellers/shop/products/test_prod')
    assert response.status_code == 401
