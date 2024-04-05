from rest_framework import routers

from airport.views import CountryViewSet, CityViewSet

router = routers.DefaultRouter()

router.register("countries", CountryViewSet, basename="country")
router.register("cities", CityViewSet, basename="city")

urlpatterns = router.urls

app_name = "airport"
