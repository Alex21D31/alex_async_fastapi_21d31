from unittest.mock import AsyncMock, patch
from models import Role
from httpx import AsyncClient

async def test_get_all_users_200(client : AsyncClient, verify_admin, admin_service, mock_user_repo, fake_user):
    mock_user_repo.get_all.return_value = [fake_user]
    response = await client.get('/admin/users')
    assert response.status_code == 200
async def test_get_all_users_401(client : AsyncClient, admin_service, mock_user_repo, fake_user):
    mock_user_repo.get_all.return_value = [fake_user]
    response = await client.get('/admin/users')
    assert response.status_code == 401
async def test_get_all_users_403(client : AsyncClient, verify_user, admin_service, mock_user_repo, fake_user):
    mock_user_repo.get_all.return_value = [fake_user]
    response = await client.get('/admin/users')
    assert response.status_code == 403

async def test_get_user_by_id_200(client : AsyncClient, verify_admin, admin_service, mock_user_repo, fake_user):
    mock_user_repo.get_by_id.return_value = fake_user
    response = await client.get('/admin/users/5')
    assert response.status_code == 200
async def test_get_user_by_id_401(client : AsyncClient, admin_service, mock_user_repo, fake_user):
    mock_user_repo.get_by_id.return_value = fake_user
    response = await client.get('/admin/users/5')
    assert response.status_code == 401
async def test_get_user_by_id_403(client : AsyncClient, verify_user, admin_service, mock_user_repo, fake_user):
    mock_user_repo.get_by_id.return_value = fake_user
    response = await client.get('/admin/users/5')
    assert response.status_code == 403
async def test_get_user_by_id_404(client : AsyncClient, verify_admin, admin_service, mock_user_repo, fake_user):
    mock_user_repo.get_by_id.return_value = None
    response = await client.get('/admin/users/5')
    assert response.status_code == 404

async def test_get_new_role_200(client : AsyncClient, verify_creator, admin_service, mock_user_repo, fake_user):
    mock_user_repo.get_by_id.return_value = fake_user
    mock_user_repo.update.return_value = fake_user
    response = await client.patch('/admin/users/5/role?role=admin')
    assert response.status_code == 200
async def test_get_new_role_403(client : AsyncClient, verify_admin, admin_service, mock_user_repo, fake_user):
    mock_user_repo.update.return_value = fake_user
    response = await client.patch('/admin/users/5/role?role=admin')
    assert response.status_code == 403
async def test_get_new_role_401(client : AsyncClient, admin_service, mock_user_repo, fake_user):
    mock_user_repo.update.return_value = fake_user
    response = await client.patch('/admin/users/5/role?role=admin')
    assert response.status_code == 401
async def test_get_new_role_404(client : AsyncClient, verify_creator, admin_service, mock_user_repo, fake_user):
    mock_user_repo.get_by_id.return_value = None
    response = await client.patch('/admin/users/5/role?role=admin')
    assert response.status_code == 404

async def test_user_ban_200(client: AsyncClient, verify_creator, admin_service, mock_user_repo, fake_user):
    mock_user_repo.get_by_id.return_value = fake_user
    mock_user_repo.update.return_value = fake_user
    response = await client.patch('/admin/users/10/ban')
    assert response.status_code == 200
async def test_user_ban_403(client : AsyncClient, verify_user, admin_service, mock_user_repo, fake_target_user):
    mock_user_repo.get_by_id.return_value = fake_target_user
    mock_user_repo.update.return_value = fake_target_user
    response = await client.patch('/admin/users/10/ban')
    assert response.status_code == 403
async def test_user_ban_401(client : AsyncClient, admin_service, mock_user_repo, fake_target_user):
    mock_user_repo.get_by_id.return_value = fake_target_user
    mock_user_repo.update.return_value = fake_target_user
    response = await client.patch('/admin/users/10/ban')
    assert response.status_code == 401
async def test_user_ban_admin_bans_admin_403(client: AsyncClient, verify_admin, admin_service, mock_user_repo, fake_target_user):
    fake_target_user.role.value = 'admin'
    mock_user_repo.get_by_id.return_value = fake_target_user
    response = await client.patch('/admin/users/10/ban')
    assert response.status_code == 403
async def test_user_ban_400(client : AsyncClient, verify_admin, admin_service, mock_user_repo, fake_target_user):
    mock_user_repo.get_by_id.return_value = fake_target_user
    mock_user_repo.update.return_value = fake_target_user
    response = await client.patch('/admin/users/5/ban')
    assert response.status_code == 400
async def test_user_ban_404(client : AsyncClient, verify_admin, admin_service, mock_user_repo, fake_target_user):
    mock_user_repo.get_by_id.return_value = None
    mock_user_repo.update.return_value = fake_target_user
    response = await client.patch('/admin/users/10/ban')
    assert response.status_code == 404
async def test_user_ban_redis_error_200(client: AsyncClient, verify_creator, admin_service, mock_user_repo, mock_redis, fake_user):
    mock_user_repo.get_by_id.return_value = fake_user
    mock_user_repo.update.return_value = fake_user
    mock_redis.sadd.side_effect = Exception("Redis недоступен")
    response = await client.patch('/admin/users/10/ban')
    assert response.status_code == 200

async def test_get_all_orders_200(client : AsyncClient, verify_creator, admin_service, mock_product_repo, fake_order):
    mock_product_repo.get_all.return_value = [fake_order]
    response = await client.get('/admin/orders')
    assert response.status_code == 200

async def test_statistics_200(client : AsyncClient, verify_creator,mock_redis, admin_service):
    mock_redis.scard.return_value = 5
    response = await client.get('/admin/statistics')
    assert response.status_code == 200
async def test_statistics_403(client : AsyncClient, verify_user,mock_redis, admin_service):
    mock_redis.scard.return_value = 5
    response = await client.get('/admin/statistics')
    assert response.status_code == 403
async def test_statistics_401(client : AsyncClient,mock_redis, admin_service):
    mock_redis.scard.return_value = 5
    response = await client.get('/admin/statistics')
    assert response.status_code == 401

async def test_user_unban_200(client: AsyncClient, verify_creator, admin_service, mock_user_repo, fake_user):
    fake_user.role = Role.banned
    mock_user_repo.get_by_id.return_value = fake_user
    mock_user_repo.update.return_value = fake_user
    response = await client.patch('/admin/users/10/unban')
    assert response.status_code == 200
async def test_user_unban_401(client: AsyncClient, admin_service, mock_user_repo, fake_user):
    mock_user_repo.get_by_id.return_value = fake_user
    mock_user_repo.update.return_value = fake_user
    response = await client.patch('/admin/users/10/unban')
    assert response.status_code == 401
async def test_user_unban_403_1(client: AsyncClient, verify_user, admin_service, mock_user_repo, fake_user):
    mock_user_repo.get_by_id.return_value = fake_user
    mock_user_repo.update.return_value = fake_user
    response = await client.patch('/admin/users/10/unban')
    assert response.status_code == 403
async def test_user_unban_400(client: AsyncClient, verify_creator, admin_service, mock_user_repo, fake_user):
    mock_user_repo.get_by_id.return_value = fake_user
    mock_user_repo.update.return_value = fake_user
    response = await client.patch('/admin/users/5/unban')
    assert response.status_code == 400
async def test_user_unban_404(client: AsyncClient, verify_creator, admin_service, mock_user_repo, fake_user):
    mock_user_repo.get_by_id.return_value = None
    mock_user_repo.update.return_value = fake_user
    response = await client.patch('/admin/users/10/unban')
    assert response.status_code == 404
async def test_user_unban_403_2(client: AsyncClient, verify_creator, admin_service, mock_user_repo, fake_user):
    fake_user.role = Role.user 
    mock_user_repo.get_by_id.return_value = fake_user
    response = await client.patch('/admin/users/10/unban')
    assert response.status_code == 403
async def test_user_unban_redis_error_200(client: AsyncClient, verify_creator, admin_service, mock_user_repo, mock_redis, fake_user):
    fake_user.role = Role.banned
    mock_user_repo.get_by_id.return_value = fake_user
    mock_user_repo.update.return_value = fake_user
    mock_redis.srem.side_effect = Exception("Redis недоступен")
    response = await client.patch('/admin/users/10/unban')
    assert response.status_code == 200