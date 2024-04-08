from rest_framework import routers

from airport.views import (
    CountryViewSet,
    CityViewSet,
    AirportViewSet,
    RouteViewSet,
    CrewViewSet,
    FlightViewSet,
    AirplaneTypeViewSet
)

router = routers.DefaultRouter()

router.register("countries", CountryViewSet, basename="country")
router.register("cities", CityViewSet, basename="city")
router.register("airports", AirportViewSet, basename="airport")
router.register("routes", RouteViewSet, basename="route")
router.register("crews", CrewViewSet, basename="crew")
router.register("flights", FlightViewSet, basename="flight")
router.register("airplane-types", AirplaneTypeViewSet, basename="airplane_type")

urlpatterns = router.urls

app_name = "airport"
