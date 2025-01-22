from django.test import TestCase
import pytest
from rest_framework.test import APIClient
from useraccounts.conftest import create_user
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from PIL import Image

@pytest.mark.django_db
def test_create_course_api(api_client: APIClient, create_user):
    user = create_user
    image = Image.new('RGB', size=(100, 100), color='red')
    temp_image = BytesIO()
    image.save(temp_image, format='JPEG')
    temp_image.seek(0)
    preview_image = SimpleUploadedFile(name='test_preview_image.jpg', content=temp_image.read(), content_type='image/jpeg')
    temp_video = BytesIO()
    temp_video.write(b"0" * 1024 * 1024)
    temp_video.seek(0)
    preview_video = SimpleUploadedFile(name='test_preview_vide.mp4', content=temp_video.read(), content_type='video/mp4')

    data = {
        "title": "Advanced Python Programming",
        "description": "Learn advanced Python concepts.",
        "category": "Programming",
        'preview_image': preview_image,
        'preview_video': preview_video,
    }
    api_client.force_authenticate(user=user)
    response = api_client.post('/api/courses/create/', data=data)
    assert response.status_code == 201
    assert response.data['course']['title'] == 'Advanced Python Programming'
    assert response.data['success'] == 'Course successfully created.'


@pytest.mark.parametrize(
    "data,expected_status",
    [
        (  # Missing title
            {
                "description": "Learn advanced Python concepts.",
                "category": "Programming",
            },
            400,
        ),
        (  # Missing description
            {
                "title": "Advanced Python Programming",
                "category": "Programming",
            },
            400,
        ),
        (  # Missing category
            {
                "title": "Advanced Python Programming",
                "description": "Learn advanced Python concepts.",
            },
            400,
        ),
        (  # Empty fields
            {
                "title": "",
                "description": "",
                "category": "",
            },
            400,
        ),
        (  # Invalid data type for category
            {
                "title": "Advanced Python Programming",
                "description": "Learn advanced Python concepts.",
                "category": 123,  # Should be a string
            },
            400,
        ),
    ],
)
@pytest.mark.django_db
def test_create_course_invalid_cases(api_client: APIClient, create_user, data, expected_status):
    user = create_user
    api_client.force_authenticate(user=user)
    response = api_client.post('/api/courses/create/', data=data)
    assert response.status_code == expected_status


@pytest.mark.django_db
def test_get_courses_api(api_client: APIClient, create_course):
    course = create_course
    response = api_client.get('/api/courses/get/')
    data = response.data
    print(data)
    assert response.status_code == 200



@pytest.mark.django_db
def test_course_delete(api_client:APIClient, create_course, create_user):
    course = create_course
    user = create_user
    api_client.force_authenticate(user=user)
    response = api_client.delete(f'/api/courses/soft_delete/{course.id}/')
    data = response.data

    assert response.status_code == 200
    assert data['success'] == 'Course successfully unpublished.'

@pytest.mark.django_db
def test_course_recover(api_client:APIClient, create_course, create_user):
    course = create_course
    user = create_user
    api_client.force_authenticate(user=user)
    response = api_client.patch(f'/api/courses/recovery/{course.id}/')
    data = response.data
    assert response.status_code == 200

@pytest.mark.django_db
def test_course_detailes(api_client:APIClient, create_course, create_user):
    user = create_user
    course = create_course
    api_client.force_authenticate(user=user)
    response = api_client.get(f'/api/courses/detailed/{course.id}/')
    data = response.data
    assert response.status_code == 200
