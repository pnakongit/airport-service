from rest_framework import serializers

from airport.models import Country, City


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ("id", "name")


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ("id", "name", "country")


class CityListDetailSerializer(serializers.ModelSerializer):
    country = serializers.CharField(source="country.name", read_only=True)

    class Meta:
        model = City
        fields = ("id", "name", "country")
