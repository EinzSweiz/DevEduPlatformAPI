from drf_yasg import openapi

# Schema for the course list response
get_all_courses_response = openapi.Response(
    description="A list of all courses",
    schema=openapi.Schema(
        type=openapi.TYPE_ARRAY,
        items=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'title': openapi.Schema(type=openapi.TYPE_STRING, description='Title of the course'),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='Course description'),
                'category': openapi.Schema(type=openapi.TYPE_STRING, description='Course category'),
                'instructor': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_STRING, description='Instructor ID'),
                        'email': openapi.Schema(type=openapi.TYPE_STRING, description='Instructor email'),
                        'name': openapi.Schema(type=openapi.TYPE_STRING, description='Instructor name'),
                    },
                ),
                'created_at': openapi.Schema(type=openapi.FORMAT_DATETIME, description='Creation date'),
            },
        ),
    ),
)


response_soft_delete = {
    200: openapi.Response(
        description="Course successfully unpublished",
        examples={"application/json": {"success": "Course unpublished successfully."}},
    ),
    404: openapi.Response(
        description="Course not found",
        examples={"application/json": {"error": "Course not found."}},
    ),
}

response_recovery_course = {
    200: openapi.Response(
        description="Course successfully restored",
        examples={"application/json": {"success": "Course restored successfully."}},
    ),
    404: openapi.Response(
        description="Course not found",
        examples={"application/json": {"error": "Course not found."}},
    ),
}

retrieve_course_response = openapi.Response(
    description="Retrieve course response",
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'title': openapi.Schema(
                type=openapi.TYPE_STRING, 
                description='Title of the course'
            ),
            'description': openapi.Schema(
                type=openapi.TYPE_STRING, 
                description='Course description'
            ),
            'category': openapi.Schema(
                type=openapi.TYPE_STRING, 
                description='Course category'
            ),
            'instructor': openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(
                        type=openapi.TYPE_STRING, 
                        description='Instructor ID'
                    ),
                    'email': openapi.Schema(
                        type=openapi.TYPE_STRING, 
                        description='Instructor email'
                    ),
                    'name': openapi.Schema(
                        type=openapi.TYPE_STRING, 
                        description='Instructor name'
                    ),
                },
                description='Instructor details'
            ),
            'created_at': openapi.Schema(
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATETIME,
                description='Creation date of the course'
            ),
            'videos': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                description='List of videos in the course',
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='Video ID'
                        ),
                        'title': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='Title of the video'
                        ),
                    },
                ),
            ),
            'progress': openapi.Schema(
                type=openapi.TYPE_OBJECT,
                description='User progress information',
                properties={
                    'current_video': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='ID of the current video being watched'
                    ),
                    'progress_percentage': openapi.Schema(
                        type=openapi.TYPE_NUMBER,
                        description='Percentage of the course completed'
                    ),
                    'completed_videos': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        description='IDs of completed videos',
                        items=openapi.Schema(
                            type=openapi.TYPE_STRING
                        ),
                    ),
                },
                nullable=True
            ),
        },
    ),
)
