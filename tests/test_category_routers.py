from httpx import AsyncClient

async def test_get_all_categories_redis_hit(client: AsyncClient, category_service, mock_redis_service, fake_category):
    mock_redis_service.get_categories_with_redis.return_value = ['Electronics', 'Food']
    response = await client.get('/products/category')
    assert response.status_code == 200
    assert 'Electronics' in response.json()

async def test_get_all_categories_db_hit(client: AsyncClient, category_service, mock_cate_repo, mock_redis_service, fake_category):
    mock_redis_service.get_categories_with_redis.return_value = None
    mock_cate_repo.get_all.return_value = [fake_category]
    response = await client.get('/products/category')
    assert response.status_code == 200
    assert response.json() == ['Electronics']

async def test_create_category_200(client: AsyncClient, verify_admin, category_service, mock_cate_repo, fake_category):
    mock_cate_repo.get_by_name.return_value = None
    mock_cate_repo.save.return_value = fake_category
    response = await client.post('/admin/categories', json={'name': 'Electronics', 'description': 'Electronic goods'})
    assert response.status_code == 200

async def test_create_category_409(client: AsyncClient, verify_admin, category_service, mock_cate_repo, fake_category):
    mock_cate_repo.get_by_name.return_value = fake_category
    response = await client.post('/admin/categories', json={'name': 'Electronics', 'description': 'Electronic goods'})
    assert response.status_code == 409

async def test_create_category_403(client: AsyncClient, verify_user, category_service, mock_cate_repo):
    response = await client.post('/admin/categories', json={'name': 'Electronics', 'description': 'Electronic goods'})
    assert response.status_code == 403

async def test_create_category_401(client: AsyncClient, category_service, mock_cate_repo):
    response = await client.post('/admin/categories', json={'name': 'Electronics', 'description': 'Electronic goods'})
    assert response.status_code == 401

async def test_delete_category_200(client: AsyncClient, verify_admin, category_service, mock_cate_repo, fake_category):
    mock_cate_repo.get_by_name.return_value = fake_category
    response = await client.delete('/admin/categories/Electronics')
    assert response.status_code == 200

async def test_delete_category_404(client: AsyncClient, verify_admin, category_service, mock_cate_repo):
    mock_cate_repo.get_by_name.return_value = None
    response = await client.delete('/admin/categories/Electronics')
    assert response.status_code == 404

async def test_delete_category_403(client: AsyncClient, verify_user, category_service, mock_cate_repo):
    response = await client.delete('/admin/categories/Electronics')
    assert response.status_code == 403

async def test_delete_category_401(client: AsyncClient, category_service, mock_cate_repo):
    response = await client.delete('/admin/categories/Electronics')
    assert response.status_code == 401
