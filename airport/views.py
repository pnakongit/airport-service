from typing import Type

from django.db.models import QuerySet
from rest_framework import viewsets
from rest_framework.serializers import Serializer

from airport.models import Country, City, Airport
from airport.serializers import (
    CountrySerializer,
    CitySerializer,
    CityListDetailSerializer,
    AirportSerializer,
    AirportListDetailSerializer
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
