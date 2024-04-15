from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.tests.helpers import detail_url, sample_flight, sample_route

FLIGHT_URL = reverse("airport:flight-list")
FLIGHT_DETAIL_VIEW_NAME = "airport:flight-detail"


class UnAuthenticatedFlightAPITest(TestCase):
    def setUp(self) -> None:
        flight = sample_flight()
        self.detail_url = detail_url(
            FLIGHT_DETAIL_VIEW_NAME,
            flight.id
        )
        self.client = APIClient()

    def test_flight_list_auth_required(self) -> None:
        response = self.client.get(FLIGHT_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_flight_detail_auth_required(self) -> None:
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_flight_create_auth_required(self) -> None:
        response = self.client.post(FLIGHT_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_flight_update_auth_required(self) -> None:
        response = self.client.put(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_flight_delete_auth_required(self) -> None:
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
