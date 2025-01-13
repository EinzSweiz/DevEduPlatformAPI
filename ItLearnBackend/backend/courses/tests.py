from django.test import TestCase
import pytest
from rest_framework.test import APIClient
from useraccounts.conftest import create_user

@pytest.mark.django_db
def test_create_course_api(api_client: APIClient, create_user):
    user = create_user
    data = {
        "title": "Advanced Python Programming",
        "description": "Learn advanced Python concepts.",
        "category": "Programming",
    }
    api_client.force_authenticate(user=user)
    response = api_client.post('/api/courses/create/', data=data)
    assert response.status_code == 201


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
    assert response.status_code == 200



@pytest.mark.django_db
def test_course_delete(api_client:APIClient, create_course, create_user):
    course = create_course
    user = create_user
    api_client.force_authenticate(user=user)
    response = api_client.delete(f'/api/courses/soft_delete/{course.id}/')
    data = response.data

    assert response.status_code == 200
    assert data['success'] == 'Course successfully unpublished'

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
    print('Response:', response)
    data = response.data
    print('Data:', data)
    assert response.status_code == 200
