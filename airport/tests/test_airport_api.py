from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.tests.helpers import detail_url, sample_airport

AIRPORT_URL = reverse("airport:airport-list")
AIRPORT_DETAIL_VIEW_NAME = "airport:airport-detail"


class UnAuthenticatedAirportAPITest(TestCase):
    def setUp(self) -> None:
        airport = sample_airport()

        self.detail_url = detail_url(
            AIRPORT_DETAIL_VIEW_NAME,
            airport.id
        )
        self.client = APIClient()

    def test_airport_list_auth_required(self) -> None:
        response = self.client.get(AIRPORT_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_airport_detail_auth_required(self) -> None:
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_airport_create_auth_required(self) -> None:
        response = self.client.post(AIRPORT_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_airport_update_auth_required(self) -> None:
        response = self.client.put(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_airport_delete_auth_required(self) -> None:
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAirportViewTest(TestCase):

    def setUp(self) -> None:
        user = get_user_model().objects.create_user(
            email="user@user.com",
            password="password123",
        )
        self.airport = sample_airport()
        self.detail_url = detail_url(
            AIRPORT_DETAIL_VIEW_NAME,
            self.airport.id
        )
        self.client = APIClient()
        self.client.force_authenticate(user=user)

    def test_airport_list_permission_denied(self) -> None:
        response = self.client.get(AIRPORT_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_airport_create_permission_denied(self) -> None:
        response = self.client.post(AIRPORT_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_airport_detail_permission_denied(self) -> None:
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_airport_update_permission_denied(self) -> None:
        response = self.client.put(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_airport_delete_permission_denied(self) -> None:
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
