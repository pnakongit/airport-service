from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator

from airport.models import (
    Country,
    City,
    Airport,
    Route
)


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ("id", "name")


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ("id", "name", "country")


class CityListDetailSerializer(CitySerializer):
    country = serializers.CharField(source="country.name", read_only=True)


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "name", "closest_big_city")

        extra_kwargs = {
            "closest_big_city": {
                "required": True,
                "allow_null": False
            }
        }


class AirportListDetailSerializer(AirportSerializer):
    closest_big_city = serializers.SlugRelatedField(
        read_only=True,
        slug_field="name"
    )


class RouteSerializer(serializers.ModelSerializer):

    def validate(self, attrs: dict) -> dict:
        source = attrs.get("source") or self.instance.source
        destination = attrs.get("destination") or self.instance.detination
        if source == destination:
            raise ValidationError(
                {
                    "non_field_errors": "The source and the destination can't be the same."
                }
            )
        return attrs

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")

        validator = [
            UniqueTogetherValidator(
                queryset=Route.objects.all(),
                fields=["source", "destination"]
            )
        ]
