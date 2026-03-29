from httpx import AsyncClient

async def test_rate_limit_429(client: AsyncClient, mock_redis):
    mock_redis.zcard.return_value = 6
    response = await client.get('/auth/login')
    assert response.status_code == 429

async def test_rate_limit_products_pass(client: AsyncClient, mock_redis, product_service, mock_product_repo):
    mock_redis.zcard.return_value = 6
    mock_product_repo.get_all.return_value = []
    response = await client.get('/products')
    assert response.status_code == 200