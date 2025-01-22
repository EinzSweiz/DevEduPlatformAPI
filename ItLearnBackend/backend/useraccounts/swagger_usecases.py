from drf_yasg import openapi

login_request_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username'),
        'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email', format='email'),
        'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password', format='password'),
    },
    required=['username', 'password'],  # Define required fields
)

login_responses = {
    200: openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'access': openapi.Schema(type=openapi.TYPE_STRING, description='Access token'),
            'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token'),
            'is_deleted': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Indicates if the user is deleted'),
        },
    ),
    401: openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'detail': openapi.Schema(type=openapi.TYPE_STRING, description='Error message'),
        },
    ),
}

# Reusable Schema Components
email_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "email": openapi.Schema(
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_EMAIL,
            description="User's email address"
        )
    },
    required=["email"]
)

password_reset_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "new_password1": openapi.Schema(
            type=openapi.TYPE_STRING,
            description="New password"
        ),
        "new_password2": openapi.Schema(
            type=openapi.TYPE_STRING,
            description="Repeat new password"
        )
    },
    required=["new_password1", "new_password2"]
)

profile_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "email": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
        "name": openapi.Schema(type=openapi.TYPE_STRING),
        "avatar": openapi.Schema(type=openapi.TYPE_STRING, description="Avatar URL"),
        "bio": openapi.Schema(type=openapi.TYPE_STRING, description="User bio", nullable=True),
        "location": openapi.Schema(type=openapi.TYPE_STRING, description="User location", nullable=True),
        "phone_number": openapi.Schema(type=openapi.TYPE_STRING, description="Phone number", nullable=True),
        "linkedin": openapi.Schema(type=openapi.TYPE_STRING, description="LinkedIn profile URL", nullable=True),
        "github": openapi.Schema(type=openapi.TYPE_STRING, description="GitHub profile URL", nullable=True),
        "subscription_plan": openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
        "subscription_start_date": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, nullable=True),
        "subscription_end_date": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, nullable=True),
        "is_subscription_active": openapi.Schema(type=openapi.TYPE_BOOLEAN),
    }
)

# Reusable Parameter Components
email_param = [openapi.Parameter(
    name="email",
    in_=openapi.IN_FORM,
    description="User's email address",
    type=openapi.TYPE_STRING,
    required=True,
)]

password_reset_params = [
    openapi.Parameter(
        name="new_password1",
        in_=openapi.IN_FORM,
        description="New password",
        type=openapi.TYPE_STRING,
        required=True,
    ),
    openapi.Parameter(
        name="new_password2",
        in_=openapi.IN_FORM,
        description="Repeat new password",
        type=openapi.TYPE_STRING,
        required=True,
    ),
]

profile_update_params = [
    openapi.Parameter(
        name="email",
        in_=openapi.IN_FORM,
        type=openapi.TYPE_STRING,
        description="User's email address",
        required=False,
    ),
    openapi.Parameter(
        name="name",
        in_=openapi.IN_FORM,
        type=openapi.TYPE_STRING,
        description="User's name",
        required=False,
    ),
    openapi.Parameter(
        name="avatar",
        in_=openapi.IN_FORM,
        type=openapi.TYPE_FILE,
        description="Avatar file",
        required=False,
    ),
    openapi.Parameter(
        name="bio",
        in_=openapi.IN_FORM,
        type=openapi.TYPE_STRING,
        description="User bio",
        required=False,
    ),
    openapi.Parameter(
        name="location",
        in_=openapi.IN_FORM,
        type=openapi.TYPE_STRING,
        description="User location",
        required=False,
    ),
    openapi.Parameter(
        name="phone_number",
        in_=openapi.IN_FORM,
        type=openapi.TYPE_STRING,
        description="Phone number",
        required=False,
    ),
    openapi.Parameter(
        name="linkedin",
        in_=openapi.IN_FORM,
        type=openapi.TYPE_STRING,
        description="LinkedIn profile URL",
        required=False,
    ),
    openapi.Parameter(
        name="github",
        in_=openapi.IN_FORM,
        type=openapi.TYPE_STRING,
        description="GitHub profile URL",
        required=False,
    ),
]
