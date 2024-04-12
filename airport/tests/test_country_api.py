from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from rest_framework.test import APIClient

from airport.models import Country

COUNTRY_URL = reverse("airport:country-list")


def detail_url(country_id: int) -> str:
    return reverse("airport:country-detail", args=[country_id])


class UnAuthenticatedCountryApiTest(TestCase):

    def setUp(self) -> None:
        self.country = Country.objects.create(
            name="Test Country"
        )
        self.client = APIClient()

    def test_country_list_auth_required(self) -> None:
        response = self.client.get(COUNTRY_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_country_detail_auth_required(self) -> None:
        response = self.client.get(detail_url(self.country.id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_country_create_auth_required(self) -> None:
        response = self.client.post(COUNTRY_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_country_update_auth_required(self) -> None:
        response = self.client.post(detail_url(self.country.id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_country_delete_auth_required(self) -> None:
        response = self.client.post(detail_url(self.country.id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


