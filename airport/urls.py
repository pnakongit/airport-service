from rest_framework import routers

from airport.views import CountryViewSet

router = routers.DefaultRouter()
router.register("countries", CountryViewSet, basename="country")

urlpatterns = router.urls

app_name = "airport"
