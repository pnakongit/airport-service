from rest_framework import viewsets

from airport.models import Country
from airport.serializers import CountrySerializer


class CountryViewSet(viewsets.ModelViewSet):
    serializer_class = CountrySerializer
    queryset = Country.objects.all()
