from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Order
from airport.tests.helpers import detail_url

ORDER_URL = reverse("airport:order-list")
ORDER_DETAIL_VIEW_NAME = "airport:order-detail"


class UnAuthenticatedOrderAPITest(TestCase):
    def setUp(self) -> None:
        user = get_user_model().objects.create_user(
            email="user@user.com",
            password="password123"
        )
        order = Order.objects.create(user=user)
        self.detail_url = detail_url(
            ORDER_DETAIL_VIEW_NAME,
            order.id
        )
        self.client = APIClient()

    def test_order_list_auth_required(self) -> None:
        response = self.client.get(ORDER_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_order_detail_auth_required(self) -> None:
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_order_create_auth_required(self) -> None:
        response = self.client.post(ORDER_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
