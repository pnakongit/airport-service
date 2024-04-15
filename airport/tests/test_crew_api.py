from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Crew
from airport.tests.helpers import detail_url

CREW_URL = reverse("airport:crew-list")
CREW_DETAIL_VIEW_NAME = "airport:crew-detail"


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
