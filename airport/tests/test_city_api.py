from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from rest_framework.test import APIClient

from airport.tests.helpers import sample_city

CITY_URL = reverse("airport:city-list")


def detail_url(city_id: int) -> str:
    return reverse("airport:city-detail", args=[city_id])


class UnAuthenticatedCountryApiTest(TestCase):
    def setUp(self) -> None:
        city = sample_city()
        self.detail_url = detail_url(city.id)
        self.client = APIClient()

    def test_city_list_auth_required(self) -> None:
        response = self.client.get(CITY_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_city_detail_auth_required(self) -> None:
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_city_create_auth_required(self) -> None:
        response = self.client.post(CITY_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_city_update_auth_required(self) -> None:
        response = self.client.put(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_city_delete_auth_required(self) -> None:
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
