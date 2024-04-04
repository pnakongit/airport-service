from django.db import models


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
