import pytest
from unittest.mock import patch
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from PIL import Image

@pytest.mark.parametrize(
    "data,expected_status",
    [
        (
            {
                "name": "Test User",
                "email": "testuser@example.com",
                "password1": "strong_password123",
                "password2": "strong_password123",
                "avatar": None
            },
            201,
        ),
        (
            {
                "name": "Test User",
                "email": "testuser@example.com",
                "password1": "password",
                "password2": "password",
                "avatar": None
            },
            400,  # Weak password
        ),
        (
            {
                "name": "Test User",
                "email": "invalidemail",
                "password1": "strong_password123",
                "password2": "strong_password123",
                "avatar": None
            },
            400,  # Invalid email
        ),
    ],
)
@pytest.mark.django_db
@patch("useraccounts.serializers.send_confirmation_message.delay")
@patch("django_redis.cache.RedisCache.get", return_value=None)  # Patch Redis cache get
@patch("django_redis.cache.RedisCache.set", return_value=None)  # Patch Redis cache set
@patch("django_redis.cache.RedisCache.delete", return_value=None)  # Patch Redis cache delete
def test_registration_user(
    mock_redis_delete,
    mock_redis_set,
    mock_redis_get,
    mock_send_confirmation_message,
    api_client: APIClient,
    data,
    expected_status
):
    if data["avatar"] is None:
        image = Image.new("RGB", (100, 100), color="red")
        temp_file = BytesIO()
        image.save(temp_file, format='JPEG')
        temp_file.seek(0)
        data["avatar"] = SimpleUploadedFile(
            name='test_avatar.jpg', 
            content=temp_file.read(), 
            content_type='image/jpeg'
        )

    mock_send_confirmation_message.return_value = None

    response = api_client.post('/api/user/accounts/register/', data=data)

    assert response.status_code == expected_status


@pytest.mark.django_db
def test_login_user(api_client: APIClient, create_user):
    user = create_user
    data = {'email': 'testemail@test.com', 'password': 'test_password'}
    
    response = api_client.post('/api/user/accounts/login/', data=data)

    # Log the response data to see what is returned
    print('Response Data:', response.data)

    assert response.status_code == 200
    assert 'access' in response.data
    assert 'refresh' in response.data
