import stripe
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
import logging
from courses.models import Course, CourseEnrollment
from .models import Subscription

stripe.api_key = settings.STRIPE_SECRET_KEY

logger = logging.getLogger('default')


class CheckoutSessionCreate(APIView):
    def post(self, request, *args, **kwargs):
        logger.info("Starting CheckoutSessionCreate API call")
        course_id = request.data.get('course_id')
        if not course_id:
            logger.warning("Course ID is missing in request")
            return Response({'error': 'Course ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            course = Course.objects.get(id=course_id)
            logger.info(f"Fetched course with ID: {course_id}")

            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                mode='payment',
                line_items=[
                    {
                        'price_data': {
                            'currency': 'usd',
                            'product_data': {
                                'name': course.title,
                                'description': course.description,
                            },
                            'unit_amount': int(float(course.price) * 100),
                        },
                        'quantity': 1,
                    }
                ],
                metadata={
                    'course_id': course.id,
                    'user_id': request.user.id,
                    'total_price': course.price,
                },
                customer_creation='always',
                success_url=settings.FRONTEND_URL + "/payment-success?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=f"{settings.FRONTEND_URL}/payment-cancel",
            )
            logger.info(f"Stripe session created successfully: {session.id}")
            return Response({'checkout_url': session.url}, status=status.HTTP_200_OK)

        except Course.DoesNotExist:
            logger.error(f"Course with ID {course_id} not found or not published")
            return Response({'error': 'Course not found or not published'}, status=status.HTTP_404_NOT_FOUND)
        except stripe.error.StripeError as e:
            logger.error(f"Stripe API error: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentSuccessAPI(APIView):
    def get(self, request):
        logger.info("Starting PaymentSuccessAPI call")
        checkout_session_id = request.GET.get("session_id")
        if not checkout_session_id:
            logger.warning("Session ID is missing in request")
            return Response({"error": "Missing session_id"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            session = stripe.checkout.Session.retrieve(checkout_session_id)
            logger.info(f"Retrieved Stripe session: {checkout_session_id}")
            customer_id = session.customer
            customer = stripe.Customer.retrieve(customer_id)
            metadata = session.metadata

            if session.mode == "subscription":
                subscription_id = session.subscription
                Subscription.objects.create(
                    user=request.user,
                    stripe_subscription_id=subscription_id,
                    status="active",
                    current_period_end=subscription_id.get('current_period_end', None),
                )
                logger.info(f"Subscription created for user {request.user.id} with subscription ID: {subscription_id}")
                return Response(
                    {
                        "success": {
                            "subscription_id": subscription_id,
                            "customer": {
                                "id": customer.id,
                                "email": customer.email,
                                "name": customer.name,
                            },
                        }
                    },
                    status=status.HTTP_200_OK,
                )

            elif session.mode == "payment":
                course_id = metadata.get("course_id")
                course_instance = Course.objects.get(pk=course_id)

                enrollment = CourseEnrollment.objects.create(
                    created_by=request.user,
                    course=course_instance,
                    total_price=metadata["total_price"],
                    has_paid=True,
                )
                logger.info(f"Enrollment created for course {course_id} and user {request.user.id}")
                return Response(
                    {
                        "success": {
                            "enrollment": {
                                "id": enrollment.id,
                                "price": enrollment.total_price,
                                "has_paid": enrollment.has_paid,
                                "course": enrollment.course.title,
                            },
                            "customer": {
                                "id": customer.id,
                                "email": customer.email,
                                "name": customer.name,
                            },
                        }
                    },
                    status=status.HTTP_200_OK,
                )

        except Course.DoesNotExist:
            logger.error(f"Course not found during payment success for session: {checkout_session_id}")
            return Response({"error": "Course not found or not published"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(f"Unhandled error in PaymentSuccessAPI: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentCancel(APIView):
    def get(self, request, pk):
        logger.info(f"Starting PaymentCancel API call for enrollment ID: {pk}")
        enrollment = get_object_or_404(CourseEnrollment, pk=pk)
        logger.info(f"Payment cancellation processed for enrollment ID: {pk}")
        return Response({'error': f'Payment for reservation {enrollment.id} was canceled.'}, status=status.HTTP_400_BAD_REQUEST)


class SubscriptionCheckoutSessionCreate(APIView):
    def post(self, request, *args, **kwargs):
        logger.info("Starting SubscriptionCheckoutSessionCreate API call")
        price_id = request.data.get("price_id")

        if not price_id:
            logger.warning("Price ID is missing in request")
            return Response({"error": "Price ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                mode='subscription',
                line_items=[
                    {
                        "price": price_id,
                        "quantity": 1,
                    }
                ],
                metadata={
                    "user_id": request.user.id,
                },
                success_url=settings.FRONTEND_URL + "/payment-success?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=f"{settings.FRONTEND_URL}/payment-cancel",
            )
            logger.info(f"Stripe subscription session created successfully: {session.id}")
            return Response({"checkout_url": session.url}, status=status.HTTP_200_OK)
        except stripe.error.StripeError as e:
            logger.error(f"Stripe API error in subscription session creation: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StripeWebhook(APIView):
    def post(self, request):
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
        payload = request.body
        signature_header = request.META.get('HTTP_STRIPE_SIGNATURE')

        try:
            event = stripe.Webhook.construct_event(payload, signature_header, endpoint_secret)
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Webhook signature verification failed: {e}")
            return Response({'error': 'Invalid signature'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            return Response({'error': 'Webhook error'}, status=status.HTTP_400_BAD_REQUEST)

        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            course_id = session.metadata.get('course_id')
            user_id = session.metadata.get('user_id')

            if course_id and user_id:
                try:
                    course_instance = Course.objects.get(pk=course_id)
                    enrollment, created = CourseEnrollment.objects.get_or_create(
                        created_by_id=user_id,
                        course=course_instance,
                        defaults={'total_price': course_instance.price, 'has_paid': True},
                    )
                    if not created:
                        enrollment.has_paid = True
                        enrollment.save()
                    logger.info(f"Payment completed for enrollment ID: {enrollment.id}")
                except Course.DoesNotExist:
                    logger.error(f"Course not found: ID {course_id}")
                    return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
            else:
                logger.error("Invalid metadata in Stripe session")
                return Response({'error': 'Invalid metadata'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'success': 'Webhook processed'}, status=status.HTTP_200_OK)
