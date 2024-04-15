from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.tests.helpers import detail_url, sample_airplane

AIRPLANE_URL = reverse("airport:airplane-list")
AIRPLANE_DETAIL_VIEW_NAME = "airport:airplane-detail"


class UnAuthenticatedAirplaneViewAPITest(TestCase):
    def setUp(self) -> None:
        airplane = sample_airplane()

        self.detail_url = detail_url(
            AIRPLANE_DETAIL_VIEW_NAME,
            airplane.id
        )
        self.client = APIClient()

    def test_airplane_list_auth_required(self) -> None:
        response = self.client.get(AIRPLANE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_airplane_detail_auth_required(self) -> None:
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_airplane_create_auth_required(self) -> None:
        response = self.client.post(AIRPLANE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_airplane_update_auth_required(self) -> None:
        response = self.client.put(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_airplane_delete_auth_required(self) -> None:
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAirplaneViewAPITest(TestCase):
    def setUp(self) -> None:
        user = get_user_model().objects.create_user(
            email="user@user.com",
            password="password123",
        )
        self.airplane = sample_airplane()
        self.detail_url = detail_url(
            AIRPLANE_DETAIL_VIEW_NAME,
            self.airplane.id
        )
        self.client = APIClient()
        self.client.force_authenticate(user=user)

    def test_airplane_list_permission_denied(self) -> None:
        response = self.client.get(AIRPLANE_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_airplane_create_permission_denied(self) -> None:
        response = self.client.post(AIRPLANE_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_airplane_detail_permission_denied(self) -> None:
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_airplane_update_permission_denied(self) -> None:
        response = self.client.put(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_airplane_delete_permission_denied(self) -> None:
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
