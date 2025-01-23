from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

payment_success_schema = swagger_auto_schema(
    operation_description="Handle the success callback for payment or subscription sessions from Stripe.",
    manual_parameters=[
        openapi.Parameter(
            'session_id',
            openapi.IN_QUERY,
            description="The session ID from Stripe to validate and process the payment or subscription.",
            type=openapi.TYPE_STRING,
            required=True,
        )
    ],
    responses={
        200: openapi.Response(
            description="Payment or subscription successfully processed.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "success": openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "subscription_id": openapi.Schema(
                                type=openapi.TYPE_STRING, 
                                description="The Stripe subscription ID, if applicable."
                            ),
                            "customer": openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "id": openapi.Schema(type=openapi.TYPE_STRING, description="Customer ID in Stripe."),
                                    "email": openapi.Schema(type=openapi.TYPE_STRING, description="Customer email."),
                                    "name": openapi.Schema(type=openapi.TYPE_STRING, description="Customer name."),
                                },
                            ),
                            "enrollment": openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "id": openapi.Schema(type=openapi.TYPE_STRING, description="Enrollment ID."),
                                    "price": openapi.Schema(type=openapi.TYPE_NUMBER, format="float", description="Price of the course."),
                                    "has_paid": openapi.Schema(type=openapi.TYPE_BOOLEAN, description="Payment status."),
                                    "course": openapi.Schema(type=openapi.TYPE_STRING, description="Title of the course."),
                                },
                            ),
                        },
                    )
                },
            ),
        ),
        400: openapi.Response(description="Missing session_id in the request."),
        404: openapi.Response(description="Course not found or not published."),
        500: openapi.Response(description="Unhandled server error or Stripe API failure."),
    }
)
payment_cancel_schema = swagger_auto_schema(
    operation_description="Handle the cancel callback for payment or subscription sessions from Stripe.",
    manual_parameters=[
        openapi.Parameter(
            'pk',
            openapi.IN_PATH,
            description="The ID of the enrollment being canceled.",
            type=openapi.TYPE_STRING,
            required=True,
        )
    ],
    responses={
        200: openapi.Response(
            description="The payment cancellation was successfully handled.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "error": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Message indicating the payment cancellation.",
                    )
                }
            )
        ),
        400: openapi.Response(description="Bad request, e.g., invalid or missing parameters."),
        404: openapi.Response(description="Enrollment ID not found."),
    }
)
