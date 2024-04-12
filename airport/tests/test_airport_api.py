from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Airport
from airport.serializers import AirportListDetailSerializer, AirportSerializer
from airport.tests.helpers import detail_url, sample_airport, sample_city

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


class AdminAirportDetailAPITest(TestCase):
    def setUp(self) -> None:
        admin_user = get_user_model().objects.create_user(
            email="admin_user@user.com",
            password="password123",
        )
        admin_user.is_staff = True
        admin_user.save()
        self.airport = sample_airport()
        self.detail_url = detail_url(
            AIRPORT_DETAIL_VIEW_NAME,
            self.airport.id
        )
        self.client = APIClient()
        self.client.force_authenticate(user=admin_user)

    def test_airport_list(self) -> None:
        sample_airport(
            name="Test Airport 1",
        )
        sample_airport(
            name="Test Airport 2",
        )

        response = self.client.get(AIRPORT_URL)
        airport_qs = Airport.objects.all()
        serializer = AirportListDetailSerializer(airport_qs, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_airport_is_paginated(self) -> None:
        page_size = 4
        airports_count = Airport.objects.count()

        for i in range(page_size - airports_count + 1):
            sample_airport(name="Test Airport" + str(i))

        first_page = Airport.objects.all()[:page_size]
        second_page = Airport.objects.all()[page_size:]

        response = self.client.get(AIRPORT_URL)
        serializer = AirportListDetailSerializer(first_page, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

        response = self.client.get(AIRPORT_URL + "?page=" + str(2))
        serializer = AirportListDetailSerializer(second_page, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_airport_detail(self) -> None:
        response = self.client.get(self.detail_url)
        serializer = AirportListDetailSerializer(self.airport)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_airport_create(self) -> None:
        closest_big_city = sample_city(name="Test Another City")
        payload = {
            "name": "Test Airport 1",
            "closest_big_city": closest_big_city.id
        }

        response = self.client.post(AIRPORT_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created_city = Airport.objects.get(id=response.data["id"])
        serializer = AirportSerializer(created_city)
        for key, value in payload.items():
            self.assertEqual(serializer.data.get(key), value)

    def test_airport_update(self) -> None:
        airport = self.airport
        payload = {
            "id": airport.id,
            "name": airport.name + "new",
            "closest_big_city": airport.closest_big_city.id
        }

        response = self.client.put(self.detail_url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated_airport = Airport.objects.get(pk=airport.id)
        serializer = AirportSerializer(updated_airport)
        self.assertEqual(serializer.data, payload)

    def test_airport_delete(self) -> None:
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Airport.objects.filter(id=self.airport.id).exists())
