from django.db import models
from django.db.models import Q, F


class Country(models.Model):
    name = models.CharField(max_length=25)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class City(models.Model):
    name = models.CharField(max_length=25)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="cities")

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Airport(models.Model):
    name = models.CharField(max_length=25)
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
            )
        ]

    def __str__(self) -> str:
        return f"{self.id}. {self.source.name} - {self.destination.name}"


class AirplaneType(models.Model):
    name = models.CharField(max_length=25)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name
