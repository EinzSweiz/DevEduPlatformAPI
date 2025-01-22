from rest_framework.views import APIView
from .models import Course, Video, CoursesProgress
from rest_framework.generics import RetrieveAPIView
from .serializers import CourseDynamicSerializer
from core.messages import COURSE_MESSAGES
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from useraccounts.mixins import ParserMixinAPI
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from .swagger_usecases import response_recovery_course, response_soft_delete, get_all_courses_response, retrieve_course_response

class CourseAPI(ParserMixinAPI, APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        """
        Override to set different permissions for different methods.
        """
        if self.request.method == 'GET':
            return [AllowAny()]
        return super().get_permissions()

    def get_authenticators(self):
        """
        Override to set different authentication for different methods.
        """
        if self.request.method == 'GET':
            return []
        return super().get_authenticators()
    @swagger_auto_schema(
        operation_description='Create new course',
        request_body=CourseDynamicSerializer,
        responses={201: CourseDynamicSerializer},
    )
    def post(self, request):
        data = request.data
        serializer = CourseDynamicSerializer(data=data, fields=['title', 'description', 'category', 'instructor', 'preview_image', 'preview_video'])

        if serializer.is_valid():
            course = serializer.save(instructor=request.user)
            return Response({'success': COURSE_MESSAGES['create_success'], 'course': CourseDynamicSerializer(course).data,}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description='Retrieve a list of all available courses.',
        responses={200: get_all_courses_response}
    )
    def get(self, request):
        qs = Course.objects.all()
        serializer = CourseDynamicSerializer(
            qs,
            many=True,
            fields=['title', 'description', 'category', 'instructor', 'created_at', 'preview_image', 'preview_video']
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class CourseUpdateAPI(APIView):
    @swagger_auto_schema(
        operation_description='Soft delete a course',
        responses=response_soft_delete
    )
    def delete(self, request, pk):
        user = request.user
        try:
            course = Course.objects.get(pk=pk, instructor=user)
            course.soft_delete()
            return Response({'success': COURSE_MESSAGES['unpublish_success']}, status=status.HTTP_200_OK)
        except Course.DoesNotExist:
            return Response({'error': COURSE_MESSAGES['not_found']}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_description='Recover a soft-deleted course',
        responses=response_recovery_course
    )
    def patch(self, request, pk):
        user = request.user
        try:
            course = Course.all_objects.get(pk=pk, instructor=user)
            course.soft_revovery()
            return Response({'success': COURSE_MESSAGES['restore_success']}, status=status.HTTP_200_OK)
        except Course.DoesNotExist:
            return Response({'error': COURSE_MESSAGES['not_found']}, status=status.HTTP_404_NOT_FOUND)


class CourseDetailAPI(RetrieveAPIView):
    lookup_field = 'pk'
    queryset = Course.objects.prefetch_related('videos').all()
    serializer_class = CourseDynamicSerializer

    @swagger_auto_schema(
        operation_description='Retrieve detailed course information',
        responses={200: retrieve_course_response}
    )
    def get(self, request, *args, **kwargs):
        course = self.get_object()
        user = request.user

        # Fetch progress if the user is authenticated
        progress = None
        # Serialize course details
        serializer = self.get_serializer(
            course, 
            fields=['title', 'description', 'category', 'instructor', 'created_at', 'videos']
        )
        course_data = serializer.data

        # Add progress information
        course_data['progress'] = {
            "current_video": progress.current_video.id if progress and progress.current_video else None,
            "progress_percentage": progress.progress_percentage if progress else 0.0,
            "completed_videos": [video.id for video in progress.completed_videos.all()] if progress else [],
        } if progress else None

        return Response(course_data)
