from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q, F


class Country(models.Model):
    name = models.CharField(max_length=25, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "countries"

    def __str__(self) -> str:
        return self.name


class City(models.Model):
    name = models.CharField(max_length=25, unique=True)
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name="cities"
    )

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "cities"

    def __str__(self) -> str:
        return self.name


class Airport(models.Model):
    name = models.CharField(max_length=25, unique=True)
    closest_big_city = models.ForeignKey(
        City,
        on_delete=models.SET_NULL,
        related_name="airports",
        blank=True,
        null=True
    )

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Route(models.Model):
    source = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="source_routes"
    )
    destination = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="destination_routes"
    )
    distance = models.PositiveIntegerField()

    class Meta:
        ordering = ["id"]
        constraints = [
            models.CheckConstraint(
                check=~Q(source=F("destination")),
                name="source_destination_not_equal",
                violation_error_message="The source and the destination can't be the same."
            ),
            models.UniqueConstraint(
                fields=("source", "destination"),
                name="unique_source_destination"
            )
        ]

    def __str__(self) -> str:
        return f"{self.id}. {self.source.name} - {self.destination.name}"


class AirplaneType(models.Model):
    name = models.CharField(max_length=25, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Airplane(models.Model):
    name = models.CharField(max_length=25, unique=True)
    rows = models.PositiveIntegerField()
    seat_in_row = models.PositiveIntegerField()
    airplane_type = models.ForeignKey(
        AirplaneType,
        on_delete=models.CASCADE,
        related_name="airplanes"
    )

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Crew(models.Model):
    first_name = models.CharField(max_length=35)
    last_name = models.CharField(max_length=35)

    def __str__(self) -> str:
        return self.get_full_name()

    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Flight(models.Model):
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name="flights"
    )
    crews = models.ManyToManyField(
        Crew,
        related_name="flights"
    )
    airplane = models.ForeignKey(
        Airplane,
        on_delete=models.SET_NULL,
        null=True,
        related_name="flights"
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    class Meta:
        ordering = ["-departure_time"]
        constraints = [
            models.CheckConstraint(
                check=Q(arrival_time__gt=F("departure_time")),
                name="arrival_time_greater_than_departure_time"
            ),
            models.UniqueConstraint(
                fields=["route", "airplane", "departure_time"],
                name="unique_route_airplane_departure_time"
            )
        ]

    def __str__(self) -> str:
        return f"{self.route} | {self.departure_time}"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="orders"
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.id}. {self.created_at}"


class Ticket(models.Model):
    row = models.PositiveIntegerField()
    seat = models.PositiveIntegerField()
    flight = models.ForeignKey(
        Flight,
        on_delete=models.CASCADE,
        related_name="tickets"
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="tickets"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("row", "seat", "flight"),
                name="unique_row_seat_flight"
            )
        ]

    def __str__(self) -> str:
        return f"Flight ID:{self.flight_id}. Seat; {self.seat}. Row; {self.row}"

    @staticmethod
    def validate_seat_and_row(
            seat: int,
            row: int,
            flight: Flight,
            error_to_raise
    ) -> None:
        attrs = (
            (row, "row", "rows"),
            (seat, "seat", "seat_in_row")
        )
        errors = {}
        for attr_value, attr_name, airplane_attr_name in attrs:
            airplane_attr_value = getattr(flight.airplane, airplane_attr_name)

            if not (0 < attr_value <= airplane_attr_value):
                errors.update(
                    {
                        attr_name: f"{attr_name.title()} must be in available range:"
                                   f"(1, {airplane_attr_value})"
                    }
                )
        if errors:
            raise error_to_raise(errors)

    def clean(self) -> None:
        self.validate_seat_and_row(
            self.seat,
            self.row,
            self.flight,
            ValidationError
        )
