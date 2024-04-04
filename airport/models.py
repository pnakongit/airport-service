from django.db import models


class Country(models.Model):
    name = models.CharField(max_length=25)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name
