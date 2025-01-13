import pytest
from .models import Course
from useraccounts.models import User
from useraccounts.conftest import create_user
@pytest.fixture
def create_course(db, create_user):
    user = create_user
    # Create a sample course
    course = Course.objects.create(
        title="Test Course",
        description="This is a test course description.",
        category="Test Category",
        instructor=user,
    )
    return course
