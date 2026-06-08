from httpx import AsyncClient

async def test_rate_limit_429(client: AsyncClient, mock_redis):
    mock_redis.zcard.return_value = 6
    response = await client.get('/auth/login')
    assert response.status_code == 429