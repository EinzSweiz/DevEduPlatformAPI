from django.urls import path
from . import api

urlpatterns = [
    path('create/', api.CourseAPI.as_view(), name='create_course_api'),
    path('get/', api.CourseAPI.as_view(), name='get_courses_api'),
    path('soft_delete/<int:pk>/', api.CourseUpdateAPI.as_view(), name='soft_delete_course_api'),
    path('recovery/<int:pk>/', api.CourseUpdateAPI.as_view(), name='recover_course_api'),
    path('detailed/<int:pk>/', api.CourseDetailAPI.as_view(), name='detailed_course_api'),
]