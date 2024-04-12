from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from rest_framework.test import APIClient

from airport.models import City, Country
from airport.serializers import CitySerializer, CityListDetailSerializer
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


class AuthenticatedCityApiTest(TestCase):

    def setUp(self) -> None:
        user = get_user_model().objects.create_user(
            email="user@user.com",
            password="password1234",
        )
        city = sample_city()
        self.detail_url = detail_url(city.id)
        self.client = APIClient()
        self.client.force_authenticate(user=user)

    def test_city_list_permission_denied(self) -> None:
        response = self.client.get(CITY_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_city_detail_permission_denied(self) -> None:
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_city_create_permission_denied(self) -> None:
        response = self.client.post(CITY_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_city_update_permission_denied(self) -> None:
        response = self.client.put(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_city_delete_permission_denied(self) -> None:
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminCityApiTest(TestCase):

    def setUp(self) -> None:
        self.city = sample_city()
        admin_user = get_user_model().objects.create_user(
            email="admin_user@user.com",
            password="password1234"
        )
        admin_user.is_staff = True
        admin_user.save()
        self.detail_url = detail_url(self.city.id)
        self.client = APIClient()
        self.client.force_authenticate(user=admin_user)

    def test_city_list(self) -> None:
        sample_city(name="Test City Name 1")
        sample_city(name="Test City Name 2")

        response = self.client.get(CITY_URL)
        city_qs = City.objects.all()
        serializer = CityListDetailSerializer(city_qs, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_city_is_paginated(self) -> None:
        page_size = 4
        cities_count = City.objects.count()

        for i in range(page_size - cities_count + 1):
            sample_city(name="Test City Name " + str(i))

        first_page = City.objects.all()[:page_size]
        second_page = City.objects.all()[page_size:]

        response = self.client.get(CITY_URL)
        serializer = CityListDetailSerializer(first_page, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

        response = self.client.get(CITY_URL + "?page=" + str(2))
        serializer = CityListDetailSerializer(second_page, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_city_detail(self) -> None:
        response = self.client.get(self.detail_url)
        serializer = CityListDetailSerializer(self.city)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_city_create(self) -> None:
        country = Country.objects.create(name="Test Country")
        payload = {
            "name": "Test City Name 1",
            "country": country.id
        }

        response = self.client.post(CITY_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created_city = City.objects.get(id=response.data["id"])
        serializer = CitySerializer(created_city)
        for key, value in payload.items():
            self.assertEqual(serializer.data.get(key), value)

    def test_city_update(self) -> None:
        city = self.city
        payload = {
            "id": city.id,
            "name": city.name + "new",
            "country": city.country.id
        }

        response = self.client.put(self.detail_url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated_city = City.objects.get(pk=city.id)
        serializer = CitySerializer(updated_city)
        self.assertEqual(serializer.data, payload)

    def test_city_delete(self) -> None:
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(City.objects.filter(id=self.city.id).exists())
