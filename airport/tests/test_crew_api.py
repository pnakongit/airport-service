from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Crew
from airport.serializers import CrewSerializer, FlightShortListSerializer
from airport.tests.helpers import detail_url, sample_flight

CREW_URL = reverse("airport:crew-list")
CREW_DETAIL_VIEW_NAME = "airport:crew-detail"
FLIGHT_SHORT_LIST_URL_NAME = "airport:crew-flight_short_list"


class UnAuthenticatedCrewAPITest(TestCase):
    def setUp(self) -> None:
        crew = Crew.objects.create(
            first_name="John",
            last_name="Doe",
        )

        self.detail_url = detail_url(
            CREW_DETAIL_VIEW_NAME,
            crew.id
        )
        self.client = APIClient()

    def test_crew_list_auth_required(self) -> None:
        response = self.client.get(CREW_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_crew_detail_auth_required(self) -> None:
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_crew_create_auth_required(self) -> None:
        response = self.client.post(CREW_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_crew_update_auth_required(self) -> None:
        response = self.client.put(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_crew_delete_auth_required(self) -> None:
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedCrewApiTest(TestCase):
    def setUp(self) -> None:
        user = get_user_model().objects.create_user(
            email="user@user.com",
            password="password1234"
        )
        self.crew = Crew.objects.create(
            first_name="John",
            last_name="Doe",
        )
        self.detail_url = detail_url(
            CREW_DETAIL_VIEW_NAME,
            self.crew.pk
        )
        self.client = APIClient()
        self.client.force_authenticate(user=user)

    def test_crew_list_permission_denied(self) -> None:
        response = self.client.get(CREW_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_crew_detail_permission_denied(self) -> None:
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_crew_create_permission_denied(self) -> None:
        response = self.client.post(CREW_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_crew_update_permission_denied(self) -> None:
        response = self.client.put(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_crew_delete_permission_denied(self) -> None:
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminCrewApiTest(TestCase):
    def setUp(self) -> None:
        admin_user = get_user_model().objects.create_user(
            email="admin_user@user.com",
            password="password123",
        )
        admin_user.is_staff = True
        admin_user.save()
        self.crew = Crew.objects.create(
            first_name="John",
            last_name="Doe",
        )
        self.detail_url = detail_url(
            CREW_DETAIL_VIEW_NAME,
            self.crew.id
        )
        self.client = APIClient()
        self.client.force_authenticate(user=admin_user)

    def test_crew_list(self) -> None:
        Crew.objects.create(
            first_name="Test first name 1",
            last_name="Test last name 1",
        )
        Crew.objects.create(
            first_name="Test first name 2",
            last_name="Test last name 2",
        )

        response = self.client.get(CREW_URL)
        crew_qs = Crew.objects.all()
        serializer = CrewSerializer(crew_qs, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_crew_list_is_paginated(self) -> None:
        page_size = 4
        crew_count = Crew.objects.count()

        for i in range(page_size - crew_count + 1):
            Crew.objects.create(
                first_name=f"Test first name {i}",
                last_name=f"Test last name {i}"
            )

        first_page = Crew.objects.all()[:page_size]
        second_page = Crew.objects.all()[page_size:]

        response = self.client.get(CREW_URL)
        serializer = CrewSerializer(first_page, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

        response = self.client.get(CREW_URL + "?page=" + str(2))
        serializer = CrewSerializer(second_page, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_crew_detail(self) -> None:
        response = self.client.get(self.detail_url)
        serializer = CrewSerializer(self.crew)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_crew_create(self) -> None:
        payload = {
            "first_name": "Test first name 1",
            "last_name": "Test last name 1",
        }

        response = self.client.post(CREW_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created_crew = Crew.objects.get(id=response.data["id"])

        for key, value in payload.items():
            self.assertEqual(getattr(created_crew, key), value)

    def test_crew_update(self) -> None:
        crew = self.crew
        payload = {
            "id": crew.id,
            "first_name": crew.first_name + "new",
            "last_name": crew.last_name + "new",
        }

        response = self.client.put(self.detail_url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        crew.refresh_from_db()

        for key, value in payload.items():
            self.assertEqual(getattr(crew, key), value)

    def test_crew_delete(self) -> None:
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Crew.objects.filter(id=self.crew.id).exists()
        )


class FlightShortListTest(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            email="user@user.com",
            password="password123",
        )
        self.user.is_staff = True
        self.user.save()
        self.crew = Crew.objects.create(
            first_name="Test first name 1",
            last_name="Test last name 1",
        )
        self.flight_short_list = detail_url(
            FLIGHT_SHORT_LIST_URL_NAME,
            self.crew.id
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_flight_short_list_auth_required(self) -> None:
        self.client.logout()
        methods = [
            self.client.get,
            self.client.post,
            self.client.put,
            self.client.delete,
        ]

        for method in methods:
            with self.subTest(method=method):
                response = method(self.flight_short_list)
                self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_flight_short_list_if_authenticated_user_permission_denied(self) -> None:
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
                response = method(self.flight_short_list)
                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_flight_short_list_post_put_delete_methods_not_allowed(self) -> None:

        methods = [
            self.client.post,
            self.client.put,
            self.client.delete,
        ]

        for method in methods:
            with self.subTest(method=method):
                response = method(self.flight_short_list)
                self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_flight_short_list(self) -> None:
        first_crew = self.crew
        second_crew = Crew.objects.create()

        first_flight = sample_flight()
        first_flight.crews.add(first_crew)
        second_flight = sample_flight()
        second_flight.crews.add(first_crew)
        third_flight = sample_flight()
        third_flight.crews.add(second_crew)

        response = self.client.get(self.flight_short_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        flight_qs = first_crew.flights.all()
        serializer = FlightShortListSerializer(flight_qs, many=True)

        self.assertEqual(response.data, serializer.data)
