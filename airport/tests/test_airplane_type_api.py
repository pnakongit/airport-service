from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import AirplaneType
from airport.tests.helpers import detail_url

AIRPLANE_TYPE_URL = reverse("airport:airplane_type-list")
AIRPLANE_TYPE_DETAIL_VIEW_NAME = "airport:airplane_type-detail"


class UnAuthenticatedAirplaneTypeViewAPITest(TestCase):
    def setUp(self) -> None:
        airplane_type = AirplaneType.objects.create(
            name="Test Airplane Type",
        )

        self.detail_url = detail_url(
            AIRPLANE_TYPE_DETAIL_VIEW_NAME,
            airplane_type.id
        )
        self.client = APIClient()

    def test_airplane_type_list_auth_required(self) -> None:
        response = self.client.get(AIRPLANE_TYPE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_airplane_type_detail_auth_required(self) -> None:
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_airplane_type_create_auth_required(self) -> None:
        response = self.client.post(AIRPLANE_TYPE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_airplane_type_update_auth_required(self) -> None:
        response = self.client.put(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_airplane_type_delete_auth_required(self) -> None:
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
