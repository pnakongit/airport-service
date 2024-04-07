from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator

from airport.models import (
    Country,
    City,
    Airport,
    Route,
    Crew,
    Flight
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


class RouteListSerializer(RouteSerializer):
    source = serializers.SlugRelatedField(slug_field="name", read_only=True)
    destination = serializers.SlugRelatedField(slug_field="name", read_only=True)


class CrewSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField(source="get_full_name")

    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name", "full_name")


class FlightShortListSerializer(serializers.Serializer):
    flight = serializers.CharField(read_only=True, source="route")

    def create(self, validated_data: dict) -> None:
        pass

    def update(self, instance, validated_data: dict) -> None:
        pass


class FlightSerializer(serializers.ModelSerializer):

    def validate(self, data: dict) -> dict:
        departure_time = data.get("departure_time") or self.instance.departure_time
        arrival_time = data.get("arrival_time") or self.instance.arrival_time

        if arrival_time <= departure_time:
            raise ValidationError(
                {
                    "non_field_errors": "Arrival_time should be greater than Departure_time"
                }
            )
        return data

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "crew",
            "airplane",
            "departure_time",
            "arrival_time"
        )

        validators = [
            UniqueTogetherValidator(
                queryset=Flight.objects.all(),
                fields=["route", "airplane", "departure_time"]
            )
        ]
