from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from rest_framework.test import APIClient

from airport.models import Route
from airport.serializers import RouteListSerializer, RouteSerializer
from airport.tests.helpers import detail_url, sample_route, sample_airport

ROUTE_URL = reverse("airport:route-list")
ROUTE_DETAIL_VIEW_NAME = "airport:route-detail"


class UnAuthenticatedRouteViewApiTests(TestCase):

    def setUp(self) -> None:
        route = sample_route()
        self.detail_url = detail_url(
            ROUTE_DETAIL_VIEW_NAME,
            route.pk
        )
        self.client = APIClient()

    def test_route_list_auth_required(self) -> None:
        response = self.client.get(ROUTE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_route_detail_auth_required(self) -> None:
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_route_create_auth_required(self) -> None:
        response = self.client.post(ROUTE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_route_update_auth_required(self) -> None:
        response = self.client.put(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_route_delete_auth_required(self) -> None:
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedRouteViewApiTests(TestCase):
    def setUp(self) -> None:
        user = get_user_model().objects.create_user(
            email="user@user.com",
            password="password1234"
        )
        self.route = sample_route()
        self.detail_url = detail_url(
            ROUTE_DETAIL_VIEW_NAME,
            self.route.pk
        )
        self.client = APIClient()
        self.client.force_authenticate(user=user)

    def test_route_list(self) -> None:
        sample_route()
        sample_route()

        response = self.client.get(ROUTE_URL)
        airport_qs = Route.objects.all()
        serializer = RouteListSerializer(airport_qs, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_route_list_is_paginated(self) -> None:
        page_size = 4
        routes_count = Route.objects.count()

        for i in range(page_size - routes_count + 1):
            sample_route()

        first_page = Route.objects.all()[:page_size]
        second_page = Route.objects.all()[page_size:]

        response = self.client.get(ROUTE_URL)
        serializer = RouteListSerializer(first_page, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

        response = self.client.get(ROUTE_URL + "?page=" + str(2))
        serializer = RouteListSerializer(second_page, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_route_create_permission_denied(self) -> None:
        response = self.client.post(ROUTE_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_route_detail(self) -> None:
        response = self.client.get(self.detail_url)
        serializer = RouteSerializer(self.route)
        self.assertEqual(response.data, serializer.data)

    def test_route_update_permission_denied(self) -> None:
        response = self.client.put(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_route_delete_permission_denied(self) -> None:
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminRouteViewApiTests(TestCase):
    def setUp(self) -> None:
        admin_user = get_user_model().objects.create_user(
            email="admin_user@user.com",
            password="password1234"
        )
        admin_user.is_staff = True
        admin_user.save()
        self.route = sample_route()
        self.detail_url = detail_url(
            ROUTE_DETAIL_VIEW_NAME,
            self.route.pk
        )
        self.client = APIClient()
        self.client.force_authenticate(user=admin_user)

    def test_route_list_available(self) -> None:
        response = self.client.get(ROUTE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_route_create(self) -> None:
        payload = {
            "source": sample_airport(name="Test Airport 1").pk,
            "destination": sample_airport(name="Test Airport 2").pk,
            "distance": 500
        }

        response = self.client.post(ROUTE_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created_route = Route.objects.get(pk=response.data["id"])
        serializer = RouteSerializer(created_route)

        for key, value in payload.items():
            self.assertEqual(serializer.data[key], value)

    def test_route_detail_available(self) -> None:
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_route_update(self) -> None:
        payload = {
            "id": self.route.id,
            "source": self.route.source.pk,
            "destination": self.route.destination.pk,
            "distance": self.route.distance + 100
        }

        response = self.client.put(self.detail_url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated_route = Route.objects.get(pk=self.route.id)
        serializer = RouteSerializer(updated_route)
        self.assertEqual(serializer.data, payload)

    def test_route_delete(self) -> None:
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Route.objects.filter(id=self.route.id).exists())
