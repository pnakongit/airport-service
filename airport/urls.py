from rest_framework import routers

from airport.views import (
    CountryViewSet,
    CityViewSet,
    AirportViewSet,
    RouteViewSet,
    CrewViewSet
)

router = routers.DefaultRouter()

router.register("countries", CountryViewSet, basename="country")
router.register("cities", CityViewSet, basename="city")
router.register("airports", AirportViewSet, basename="airport")
router.register("routes", RouteViewSet, basename="route")
router.register("crews", CrewViewSet, basename="crew")

urlpatterns = router.urls

app_name = "airport"
