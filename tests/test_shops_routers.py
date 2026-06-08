from httpx import AsyncClient

async def test_get_all_verified_shops_200(client: AsyncClient, shop_service, mock_shop_repo, fake_shop):
    mock_shop_repo.get_all_verified.return_value = [fake_shop]
    response = await client.get('/shops')
    assert response.status_code == 200

async def test_get_all_verified_shops_empty(client: AsyncClient, shop_service, mock_shop_repo):
    mock_shop_repo.get_all_verified.return_value = []
    response = await client.get('/shops')
    assert response.status_code == 200
    assert response.json() == []

async def test_get_shop_by_name_200(client: AsyncClient, shop_service, mock_shop_repo, fake_shop):
    mock_shop_repo.get_by_shop_name.return_value = fake_shop
    response = await client.get('/shops/test_shop')
    assert response.status_code == 200

async def test_get_shop_by_name_404(client: AsyncClient, shop_service, mock_shop_repo):
    mock_shop_repo.get_by_shop_name.return_value = None
    response = await client.get('/shops/test_shop')
    assert response.status_code == 404
