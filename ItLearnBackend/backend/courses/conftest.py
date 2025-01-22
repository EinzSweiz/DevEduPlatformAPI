import pytest
from .models import Course
from useraccounts.models import User
from useraccounts.conftest import create_user
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

@pytest.fixture
def create_course(db, create_user):
    user = create_user
    image = Image.new('RGB', size=(100, 100), color='blue')
    temp_image = BytesIO()
    image.save(temp_image, format='JPEG')
    temp_image.seek(0)
    preview_image = SimpleUploadedFile('test_preview_image.jpg', content=temp_image.read(), content_type='image/jpeg')

    temp_video = BytesIO()
    temp_video.write(b'0' * 1024 * 1024)  # 1 MB dummy video
    temp_video.seek(0)
    preview_video = SimpleUploadedFile('test_preview_video.mp4', content=temp_video.read(), content_type='video/mp4')

    # Create a sample course
    course = Course.objects.create(
        title="Test Course",
        description="This is a test course description.",
        category="Test Category",
        instructor=user,
        preview_image=preview_image,
        preview_video=preview_video
    )
    return course
