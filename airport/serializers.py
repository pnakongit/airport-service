from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator

from airport.models import (
    Country,
    City,
    Airport,
    Route,
    Crew,
    Flight,
    AirplaneType,
    Airplane,
    Ticket,
    Order
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
            "crews",
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


class FlightDetailSerializer(FlightSerializer):
    route = serializers.StringRelatedField()
    crews = serializers.StringRelatedField(many=True)
    airplane = serializers.StringRelatedField()


class FlightListSerializer(FlightDetailSerializer):
    available_tickets = serializers.IntegerField(read_only=True)

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "crews",
            "airplane",
            "departure_time",
            "arrival_time",
            "available_tickets"
        )


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name")


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = (
            "id",
            "name",
            "rows",
            "seat_in_row",
            "image",
            "capacity",
            "airplane_type"
        )
        read_only_fields = ("image",)


class AirplaneImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ("id", "image")


class TicketSerializer(serializers.ModelSerializer):

    def validate(self, data: dict) -> dict:
        Ticket.validate_seat_and_row(
            data.get("seat"),
            data.get("row"),
            data.get("flight"),
            ValidationError
        )
        return data

    class Meta:
        model = Ticket
        fields = ("id", "seat", "row", "flight", "order")
        extra_kwargs = {
            "order": {
                "allow_null": True,
                "required": False
            }
        }


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ("id", "created_at", "user", "tickets")


class OrderCreateSerializer(OrderSerializer):
    tickets = TicketSerializer(many=True, required=False)

    def create(self, validated_data: dict) -> Order:
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets", None)
            order = Order.objects.create(**validated_data)
            if tickets_data:
                for ticket in tickets_data:
                    Ticket.objects.create(order=order, **ticket)
            return order
