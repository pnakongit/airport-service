from typing import Type

from rest_framework import viewsets
from rest_framework.serializers import Serializer

from airport.models import Country, City
from airport.serializers import CountrySerializer, CitySerializer, CityListDetailSerializer


class CountryViewSet(viewsets.ModelViewSet):
    serializer_class = CountrySerializer
    queryset = Country.objects.all()


class CityViewSet(viewsets.ModelViewSet):
    serializer_class = CitySerializer
    queryset = City.objects.all()

    def get_serializer_class(self) -> Type[Serializer]:
        if self.action in ["list", "retrieve"]:
            return CityListDetailSerializer
        return super().get_serializer_class()
