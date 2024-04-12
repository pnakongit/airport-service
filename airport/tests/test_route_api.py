from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from rest_framework.test import APIClient

from airport.tests.helpers import detail_url, sample_route

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
