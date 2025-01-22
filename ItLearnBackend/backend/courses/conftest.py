import pytest
from .models import Course, CourseEnrollment
from useraccounts.models import User
from useraccounts.conftest import create_user
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from unittest.mock import Mock

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
        preview_image=preview_image,
        instructor=user,
        preview_video=preview_video,
        price=29.99,
    )
    return course


@pytest.fixture
def create_course_enrollment(db, create_course, create_user):
    course = create_course
    course_enrollment = CourseEnrollment.objects.create(
        created_by = course.instructor,
        course = course,
        total_price = course.price,
        stripe_checkout_id = Mock(return_value='mock_checkout_id')(),
    )
    return course_enrollment