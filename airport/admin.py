from django.contrib import admin

from airport.models import (
    Country,
    City,
    Airport,
    Route,
    AirplaneType,
    Airplane
)

admin.site.register(Country)
admin.site.register(City)
admin.site.register(Airport)
admin.site.register(Route)
admin.site.register(AirplaneType)
admin.site.register(Airplane)
