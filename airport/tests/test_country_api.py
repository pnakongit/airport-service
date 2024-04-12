from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from rest_framework.test import APIClient

from airport.models import Country
from airport.serializers import CountrySerializer

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


class AuthenticatedCountryApiTest(TestCase):

    def setUp(self) -> None:
        user = get_user_model().objects.create_user(
            email="user@user.com",
            password="password123",
        )
        self.country = Country.objects.create(
            name="Test Country"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=user)

    def test_country_list_permission_denied(self) -> None:
        response = self.client.get(COUNTRY_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_country_create_permission_denied(self) -> None:
        response = self.client.post(COUNTRY_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_country_detail_permission_denied(self) -> None:
        response = self.client.get(detail_url(self.country.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_country_update_permission_denied(self) -> None:
        response = self.client.put(detail_url(self.country.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_country_delete_permission_denied(self) -> None:
        response = self.client.delete(detail_url(self.country.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class IsAdminCountryApiTest(TestCase):
    def setUp(self) -> None:
        admin_user = get_user_model().objects.create_user(
            email="admin_user@user.com",
            password="password123",
        )
        admin_user.is_staff = True
        admin_user.save()

        self.country = Country.objects.create(
            name="Country detail"
        )
        self.detail_url = detail_url(self.country.id)

        self.client = APIClient()
        self.client.force_authenticate(user=admin_user)

    def test_country_list(self) -> None:
        Country.objects.create(name="The USA")
        Country.objects.create(name="Poland")

        counties = Country.objects.all()
        expected_data = CountrySerializer(counties, many=True).data

        response = self.client.get(COUNTRY_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], expected_data)

    def test_country_list_is_paginated(self) -> None:
        page_size = 4

        count_countries = Country.objects.count()

        for i in range(page_size - count_countries + 1):
            Country.objects.create(name=f"Paginated Test Name {i}")

        first_page_country = Country.objects.all()[:page_size]
        second_page_country = Country.objects.all()[page_size:]

        serializer = CountrySerializer(first_page_country, many=True)
        response = self.client.get(COUNTRY_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

        response = self.client.get(COUNTRY_URL + "?page=" + str(2))
        serializer = CountrySerializer(second_page_country, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_country_create(self) -> None:
        payload = {"name": "Test Create Country"}

        response = self.client.post(COUNTRY_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        country = Country.objects.get(pk=response.data["id"])

        for key, value in payload.items():
            self.assertEqual(value, getattr(country, key))

    def test_country_detail(self) -> None:
        response = self.client.get(self.detail_url)
        serializer = CountrySerializer(self.country)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_country_update(self) -> None:
        country = self.country
        payload = {
            "id": country.id,
            "name": country.name + "new"
        }

        response = self.client.put(self.detail_url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        country = Country.objects.get(pk=response.data["id"])
        for key, value in payload.items():
            self.assertEqual(value, getattr(country, key))

    def test_country_delete(self) -> None:
        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Country.objects.filter(id=self.country.id).exists())
