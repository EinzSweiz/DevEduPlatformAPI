import pytest
from unittest.mock import patch, Mock
from rest_framework import status
from rest_framework.test import APIClient
from courses.conftest import create_course_enrollment, create_course
from useraccounts.conftest import create_user

@pytest.mark.django_db
@patch('stripe.checkout.Session.retrieve')
@patch('stripe.Customer.retrieve')
@pytest.mark.parametrize("mode", ["payment", "subscription"])
def test_payment_success(
    mock_stripe_customer_retrieve,
    mock_stripe_session_retrieve,
    api_client: APIClient,
    create_course,
    create_user,
    mode,
):
    user = create_user
    api_client.force_authenticate(user=user)

    # Mock Stripe session
    mock_session = Mock()
    mock_session.customer = "mock_customer_id"
    mock_session.metadata = {
        'course_id': create_course.id,
        'user_id': user.id,
        'total_price': create_course.price,
    }
    mock_session.mode = mode

    if mode == "subscription":
        # Properly structure subscription data
        mock_session.subscription = {"current_period_end": "2025-01-01T00:00:00Z"}
    mock_stripe_session_retrieve.return_value = mock_session

    # Mock Stripe customer
    mock_customer = Mock()
    mock_customer.id = user.id
    mock_customer.email = user.email
    mock_customer.name = user.name
    mock_stripe_customer_retrieve.return_value = mock_customer

    # Send GET request
    url = f"/api/stripe/payment/success/?session_id=mock_session_id"
    response = api_client.get(url)
    print("Response:", response)
    print("Data:", response.data)

    # Assertions
    assert response.status_code == 200
    data = response.data
    assert "success" in data

    if mode == "payment":
        assert "enrollment" in data["success"]
    elif mode == "subscription":
        assert "subscription_id" in data["success"]


@pytest.mark.django_db
@pytest.mark.parametrize("auth", [True, False])
def test_payment_cancel_view_parametrized(api_client: APIClient, create_course_enrollment, auth):
    course_enrollment = create_course_enrollment
    if auth:
        api_client.force_authenticate(user=course_enrollment.created_by)

    url = f"/api/stripe/payment/cancel/{course_enrollment.id}/"
    response = api_client.get(url)

    if auth:
        assert response.status_code == 400
        assert "error" in response.data
    else:
        assert response.status_code == 401

# @pytest.mark.django_db
# @patch('stripe.Webhook.construct_event')
# def test_webhook_checkout_session_completed(mock_construct_event, create_course, create_user, api_client:APIClient):
#     user = create_user
#     course = create_course
#     mock_event = {
#         "type": "checkout.session.completed",
#         "data": {
#             "object": {
#                 "metadata": {
#                     "course_id": str(course.id),
#                     "user_id": str(user.id),
#                 }
#             }
#         }
#     }
#     mock_construct_event.return_value = mock_event
#     api_client.force_authenticate(user=user)
#     response = api_client.post('/api/stripe/webhook/', data=mock_event, format='json')

#     assert response.status_code == 200
#     assert "success" in response.data
