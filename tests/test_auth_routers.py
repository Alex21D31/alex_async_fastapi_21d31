from unittest.mock import  patch

async def test_register_200(client, mock_user_repo, user_service, fake_user):
    mock_user_repo.get_by_email.return_value = None
    mock_user_repo.save.return_value = fake_user
    data = {'email': 'alex@test.com', 'name': 'alex', 'password': 'pass', 'phone': '123'}
    response = await client.post('/auth/register', json=data)
    assert response.status_code == 200

async def test_register_409(client, mock_user_repo, user_service, fake_user):
    mock_user_repo.get_by_email.return_value = fake_user
    data = {'name': 'alex','phone': '123','email': 'alex@test.com',  'password': 'pass',}
    response = await client.post('/auth/register', json=data)
    assert response.status_code == 409

async def test_login_200(client, mock_user_repo, user_service, fake_user_for_login):
    mock_user_repo.get_by_email.return_value = fake_user_for_login
    data = {'email' : 'alex@test.com', 'password': 'pass'}
    with patch('services.user_service.verify_password', return_value=True), \
         patch('services.user_service.create_access_token', return_value='access_token'), \
         patch('services.user_service.create_refresh_token', return_value='refresh_token'):
        response = await client.post('/auth/login', json=data)
        assert response.status_code == 200

async def test_login_401_1(client, mock_user_repo, user_service):
    mock_user_repo.get_by_email.return_value = None
    data = {'email' : 'alex@test.com', 'password': 'pass'}
    response = await client.post('/auth/login', json=data)
    assert response.status_code == 401

async def test_login_401_2(client, mock_user_repo, user_service, fake_user_for_login):
    mock_user_repo.get_by_email.return_value = fake_user_for_login
    data = {'email' : 'alex@test.com', 'password': 'pass'}
    with patch('services.user_service.verify_password', return_value=False):
        response = await client.post('/auth/login', json=data)
        assert response.status_code == 401

async def test_login_409(client, mock_user_repo, user_service,fake_user_banned):
    mock_user_repo.get_by_email.return_value = fake_user_banned
    data = {'email' : 'alex@test.com', 'password': 'pass'}
    response = await client.post('/auth/login', json=data)
    assert response.status_code == 409

