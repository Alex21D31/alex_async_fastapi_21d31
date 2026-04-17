from unittest.mock import patch, MagicMock
from httpx import AsyncClient

async def test_get_me_200(client : AsyncClient, fake_user, mock_user_repo, verify_user, user_service):
    mock_user_repo.get_by_id.return_value = fake_user
    response = await client.get('/users/me')
    assert response.status_code == 200
async def test_get_me_401(client : AsyncClient, fake_user, mock_user_repo, user_service):
    mock_user_repo.get_by_id.return_value = fake_user
    response = await client.get('/users/me')
    assert response.status_code == 401
async def test_get_me_404(client : AsyncClient, mock_user_repo,verify_user, user_service):
    mock_user_repo.get_by_id.return_value = None
    response = await client.get('/users/me')
    assert response.status_code == 404

async def test_update_me_200(client : AsyncClient, fake_user, mock_user_repo, verify_user, user_service):
    mock_user_repo.update.return_value = fake_user
    with patch('services.user_service.verify_password', return_value = True):
        response = await client.patch('/users/me', json={'name' : 'alex', 'phone' : '13891631768', 'email' : 'eiq@.eq'}, headers={'x-password' : 'old_pass'})
        assert response.status_code == 200
async def test_update_me_403(client : AsyncClient, fake_user, mock_user_repo, verify_user, user_service):
    mock_user_repo.update.return_value = fake_user
    with patch('services.user_service.verify_password', return_value = False):
        response = await client.patch('/users/me', json={'name' : 'alex', 'phone' : '13891631768', 'email' : 'eiq@.eq'}, headers={'x-password' : 'old_pass'})
        assert response.status_code == 403
async def test_update_me_404(client : AsyncClient, fake_user, mock_user_repo, verify_user, user_service):
    mock_user_repo.get_by_id.return_value = None
    mock_user_repo.update.return_value = fake_user
    with patch('services.user_service.verify_password', return_value = True):
        response = await client.patch('/users/me', json={'name' : 'alex', 'phone' : '13891631768', 'email' : 'eiq@.eq'}, headers={'x-password' : 'old_pass'})
        assert response.status_code == 404
async def test_update_me_401(client : AsyncClient, fake_user, mock_user_repo, user_service):
    mock_user_repo.update.return_value = fake_user
    with patch('services.user_service.verify_password', return_value = True):
        response = await client.patch('/users/me', json={'name' : 'alex', 'phone' : '13891631768', 'email' : 'eiq@.eq'}, headers={'x-password' : 'old_pass'})
        assert response.status_code == 401 

@patch('services.user_service.change_password_email.delay', new_callable=MagicMock)
async def test_update_password_200(mock_kafka,client : AsyncClient, fake_user, verify_user,mock_user_repo, user_service):
    mock_user_repo.save.return_value = fake_user
    with patch('services.user_service.verify_password', return_value = True):
        with patch('services.user_service.hash_password', return_value = 'hash_password'):
            response = await client.patch('/users/me/password', json={'old_password' : 'old_pass', 'new_password' : 'new_pass'})
            assert response.status_code == 200
async def test_update_password_401(client : AsyncClient, fake_user,mock_user_repo, user_service):
    mock_user_repo.save.return_value = fake_user
    with patch('services.user_service.verify_password', return_value = True):
        with patch('services.user_service.hash_password', return_value = 'hash_password'):
            response = await client.patch('/users/me/password', json={'old_password' : 'old_pass', 'new_password' : 'new_pass'})
            assert response.status_code == 401
async def test_update_password_404(client : AsyncClient, fake_user, verify_user,mock_user_repo, user_service):
    mock_user_repo.get_by_id.return_value = None
    mock_user_repo.save.return_value = fake_user
    with patch('services.user_service.verify_password', return_value = True):
        with patch('services.user_service.hash_password', return_value = 'hash_password'):
            response = await client.patch('/users/me/password', json={'old_password' : 'old_pass', 'new_password' : 'new_pass'})
            assert response.status_code == 404
async def test_update_password_403(client : AsyncClient, fake_user, verify_user,mock_user_repo, user_service):
    mock_user_repo.save.return_value = fake_user
    with patch('services.user_service.verify_password', return_value = False):
        with patch('services.user_service.hash_password', return_value = 'hash_password'):
            response = await client.patch('/users/me/password', json={'old_password' : 'old_pass', 'new_password' : 'new_pass'})
            assert response.status_code == 403

async def test_delete_me_200(client : AsyncClient, fake_user, verify_user,mock_user_repo, user_service):
    mock_user_repo.get_by_id.return_value = fake_user
    with patch('services.user_service.verify_password', return_value = True):
        response = await client.delete('/users/me', headers={'x-password' : 'old_pass'})
        assert response.status_code == 200
async def test_delete_me_401(client : AsyncClient, fake_user,mock_user_repo, user_service):
    mock_user_repo.get_by_id.return_value = fake_user
    with patch('services.user_service.verify_password', return_value = True):
        response = await client.delete('/users/me', headers={'x-password' : 'old_pass'})
        assert response.status_code == 401
async def test_delete_me_403(client : AsyncClient, fake_user, verify_user,mock_user_repo, user_service):
    mock_user_repo.get_by_id.return_value = fake_user
    with patch('services.user_service.verify_password', return_value = False):
        response = await client.delete('/users/me', headers={'x-password' : 'old_pass'})
        assert response.status_code == 403
async def test_delete_me_404(client : AsyncClient, fake_user, verify_user,mock_user_repo, user_service):
    mock_user_repo.get_by_id.return_value = None
    with patch('services.user_service.verify_password', return_value = True):
        response = await client.delete('/users/me', headers={'x-password' : 'old_pass'})
        assert response.status_code == 404


