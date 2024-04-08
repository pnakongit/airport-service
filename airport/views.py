from typing import Type

from django.db.models import QuerySet, F, Count
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from airport.models import (
    Country,
    City,
    Airport,
    Route,
    Crew,
    Flight,
    Airplane,
    AirplaneType
)
from airport.serializers import (
    CountrySerializer,
    CitySerializer,
    CityListDetailSerializer,
    AirportSerializer,
    AirportListDetailSerializer,
    RouteSerializer,
    RouteListSerializer,
    CrewSerializer,
    FlightShortListSerializer,
    FlightSerializer,
    FlightDetailSerializer,
    FlightListSerializer,
    AirplaneTypeSerializer,
    AirplaneSerializer,
    AirplaneImageSerializer
)


class CountryViewSet(viewsets.ModelViewSet):
    serializer_class = CountrySerializer
    queryset = Country.objects.all()


class CityViewSet(viewsets.ModelViewSet):
    serializer_class = CitySerializer
    queryset = City.objects.all()

    def get_queryset(self) -> QuerySet:
        city_qs = super().get_queryset()
        if self.action == "list":
            return city_qs.select_related("country")
        return city_qs

    def get_serializer_class(self) -> Type[Serializer]:
        if self.action in ["list", "retrieve"]:
            return CityListDetailSerializer
        return super().get_serializer_class()


class AirportViewSet(viewsets.ModelViewSet):
    serializer_class = AirportSerializer
    queryset = Airport.objects.all()

    def get_queryset(self) -> QuerySet:
        airport_qs = super().get_queryset()
        if self.action == "list":
            return airport_qs.select_related("closest_big_city")

    def get_serializer_class(self) -> Type[Serializer]:
        if self.action in ["list", "retrieve"]:
            return AirportListDetailSerializer
        return super().get_serializer_class()


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer

    def get_queryset(self) -> QuerySet:
        route_qs = super().get_queryset()
        if self.action == "list":
            return route_qs.select_related("source", "destination")
        return route_qs

    def get_serializer_class(self) -> Type[Serializer]:
        if self.action in ["list"]:
            return RouteListSerializer
        return super().get_serializer_class()


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer

    def get_serializer_class(self) -> Type[Serializer]:
        if self.action == "flight_short_list":
            return FlightShortListSerializer
        return super().get_serializer_class()

    @action(
        methods=["get"],
        detail=True,
        url_path="flights",
        url_name="flight_short_list"
    )
    def flight_short_list(self, request: Request, pk=None) -> Response:
        """Endpoint returns a list of flights for the specific crew"""

        crew = self.get_object()
        flight_qs = crew.flights.all()
        serializer = self.get_serializer(flight_qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FlightViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer

    def get_serializer_class(self) -> Type[Serializer]:
        if self.action == "retrieve":
            return FlightDetailSerializer

        if self.action == "list":
            return FlightListSerializer
        return super().get_serializer_class()

    def get_queryset(self) -> QuerySet:
        flight_qs = super().get_queryset()
        if self.action in ["retrieve", "list"]:
            flight_qs = flight_qs.select_related(
                "airplane",
                "route__source",
                "route__destination"
            ).prefetch_related(
                "crews"
            )
        if self.action == "list":
            flight_qs = flight_qs.annotate(
                available_tickets=(
                                          F("airplane__rows") *
                                          F("airplane__seat_in_row")
                                  ) - Count("tickets")
            )
        return flight_qs


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    serializer_class = AirplaneTypeSerializer
    queryset = AirplaneType.objects.all()


class AirplaneViewSet(viewsets.ModelViewSet):
    serializer_class = AirplaneSerializer
    queryset = Airplane.objects.all()

    def get_serializer_class(self) -> Type[Serializer]:
        if self.action == "upload_image":
            return AirplaneImageSerializer
        return super().get_serializer_class()

    @action(
        methods=["post"],
        detail=True,
        url_path="upload-image",
        url_name="upload_image"
    )
    def upload_image(self, request: Request, pk: int = None) -> Response:
        """Endpoint for uploading image to specific airplane"""
        airplane = self.get_object()
        serializer = self.get_serializer(airplane, data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
