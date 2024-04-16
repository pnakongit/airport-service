from django.urls import path, include
from rest_framework import routers
from rest_framework_nested import routers as nested_routers
from airport.views import (
    CountryViewSet,
    CityViewSet,
    AirportViewSet,
    RouteViewSet,
    CrewViewSet,
    FlightViewSet,
    AirplaneViewSet,
    AirplaneTypeViewSet,
    OrderViewSet,
    TicketNestedViewSet
)

router = routers.DefaultRouter()

router.register("countries", CountryViewSet, basename="country")
router.register("cities", CityViewSet, basename="city")
router.register("airports", AirportViewSet, basename="airport")
router.register("routes", RouteViewSet, basename="route")
router.register("crews", CrewViewSet, basename="crew")
router.register("flights", FlightViewSet, basename="flight")
router.register("airplanes", AirplaneViewSet, basename="airplane")
router.register("airplane-types", AirplaneTypeViewSet, basename="airplane_type")
router.register("orders", OrderViewSet, basename="order")

orders_router = nested_routers.NestedSimpleRouter(router, "orders", lookup="order")
orders_router.register("tickets", TicketNestedViewSet, basename="order_ticket")

urlpatterns = [
    path("", include(router.urls)),
    path("", include(orders_router.urls))
]

app_name = "airport"
