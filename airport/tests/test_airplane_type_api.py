from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import AirplaneType
from airport.serializers import AirplaneTypeSerializer
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


class AuthenticatedAirplaneTypeViewApiTests(TestCase):
    def setUp(self) -> None:
        user = get_user_model().objects.create_user(
            email="user@user.com",
            password="password1234"
        )
        self.airplane_type = AirplaneType.objects.create(
            name="Test Airplane Type",
        )
        self.detail_url = detail_url(
            AIRPLANE_TYPE_DETAIL_VIEW_NAME,
            self.airplane_type.pk
        )
        self.client = APIClient()
        self.client.force_authenticate(user=user)

    def test_airplane_type_list_permission_denied(self) -> None:
        response = self.client.get(AIRPLANE_TYPE_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_airplane_type_detail_permission_denied(self) -> None:
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_airplane_type_create_permission_denied(self) -> None:
        response = self.client.post(AIRPLANE_TYPE_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_airplane_type_update_permission_denied(self) -> None:
        response = self.client.put(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_airplane_type_delete_permission_denied(self) -> None:
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirplaneTypeViewApiTests(TestCase):
    def setUp(self) -> None:
        admin_user = get_user_model().objects.create_user(
            email="admin_user@user.com",
            password="password123",
        )
        admin_user.is_staff = True
        admin_user.save()
        self.airplane_type = AirplaneType.objects.create(
            name="Test Airplane Type",
        )
        self.detail_url = detail_url(
            AIRPLANE_TYPE_DETAIL_VIEW_NAME,
            self.airplane_type.id
        )
        self.client = APIClient()
        self.client.force_authenticate(user=admin_user)

    def test_airplane_type_list(self) -> None:
        AirplaneType.objects.create(
            name="Test Airplane Type 1",
        )
        AirplaneType.objects.create(
            name="Test Airplane Type 2",
        )

        response = self.client.get(AIRPLANE_TYPE_URL)
        airplane_type_qs = AirplaneType.objects.all()
        serializer = AirplaneTypeSerializer(airplane_type_qs, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_airplane_type_is_paginated(self) -> None:
        page_size = 4
        airplane_types_count = AirplaneType.objects.count()

        for i in range(page_size - airplane_types_count + 1):
            AirplaneType.objects.create(name="Test Airport Type" + str(i))

        first_page = AirplaneType.objects.all()[:page_size]
        second_page = AirplaneType.objects.all()[page_size:]

        response = self.client.get(AIRPLANE_TYPE_URL)
        serializer = AirplaneTypeSerializer(first_page, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

        response = self.client.get(AIRPLANE_TYPE_URL + "?page=" + str(2))
        serializer = AirplaneTypeSerializer(second_page, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_airplane_type_detail(self) -> None:
        response = self.client.get(self.detail_url)
        serializer = AirplaneTypeSerializer(self.airplane_type)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_airplane_type_create(self) -> None:
        payload = {
            "name": "Test Airplane Type 1"
        }

        response = self.client.post(AIRPLANE_TYPE_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created_airplane_type = AirplaneType.objects.get(id=response.data["id"])
        self.assertEqual(created_airplane_type.name, payload["name"])

    def test_airplane_type_update(self) -> None:
        airplane_type = self.airplane_type
        payload = {
            "id": airplane_type.id,
            "name": airplane_type.name + "new"
        }

        response = self.client.put(self.detail_url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        airplane_type.refresh_from_db()

        self.assertEqual(airplane_type.name, payload["name"])

    def test_airplane_type_delete(self) -> None:
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            AirplaneType.objects.filter(id=self.airplane_type.id).exists()
        )
