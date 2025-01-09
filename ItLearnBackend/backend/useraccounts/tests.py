import pytest
from unittest.mock import patch
from rest_framework.test import APIClient
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator
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
    assert response.status_code == 200
    assert 'access' in response.data
    assert 'refresh' in response.data


@pytest.mark.django_db
@patch("useraccounts.api.send_reset_email.delay")
@patch("django_redis.cache.RedisCache.get", return_value=None)  # Patch Redis cache get
@patch("django_redis.cache.RedisCache.set", return_value=None)  # Patch Redis cache set
@patch("django_redis.cache.RedisCache.delete", return_value=None)  # Patch Redis cache delete
@pytest.mark.parametrize(
    "email, expected_status, expected_response_key",
    [
        ("valid@example.com", 200, "message"),  # Valid email
        ("invalid@example.com", 404, "detail"),  # Invalid email (doesn't exist)
        ("", 400, "email"),  # Missing email
    ]
)
def test_password_reset(
    mock_get,
    mock_set,
    mock_delete,
    mock_send_reset_email,
    api_client: APIClient,
    create_user,
    email,
    expected_status,
    expected_response_key,
):
    if email == "valid@example.com":
        email = create_user.email
        mock_send_reset_email.return_value = None

    response = api_client.post('/api/user/accounts/password/reset/', data={'email': email})

    # Assert the response status code and check for the expected key
    assert response.status_code == expected_status
    assert expected_response_key in response.data


@pytest.mark.django_db
def test_password_reset_confirm(api_client: APIClient, create_user):
    user = create_user
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = PasswordResetTokenGenerator().make_token(user)
    data = {
        'new_password1': 'CNX2023Posejdon',
        'new_password2': 'CNX2023Posejdon',
    }

    response = api_client.post(f'/api/user/accounts/password/reset/confirm/{uid}/{token}/', data=data)
    # Print response for debugging
    print("Response Status Code:", response.status_code)
    print("Response Data:", response.data)

    assert response.status_code == 200
    assert response.data["message"] == "Password has been reset successfully."

    # Verify the password was updated
    user.refresh_from_db()
    assert user.check_password("CNX2023Posejdon")



@pytest.mark.django_db
def test_profile_detail_view(api_client: APIClient, create_user):
    user = create_user
    api_client.force_authenticate(user=user)
    response = api_client.get('/api/user/accounts/profile/detail/')

    assert response.status_code == 200

    data = response.data

    assert data['name'] == "Test User"
    assert data['email'] == user.email
    assert data['avatar'] is None
    assert data['avatar_url'] == ''
    assert data['is_subscription_active'] is False

@pytest.mark.django_db
def test_profile_detail_update(api_client: APIClient, create_user):
    user = create_user
    api_client.force_authenticate(user=user)

    payload = {'name': 'Updated Name'}

    response = api_client.put('/api/user/accounts/profile/detail/', data=payload)

    assert response.status_code == 200

    assert response.data['name'] == 'Updated Name'