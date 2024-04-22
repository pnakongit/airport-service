from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.db.models import F, Count
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Flight
from airport.serializers import FlightListSerializer, FlightDetailSerializer
from airport.tests.helpers import detail_url, sample_flight, sample_route, sample_airport

FLIGHT_URL = reverse("airport:flight-list")
FLIGHT_DETAIL_VIEW_NAME = "airport:flight-detail"


class UnAuthenticatedFlightAPITest(TestCase):
    def setUp(self) -> None:
        flight = sample_flight()
        self.detail_url = detail_url(
            FLIGHT_DETAIL_VIEW_NAME,
            flight.id
        )
        self.client = APIClient()

    def test_flight_list_auth_required(self) -> None:
        response = self.client.get(FLIGHT_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_flight_detail_auth_required(self) -> None:
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_flight_create_auth_required(self) -> None:
        response = self.client.post(FLIGHT_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_flight_update_auth_required(self) -> None:
        response = self.client.put(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_flight_delete_auth_required(self) -> None:
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedFlightApiTest(TestCase):
    def setUp(self) -> None:
        user = get_user_model().objects.create_user(
            email="user@user.com",
            password="password123",
        )
        self.flight = sample_flight()
        self.detail_url = detail_url(
            FLIGHT_DETAIL_VIEW_NAME,
            self.flight.id
        )
        self.client = APIClient()
        self.client.force_authenticate(user=user)

    def test_flight_list(self) -> None:
        sample_flight()
        sample_flight()

        response = self.client.get(FLIGHT_URL)
        flight_qs = Flight.objects.annotate(
            available_tickets=(
                                      F("airplane__rows") *
                                      F("airplane__seats_in_row")
                              ) - Count("tickets")
        ).order_by("-departure_time", "id")
        serializer = FlightListSerializer(flight_qs, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_flight_list_is_paginated(self) -> None:
        page_size = 4
        flight_count = Flight.objects.count()

        for i in range(page_size - flight_count + 1):
            sample_flight()

        flight_qs = Flight.objects.annotate(
            available_tickets=(
                                      F("airplane__rows") *
                                      F("airplane__seats_in_row")
                              ) - Count("tickets")
        ).order_by("-departure_time", "id")
        first_page = flight_qs[:page_size]
        second_page = flight_qs[page_size:]

        response = self.client.get(FLIGHT_URL)
        serializer = FlightListSerializer(first_page, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

        response = self.client.get(FLIGHT_URL + "?page=" + str(2))
        serializer = FlightListSerializer(second_page, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_flight_list_filtering_by_start_departure_date(self) -> None:
        current_datetime = datetime.now()
        sample_flight(
            departure_time=current_datetime,
            arrival_time=current_datetime + timedelta(hours=2),
        )
        sample_flight(
            departure_time=current_datetime - timedelta(days=1),
            arrival_time=current_datetime,
        )
        sample_flight(
            departure_time=current_datetime + timedelta(days=1),
            arrival_time=current_datetime + timedelta(days=1, hours=2),
        )

        flight_qs = (
            Flight.objects
            .annotate(
                available_tickets=(
                                          F("airplane__rows") *
                                          F("airplane__seats_in_row")
                                  ) - Count("tickets")
            )
            .order_by("-departure_time", "id")
            .filter(
                departure_time__date__gte=current_datetime.date()
            )
        )
        response = self.client.get(
            FLIGHT_URL + f"?start_departure_date={current_datetime.date()}"
        )

        serializer = FlightListSerializer(flight_qs, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_flight_list_filtering_by_end_departure_date(self) -> None:
        current_datetime = datetime.now()
        sample_flight(
            departure_time=current_datetime,
            arrival_time=current_datetime + timedelta(hours=2),
        )
        sample_flight(
            departure_time=current_datetime - timedelta(days=1),
            arrival_time=current_datetime,
        )
        sample_flight(
            departure_time=current_datetime + timedelta(days=1),
            arrival_time=current_datetime + timedelta(days=1, hours=2),
        )

        flight_qs = (
            Flight.objects
            .annotate(
                available_tickets=(
                                          F("airplane__rows") *
                                          F("airplane__seats_in_row")
                                  ) - Count("tickets")
            )
            .filter(departure_time__date__lte=current_datetime.date())
            .order_by("-departure_time", "id")
        )

        response = self.client.get(
            FLIGHT_URL + f"?end_departure_date={current_datetime.date()}"
        )
        serializer = FlightListSerializer(flight_qs, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_flight_list_filtering_by_start_arrival_date(self) -> None:
        current_datetime = datetime.now()
        sample_flight(
            departure_time=current_datetime - timedelta(hours=1),
            arrival_time=current_datetime,
        )
        sample_flight(
            departure_time=current_datetime - timedelta(days=1, hours=1),
            arrival_time=current_datetime - timedelta(days=1),
        )
        sample_flight(
            departure_time=current_datetime + timedelta(days=1),
            arrival_time=current_datetime + timedelta(days=1, hours=1),
        )

        flight_qs = (
            Flight.objects
            .annotate(
                available_tickets=(
                                          F("airplane__rows") *
                                          F("airplane__seats_in_row")
                                  ) - Count("tickets")
            )
            .filter(arrival_time__date__gte=current_datetime.date())
            .order_by("-departure_time", "id")
        )

        response = self.client.get(
            FLIGHT_URL + f"?start_arrival_date={current_datetime.date()}"
        )
        serializer = FlightListSerializer(flight_qs, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_flight_list_filtering_by_end_arrival_date(self) -> None:
        current_datetime = datetime.now()
        sample_flight(
            departure_time=current_datetime - timedelta(hours=1),
            arrival_time=current_datetime,
        )
        sample_flight(
            departure_time=current_datetime - timedelta(days=1, hours=1),
            arrival_time=current_datetime - timedelta(days=1),
        )
        sample_flight(
            departure_time=current_datetime + timedelta(days=1),
            arrival_time=current_datetime + timedelta(days=1, hours=1),
        )

        flight_qs = (
            Flight.objects
            .annotate(
                available_tickets=(
                                          F("airplane__rows") *
                                          F("airplane__seats_in_row")
                                  ) - Count("tickets")
            )
            .filter(arrival_time__date__lte=current_datetime.date())
            .order_by("-departure_time", "id")
        )

        response = self.client.get(
            FLIGHT_URL + f"?end_arrival_date={current_datetime.date()}"
        )
        serializer = FlightListSerializer(flight_qs, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_flight_list_filtering_by_source(self) -> None:
        first_airport = sample_airport(name="ABC")
        second_airport = sample_airport(name="DBV")
        third_airport = sample_airport(name="RTG")

        first_route = sample_route(source=first_airport, destination=second_airport)
        second_route = sample_route(source=second_airport, destination=third_airport)
        third_route = sample_route(source=first_airport, destination=third_airport)

        sample_flight(route=first_route)
        sample_flight(route=second_route)
        sample_flight(route=third_route)

        flight_qs = (
            Flight.objects
            .annotate(
                available_tickets=(
                                          F("airplane__rows") *
                                          F("airplane__seats_in_row")
                                  ) - Count("tickets")
            )
            .filter(route__source__name__iexact=first_airport.name)
            .order_by("-departure_time", "id")
        )

        response = self.client.get(
            FLIGHT_URL + f"?source={first_airport.name}"
        )
        serializer = FlightListSerializer(flight_qs, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_flight_list_filtering_by_destination(self) -> None:
        first_airport = sample_airport(name="ABC")
        second_airport = sample_airport(name="DBV")
        third_airport = sample_airport(name="RTG")

        first_route = sample_route(source=first_airport, destination=second_airport)
        second_route = sample_route(source=second_airport, destination=third_airport)
        third_route = sample_route(source=first_airport, destination=third_airport)

        sample_flight(route=first_route)
        sample_flight(route=second_route)
        sample_flight(route=third_route)

        flight_qs = (
            Flight.objects
            .annotate(
                available_tickets=(
                                          F("airplane__rows") *
                                          F("airplane__seats_in_row")
                                  ) - Count("tickets")
            )
            .filter(route__destination__name__iexact=first_airport.name)
            .order_by("-departure_time", "id")
        )

        response = self.client.get(
            FLIGHT_URL + f"?destination={first_airport.name}"
        )
        serializer = FlightListSerializer(flight_qs, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_flight_detail(self) -> None:
        response = self.client.get(self.detail_url)
        serializer = FlightDetailSerializer(self.flight)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_flight_list_post_method_not_allowed(self) -> None:
        response = self.client.post(FLIGHT_URL)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_flight_detail_put_method_mot_allowed(self) -> None:
        response = self.client.put(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_flight_detail_delete_method_not_allowed(self) -> None:
        response = self.client.put(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
