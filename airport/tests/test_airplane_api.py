import os
import tempfile

from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Airplane, AirplaneType
from airport.serializers import AirplaneSerializer
from airport.tests.helpers import detail_url, sample_airplane

AIRPLANE_URL = reverse("airport:airplane-list")
AIRPLANE_DETAIL_VIEW_NAME = "airport:airplane-detail"
IMAGE_UPLOAD_VIEW_NAME = "airport:airplane-upload_image"


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


class AdminAirplaneViewApiTest(TestCase):
    def setUp(self) -> None:
        admin_user = get_user_model().objects.create_user(
            email="admin_user@user.com",
            password="password123",
        )
        admin_user.is_staff = True
        admin_user.save()
        self.airplane = sample_airplane()
        self.detail_url = detail_url(
            AIRPLANE_DETAIL_VIEW_NAME,
            self.airplane.id
        )
        self.client = APIClient()
        self.client.force_authenticate(user=admin_user)

    def test_airplane_list(self) -> None:
        sample_airplane(name="Test Airplane Name 1")
        sample_airplane(name="Test Airplane Name 2")

        response = self.client.get(AIRPLANE_URL)
        airplane_qs = Airplane.objects.all()
        serializer = AirplaneSerializer(airplane_qs, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_airplane_is_paginated(self) -> None:
        page_size = 4
        airplane_count = Airplane.objects.count()

        for i in range(page_size - airplane_count + 1):
            sample_airplane(name="Test Airplane Name " + str(i))

        first_page = Airplane.objects.all()[:page_size]
        second_page = Airplane.objects.all()[page_size:]

        response = self.client.get(AIRPLANE_URL)
        serializer = AirplaneSerializer(first_page, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

        response = self.client.get(AIRPLANE_URL + "?page=" + str(2))
        serializer = AirplaneSerializer(second_page, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_airplane_detail(self) -> None:
        response = self.client.get(self.detail_url)
        serializer = AirplaneSerializer(self.airplane)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_airplane_create(self) -> None:
        airplane_type = AirplaneType.objects.create(
            name="Test Airplane Type 1"
        )
        payload = {
            "name": "Test Airplane 1",
            "rows": 15,
            "seats_in_row": 15,
            "airplane_type": airplane_type.id
        }

        response = self.client.post(AIRPLANE_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created_airplane = Airplane.objects.get(id=response.data["id"])
        serializer = AirplaneSerializer(created_airplane)

        for key, value in payload.items():
            self.assertEqual(serializer.data[key], value)

    def test_airplane_update(self) -> None:
        airplane = self.airplane
        payload = {
            "id": airplane.id,
            "name": airplane.name + "new",
            "rows": airplane.rows,
            "seats_in_row": airplane.seats_in_row,
            "airplane_type": airplane.airplane_type.id
        }

        response = self.client.put(self.detail_url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        airplane.refresh_from_db()
        serializer = AirplaneSerializer(airplane)

        for key, value in payload.items():
            self.assertEqual(serializer.data[key], value)

    def test_airplane_delete(self) -> None:
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Airplane.objects.filter(id=self.airplane.id).exists()
        )


class UploadImageTest(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            email="user@user.com",
            password="password123",
        )
        self.user.is_staff = True
        self.user.save()
        self.airplane = sample_airplane()
        self.upload_url = detail_url(
            IMAGE_UPLOAD_VIEW_NAME,
            self.airplane.id
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_upload_image_auth_required(self) -> None:
        self.client.logout()
        methods = [
            self.client.get,
            self.client.post,
            self.client.put,
            self.client.delete,
        ]

        for method in methods:
            with self.subTest(method=method):
                response = method(self.upload_url)
                self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_upload_image_if_authenticated_user_permission_denied(self) -> None:
        self.user.is_staff = False
        self.user.save()
        methods = [
            self.client.get,
            self.client.post,
            self.client.put,
            self.client.delete,
        ]

        for method in methods:
            with self.subTest(method=method):
                response = method(self.upload_url)
                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_upload_image_get_put_delete_methods_not_allowed(self) -> None:

        methods = [
            self.client.get,
            self.client.put,
            self.client.delete,
        ]

        for method in methods:
            with self.subTest(method=method):
                response = method(self.upload_url)
                self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_upload_image_add_image_to_airplane(self) -> None:

        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            response = self.client.post(
                self.upload_url, {"image": ntf}, format="multipart"
            )

        self.airplane.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(os.path.exists(self.airplane.image.path))
