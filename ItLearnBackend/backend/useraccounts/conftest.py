import pytest
from .models import User
from uuid import uuid4

@pytest.fixture(scope='function')
def create_user(db):
    """Fixture to create a user."""
    user = User.objects.create(
        id=uuid4(),
        email="testemail@test.com",
        name="Test User",
        is_verified=True,
        role=User.RoleChoises.USER.value,
    )
    user.set_password('test_password')
    user.save()
    return user